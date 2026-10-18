import Foundation
import SQLite3
import Darwin

// Read-only KVPN SMS reader. The secret-bearing mode is private child-process
// IPC only; never invoke it through a terminal/tool whose output is displayed.
let arguments = Array(CommandLine.arguments.dropFirst())
func option(_ name:String) -> String? {
    guard let i=arguments.firstIndex(of:name),i+1<arguments.count else{return nil}
    return arguments[i+1]
}
func emit(_ value:[String:Any]) {
    let data=try! JSONSerialization.data(withJSONObject:value,options:[.sortedKeys])
    print(String(data:data,encoding:.utf8)!)
}
func fail(_ reason:String)->Never {emit(["status":"error","reason":reason]);exit(1)}
let privateMode=arguments.contains("--wait")
if privateMode && (ProcessInfo.processInfo.environment["KVPN_PRIVATE_PIPE"] != "1" || isatty(STDOUT_FILENO) != 0) {fail("private_pipe_required")}
var db:OpaquePointer?
let path=NSHomeDirectory()+"/Library/Messages/chat.db"
guard sqlite3_open_v2(path,&db,SQLITE_OPEN_READONLY,nil)==SQLITE_OK else{fail("messages_read_unavailable")}
defer{sqlite3_close(db)}
sqlite3_busy_timeout(db,1500)
let pattern=try! NSRegularExpression(pattern:#"^\[Web발신\]\s*KVPN OTP number\s*:\s*\[([0-9]{6})\]\s*$"#)
func code(_ st:OpaquePointer?)->String? {
    let body:String
    if let plain=sqlite3_column_text(st,3) {body=String(cString:plain)}
    else if let ptr=sqlite3_column_blob(st,4) {
        let data=Data(bytes:ptr,count:Int(sqlite3_column_bytes(st,4)))
        // Messages currently uses the legacy typed-stream archive format.
        // NSKeyedUnarchiver does not decode this format.
        guard let value=NSUnarchiver.unarchiveObject(with:data) as? NSAttributedString else{return nil}
        body=value.string
    } else {return nil}
    guard let m=pattern.firstMatch(in:body,range:NSRange(body.startIndex...,in:body)),let range=Range(m.range(at:1),in:body) else{return nil}
    return String(body[range])
}
let now=Date().timeIntervalSince1970
if !privateMode {
    var st:OpaquePointer?
    let sql="SELECT ROWID,date,handle_id,text,attributedBody FROM message WHERE is_from_me=0 AND service='SMS' AND date>? ORDER BY ROWID DESC LIMIT 200"
    guard sqlite3_prepare_v2(db,sql,-1,&st,nil)==SQLITE_OK else{fail("messages_schema_unavailable")}
    defer{sqlite3_finalize(st)}
    sqlite3_bind_int64(st,1,Int64((now-978307200-7*86400)*1e9))
    var senders=Set<Int64>();var matches=0
    while sqlite3_step(st)==SQLITE_ROW {if code(st) != nil {senders.insert(sqlite3_column_int64(st,2));matches+=1}}
    guard senders.count==1 else{fail("kvpn_sender_not_unique")}
    var cursor:OpaquePointer?;sqlite3_prepare_v2(db,"SELECT COALESCE(MAX(ROWID),0) FROM message",-1,&cursor,nil);defer{sqlite3_finalize(cursor)}
    guard sqlite3_step(cursor)==SQLITE_ROW else{fail("cursor_unavailable")}
    emit(["status":"ready","cursor":sqlite3_column_int64(cursor,0),"senderHandle":senders.first!,"matchedRecent":matches,"capturedAtMs":Int64(now*1000)])
    exit(0)
}
guard let after=option("--after").flatMap(Int64.init),let since=option("--since-ms").flatMap(Int64.init),let sender=option("--sender").flatMap(Int64.init) else{fail("missing_request_scope")}
let timeout=min(max(option("--timeout").flatMap(Double.init) ?? 90,1),120)
guard abs(now-Double(since)/1000)<120 else{fail("stale_request_scope")}
let deadline=Date().addingTimeInterval(timeout)
let minDate=Int64((Double(since)/1000-978307200-2)*1e9)
let sql="SELECT ROWID,date,handle_id,text,attributedBody FROM message WHERE ROWID>? AND date>=? AND is_from_me=0 AND service='SMS' AND handle_id=? ORDER BY ROWID DESC LIMIT 20"
while Date()<deadline {
    var st:OpaquePointer?
    guard sqlite3_prepare_v2(db,sql,-1,&st,nil)==SQLITE_OK else{fail("messages_query_failed")}
    sqlite3_bind_int64(st,1,after);sqlite3_bind_int64(st,2,minDate);sqlite3_bind_int64(st,3,sender)
    var found:[String:Any]?
    while sqlite3_step(st)==SQLITE_ROW {
        let messageTime=Double(sqlite3_column_int64(st,1))/1e9+978307200
        let age=Date().timeIntervalSince1970-messageTime
        if age < -30 || age > 120 {continue}
        if let value=code(st) {found=["status":"received","code":value,"rowid":sqlite3_column_int64(st,0),"ageSeconds":Int(max(0,age))];break}
    }
    sqlite3_finalize(st)
    if let value=found {emit(value);exit(0)}
    Thread.sleep(forTimeInterval:0.5)
}
emit(["status":"timeout"]);exit(2)
