#Requires -RunAsAdministrator
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$BackupPath)

$ErrorActionPreference = "Stop"
$running = @(Get-Process -Name Rhino -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
    $ids = ($running | ForEach-Object { $_.Id }) -join ", "
    throw "Rollback refused: Rhino.exe is running (PID(s): $ids). Close every Rhino process first."
}
$backup = (Resolve-Path $BackupPath).Path
$sourceNet = Join-Path $backup "net8.0"
$sourceRouter = Join-Path $backup "router\win-x64"
if (-not (Test-Path (Join-Path $sourceNet "RhinoAI.rhp"))) { throw "Backup is missing net8.0\RhinoAI.rhp." }
if (-not (Test-Path (Join-Path $sourceRouter "rhino-mcp-router.exe"))) { throw "Backup is missing router\win-x64." }

$installRoot = Join-Path $env:ProgramFiles "Rhino 9\Plug-ins\RhinoAI"
if (-not (Test-Path $installRoot)) { throw "Installed RhinoAI folder not found: $installRoot" }
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$failed = Join-Path $env:LOCALAPPDATA ("Inventaur\RhinoAI\FailedRollback_" + $stamp)
New-Item -ItemType Directory -Path $failed -Force | Out-Null

$newNet = Join-Path $installRoot "net8.0"
$newRouter = Join-Path $installRoot "router\win-x64"
if (Test-Path $newNet) { Move-Item $newNet (Join-Path $failed "net8.0") }
if (Test-Path $newRouter) { Move-Item $newRouter (Join-Path $failed "win-x64") }
try {
    Copy-Item $sourceNet $newNet -Recurse -Force
    Copy-Item $sourceRouter $newRouter -Recurse -Force
    $expected = (Get-FileHash (Join-Path $sourceNet "RhinoAI.rhp") -Algorithm SHA256).Hash
    $actual = (Get-FileHash (Join-Path $newNet "RhinoAI.rhp") -Algorithm SHA256).Hash
    if ($expected -ne $actual) { throw "Rollback RHP hash verification failed." }
    Write-Output "ROLLBACK_PASS"
    Write-Output ("RESTORED_FROM=" + $backup)
    Write-Output ("REPLACED_BUILD_SAVED=" + $failed)
    Write-Output "Restart Rhino 9 manually."
} catch {
    if (Test-Path $newNet) { Remove-Item $newNet -Recurse -Force }
    if (Test-Path $newRouter) { Remove-Item $newRouter -Recurse -Force }
    if (Test-Path (Join-Path $failed "net8.0")) { Move-Item (Join-Path $failed "net8.0") $newNet }
    if (Test-Path (Join-Path $failed "win-x64")) {
        New-Item -ItemType Directory -Path (Split-Path $newRouter -Parent) -Force | Out-Null
        Move-Item (Join-Path $failed "win-x64") $newRouter
    }
    throw
}
