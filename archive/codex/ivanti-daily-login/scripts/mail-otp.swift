import Foundation
import Darwin

// Read-only KVPN email OTP reader. Secret-bearing wait output is private
// child-process IPC only; never invoke it through a terminal/tool that
// displays stdout.
let arguments = Array(CommandLine.arguments.dropFirst())
func option(_ name:String) -> String? {
    guard let index=arguments.firstIndex(of:name), index+1<arguments.count else{return nil}
    return arguments[index+1]
}
func emit(_ value:[String:Any]) {
    guard let data=try? JSONSerialization.data(withJSONObject:value), let line=String(data:data,encoding:.utf8) else{exit(1)}
    print(line)
}

let privateMode=arguments.contains("--wait")
if privateMode && (ProcessInfo.processInfo.environment["KVPN_PRIVATE_PIPE"] != "1" || isatty(STDOUT_FILENO) != 0) {exit(1)}

let manager=FileManager.default
let template=try! NSRegularExpression(pattern:#"(?is)KVPN\s+OTP\s+number.{0,4096}?(?<![0-9])([0-9]{6})(?![0-9])"#)

func fnv1a(_ value:String) -> String {
    var hash:UInt64=14695981039346656037
    for byte in value.utf8 {
        hash ^= UInt64(byte)
        hash &*= 1099511628211
    }
    return String(hash,radix:16)
}

func mailRoots() -> [URL] {
    let root=URL(fileURLWithPath:NSHomeDirectory()).appendingPathComponent("Library/Mail",isDirectory:true)
    guard let versions=try? manager.contentsOfDirectory(at:root,includingPropertiesForKeys:[.isDirectoryKey],options:[.skipsHiddenFiles]) else{return []}
    var roots:[URL]=[]
    for version in versions where version.lastPathComponent.range(of:#"^V[0-9]+$"#,options:.regularExpression) != nil {
        guard let enumerator=manager.enumerator(at:version,includingPropertiesForKeys:[.isDirectoryKey],options:[.skipsHiddenFiles]) else{continue}
        while let candidate=enumerator.nextObject() as? URL {
            if candidate.lastPathComponent == "[Gmail].mbox" {roots.append(candidate);enumerator.skipDescendants()}
        }
    }
    return roots
}

func emlxFiles() -> [(URL,Date)] {
    var files:[(URL,Date)]=[]
    for root in mailRoots() {
        guard let enumerator=manager.enumerator(at:root,includingPropertiesForKeys:[.contentModificationDateKey,.isRegularFileKey],options:[.skipsHiddenFiles]) else{continue}
        while let candidate=enumerator.nextObject() as? URL {
            guard candidate.pathExtension == "emlx", let values=try? candidate.resourceValues(forKeys:[.isRegularFileKey,.contentModificationDateKey]), values.isRegularFile == true, let changed=values.contentModificationDate else{continue}
            files.append((candidate,changed))
        }
    }
    return files
}

func contents(_ file:URL) -> String? {
    guard let handle=try? FileHandle(forReadingFrom:file) else{return nil}
    defer{try? handle.close()}
    guard let data=try? handle.read(upToCount:262144) else{return nil}
    return String(data:data,encoding:.utf8) ?? String(data:data,encoding:.isoLatin1)
}

func senderHash(_ message:String) -> String? {
    guard let match=try? NSRegularExpression(pattern:#"(?mi)^From:[ \t]*([^\r\n]*(?:\r?\n[ \t]+[^\r\n]*)*)"#).firstMatch(in:message,range:NSRange(message.startIndex...,in:message)), let range=Range(match.range(at:1),in:message) else{return nil}
    let value=message[range].replacingOccurrences(of:#"\s+"#,with:" ",options:.regularExpression).trimmingCharacters(in:.whitespacesAndNewlines).lowercased()
    return value.isEmpty ? nil : fnv1a(value)
}

func receipt(_ message:String, expectedSender:String?=nil) -> (String,String)? {
    guard let sender=senderHash(message), expectedSender == nil || sender == expectedSender, let match=template.firstMatch(in:message,range:NSRange(message.startIndex...,in:message)), let range=Range(match.range(at:1),in:message) else{return nil}
    return (sender,String(message[range]))
}

if !privateMode {
    let known=emlxFiles().compactMap { receipt(contents($0.0) ?? "")?.0 }
    let unique=Set(known)
    guard !unique.isEmpty, unique.count == 1, let sender=unique.first else {emit(["status":"unavailable"]);exit(0)}
    emit(["status":"ready","senderHash":sender,"matchedRecent":known.count,"capturedAtMs":Int64(Date().timeIntervalSince1970*1000)])
    exit(0)
}

guard let sender=option("--sender-hash"), let since=option("--since-ms").flatMap(Int64.init), let timeout=option("--timeout").flatMap(Double.init), abs(Date().timeIntervalSince1970-Double(since)/1000)<120 else{exit(1)}
let deadline=Date().addingTimeInterval(timeout)
let minimum=Date(timeIntervalSince1970:Double(since)/1000-2)
var inspected=Set<String>()
while Date()<deadline {
    for (file,changed) in emlxFiles() where changed >= minimum {
        let key=file.path + "|" + String(changed.timeIntervalSince1970)
        guard inspected.insert(key).inserted, let message=contents(file), let result=receipt(message,expectedSender:sender) else{continue}
        emit(["status":"received","code":result.1])
        exit(0)
    }
    usleep(500000)
}
exit(2)
