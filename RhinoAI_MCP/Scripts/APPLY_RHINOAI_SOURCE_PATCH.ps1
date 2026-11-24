[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$RhinoAISourceRoot)

$ErrorActionPreference = "Stop"
$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$target = Join-Path $RhinoAISourceRoot "rhino\plugin\Commands\MCPStartCommand.cs"
$patched = Join-Path $packageRoot "Source\RhinoAI\MCPStartCommand.cs"
$before = Join-Path $packageRoot "Source\RhinoAI\MCPStartCommand.cs.before.cs"
$expectedBefore = "4e81ffedac3acfe7cf7181c0f80184b4b1f8498f52632aa8efe4302d63af99cb"
$expectedAfter = "a984b21db917a4de301c4bfc0e3544656811381702953b43670b034dbc800cd5"
foreach ($file in @($target,$patched,$before)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Required file missing: $file" }
}
$patchedHash = (Get-FileHash -LiteralPath $patched -Algorithm SHA256).Hash.ToLowerInvariant()
if ($patchedHash -ne $expectedAfter) { throw "Package patched source hash mismatch." }
$currentHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
if ($currentHash -eq $expectedAfter) {
    Write-Output "SOURCE_PATCH_ALREADY_APPLIED"
    exit 0
}
if ($currentHash -ne $expectedBefore) {
    throw "Refusing to overwrite an unknown RhinoAI source revision. Expected exact pre-repair SHA-256 $expectedBefore; found $currentHash. Review/merge the patch manually."
}
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = Join-Path $env:LOCALAPPDATA "Inventaur\RhinoAI\SourceBackups"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$backup = Join-Path $backupRoot ("MCPStartCommand_before_repair_" + $stamp + ".cs")
if (Test-Path -LiteralPath $backup) { throw "Refusing to overwrite an existing backup: $backup" }
$temp = $target + ".repair.tmp"
$originalMoved = $false
try {
    Copy-Item -LiteralPath $patched -Destination $temp -Force
    $tempHash = (Get-FileHash -LiteralPath $temp -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($tempHash -ne $expectedAfter) { throw "Staged source hash mismatch." }
    [IO.File]::Move($target,$backup)
    $originalMoved = $true
    try {
        [IO.File]::Move($temp,$target)
    } catch {
        if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
        if (Test-Path -LiteralPath $backup) { [IO.File]::Move($backup,$target); $originalMoved = $false }
        throw
    }
} finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
}
if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) { throw "Source backup was not created." }
$backupHash = (Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant()
if ($backupHash -ne $expectedBefore) {
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
    [IO.File]::Move($backup,$target)
    throw "Source backup hash mismatch; original source restored."
}
$installedHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
if ($installedHash -ne $expectedAfter) {
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
    [IO.File]::Move($backup,$target)
    throw "Source patch postcondition failed; original source restored."
}
Write-Output "SOURCE_PATCH_PASS"
Write-Output ("BACKUP=" + $backup)
Write-Output ("SOURCE_SHA256=" + $installedHash)
Write-Output "Rebuild RhinoAI from this source before installing/reloading the plugin."
