import AppKit
import Darwin
func emit(_ s:String){print(s)}
guard ProcessInfo.processInfo.environment["KVPN_PRIVATE_PIPE"]=="1",isatty(STDIN_FILENO)==0 else{emit("{\"status\":\"private_pipe_required\"}");exit(1)}
let input=FileHandle.standardInput.readDataToEndOfFile()
guard let raw=String(data:input,encoding:.utf8),let url=URL(string:raw.trimmingCharacters(in:.whitespacesAndNewlines)),url.scheme?.lowercased()=="pulsesecure" else{emit("{\"status\":\"invalid_launcher_scheme\"}");exit(1)}
let app=URL(fileURLWithPath:NSHomeDirectory()+"/Library/Application Support/Pulse Secure/PulseApplicationLauncher.app")
let configuration=NSWorkspace.OpenConfiguration();configuration.activates=false;configuration.hides=true;configuration.promptsUserIfNeeded=false;configuration.addsToRecentItems=false
var done=false;var failed=false
NSWorkspace.shared.open([url],withApplicationAt:app,configuration:configuration){_,error in failed=error != nil;done=true}
let deadline=Date().addingTimeInterval(10)
while !done && Date()<deadline {_=RunLoop.current.run(mode:.default,before:Date().addingTimeInterval(0.1))}
if done && !failed{emit("{\"status\":\"launcher_request_delivered\"}")}else{emit("{\"status\":\"launcher_delivery_failed\"}");exit(1)}
