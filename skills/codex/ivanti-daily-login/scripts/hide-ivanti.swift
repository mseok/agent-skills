import AppKit
import ApplicationServices

let ivanti = NSWorkspace.shared.runningApplications.first {
    $0.bundleIdentifier == "net.pulsesecure.Pulse-Secure"
}

guard let ivanti else {
    print("{\"status\":\"not_running\"}")
    exit(0)
}

if ivanti.isHidden {
    print("{\"status\":\"already_hidden\"}")
    exit(0)
}

let root = AXUIElementCreateApplication(ivanti.processIdentifier)
var value: CFTypeRef?
let windows = AXUIElementCopyAttributeValue(root, kAXWindowsAttribute as CFString, &value) == .success
    ? value as? [AXUIElement] ?? []
    : []
var minimized = 0
for window in windows {
    var settable: DarwinBoolean = false
    if AXUIElementIsAttributeSettable(window, kAXMinimizedAttribute as CFString, &settable) == .success,
       settable.boolValue,
       AXUIElementSetAttributeValue(window, kAXMinimizedAttribute as CFString, kCFBooleanTrue) == .success {
        minimized += 1
    }
}

if minimized > 0 {
    print("{\"status\":\"minimized\"}")
} else if ivanti.hide() {
    print("{\"status\":\"hidden\"}")
} else {
    print("{\"status\":\"no_visible_window\"}")
}
