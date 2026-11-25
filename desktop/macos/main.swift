import AppKit
import WebKit

final class Reader: NSObject, NSApplicationDelegate, WKUIDelegate {
    let service = Process()
    var window: NSWindow!
    func applicationDidFinishLaunching(_ notification: Notification) {
        let resources = Bundle.main.resourceURL!
        service.executableURL = resources.appendingPathComponent("python/bin/python3.12")
        service.arguments = ["-E", "-s", "-B", resources.appendingPathComponent("backend/desktop.py").path]
        let ready = Pipe()
        service.standardOutput = ready
        do {
            try service.run()
            guard ready.fileHandleForReading.availableData == Data("ready\n".utf8) else {
                throw NSError(domain: "SOS My Feed", code: 1, userInfo: [NSLocalizedDescriptionKey: "Could not start the local feed server on port 18371."])
            }
        } catch {
            NSAlert(error: error).runModal()
            NSApp.terminate(nil)
            return
        }
        let view = WKWebView()
        view.uiDelegate = self
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 990, height: 750), styleMask: [.titled,.closable,.miniaturizable,.resizable], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        window.title = "SOS My Feed"
        window.contentView = view
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        view.load(URLRequest(url: URL(string: "http://127.0.0.1:18371/")!))
    }
    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration, for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = navigationAction.request.url, ["https","http"].contains(url.scheme) { NSWorkspace.shared.open(url) }
        return nil
    }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
    func applicationWillTerminate(_ notification: Notification) { if service.isRunning { service.terminate() } }
}
let app = NSApplication.shared
let delegate = Reader()
app.delegate = delegate
app.setActivationPolicy(.regular)
let menu = NSMenu()
let appItem = menu.addItem(withTitle: "SOS My Feed", action: nil, keyEquivalent: "")
appItem.submenu = NSMenu()
appItem.submenu?.addItem(withTitle: "Quit SOS My Feed", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
let edit = menu.addItem(withTitle: "Edit", action: nil, keyEquivalent: "")
edit.submenu = NSMenu(title: "Edit")
for (title, key, action) in [("Cut","x","cut:"),("Copy","c","copy:"),("Paste","v","paste:"),("Select All","a","selectAll:")] {
    edit.submenu?.addItem(withTitle: title, action: NSSelectorFromString(action), keyEquivalent: key)
}
app.mainMenu = menu
app.run()
