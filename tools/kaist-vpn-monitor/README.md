# KAIST VPN Monitor Community

KAIST KVPN의 공식 Ivanti 클라이언트를 5분마다 점검하고, 연결이 끊어지면 이메일 OTP로 다시 연결하는 **macOS용 실험적 자동화 도구**입니다. KAIST·Ivanti의 공식 배포물이 아닙니다.

**현재는 Mac + Codex Gmail 연결 + 검증 가능한 DKIM 서명이 있는 KVPN 메일이 필요합니다.** 앱 하나만 받아 실행하는 완제품은 아닙니다. 개인용으로 사용하던 자동화를 공유용으로 분리했으며, 공유판의 다른 사용자 계정에서 최초 로그인은 아직 검증하지 않았습니다. Windows/Linux는 지원하지 않습니다.

## 동작

1. 정확한 `SA (kvpn.kaist.ac.kr)` 프로필과 사용자가 지정한 서버의 SSH 접속을 확인합니다.
2. 복구가 필요하면 별도 headless Chrome 프로필에서 KVPN에 로그인합니다. 사용 중인 Chrome 창이나 프로필을 사용하지 않습니다.
3. 계정 정보는 macOS 키체인에서 읽습니다. Gmail 연결에서 새 OTP 메일을 읽고, 사용자가 등록한 발신 주소, 암호학적 DKIM 서명, Gmail 수신 시각과 서명된 내용을 검증합니다. macOS Mail을 읽지 않습니다.
4. 공식 PulseApplicationLauncher로 세션을 전달합니다. Ivanti 프로필과 SSH를 다시 확인해야 성공입니다.

통상 점검·복구뿐 아니라 공유판의 오류 처리에도 AI 모델을 호출하지 않습니다. Codex는 Gmail 도구 연결에만 사용합니다. 로그인 세션을 유지해야 하므로 Chrome 프로필에는 민감한 세션 데이터가 저장됩니다. 비밀번호·OTP·원문 메일·세션 URL을 로그로 출력하거나 저장하지 않도록 구현했습니다.

## 설치 전에

- macOS 및 `/Applications/Ivanti Secure Access.app`. 기존 구현은 Ivanti 22.8 계열의 영어 상태 메뉴와 `SA (kvpn.kaist.ac.kr)` 프로필을 대상으로 합니다. 다른 메뉴·프로필이면 중단할 수 있습니다.
- KVPN 웹사이트에서 **본인 계정으로 수동 연결에 성공한 상태**. Email OTP가 Gmail로 도착해야 합니다.
- Google Chrome, Node.js **22.19 이상** 및 npm, Xcode Command Line Tools (`xcode-select --install`). Node 26에서 공유판 빌드를 확인했습니다. Intel Mac은 검증하지 않았습니다.
- 로그인된 Codex CLI와 연결된 Gmail. 이 코드는 Codex의 실험적 app-server 인터페이스와 `gmail.search_emails` / `gmail.read_email` 도구에 의존합니다. 배포 채널·계정·버전에 따라 제공되지 않을 수 있습니다. **CLI 설치만으로 Gmail 연결이 제공된다는 뜻은 아닙니다.** 사용할 수 없으면 자동 복구는 중단됩니다.
- 정상 KVPN 메일의 **발신 주소를 사용자가 직접 확인해 등록**해야 합니다. 수신함에서 자동 추정하지 않습니다. 해당 메일은 발신 주소와 같은 도메인의 DKIM 서명으로 From과 본문 전체가 검증돼야 합니다. Gmail의 같은 메시지 ID에서 메타데이터 수신 시각을 읽고 요청 시각 2초 전부터 만료까지 확인합니다. 서명 시각이 있으면 요청 시각 120초 전부터 만료까지 확인합니다. 실제 KVPN 형식은 서명된 제목과 ASCII 본문의 단 하나인 6자리 코드를 사용하며, 서명되지 않은 MIME 설정은 무시합니다. `l=` 부분 본문 서명, 시험용 키, RSA 2048비트 미만 키, 서명이 없거나 본문이 변조된 메일은 거부합니다. DNS로 공개 DKIM TXT 키를 조회하며, 로컬 DNS 환경을 신뢰합니다.
- **v0.2.1에서 실제 KVPN 메일의 서명·수신 시각·본문 검증을 확인했습니다.** v0.2.0은 실제 메일에 없는 서명 시각과 MIME 서명을 요구해 호환되지 않으므로 사용하지 마세요. 서명이 없거나 다른 도메인의 위임 서명을 쓰면 자동 복구가 실패합니다. 보안 검사를 끄는 옵션은 제공하지 않습니다.
- 본인이 접속할 권한이 있고 VPN 경로를 확인할 수 있는 연구실 서버의 **SSH 키 인증**. SSH 설정 별칭을 사용하세요. 확인 명령은 `hostname`이며, 비밀번호 입력 없이 성공해야 합니다. 다른 경로로도 접근 가능한 서버이면 VPN 경로 확인이 약해집니다.

VPN 정상 상태에서 본인의 별칭으로 먼저 확인하세요. 최초 호스트 키 확인도 사용자가 직접 마쳐야 합니다.

```sh
ssh -o BatchMode=yes -o ConnectTimeout=10 -o ConnectionAttempts=1 lab-vpn-check hostname
```

`lab-vpn-check`는 예시이며 실제 서버나 계정이 들어 있지 않습니다. 본인의 `~/.ssh/config`에 설정한 별칭으로 바꾸세요.

## 설치

### Codex 스킬로 설치하기

Codex에 다음 요청을 전달하면 스킬을 설치할 수 있습니다.

> https://github.com/mseok/agent-skills/tree/kaist-vpn-monitor-v0.2.3/tools/kaist-vpn-monitor 의 스킬을 설치해줘.

스킬이 설치된 다음 턴에 다음처럼 요청하세요.

> $kaist-vpn-monitor 이 Mac에 VPN 자동화를 설치해줘. 연결 확인용 SSH 별칭은 lab-vpn-check야.

별칭은 본인 설정으로 바꾸세요. 스킬 안에 앱 소스가 함께 있어 Codex가 의존성 설치,
로컬 설정과 앱 빌드까지 진행할 수 있습니다. **계정 비밀번호 입력과 macOS 권한
승인은 본인이 직접 해야 합니다.** 첫 복구를 확인하기 전에는 자동 실행을 켜지 않습니다.

아래는 직접 설치하거나 각 단계를 확인할 때의 절차입니다.

### 1. 소스와 의존성

[공유용 소스 ZIP](https://github.com/mseok/agent-skills/releases/tag/kaist-vpn-monitor-v0.2.3)을
받았다면 압축을 풀고 `kaist-vpn-monitor` 폴더에서 아래의 `npm ci`부터 실행하세요.
Git으로 받는 경우는 다음과 같습니다.

```sh
git clone --depth 1 https://github.com/mseok/agent-skills.git
cd agent-skills/tools/kaist-vpn-monitor
npm ci --prefix scripts/background-login --ignore-scripts --no-audit --no-fund
node setup.cjs
zsh scripts/configure-keychain.zsh
node install.cjs --install
```

`setup.cjs`는 SSH 별칭, Codex 실행 파일 경로, 본인이 확인한 OTP 발신 주소를 로컬에 저장합니다. 키체인 설정은 별도의 숨김 입력 프롬프트로 본인 KVPN 아이디와 비밀번호를 받습니다. 비밀번호를 명령 인자, 설정 JSON, GitHub 이슈에 넣지 마세요.

앱은 `~/Applications/KAIST VPN Monitor Community.app`에 설치됩니다. 실행 스크립트와 의존성을 앱에 복사하므로 소스 디렉터리 위치에는 의존하지 않습니다. 설치 시 사용한 Node 실행 파일 경로는 유지되어야 합니다. **설치만으로 자동 실행이나 로그인을 시작하지 않습니다.**

### 2. macOS 권한

앱을 Finder에서 한 번 열면 손쉬운 사용 권한을 요청합니다. 시스템 설정 → 개인정보 보호 및 보안에서 **KAIST VPN Monitor Community**에 아래 권한을 직접 부여하세요.

- **손쉬운 사용:** Ivanti 메뉴의 상태 확인 및 제한된 Ivanti 동작에 사용합니다.

**전체 디스크 접근 권한은 필요하지 않습니다.** v0.1.0에서 Community 앱에 부여했다면 시스템 설정에서 해제하세요. 개인용 또는 다른 앱의 권한은 별개입니다.

앱은 소스에서 로컬 빌드하고 ad-hoc 서명합니다. 공증된 다운로드 앱이 아닙니다. macOS 보안 설정을 우회하거나 비활성화하지 마세요. 키체인 접근 프롬프트가 나타나면 본인이 요청한 실행인지 확인하세요.

### 3. 연결 상태 확인과 최초 복구

이미 수동으로 연결된 상태에서 실행합니다.

```sh
APP="$HOME/Applications/KAIST VPN Monitor Community.app/Contents/MacOS/kaist-vpn-monitor"
"$APP" --check-only
```

`status: connected`, `native: SA`, `ssh: ok`, `attempts: 0`를 확인하세요. 이 점검은 재로그인하지 않습니다. 실패하면 아래 문제 해결을 먼저 확인하세요.

다음에 자연스럽게 연결이 끊겼을 때, 사용자가 지켜보는 상태에서 한 번 실행합니다. 테스트 목적으로 정상 VPN을 끊을 필요는 없습니다.

```sh
"$APP" --retry
```

**이 명령은 실제 로그인을 시도합니다.** 같은 KVPN 계정에 다른 웹 세션이 남아 있으면 포털의 세션 계속하기를 누르므로 이전 세션이 종료될 수 있습니다. 계정은 공유하지 마세요. 이메일 대기 시간 초과에 한해 최대 3회 로그인하며, 비밀번호 거부 등 다른 오류는 중단합니다.

### 4. 자동 실행 켜기

최초 복구에서 연결과 SSH 성공을 확인한 뒤 켜세요. 다른 VPN 자동 복구 도구와 동시에 실행하지 마세요.

```sh
node install.cjs --enable
"$APP" --status
```

활성화 직후와 macOS 사용자 로그인 시 실행하고, 이후 **300초마다** 점검합니다. 잠자기·로그아웃 중에는 주기 실행을 보장하지 않습니다. `--status`는 마지막 저장 기록이므로 `lastCheckedAt`을 함께 보세요. 최신 연결 점검은 `--check-only`입니다.

## 중지, 업데이트, 제거

```sh
node install.cjs --disable
```

자동 실행을 꺼도 현재 Ivanti 연결은 직접 해제하지 않습니다. 실행 중 인증을 중단하면 해당 시도는 완료되지 않을 수 있습니다. 다음 로그인에도 비활성 상태가 유지됩니다.

업데이트는 실행이 끝난 뒤 자동 실행을 끄고, 기존 Community 앱을 Finder에서 휴지통으로 옮긴 다음 새 소스로 설치하세요. 설치기는 기존 앱을 덮어쓰지 않습니다. 권한과 연결을 다시 확인하고 자동 실행을 켜세요.

v0.1.0에서 올라온다면 `node setup.cjs`를 다시 실행해 정상 메일의 발신 주소를 등록하고,
Community 앱의 전체 디스크 접근 권한을 해제하세요. 새 버전의 DKIM 조건을 만족하는
메일로 첫 복구가 성공하기 전에는 자동 실행을 다시 켜지 마세요.

제거하려면 먼저 자동 실행을 끈 뒤 앱과 아래 Community 전용 파일을 삭제하세요. 키체인 접근 앱에서 `kaist-vpn-monitor.username`, `kaist-vpn-monitor.password` 항목도 삭제할 수 있습니다. Ivanti 자체나 다른 자동화의 파일을 지우지 마세요.

| 로컬 위치 | 내용 |
| --- | --- |
| `~/.config/kaist-vpn-monitor/config.json` | 본인의 SSH 별칭·Codex 경로·등록한 발신 주소. 공유 금지 |
| `~/Library/Caches/kaist-vpn-monitor/` | 로그인 세션·잠금·일회성 OTP 전달 파일. 공유 금지 |
| `~/.local/state/kaist-vpn-monitor/` | 마지막 점검 결과와 진단용 오류 로그 |
| `~/Library/LaunchAgents/local.kaist.vpn-monitor.community.plist` | 자동 실행 설정 |

## 문제 해결과 한계

- `settings_unavailable`: `node setup.cjs`로 로컬 설정을 만드세요.
- `accessibility_unavailable` / `native_state_unavailable`: 앱 권한과 Ivanti의 정확한 프로필·영어 상태 메뉴를 확인하세요. 알 수 없는 상태에서 무작정 비밀번호를 제출하지 않습니다.
- `gmail_connector_unavailable`: Codex에서 Gmail 연결을 확인하세요. 인증 시도 전 발생한 일시적 연결 장애는 다음 5분 점검에서 다시 확인합니다. 이 도구는 연결이 허용되지 않은 계정에서 Gmail 접근을 우회하지 않습니다.
- `connector_email_timeout`: 유효한 메일을 시간 내 찾지 못했습니다. Gmail 연결, 등록한 발신 주소, 실제 메일의 DKIM·MIME 호환성을 확인하세요. 잘못된 후보는 무시하며, 검증을 우회해 OTP를 넣지 않습니다.
- `ssh_check_failed`: VPN이 연결돼 있어도 SSH 서버·키·별칭에 문제가 있으면 실패합니다. 이 경우 재인증으로 VPN을 교체하지 않습니다.
- 인증 실패 후에는 원인을 해결하고 `--retry`로 명시적으로 재시도하세요. 재시작을 반복해서 OTP를 계속 요청하지 마세요.
- 약 10시간 세션 만료 시 Ivanti 자체가 전면 로그인 창을 띄울 수 있습니다. 이 공유판은 서비스나 시스템 프로필을 강제로 바꾸는 스크립트를 포함하지 않습니다. 따라서 **항상 무창·무중단인 동작은 보장하지 않습니다.**
- KVPN 화면·서명·메일 형식, Ivanti 메뉴 또는 Codex 내부 인터페이스가 바뀌면 중단할 수 있습니다. 기존 설치에서의 사용 경험과 다른 사용자 환경의 호환성은 별개입니다.

## 보안 검토와 남은 한계

별도 **Astra High** 소스 검토에서 v0.1.0의 메일 기반 복구 방해 문제를 찾아
v0.2.0에서 수정했습니다. [보안 검토 요약](SECURITY-REVIEW.md)을 함께 읽으세요.
발신자·서명 검증은 서버의 OTP 검증을 대체하지 않습니다. 과거의 정상 서명 메일을 새로
수신하도록 재전송하는 공격, 메일 홍수, 동일 사용자 권한의 악성 코드, 신뢰한 KVPN
사이트·DNS·클라이언트 자체 침해까지 방어한다는 뜻은 아닙니다.

브라우저의 HTTP(S) 통신에는 임시 로컬 CONNECT 프록시를 적용해 KVPN·OTP 두 TLS 주소 외의
터널을 거부합니다. 전체 브라우저·시스템 네트워크의 격리를 보장하는 것은 아닙니다. 리디렉션도 이 연결 제한을 받으며, TLS는 포털까지 유지됩니다.
OTP iframe의 실제 URL도 확인합니다. 네이티브 launcher 전달은 신뢰한 포털이
열린 상태에서 메인 프레임을 대상으로 관찰한 이동만 받습니다. 이것이 이동을
시작한 스크립트의 출처나 URI 내용까지 검증한다는 뜻은 아닙니다.
다른 CDN·팝업을 필수로 사용하는 포털 변경은 연결 실패로 이어질 수 있습니다.
Pulse URI 내부 형식과 공급업체 바이너리의 안전성은 별도 검증하지 않았습니다.

## 검증 및 공개 범위

[검증 기록](VALIDATION.md)에 공유판 빌드와 테스트 범위를 적었습니다. 다른 계정의 실제 OTP 로그인과 설치 권한 승인은 배포 전 자동 테스트로 대신 검증하지 않았습니다.

배포물에는 소스·설치 안내·고정 의존성 목록·합성 테스트 데이터만 포함합니다. 개인 계정, 서버 주소, 원본 메일, 키체인, 설정, 상태 기록, 브라우저 프로필, 실행 바이너리는 포함하지 않습니다. 공개 이슈에는 오류 이름과 버전만 적고 원문 메일·설정·세션 데이터는 올리지 마세요.

2026-10-13: 같은 보안 코드로 개인용 앱을 새 소스·의존성에서 설치하고,
새 브라우저 프로필의 실제 KVPN 로그인 1회, OTP, 네이티브 연결과 SSH를
검증했습니다. 기존 Keychain·Ivanti·Gmail 연결은 재사용했으며, 새 Mac이나
다른 계정 전체 설치를 대신 검증한 것은 아닙니다. 새 앱 빌드는 macOS
손쉬운 사용 권한 재승인이 필요할 수 있습니다.


v0.2.2는 Gmail의 간헐적인 검색 실패와 읽기 시간 초과에 대해 같은 요청을
2초·5초 간격으로 최대 두 번 재조회합니다. 진행 중인 OTP의 90초 만료
시간을 넘기지 않으며, 새로운 OTP나 로그인을 추가로 요청하지 않습니다.
권한 거부와 다른 오류는 즉시 중단합니다. 실패 원인은 개인정보 없는
고정 오류 코드로 상태에 남깁니다. 업데이트 후 앱 서명이 바뀌면 macOS
손쉬운 사용 권한을 다시 승인해야 합니다.


## 로고가 포함된 앱 다운로드 (v0.2.3)

[GitHub Release](https://github.com/mseok/agent-skills/releases/tag/kaist-vpn-monitor-v0.2.3)의
`kaist-vpn-monitor-v0.2.3-macos-arm64.zip`은 Apple Silicon용 앱입니다.
macOS 13 이상을 빌드 대상으로 하며 실제 실행 검증 환경은 macOS 26입니다.
Homebrew Node.js 22.19 이상이 `/opt/homebrew/bin/node`에 필요합니다.
Ivanti, Chrome, Codex CLI와 Gmail 연결 및 개인 설정·키체인 등록은 별도입니다.
Intel Mac 또는 다른 Node 경로에서는 위 소스 설치 방법을 사용하세요.

ZIP을 풀고 `KAIST VPN Monitor Community.app`을 `~/Applications`에 넣으세요.
이미 이 앱을 배치했다면 설치 단계의 `node install.cjs --install`은 생략하고,
설정·키체인·권한 승인·연결 검증 단계를 진행하세요. 자동 실행은 별도로
켜야 합니다. 이 앱은 ad-hoc 서명이며 Apple 공증을 받지 않았습니다.
macOS 차단은 사용자가 시스템 설정에서 확인하고 승인해야 하며,
Gatekeeper나 손쉬운 사용 보호 설정을 명령어로 우회하지 마세요.

![KVPN logo](assets/kvpn-logo-concept-v1.png)


v0.2.3은 로그인 중 교체되는 OTP iframe을 준비 완료 후 다시 확인하고,
이미 준비된 신뢰 포털의 중복 이동을 생략합니다. 수정한 실행 코드로
실제 예약 환경에서 로그인 1회·OTP·SA·SSH 복구를 확인했습니다. 최종
설치본 재서명 후에는 macOS 손쉬운 사용을 다시 승인해야 합니다.
