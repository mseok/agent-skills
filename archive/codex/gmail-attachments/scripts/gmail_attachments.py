#!/usr/bin/env python3
"""Download Gmail attachments to disk over IMAP; standard library only.

Credentials are a Gmail address and a Google app password stored with mode 600 under
~/.config/gmail-attachments/ (create them with --store-app-password in your own terminal).
The mailbox is opened read-only and messages are fetched with BODY.PEEK, so nothing is
marked as read or changed.
"""

import argparse
import email
import email.policy
import getpass
import hashlib
import imaplib
import json
import os
import re
import ssl
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

HOST = "imap.gmail.com"
MAX_STEM_BYTES = 180
DEFAULT_DEST = Path("references") / "gmail"  # relative to the current directory


class GmailError(RuntimeError):
    pass


def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "gmail-attachments"


def write_private(path, raw):
    tmp = path.with_name(path.name + ".part")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(raw)
    os.replace(tmp, path)


def read_private(path):
    if not path.exists():
        raise GmailError(
            f"missing {path}; run --store-app-password in your own terminal"
        )
    if path.stat().st_mode & 0o077:
        raise GmailError(f"{path} must not be group/world accessible: chmod 600 {path}")
    return path.read_text().strip()


def store_credentials():
    if not sys.stdin.isatty():
        raise GmailError(
            "run --store-app-password in your own terminal (hidden prompt needs a TTY)"
        )
    user = input("Gmail address: ").strip()
    password = "".join(getpass.getpass("App password (hidden): ").split())
    if "@" not in user or len(password) != 16:
        raise GmailError("expected a Gmail address and a 16-character app password")
    cfg = config_dir()
    cfg.mkdir(parents=True, exist_ok=True)
    cfg.chmod(0o700)
    write_private(cfg / "user", (user + "\n").encode())
    write_private(cfg / "app_password", (password + "\n").encode())
    print(f"stored in {cfg} (mode 600); verify with --check")
    return 0


def ok(reply, what):
    typ, data = reply
    if typ != "OK":
        raise GmailError(f"IMAP {what} failed: {data}")
    return data


def connect():
    cfg = config_dir()
    user = os.environ.get("GMAIL_USER") or read_private(cfg / "user")
    password = "".join(read_private(cfg / "app_password").split())
    try:
        context = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(HOST, 993, ssl_context=context, timeout=60)
        imap.login(user, password)
    except imaplib.IMAP4.error as e:
        raise GmailError(f"IMAP login failed: {e}") from e
    return imap


def all_mail(imap):
    for raw in ok(imap.list(), "list"):
        match = re.match(r'\(([^)]*)\) "[^"]*" (.+)$', raw.decode())
        if match and "\\All" in match[1].split():
            return match[2]
    raise GmailError("Gmail 'All Mail' mailbox not found")


def find_uids(imap, args):
    uids = []
    for mid in args.message:
        try:
            gm_id = int(mid, 16)
        except ValueError:
            raise GmailError(
                f"--message expects a Gmail message ID (hex), got {mid!r}"
            ) from None
        uids += ok(imap.uid("SEARCH", "X-GM-MSGID", str(gm_id)), "search")[0].split()
    if args.query:
        imap.literal = args.query.encode()
        reply = imap.uid("SEARCH", "CHARSET", "UTF-8", "X-GM-RAW")
        uids += ok(reply, "search")[0].split()[-args.max :]
    return list(dict.fromkeys(uids))


def fetch_message(imap, uid):
    data = ok(
        imap.uid("FETCH", uid, "(X-GM-MSGID X-GM-THRID INTERNALDATE BODY.PEEK[])"),
        "fetch",
    )
    meta = b" ".join(item[0] if isinstance(item, tuple) else item for item in data)
    raw = next(item[1] for item in data if isinstance(item, tuple))
    msg_id = format(int(re.search(rb"X-GM-MSGID (\d+)", meta)[1]), "x")
    thread_id = format(int(re.search(rb"X-GM-THRID (\d+)", meta)[1]), "x")
    received = imaplib.Internaldate2tuple(meta)
    return (
        msg_id,
        thread_id,
        received,
        email.message_from_bytes(raw, policy=email.policy.default),
    )


def attachments(msg):
    for part in msg.walk():
        name = part.get_filename()
        if name and not part.is_multipart():
            payload = part.get_payload(decode=True)
            if payload is not None:
                yield name, part.get_content_type(), payload


def safe_name(name):
    clean = unicodedata.normalize("NFC", name)
    clean = re.sub(r'[\x00-\x1f/\\:*?"<>|\s]+', "_", clean).strip("._")
    stem, suffix = os.path.splitext(clean or "attachment")
    return stem.encode()[:MAX_STEM_BYTES].decode(errors="ignore") + suffix


def parse_exts(value):
    if value == "all":
        return None
    return {e.strip().lower().lstrip(".") for e in value.split(",") if e.strip()}


def fetch(args):
    exts = parse_exts(args.ext)
    dest = Path(args.dest).expanduser().resolve()
    counts = {"saved": 0, "exists": 0, "dry-run": 0}
    imap = connect()
    try:
        ok(imap.select(all_mail(imap), readonly=True), "select")
        for uid in find_uids(imap, args):
            mid, thread_id, received, msg = fetch_message(imap, uid)
            taken = set()
            for index, (name, mime, payload) in enumerate(attachments(msg)):
                if (
                    exts is not None
                    and os.path.splitext(name)[1].lower().lstrip(".") not in exts
                ):
                    continue
                path = (
                    dest
                    / f"{time.strftime('%Y%m%d', received)}_{mid[:8]}_{safe_name(name)}"
                )
                if path in taken:
                    path = path.with_name(f"{path.stem}_{index}{path.suffix}")
                taken.add(path)
                size = len(payload)
                if path.exists() and path.stat().st_size == size:
                    status = "exists"
                elif args.dry_run:
                    status = "dry-run"
                else:
                    dest.mkdir(parents=True, exist_ok=True)
                    write_private(path, payload)
                    record = {
                        "saved_at": datetime.now(timezone.utc).isoformat(
                            timespec="seconds"
                        ),
                        "message_id": mid,
                        "thread_id": thread_id,
                        "from": str(msg.get("From", "")),
                        "subject": str(msg.get("Subject", "")),
                        "date": str(msg.get("Date", "")),
                        "mime": mime,
                        "size": size,
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "path": str(path),
                    }
                    fd = os.open(
                        dest / "manifest.jsonl",
                        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                        0o600,
                    )
                    with os.fdopen(fd, "a", encoding="utf-8") as manifest:
                        manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
                    status = "saved"
                counts[status] += 1
                print(f"{status:8} {size:>10}  {path}")
    finally:
        imap.logout()
    print(", ".join(f"{n} {k}" for k, n in counts.items()))
    return 0


def check():
    imap = connect()
    try:
        box = all_mail(imap)
        count = ok(imap.select(box, readonly=True), "select")[0].decode()
        print(f"login ok; {box} has {count} messages")
    finally:
        imap.logout()
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "query",
        nargs="?",
        help='Gmail search, e.g. "subject:현대바이오랜드 has:attachment"',
    )
    parser.add_argument(
        "--message",
        action="append",
        default=[],
        metavar="ID",
        help="Gmail message ID (hex)",
    )
    parser.add_argument(
        "--max", type=int, default=10, help="newest N messages for QUERY"
    )
    parser.add_argument(
        "--ext", default="pdf", help='comma-separated, or "all" (default pdf)'
    )
    parser.add_argument("--dest", default=str(DEFAULT_DEST))
    parser.add_argument(
        "--dry-run", action="store_true", help="list without writing files"
    )
    parser.add_argument(
        "--store-app-password",
        action="store_true",
        help="save credentials (own terminal)",
    )
    parser.add_argument(
        "--check", action="store_true", help="test login; prints mailbox size only"
    )
    args = parser.parse_args()
    try:
        if args.store_app_password:
            return store_credentials()
        if args.check:
            return check()
        if not args.query and not args.message:
            parser.error("give a QUERY or --message ID")
        return fetch(args)
    except (GmailError, imaplib.IMAP4.error, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
