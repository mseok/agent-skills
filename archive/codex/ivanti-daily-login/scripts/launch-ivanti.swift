import AppKit

func emit(_ status: String) {
    print("{\"status\":\"\(status)\"}")
}

let app = URL(fileURLWithPath: "/Applications/Ivanti Secure Access.app")
guard FileManager.default.fileExists(atPath: app.path) else {
    emit("app_missing")
    exit(1)
}

let configuration = NSWorkspace.OpenConfiguration()
configuration.activates = false
configuration.hides = true
configuration.promptsUserIfNeeded = false
configuration.addsToRecentItems = false
configuration.createsNewApplicationInstance = false

var completed = false
var succeeded = false
NSWorkspace.shared.openApplication(at: app, configuration: configuration) { _, error in
    succeeded = error == nil
    completed = true
}

let deadline = Date().addingTimeInterval(10)
while !completed && Date() < deadline {
    _ = RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.1))
}

if completed && succeeded {
    emit("started")
} else {
    emit("start_failed")
    exit(1)
}
