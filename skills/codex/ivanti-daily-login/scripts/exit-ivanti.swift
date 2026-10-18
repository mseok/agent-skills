import AppKit
import ApplicationServices

// This is a bounded fallback for a stuck Ivanti user app.  It scopes every
// accessibility operation to that app's own status menu, never activates an
// app or sends global input, and never force-quits a process or service.
let bundleIdentifier = "net.pulsesecure.Pulse-Secure"
let acceptPendingConfirmation = CommandLine.arguments.contains("--accept-pending")

func emit(_ status: String) {
    print("{\"status\":\"\(status)\"}")
}

func runningIvanti() -> [NSRunningApplication] {
    NSWorkspace.shared.runningApplications.filter { $0.bundleIdentifier == bundleIdentifier }
}

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success ? value : nil
}

func text(_ element: AXUIElement, _ name: String) -> String {
    attribute(element, name) as? String ?? ""
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    attribute(element, kAXChildrenAttribute) as? [AXUIElement] ?? []
}

func enabled(_ element: AXUIElement) -> Bool {
    attribute(element, kAXEnabledAttribute) as? Bool ?? false
}

func statusMenus(_ element: AXUIElement, _ depth: Int) -> [AXUIElement] {
    if text(element, kAXRoleAttribute) == "AXMenu" {
        return text(element, kAXDescriptionAttribute) == "Pulse Tray Menu" ? [element] : []
    }
    guard depth > 0 else { return [] }
    return children(element).flatMap { statusMenus($0, depth - 1) }
}

func exactExitItem(_ element: AXUIElement, _ depth: Int) -> AXUIElement? {
    for child in children(element) {
        if text(child, kAXTitleAttribute) == "Exit", enabled(child) {
            return child
        }
        if depth > 0, let item = exactExitItem(child, depth - 1) {
            return item
        }
    }
    return nil
}

func button(_ element: AXUIElement, named name: String, _ depth: Int) -> AXUIElement? {
    if text(element, kAXRoleAttribute) == "AXButton", enabled(element),
       text(element, kAXTitleAttribute) == name {
        return element
    }
    guard depth > 0 else { return nil }
    for child in children(element) {
        if let found = button(child, named: name, depth - 1) { return found }
    }
    return nil
}

func exitConfirmation(_ element: AXUIElement, _ depth: Int) -> AXUIElement? {
    let role = text(element, kAXRoleAttribute)
    let subrole = text(element, kAXSubroleAttribute)
    if role == "AXSheet" || role == "AXDialog" ||
        (role == "AXWindow" && subrole == "AXDialog") {
        // Ivanti 22.8 presents the status-menu Exit confirmation as an
        // AXWindow/AXDialog with OK and Cancel, not as an AXSheet with an
        // Exit-labelled button.  Accept only either exact known shape.
        if button(element, named: "Cancel", 6) != nil,
           (button(element, named: "Exit", 6) != nil ||
            button(element, named: "OK", 6) != nil) {
            return element
        }
    }
    guard depth > 0 else { return nil }
    for child in children(element) {
        if let found = exitConfirmation(child, depth - 1) { return found }
    }
    return nil
}

func confirmExit(_ confirmation: AXUIElement) -> Bool {
    // Prefer the explicit Exit label if a future client uses it; the current
    // client uses OK as its affirmative Exit action.  Both require the exact
    // companion Cancel button validated by exitConfirmation above.
    let confirm = button(confirmation, named: "Exit", 6) ??
        button(confirmation, named: "OK", 6)
    guard let confirm else { return false }
    return AXUIElementPerformAction(confirm, kAXPressAction as CFString) == .success
}

guard let initial = runningIvanti().first else {
    emit("already_exited")
    exit(0)
}

let root = AXUIElementCreateApplication(initial.processIdentifier)
AXUIElementSetMessagingTimeout(root, 0.5)
var confirmed = false
if let pending = exitConfirmation(root, 8) {
    // A normal invocation must not accept an alert that predates its own
    // exact Exit selection.  The opt-in path exists solely to finish a
    // confirmation already proven to have been created by this helper.
    guard acceptPendingConfirmation, confirmExit(pending) else {
        emit("exit_confirmation_pending")
        exit(1)
    }
    confirmed = true
}
if !confirmed {
    guard let exitItem = statusMenus(root, 3).lazy.compactMap({ exactExitItem($0, 4) }).first else {
        emit("exit_unavailable")
        exit(1)
    }
    // AXMenuItem exposes AXPick for selecting a menu command. AXPress can report
    // success without dispatching this status-menu item, so use AXPick first and
    // retain AXPress only for older client accessibility trees lacking AXPick.
    let selected = AXUIElementPerformAction(exitItem, kAXPickAction as CFString) == .success ||
        AXUIElementPerformAction(exitItem, kAXPressAction as CFString) == .success
    guard selected else {
        emit("exit_unavailable")
        exit(1)
    }
}

let deadline = Date().addingTimeInterval(15)
while Date() < deadline {
    if runningIvanti().isEmpty {
        emit("exited")
        exit(0)
    }
    if !confirmed,
       let current = runningIvanti().first {
        let currentRoot = AXUIElementCreateApplication(current.processIdentifier)
        AXUIElementSetMessagingTimeout(currentRoot, 0.5)
        if let confirmation = exitConfirmation(currentRoot, 8),
           confirmExit(confirmation) {
            confirmed = true
        }
    }
    _ = RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.1))
}

emit("exit_timeout")
exit(1)
