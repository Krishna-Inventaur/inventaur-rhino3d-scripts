# Inventaur Rhino3D Scripts

Maintained Rhino 8/9 startup automation and Rhino 9 drafting standards by Inventaur Inc.

This repository has two clearly separated components with different licences:

- RhinoStandards: Inventaur drafting standards, AutoLayer startup, installer, hatch export and legacy reference scripts. Governed by the repository's commercial licence in LICENSE.md.
- RhinoAI_MCP: a client-neutral RhinoAI MCP reliability repair, built RhinoAI plugin, stdio router, source patch and guarded deployment tools. This subtree has its own MIT licence in RhinoAI_MCP/LICENSE.md; McNeel's original MIT licence and notices are included.

## RhinoAI MCP — connect any compatible AI client

RhinoAI is the MCP server running inside Rhino. It is not tied to IvyGPT or any one AI application.

1. Install the RhinoAI plugin using the guarded instructions in RhinoAI_MCP/README.md.
2. Open Rhino 9 and run MCPConnect.
3. Use the Install tab to add the server to a detected client.
4. Use the Prompt or mcp.json tab for a compatible client that is not detected.
5. Run MCPStatus in Rhino and use its actual listener endpoint.

The built-in RhinoAI connection dialog currently detects Claude Code, Cursor, Gemini CLI, Windsurf, OpenCode and Codex. Other MCP-compatible clients can use the standard configuration snippet or stdio router. The same Rhino-side MCP server is used by all clients.

The editable RhinoAI source tree includes the loadable RhinoAI.rhp, runtime files, Windows x64 stdio router, patched MCPStart source, original source, install/rollback scripts, tests and reports. No ZIP is required.

- Project guide: RhinoAI_MCP/README.md
- Loadable plugin: RhinoAI_MCP/Build/RhinoAI/net8.0/RhinoAI.rhp
- Standard stdio router: RhinoAI_MCP/Build/RhinoAI/router/win-x64/rhino-mcp-router.exe
- Source patch: RhinoAI_MCP/Source/RhinoAI/MCPStartCommand.cs
- Verification: RhinoAI_MCP/Reports/TEST_RESULTS.md

## RhinoStandards

The RhinoStandards source contains:

- AutoLayer startup entrypoint and automatic TEXT / ANNOTATIONS / HATCH routing.
- Drafting standards installer and metric template workflow.
- Dimension and text styles.
- Native Rhino hatch export utility.
- Retained legacy router for reference only.

Rhino 9 AutoLayer now delegates MCP listener allocation to RhinoAI through _MCPStart _Enter. It does not scan ports or issue synchronous network probes on Rhino's startup/UI thread. RhinoAI owns the listener allocation and document-scoped registration. Rhino 8 retains its separate MCP-only 10508 path.

- Package guide: RhinoStandards/README.md
- AutoLayer guide: RhinoStandards/AutoLayer/README.md
- Standards installer: RhinoStandards/Installer/README.md
- Hatch export: RhinoStandards/HatchLibrary/README.md

## Source and release policy

The editable folders in this repository are the canonical sources. Historical release snapshots remain in Releases for traceability; ongoing work is performed against the source files. New maintenance is not handed off as date-stamped ZIP archives.

## Licensing

The repository root licence applies to RhinoStandards and other existing Inventaur-authored content. The RhinoAI_MCP folder is an explicit separately licensed MIT subtree. Third-party McNeel source and licence attribution is retained inside that folder.
