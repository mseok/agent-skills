#!/usr/bin/env python3
"""Drive the Nexon Play app on an Android phone over adb.

  nxplay.py auth 7311        wake the phone, open the Nexon OTP screen of Nexon Play, type 7311
  nxplay.py texts            list what is on the phone screen (label, centre, tappable)
  nxplay.py tap-text 확인     tap the one element with exactly this label
  nxplay.py tap 540 1200     tap a coordinate
  nxplay.py shot out.png     save a screenshot
  nxplay.py status           connection, lock state, foreground app
  nxplay.py connect          only connect, print the adb serial
  nxplay.py adb <args...>    run adb against the connected phone
  nxplay.py persist          make adb listen on port 5555 until the phone reboots

Exit codes: 0 done, 2 the screen or label was not found (or is ambiguous),
3 the phone is locked, 4 no adb connection.

Optional settings in ~/.config/nexon-play-auth/config.json:
  {"adb": "/path/to/adb", "hosts": ["extra-host-or-ip"], "package": "com.nexon.nxplay"}
"""

import argparse
import asyncio
import json
import os
import pty
import re
import select
import shutil
import socket
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

CONFIG = Path(os.environ.get("NXPLAY_CONFIG", "~/.config/nexon-play-auth/config.json")).expanduser()
ENDPOINT = Path("~/.local/state/nexon-play-auth/endpoint").expanduser()
PACKAGE = "com.nexon.nxplay"
ADB_SERVICE = "_adb-tls-connect._tcp"

cfg = {}
ADB = ""


def say(*parts):
    print(*parts, file=sys.stderr, flush=True)


def die(code, message):
    say(message)
    sys.exit(code)


def find_adb():
    candidates = [
        os.environ.get("ADB"),
        cfg.get("adb"),
        shutil.which("adb"),
        "/opt/homebrew/bin/adb",
        str(Path("~/Library/Android/sdk/platform-tools/adb").expanduser()),
    ]
    for path in candidates:
        if path and os.access(os.path.expanduser(path), os.X_OK):
            return os.path.expanduser(path)
    die(4, f'adb not found. Install Android platform-tools or set "adb" in {CONFIG}.')


def adb(*args, serial=None, timeout=20, binary=False):
    cmd = [ADB] + (["-s", serial] if serial else []) + list(args)
    try:
        done = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return b"" if binary else ""
    out = done.stdout + done.stderr
    return out if binary else out.decode(errors="replace")


# ---------------------------------------------------------------- connection


def devices():
    rows = []
    for line in adb("devices").splitlines()[1:]:
        parts = line.rsplit("\t", 1)  # a serial found over mDNS can contain spaces
        if len(parts) == 2:
            rows.append((parts[0], parts[1].strip()))
    return rows


def tailscale_phones():
    """IPv4 addresses of the online Android devices in this tailnet."""
    cli = shutil.which("tailscale") or "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
    try:
        status = json.loads(subprocess.run([cli, "status", "--json"], capture_output=True, timeout=10).stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return []
    hosts = []
    for peer in (status.get("Peer") or {}).values():
        if peer.get("OS") == "android" and peer.get("Online"):
            hosts += [ip for ip in peer.get("TailscaleIPs", []) if "." in ip]
    return hosts


def run_pty(args, seconds):
    """dns-sd flushes its output only to a terminal, so it gets one."""
    master, slave = pty.openpty()
    proc = subprocess.Popen(args, stdout=slave, stderr=slave)
    os.close(slave)
    out, end = b"", time.time() + seconds
    while time.time() < end:
        if select.select([master], [], [], 0.2)[0]:
            try:
                out += os.read(master, 4096)
            except OSError:
                break
    proc.kill()
    proc.wait()
    os.close(master)
    return out.decode(errors="replace")


def mdns_endpoints(service=ADB_SERVICE):
    """(host, port) of every wireless debugging service on this LAN."""
    names = []
    for line in run_pty(["dns-sd", "-B", service, "local."], 2.5).splitlines():
        found = re.search(r"\sAdd\s+\d+\s+\d+\s+\S+\s+" + re.escape(service) + r"\.\s+(.+?)\s*$", line)
        if found and found.group(1) not in names:
            names.append(found.group(1))
    endpoints = []
    for name in names:
        found = re.search(r"can be reached at (\S+?)\.?:(\d+)", run_pty(["dns-sd", "-L", name, service, "local."], 2))
        if found:
            endpoints.append((found.group(1), int(found.group(2))))
    return endpoints


def port_open(host, port, timeout=3):
    try:
        socket.create_connection((host, port), timeout).close()
        return True
    except OSError:
        return False


def speaks_adb(host, port):
    """True when the port answers an adb connect packet like adbd does."""
    payload = b"host::\x00"
    connect = 0x4E584E43  # "CNXN"
    packet = struct.pack("<6I", connect, 0x01000001, 1 << 20, len(payload), sum(payload), connect ^ 0xFFFFFFFF)
    try:
        with socket.create_connection((host, port), 4) as sock:
            sock.settimeout(4)
            sock.sendall(packet + payload)
            return sock.recv(4) in (b"STLS", b"CNXN", b"AUTH")
    except OSError:
        return False


def scan(host):
    """Away from the home LAN there is no mDNS, so look for adbd in the ephemeral port range."""

    async def probe(gate, port, found):
        async with gate:
            try:
                _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), 2.5)
            except (OSError, asyncio.TimeoutError):
                return
            found.append(port)
            writer.close()

    async def sweep():
        gate, found = asyncio.Semaphore(200), []
        await asyncio.gather(*(probe(gate, port, found) for port in range(30000, 61000)))
        return sorted(found)

    return [port for port in asyncio.run(sweep()) if speaks_adb(host, port)]


def connect():
    cached = ENDPOINT.read_text().strip() if ENDPOINT.exists() else ""
    ready = [serial for serial, state in devices() if state == "device"]
    if ready:
        return cached if cached in ready else ready[0]

    notes = []

    def attempt(endpoint):
        host, port = endpoint.rsplit(":", 1)
        if not port_open(host, int(port)):
            return False
        adb("connect", endpoint)
        state = ""
        for _ in range(8):
            state = adb("get-state", serial=endpoint).strip()
            if state == "device":
                ENDPOINT.parent.mkdir(parents=True, exist_ok=True)
                ENDPOINT.write_text(endpoint + "\n")
                return True
            time.sleep(0.5)
        notes.append(f"{endpoint}: {state.splitlines()[-1] if state else 'no answer'}")
        adb("disconnect", endpoint)
        return False

    if cached and attempt(cached):
        return cached
    hosts = tailscale_phones() + cfg.get("hosts", [])
    for host in hosts:
        if attempt(f"{host}:5555"):
            return f"{host}:5555"
    for lan_host, port in mdns_endpoints():
        for host in hosts + [lan_host]:
            if attempt(f"{host}:{port}"):
                return f"{host}:{port}"
        notes.append(f"wireless debugging is advertised on port {port} but nothing listens there; its switch is probably off")
    for host in hosts:
        say(f"looking for the wireless debugging port on {host} ...")
        for port in scan(host):
            if attempt(f"{host}:{port}"):
                return f"{host}:{port}"

    for serial, state in devices():
        notes.append(f"{serial}: {state}")
    reason = "; ".join(notes) if notes else "no adb port is open on the phone"
    if not hosts:
        reason += "; no Android device is online in Tailscale"
    die(
        4,
        f"cannot reach the phone over adb ({reason}).\n"
        "The phone needs Developer options > Wireless debugging switched on (this requires Wi-Fi), "
        "a USB cable, or the 5555 listener from `nxplay.py persist`. "
        "`unauthorized` means the phone is showing an allow-debugging prompt.",
    )


# ---------------------------------------------------------------- phone screen


class Node:
    def __init__(self, element, tappable):
        self.text = (element.get("text") or "").strip()
        self.desc = (element.get("content-desc") or "").strip()
        self.package = element.get("package") or ""
        self.tappable = tappable
        x1, y1, x2, y2 = (int(n) for n in re.findall(r"-?\d+", element.get("bounds") or "[0,0][0,0]")[:4])
        self.x, self.y, self.area = (x1 + x2) // 2, (y1 + y2) // 2, (x2 - x1) * (y2 - y1)

    @property
    def label(self):
        return self.text or self.desc

    def matches(self, wanted):
        return wanted in (squash(self.text), squash(self.desc))

    def line(self):
        mark = "tap" if self.tappable else "   "
        return f"{self.x:>5},{self.y:<5} {mark}  {self.package.split('.')[-1]:<12} {self.label}"


def squash(text):
    return re.sub(r"\s+", "", text)


def sh(serial, command, timeout=20):
    return adb("shell", command, serial=serial, timeout=timeout)


def dump(serial):
    """Labelled elements on screen and the set of packages that own a window part."""
    raw = adb("exec-out", "uiautomator", "dump", "/dev/tty", serial=serial, binary=True)
    found = re.search(rb"<\?xml.*</hierarchy>", raw, re.S)
    if not found:
        sh(serial, "uiautomator dump /sdcard/window_dump.xml")
        raw = adb("exec-out", "cat", "/sdcard/window_dump.xml", serial=serial, binary=True)
        sh(serial, "rm -f /sdcard/window_dump.xml")
        found = re.search(rb"<\?xml.*</hierarchy>", raw, re.S)
    if not found:
        return [], set()
    nodes, packages = [], set()

    def walk(element, tappable):
        for child in element:
            child_tappable = tappable or child.get("clickable") == "true"
            node = Node(child, child_tappable)
            packages.add(node.package)
            if node.label and node.area > 0:
                nodes.append(node)
            walk(child, child_tappable)

    walk(ET.fromstring(found.group(0)), False)
    return nodes, packages


def show(nodes, limit=80):
    for node in nodes[:limit]:
        print(node.line())
    if len(nodes) > limit:
        print(f"... {len(nodes) - limit} more")


def keyguard(serial):
    """'locked', 'unlocked' or 'unknown' (the dump format differs between Android versions)."""
    found = re.search(r"KeyguardServiceDelegate.*?showing=(true|false)", sh(serial, "dumpsys window policy"), re.S)
    if not found:
        return "unknown"
    return "locked" if found.group(1) == "true" else "unlocked"


def wake(serial):
    sh(serial, "input keyevent KEYCODE_WAKEUP")
    sh(serial, "wm dismiss-keyguard")  # clears a swipe-only lock; a PIN or biometric lock stays
    time.sleep(0.4)


def tap(serial, node_or_x, y=None):
    x, y = (node_or_x.x, node_or_x.y) if y is None else (node_or_x, y)
    sh(serial, f"input tap {x} {y}")


def package_name(serial):
    package = cfg.get("package", PACKAGE)
    if "package:" in sh(serial, f"pm path {package}"):
        return package
    others = sh(serial, "pm list packages | grep -iE 'nexon|nxplay'").strip() or "none"
    die(2, f"{package} is not installed on the phone. Nexon packages found: {others}")


def choose(nodes, wanted):
    """Elements showing exactly this label; tappable ones win over plain text."""
    hits = [node for node in nodes if node.matches(wanted)]
    return [node for node in hits if node.tappable] or hits


# ---------------------------------------------------------------- commands


def on_otp_screen(nodes):
    # "게임 화면의 인증번호 4자리를 입력해 주세요."
    return any("인증번호4자리" in squash(node.label) for node in nodes)


def cmd_auth(args):
    number = squash(args.number)
    if not (number.isdigit() and len(number) == 4):
        die(2, f"'{args.number}' is not a 4-digit code")
    serial = connect()
    wake(serial)
    if keyguard(serial) == "locked":
        die(3, "the phone is locked; it has to be unlocked by its owner first")
    package = package_name(serial)
    nodes, packages = dump(serial)
    if package not in packages:
        sh(serial, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
    deadline = time.time() + args.wait
    while not on_otp_screen(nodes):
        if time.time() > deadline:
            say("could not reach the Nexon OTP screen")
            show(nodes)
            sys.exit(2)
        # Bottom-centre button of the main screen; the authenticator page has the same entry.
        opener = choose([node for node in nodes if node.package == package], "넥슨OTP")
        if opener:
            tap(serial, opener[0])
        time.sleep(0.7)
        nodes, packages = dump(serial)
    boxes = sorted((node for node in nodes if node.tappable and node.label == "-"), key=lambda node: node.x)
    if len(boxes) != 4:
        say("the four code boxes are not empty; nothing was typed")
        show(nodes)
        sys.exit(2)
    tap(serial, boxes[0])
    sh(serial, f"input text {number}")
    print(f"typed {number}")
    time.sleep(0.5)
    nodes = dump(serial)[0]
    if any("전송하고" in node.label for node in nodes):  # "인증번호를 전송하고 있습니다."
        print("the app is sending the code")
        time.sleep(1.0)
        nodes = dump(serial)[0]
    print("screen now:")
    show(nodes)


def cmd_texts(args):
    show(dump(connect())[0], limit=200)


def cmd_tap_text(args):
    serial = connect()
    nodes = dump(serial)[0]
    picks = choose(nodes, squash(args.text))
    if len(picks) != 1:
        say(f"{len(picks)} elements show '{args.text}'; nothing was tapped")
        show(nodes)
        sys.exit(2)
    tap(serial, picks[0])
    print(f"tapped '{args.text}' at {picks[0].x},{picks[0].y}")
    time.sleep(1.0)
    show(dump(serial)[0])


def cmd_tap(args):
    tap(connect(), args.x, args.y)


def cmd_shot(args):
    data = adb("exec-out", "screencap", "-p", serial=connect(), binary=True)
    if not data.startswith(b"\x89PNG"):
        die(2, "the phone did not return a screenshot")
    Path(args.path).write_bytes(data)
    print(args.path)


def cmd_status(args):
    serial = connect()
    package = cfg.get("package", PACKAGE)
    awake = re.search(r"mWakefulness=(\w+)", sh(serial, "dumpsys power"))
    print("serial:    ", serial)
    print("screen:    ", awake.group(1) if awake else "unknown")
    print("keyguard:  ", keyguard(serial))
    print("nexon play:", "installed" if "package:" in sh(serial, f"pm path {package}") else "missing")
    print("on screen: ", ", ".join(sorted(dump(serial)[1])) or "nothing")


def cmd_connect(args):
    print(connect())


def cmd_adb(args):
    sys.stdout.write(adb(*args.args, serial=connect(), timeout=60))


def cmd_persist(args):
    serial = connect()
    if serial.endswith(":5555"):
        print(f"already listening: {serial}")
        return
    print(adb("tcpip", "5555", serial=serial).strip())
    hosts = tailscale_phones() + cfg.get("hosts", []) or [serial.rsplit(":", 1)[0]]
    for _ in range(10):
        time.sleep(1)
        for host in hosts:
            if port_open(host, 5555) and "connected" in adb("connect", f"{host}:5555"):
                if adb("get-state", serial=f"{host}:5555").strip() == "device":
                    ENDPOINT.parent.mkdir(parents=True, exist_ok=True)
                    ENDPOINT.write_text(f"{host}:5555\n")
                    print(f"connected: {host}:5555 (lasts until the phone reboots)")
                    return
    die(4, "adb restarted on port 5555 but the connection did not come back; check the phone for a prompt")


def main():
    global cfg, ADB
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    auth = sub.add_parser("auth")
    auth.add_argument("number")
    auth.add_argument("--wait", type=float, default=12, help="seconds to wait for the Nexon OTP screen")
    auth.set_defaults(run=cmd_auth)
    sub.add_parser("texts").set_defaults(run=cmd_texts)
    tap_text = sub.add_parser("tap-text")
    tap_text.add_argument("text")
    tap_text.set_defaults(run=cmd_tap_text)
    tap_xy = sub.add_parser("tap")
    tap_xy.add_argument("x", type=int)
    tap_xy.add_argument("y", type=int)
    tap_xy.set_defaults(run=cmd_tap)
    shot = sub.add_parser("shot")
    shot.add_argument("path")
    shot.set_defaults(run=cmd_shot)
    sub.add_parser("status").set_defaults(run=cmd_status)
    sub.add_parser("connect").set_defaults(run=cmd_connect)
    raw = sub.add_parser("adb")
    raw.add_argument("args", nargs=argparse.REMAINDER)
    raw.set_defaults(run=cmd_adb)
    sub.add_parser("persist").set_defaults(run=cmd_persist)
    args = parser.parse_args()

    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text())
    ADB = find_adb()
    args.run(args)


if __name__ == "__main__":
    main()
