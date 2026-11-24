# RhinoAI MCP startup reliability repair

**Repair date:** 24 November 2026  
**Upstream:** McNeel RhinoAI, Rhino 9 branch  
**Target:** Rhino 9 / Windows / .NET 8

## Root cause and changes

Inventaur's AutoLayer bootstrap previously performed synchronous TCP port-range scanning and JSON-RPC endpoint probes on Rhino's startup/UI thread. This duplicated work already owned by RhinoAI and allowed unrelated or non-responsive endpoints to delay Rhino startup.

The startup entrypoint now delegates allocation to RhinoAI with _MCPStart _Enter on Rhino 9. RhinoAI's allocator owns the actual listener bind and collision handling. The AutoLayer script no longer scans 10500–10600 synchronously, creates TCP clients for MCP discovery, calls tools/list during startup, or treats an occupied TCP port as proof that the current document owns a working MCP endpoint.

MCPStartCommand.cs also now verifies the postcondition against the active document with RhinoAIHost.TryGetPortFor(doc, out registeredPort). The command reports success only when the selected port matches the listener registered to that exact Rhino document. An accepted macro or unrelated listener is not sufficient.

## Fresh-process evidence

- Rhino 9.1.26314.9001 disposable process started with the revised AutoLayer script.
- Total bootstrap: approximately 1.03 s; MCPStart phase: approximately 303 ms.
- RhinoAI exposed its endpoint on OS-assigned fallback port 53318 in this run.
- JSON-RPC tools/list: HTTP 200, 44 tools.
- The disposable process was closed gracefully and port 53318 closed.
- Existing user Rhino process PID 1784 and its port 10500 remained untouched.
- The test did not establish that preferred next port 10501 was selected. Do not report that it did.

## Build and promotion

The patched RhinoAI plugin and Windows x64 router build successfully in Release/net8.0 using .NET SDK 8.0.427 and cached Rhino 9 reference packages. One unrelated pre-existing CS1998 warning in the router was excluded from warning-as-error for this isolated build; no unrelated source code was changed.

The RHP was not copied over the installed plugin while a working Rhino session was active. The separate community package contains a guarded installer and rollback. Both refuse to operate while any Rhino.exe process is running; neither terminates or restarts Rhino.

## Regression tests

- Combined RhinoAI MCP autostart and Rhino Standards File3dm/template regressions: 34 passed.
- Community package contract and Windows modal-dialog supervisor tests: 11 passed.
- All five community package PowerShell scripts (source patch, AutoLayer install, plugin install, verification and rollback) parse successfully. The source-patch script also passed an isolated apply/backup/hash/idempotence test, while the AutoLayer installer correctly refused deployment while Rhino was open.
- The former community ZIP passed CRC and file-hash verification before it was retired; the maintained handoff is the editable working folder.

## Related artifacts

- Editable working tree: CAD/Rhino3D_OS/tools/RhinoAI_MCP_Reliability_Repair/
- Package README: the package root README.md
- Rhino Standards source and distribution files remain in tools/Rhino3D_Scripts/RhinoStandards/.
- Canonical AutoLayer source: tools/Rhino3D_Scripts/RhinoStandards/AutoLayer/Inventaur_RhinoAutoLayer.py
- Distribution AutoLayer source: tools/Rhino3D_Scripts/RhinoStandards/Distribution/Core/AutoLayer/Inventaur_RhinoAutoLayer.py
- RhinoAI source patch: tools/RHINO3D-AI/rhino/plugin/Commands/MCPStartCommand.cs.patch

## Operational rule

Keep Rhino's UI-thread startup path short and deterministic. Port allocation belongs to RhinoAI. Post-start health checks belong in an external bounded diagnostic that verifies JSON-RPC tools/list, identifies the owning process and records the real selected port. Never auto-bind an arbitrary worker/controller chat or infer MCP health from an open port alone.
