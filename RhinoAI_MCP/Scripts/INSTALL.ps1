#Requires -RunAsAdministrator
[CmdletBinding()]
param([switch]$ConfirmInstall)

$ErrorActionPreference = "Stop"
if (-not $ConfirmInstall) {
    throw "Explicit confirmation required. Review the package README, close Rhino, then rerun with -ConfirmInstall."
}
$running = @(Get-Process -Name Rhino -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
    $ids = ($running | ForEach-Object { $_.Id }) -join ", "
    throw "Install refused: Rhino.exe is running (PID(s): $ids). Close every Rhino process; this script never terminates Rhino."
}

$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$source = Join-Path $packageRoot "Build\RhinoAI"
$sourceNet = Join-Path $source "net8.0"
$sourceRouter = Join-Path $source "router\win-x64"
$installRoot = Join-Path $env:ProgramFiles "Rhino 9\Plug-ins\RhinoAI"
if (-not (Test-Path (Join-Path $sourceNet "RhinoAI.rhp"))) { throw "Package is missing the RhinoAI RHP." }
if (-not (Test-Path (Join-Path $sourceNet "Acp.dll"))) { throw "Package is missing Acp.dll." }
if (-not (Test-Path (Join-Path $sourceRouter "rhino-mcp-router.exe"))) { throw "Package is missing the Windows x64 router." }
if (-not (Test-Path $installRoot)) { throw "Installed RhinoAI folder not found: $installRoot" }

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupBase = Join-Path $env:LOCALAPPDATA "Inventaur\RhinoAI\Backups"
$backup = Join-Path $backupBase ("RhinoAI_before_repair_" + $stamp)
$stage = Join-Path $env:TEMP ("RhinoAI_repair_stage_" + $stamp)
New-Item -ItemType Directory -Path $backup -Force | Out-Null
New-Item -ItemType Directory -Path $stage -Force | Out-Null

$newNet = Join-Path $installRoot "net8.0"
$newRouter = Join-Path $installRoot "router\win-x64"
$oldNetStage = Join-Path $stage "old_net8.0"
$oldRouterStage = Join-Path $stage "old_router_win-x64"
$hadNet = Test-Path $newNet
$hadRouter = Test-Path $newRouter
$oldNetMoved = $false
$oldRouterMoved = $false
$newNetInstalled = $false
$newRouterInstalled = $false

try {
    if ($hadNet) {
        New-Item -ItemType Directory -Path (Join-Path $backup "net8.0") -Force | Out-Null
        Copy-Item (Join-Path $newNet "*") (Join-Path $backup "net8.0") -Recurse -Force
        $oldHash = (Get-FileHash (Join-Path $newNet "RhinoAI.rhp") -Algorithm SHA256).Hash
        $backupHash = (Get-FileHash (Join-Path $backup "net8.0\RhinoAI.rhp") -Algorithm SHA256).Hash
        if ($oldHash -ne $backupHash) { throw "Existing RHP backup hash mismatch; install aborted before mutation." }
    }
    if ($hadRouter) {
        New-Item -ItemType Directory -Path (Join-Path $backup "router\win-x64") -Force | Out-Null
        Copy-Item (Join-Path $newRouter "*") (Join-Path $backup "router\win-x64") -Recurse -Force
        if (-not (Test-Path (Join-Path $backup "router\win-x64\rhino-mcp-router.exe"))) {
            throw "Existing router backup incomplete; install aborted before mutation."
        }
    }

    Copy-Item $sourceNet (Join-Path $stage "new_net8.0") -Recurse -Force
    Copy-Item $sourceRouter (Join-Path $stage "new_router_win-x64") -Recurse -Force
    $expected = (Get-FileHash (Join-Path $sourceNet "RhinoAI.rhp") -Algorithm SHA256).Hash
    $staged = (Get-FileHash (Join-Path $stage "new_net8.0\RhinoAI.rhp") -Algorithm SHA256).Hash
    if ($expected -ne $staged) { throw "Staged RhinoAI RHP SHA-256 mismatch." }

    if ($hadNet) {
        Move-Item $newNet $oldNetStage
        $oldNetMoved = $true
    }
    if ($hadRouter) {
        Move-Item $newRouter $oldRouterStage
        $oldRouterMoved = $true
    }

    Move-Item (Join-Path $stage "new_net8.0") $newNet
    $newNetInstalled = $true
    New-Item -ItemType Directory -Path (Split-Path $newRouter -Parent) -Force | Out-Null
    Move-Item (Join-Path $stage "new_router_win-x64") $newRouter
    $newRouterInstalled = $true

    $installed = (Get-FileHash (Join-Path $newNet "RhinoAI.rhp") -Algorithm SHA256).Hash
    if ($installed -ne $expected) { throw "Installed RhinoAI RHP SHA-256 mismatch." }
    if (-not (Test-Path (Join-Path $newRouter "rhino-mcp-router.exe"))) { throw "Installed router executable is missing." }
} catch {
    if ($newRouterInstalled -and (Test-Path $newRouter)) { Remove-Item $newRouter -Recurse -Force }
    if ($newNetInstalled -and (Test-Path $newNet)) { Remove-Item $newNet -Recurse -Force }
    if ($oldNetMoved -and (Test-Path $oldNetStage)) { Move-Item $oldNetStage $newNet }
    if ($oldRouterMoved -and (Test-Path $oldRouterStage)) { Move-Item $oldRouterStage $newRouter }
    throw
} finally {
    if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
}

$receipt = [ordered]@{
    installed_at = (Get-Date).ToString("o")
    install_root = $installRoot
    backup_path = $backup
    rhinoai_rhp_sha256 = $expected
    note = "Start Rhino 9 manually. This installer never starts, stops or closes Rhino."
}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $backup "INSTALL_RECEIPT.json")
Write-Output "INSTALL_PASS"
Write-Output ("BACKUP_PATH=" + $backup)
Write-Output ("RHINOAI_RHP_SHA256=" + $expected)
Write-Output "Restart Rhino 9 manually, then verify the actual MCP endpoint with Scripts\VERIFY.ps1."
