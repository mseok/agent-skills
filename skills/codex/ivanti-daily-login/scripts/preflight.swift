import AppKit
import ApplicationServices

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
let apps = NSWorkspace.shared.runningApplications
let ivanti = apps.first { $0.bundleIdentifier == "net.pulsesecure.Pulse-Secure" }
var exactProfile = false
var noActiveConnections = false
var profileDisconnectAvailable = false
var profileConnectAvailable = false
var connectAvailable = false
var disconnectAvailable = false
var exitAvailable = false
var trayFound = false
if let app = ivanti {
    let root = AXUIElementCreateApplication(app.processIdentifier)
    AXUIElementSetMessagingTimeout(root, 0.5)
    // Read only the Ivanti status menu. Do not enumerate unrelated menu contents
    // or read editable fields, user names, passwords, OTPs, URLs, or values.
    func findStatusMenus(_ element: AXUIElement, _ depth: Int) -> [AXUIElement] {
        if text(element, kAXRoleAttribute) == "AXMenu" {
            return text(element, kAXDescriptionAttribute) == "Pulse Tray Menu" ? [element] : []
        }
        if depth >= 3 { return [] }
        return children(element).flatMap { findStatusMenus($0, depth + 1) }
    }
    for node in findStatusMenus(root, 0) {
        trayFound = true
        func statusItems(_ element: AXUIElement, _ depth: Int) -> [AXUIElement] {
            if depth >= 4 { return [] }
            return children(element).flatMap { [$0] + statusItems($0, depth + 1) }
        }
        for item in statusItems(node, 0) {
            let title = text(item, kAXTitleAttribute)
            exactProfile = exactProfile || title == "SA (kvpn.kaist.ac.kr)"
            noActiveConnections = noActiveConnections || title.lowercased().contains("no active connections")
            if title == "SA (kvpn.kaist.ac.kr)" {
                for action in statusItems(item, 0) {
                    let enabled = attribute(action, kAXEnabledAttribute) as? Bool ?? false
                    profileDisconnectAvailable = profileDisconnectAvailable || (enabled && text(action, kAXTitleAttribute) == "Disconnect")
                    profileConnectAvailable = profileConnectAvailable || (enabled && text(action, kAXTitleAttribute) == "Connect")
                }
            }
            connectAvailable = connectAvailable || title == "Connect"
            disconnectAvailable = disconnectAvailable || title == "Disconnect"
            exitAvailable = exitAvailable || title == "Exit"
        }
    }
}
let state: [String: Any] = [
    "axTrusted": AXIsProcessTrusted(),
    "ivantiRunning": ivanti != nil,
    "trayObserved": trayFound,
    "exactProfile": exactProfile,
    "noActiveConnections": noActiveConnections,
    "profileDisconnectAvailable": profileDisconnectAvailable,
    "profileConnectAvailable": profileConnectAvailable,
    "connectAvailable": connectAvailable,
    "disconnectAvailable": disconnectAvailable,
    "exitAvailable": exitAvailable
]
let data = try JSONSerialization.data(withJSONObject: state, options: [.sortedKeys])
print(String(data: data, encoding: .utf8)!)
