import AppKit
import ApplicationServices

// This helper is intentionally scoped to the already-running Ivanti app.  It
// never activates an app, reads editable fields, or sends global input.
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
func labels(_ element: AXUIElement) -> [String] {
    var values = [text(element, kAXTitleAttribute), text(element, kAXDescriptionAttribute)]
    // AXValue is inspected only for static text, never for an editable field.
    if text(element, kAXRoleAttribute) == "AXStaticText" {
        values.append(text(element, kAXValueAttribute))
    }
    return values
}
func containsTimeoutText(_ element: AXUIElement, _ depth: Int) -> Bool {
    if labels(element).contains("User input timeout. (1382)") { return true }
    guard depth > 0 else { return false }
    return children(element).contains { containsTimeoutText($0, depth - 1) }
}
func cancelButton(_ element: AXUIElement, _ depth: Int) -> AXUIElement? {
    if text(element, kAXRoleAttribute) == "AXButton",
       (attribute(element, kAXEnabledAttribute) as? Bool ?? false),
       labels(element).contains("Cancel") {
        return element
    }
    guard depth > 0 else { return nil }
    for child in children(element) {
        if let button = cancelButton(child, depth - 1) { return button }
    }
    return nil
}
func timeoutScope(_ element: AXUIElement, _ depth: Int) -> AXUIElement? {
    guard depth >= 0 else { return nil }
    for child in children(element) {
        if let scope = timeoutScope(child, depth - 1) { return scope }
    }
    if containsTimeoutText(element, min(depth, 5)), cancelButton(element, min(depth, 5)) != nil {
        return element
    }
    return nil
}

guard let app = NSWorkspace.shared.runningApplications.first(where: { $0.bundleIdentifier == "net.pulsesecure.Pulse-Secure" }) else {
    print("{\"status\":\"absent\"}")
    exit(0)
}
let root = AXUIElementCreateApplication(app.processIdentifier)
AXUIElementSetMessagingTimeout(root, 0.5)
for child in children(root) {
    guard let scope = timeoutScope(child, 8), let button = cancelButton(scope, 6) else { continue }
    if AXUIElementPerformAction(button, kAXPressAction as CFString) == .success {
        print("{\"status\":\"dismissed\"}")
        exit(0)
    }
    print("{\"status\":\"unavailable\"}")
    exit(0)
}
print("{\"status\":\"absent\"}")
