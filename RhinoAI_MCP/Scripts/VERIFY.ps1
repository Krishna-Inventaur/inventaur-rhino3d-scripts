[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateRange(1,65535)]
    [int]$Port,
    [string]$Address = "127.0.0.1"
)
$ErrorActionPreference = "Stop"
$client = [Net.Sockets.TcpClient]::new()
try {
    $async = $client.BeginConnect($Address,$Port,$null,$null)
    if (-not $async.AsyncWaitHandle.WaitOne(1500)) {
        throw "Timed out connecting to $Address port $Port. Run MCPStatus in Rhino and use the reported port."
    }
    $client.EndConnect($async)
} finally {
    $client.Close()
}
$body = '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
$response = Invoke-RestMethod -Uri ("http://{0}:{1}/" -f $Address,$Port) -Method Post -ContentType "application/json" -Body $body -TimeoutSec 10
$tools = @($response.result.tools)
if ($response.jsonrpc -ne "2.0" -or $tools.Count -lt 1) {
    throw "The endpoint did not return a valid JSON-RPC tools/list response."
}
Write-Output "VERIFY_PASS"
Write-Output ("ENDPOINT=http://{0}:{1}/" -f $Address,$Port)
Write-Output ("TOOL_COUNT=" + $tools.Count)
