#!/usr/bin/env python3
"""Install the named VPN monitor (5-minute checks); never retire an existing schedule."""
from pathlib import Path
import hashlib
import os
import plistlib
import subprocess

root = Path(__file__).resolve().parent
home = Path.home()
app = home / 'Applications/KAIST VPN Monitor.app'
if (app / 'Contents/Resources/scripts/background-login/monitor.cjs').exists():
    raise SystemExit(
        'The self-contained app is already installed. This legacy installer must not '
        'overwrite its signed bundle or schedule; use the maintenance procedure in SKILL.md.'
    )
identifier = 'local.mseok.kaist-vpn-monitor'
contents = app / 'Contents'
binary = contents / 'MacOS/kaist-vpn-monitor'
info = contents / 'Info.plist'
source = root / 'monitor-launcher.swift'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
if info.exists():
    existing = plistlib.loads(info.read_bytes())
    if existing.get('CFBundleIdentifier') != identifier:
        raise SystemExit('Existing application has a different identity; review it first')
else:
    existing = {}
if not binary.exists() or existing.get('MonitorSourceSHA256') != digest:
    binary.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['/usr/bin/swiftc', str(source), '-o', str(binary)], check=True)
    info.write_bytes(plistlib.dumps({
        'CFBundleIdentifier': identifier,
        'CFBundleName': 'KAIST VPN Monitor',
        'CFBundleDisplayName': 'KAIST VPN Monitor',
        'CFBundleExecutable': binary.name,
        'CFBundlePackageType': 'APPL',
        'CFBundleVersion': '1',
        'LSUIElement': True,
        'MonitorSourceSHA256': digest,
    }))
    subprocess.run(['/usr/bin/codesign', '--force', '--sign', '-', str(app)], check=True)
state = home / '.local/state/codex-vpn-monitor'
state.mkdir(parents=True, exist_ok=True, mode=0o700)
state.chmod(0o700)
plist = home / 'Library/LaunchAgents' / (identifier + '.plist')
plist.parent.mkdir(parents=True, exist_ok=True)
plist.write_bytes(plistlib.dumps({
    'Label': identifier,
    'AssociatedBundleIdentifiers': [identifier],
    'ProgramArguments': [str(binary), '--scheduled'],
    'StartInterval': 300,
    'RunAtLoad': True,
    'ProcessType': 'Background',
    'Nice': 19,
    'LowPriorityIO': True,
    'LowPriorityBackgroundIO': True,
    'EnvironmentVariables': {'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:' + str(home / '.local/bin')},
    'StandardOutPath': '/dev/null',
    'StandardErrorPath': str(state / 'launchd-error.log'),
}))
domain = 'gui/' + str(os.getuid())
subprocess.run(['/bin/launchctl', 'bootout', domain + '/' + identifier], capture_output=True)
subprocess.run(['/bin/launchctl', 'enable', domain + '/' + identifier], check=True)
subprocess.run(['/bin/launchctl', 'bootstrap', domain, str(plist)], check=True)
print(str(app))
print('Monitor installed (5-minute checks). Confirm accessibility and live health before retiring prior schedules.')
