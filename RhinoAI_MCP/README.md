# RhinoAI MCP

Client-neutral RhinoAI MCP reliability repair for Rhino 9 on Windows x64.

This is a normal, editable source tree. The plugin (RhinoAI.rhp), router and supporting runtime files are kept as individual files under Build; no ZIP is required.

## What this provides

- The RhinoAI plugin is the MCP server inside Rhino.
- The router exposes the same RhinoAI server through standard MCP stdio for AI clients.
- Rhino's MCPConnect command opens the built-in connection dialog. Its Install tab detects supported AI clients and adds/removes the RhinoAI MCP entry; its Prompt and mcp.json tabs provide manual configuration for other MCP-compatible clients.
- The MCP server exposes Rhino document, command, scripting, viewport and Grasshopper tools through the standard MCP protocol.
- The source patch adds a per-document listener ownership check to MCPStart; success is not inferred from an unrelated process occupying a port.
- Installation is guarded, backs up the existing plugin and refuses to run while Rhino is open.

## Layout

| Path | Purpose |
|---|---|
| Build/RhinoAI/ | Loadable RhinoAI RHP, required runtime files and Windows x64 stdio router |
| Source/RhinoAI/ | Patched MCPStart source, original source, patch and upstream attribution |
| Scripts/ | Guarded source patch, install, rollback and exact-endpoint verification |
| Tests/ | Project contract tests and upstream source regression reference |
| Reports/ | Build, fresh-process MCP and test evidence |
| Licenses/ | McNeel MIT licence and third-party notices |
| manifest.json | File inventory, byte counts and SHA-256 hashes |

## Requirements

- Windows 10/11 x64
- Rhino 9
- A valid Rhino licence
- .NET 8 runtime supplied/used by the Rhino 9 plugin environment
- An AI application that supports MCP for direct connection

This build is for Rhino 9 Windows x64. It does not claim Rhino 8 binary compatibility.

## Connect an AI client

1. Install the plugin using the guarded procedure below.
2. Start Rhino 9 and run MCPConnect.
3. Use the Install tab for a detected client. RhinoAI writes that client's standard MCP configuration.
4. For an undetected client, use the mcp.json or Prompt tab and follow that client's MCP configuration instructions. Point stdio clients to rhino-mcp-router.exe in the installed RhinoAI router directory.
5. Restart/reload the AI client if its MCP configuration requires it.
6. In Rhino, run MCPStatus. Use the actual endpoint/port it reports.

The same RhinoAI server is used by all clients. Do not install a separate Rhino-side MCP server for each AI application.

## Install the rebuilt RhinoAI plugin

The build is staged; it has not been installed over an active user Rhino process.

1. Close every Rhino process normally.
2. Open an elevated PowerShell in this folder.
3. Run: .\Scripts\INSTALL.ps1 -ConfirmInstall
4. Start Rhino 9 manually.
5. Run MCPStatus and note the actual port.
6. Verify that exact endpoint: .\Scripts\VERIFY.ps1 -Port 10500
   Replace 10500 with the port reported by Rhino. The verification script never scans a port range.

The installer does not launch, terminate or restart Rhino. It backs up the current net8.0 and router folders, validates the staged RHP hash, installs the staged files and rolls back on failure.

## Apply the source patch to a RhinoAI checkout

Run .\Scripts\APPLY_RHINOAI_SOURCE_PATCH.ps1 -RhinoAISourceRoot "C:\path\to\RhinoAI".

The patcher requires the exact expected upstream preimage. It refuses unknown source revisions. Build the plugin from the patched checkout before installing it.

## Roll back

Close all Rhino processes, then run Scripts/ROLLBACK.ps1 with the backup path printed by the installer.

## Verify and reproduce

Run from this folder: python -m pytest Tests/test_project_contract.py -q

The upstream static source regression in Tests/reference/ is intended to run from a complete RhinoAI source checkout.

Build evidence and exact hashes are in Reports/BUILD_REPORT.json. Fresh-process listener allocation evidence is in Reports/LIVE_MCP_E2E.json. Consolidated repair evidence is in Reports/REPAIR_E2E_REPORT.json.

## Test boundary and known limits

- Fresh Rhino 9 startup with the revised Inventaur AutoLayer completed in about 1.03 seconds; MCPStart took about 303 ms.
- The disposable Rhino endpoint returned JSON-RPC tools/list with 44 tools. The OS selected port 53318 in that test; this does not prove 10501 was selected.
- The existing user Rhino session on port 10500 was preserved.
- The replacement RHP is built and staged, not yet installed/reloaded into the user's active Rhino runtime.
- Use the exact port reported by MCPStatus; dynamic allocation means a fixed port must not be assumed.
- Unknown native dialogs and save/discard prompts are not auto-accepted.

## Licensing and attribution

The RhinoAI_MCP subtree has its own MIT licence for Inventaur-authored repair changes. McNeel's original RhinoAI MIT licence is included under Licenses. This is an independent community repair, not an official or endorsed McNeel release.

The parent repository's commercial licence continues to apply to RhinoStandards and the other existing Inventaur-authored components; it does not override the explicit MIT licence in this subtree.
