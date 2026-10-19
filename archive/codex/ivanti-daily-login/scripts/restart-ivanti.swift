import AppKit

let bundleIdentifier = "net.pulsesecure.Pulse-Secure"

func emit(_ status: String) {
    print("{\"status\":\"\(status)\"}")
}

func runningIvanti() -> [NSRunningApplication] {
    NSWorkspace.shared.runningApplications.filter { $0.bundleIdentifier == bundleIdentifier }
}

let apps = runningIvanti()
guard let ivanti = apps.first else {
    emit("already_exited")
    exit(0)
}

// Request the application's own normal termination path.  This deliberately
// does not force-quit the process or touch any Ivanti service.
guard ivanti.terminate() else {
    emit("exit_refused")
    exit(1)
}

let deadline = Date().addingTimeInterval(10)
while Date() < deadline {
    if runningIvanti().isEmpty {
        emit("exited")
        exit(0)
    }
    _ = RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.1))
}

emit("exit_timeout")
exit(1)
