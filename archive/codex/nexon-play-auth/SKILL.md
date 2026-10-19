---
name: nexon-play-auth
description: Type the 4-digit Nexon OTP code from the user's MapleStory or Nexon game login screen into the Nexon Play (넥슨플레이) app on their Android phone over adb. Use when the user gives the code, for example "넥슨플레이 7311", "메이플 인증 7311" or /nexon-play-auth 7311.
allowed-tools: Bash(~/.claude/skills/nexon-play-auth/scripts/nxplay.py *)
---

# Nexon OTP entry

When the user starts MapleStory, the game shows a 4-digit code that has to be
typed into the Nexon OTP screen of the Nexon Play app on their phone within 60
seconds. This skill types it for them.

## Do this

The code comes from the user's message or the skill arguments. If there is none,
ask for it in one line and wait; never invent one.

```sh
~/.claude/skills/nexon-play-auth/scripts/nxplay.py auth <code>
```

Run this as the very first action, with nothing before it: the code expires 60
seconds after the game shows it. The command takes about 10 seconds with a live
connection; finding the phone again can add about 15.

| Exit | Meaning | What to do |
|---|---|---|
| 0 | Typed | Report in one line what the app showed (see Observed flow). |
| 2 | The OTP screen or its empty boxes were not found | Use the fallback below. |
| 3 | The phone is locked | Tell the user to unlock it, then run `auth` again. |
| 4 | No adb connection | Report the printed reason. See Connection. |

A code that has expired needs a new one from the user; do not retry the old one.

## Observed flow (2026-10-04, SM-F966N, package `com.nexon.nxplay`)

1. The main screen of Nexon Play has a `넥슨OTP` button at the bottom centre. The
   authenticator page (`넥슨인증기`) has the same entry, labelled `넥슨 OTP`.
2. The OTP screen says `게임 화면의 인증번호 4자리를 입력해 주세요.` and has four
   tappable boxes labelled `-`. While a login waits, it also says
   `메이플스토리에서 로그인을 시도 중입니다.`
3. Tapping the first box and sending the four digits as text submits by itself;
   there is no confirm button.
4. The app shows `인증번호를 전송하고 있습니다.` for about a second, then returns to
   the empty OTP screen without the login line. The user confirmed that the game
   login went through.

What a wrong or expired code looks like has not been seen yet. If the screen
after typing shows anything other than step 4, quote it to the user.

## Fallback

- `nxplay.py texts` lists every label on screen with its centre and whether it
  is tappable.
- `nxplay.py tap-text <label>` taps the one element with that label.
- `nxplay.py adb shell input keyevent KEYCODE_BACK` leaves a wrong screen.
- `nxplay.py adb shell input keyevent KEYCODE_DEL` clears a digit left in a box.
- `nxplay.py tap <x> <y>` and `nxplay.py shot <file>` exist for a screen without
  labels.

## Limits

- Act only on a request in the current message, with the code the user gave.
- Do only the entry. The user turned down exploratory taps and screenshots on
  their phone (2026-10-04): do not browse the app, open other pages or capture
  the screen to learn about it. Use the fallback only to finish the entry that
  was asked for.
- Tap only inside Nexon Play. Do not enter the phone's PIN or pattern, any
  password or an app lock code, and do not accept other prompts.
- Do not change phone settings or install anything. `persist` is the one
  exception and needs the user's explicit agreement each time.
- Report what the phone showed. If the result is unclear, say so.

## Connection

`nxplay.py` uses an adb connection that already exists, then the last endpoint
that worked, then port 5555, then the wireless debugging port advertised on the
LAN, and finally a port search on the phone's Tailscale address (about 15
seconds).

Wireless debugging (Developer options) has to be switched on by the user. Android
switches it off when Wi-Fi drops and at every reboot, and its port changes each
time. `nxplay.py persist` makes adb listen on port 5555 on every interface until
the phone reboots, so the phone is also reachable on mobile data through
Tailscale. Unknown computers still need to be allowed on the phone. The user has
not agreed to this yet; an attempt to make it automatic was refused by the
session's permission check, so leave it to the user.

`nxplay.py status` shows the connection, screen, lock state and foreground app.
Settings are optional and live in `~/.config/nexon-play-auth/config.json`
(`adb`, `hosts`, `package`); the last working endpoint is in
`~/.local/state/nexon-play-auth/endpoint`.
