import AppKit
import ApplicationServices

// Keep scheduled runs associated with one named app for macOS privacy approval.
let arguments = Array(CommandLine.arguments.dropFirst())
if arguments.isEmpty || arguments == ["--request-access"] {
    let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
    let trusted = AXIsProcessTrustedWithOptions(options)
    print(trusted ? "accessibility_ready" : "accessibility_requires_user_approval")
    exit(trusted ? 0 : 2)
}

let allowed = ["--scheduled", "--status", "--check-only", "--retry"]
guard arguments.count == 1, allowed.contains(arguments[0]) else {
    fputs("Unsupported monitor action\n", stderr)
    exit(2)
}
guard let resources = Bundle.main.resourceURL,
      let node = Bundle.main.object(forInfoDictionaryKey: "MonitorNodePath") as? String else {
    fputs("monitor_installation_incomplete\n", stderr)
    exit(1)
}
let process = Process()
process.executableURL = URL(fileURLWithPath: node)
let script = resources.appendingPathComponent("scripts/background-login/monitor.cjs")
process.arguments = [script.path] + (arguments == ["--scheduled"] ? [] : arguments)
do {
    try process.run()
    process.waitUntilExit()
    exit(process.terminationStatus)
} catch {
    fputs("monitor_launcher_unavailable\n", stderr)
    exit(1)
}
