# Verification Summary

## RhinoAI MCP and AutoLayer

Verified on Rhino 9.1.26314.9001, Windows x64, net8.0:

- AutoLayer startup no longer scans 10500–10600 or sends synchronous JSON-RPC probes during Rhino startup.
- Rhino 9 delegates listener allocation to RhinoAI through _MCPStart _Enter.
- RhinoAI MCPStart verifies that the selected listener belongs to the active RhinoDoc.
- A fresh disposable Rhino 9 process completed the revised AutoLayer bootstrap in approximately 1.03 seconds; MCPStart phase approximately 303 ms.
- The fresh process exposed a JSON-RPC tools/list endpoint on OS-assigned port 53318; HTTP 200 and 44 tools were returned. This run does not claim that preferred port 10501 was selected.
- The disposable Rhino process and endpoint closed cleanly.
- The existing user Rhino process and its port 10500 endpoint were preserved.
- The standard stdio router initialized, returned 44 tools and adopted the already-running Rhino through list_slots; it exited without closing that Rhino session.
- The source patch applies only when the upstream file matches the exact expected preimage SHA-256. The backup, postimage and idempotent second run were verified.
- The guarded installer refuses to run while any Rhino process is open, backs up the existing plugin and validates the staged RHP hash.
- The exact-endpoint verification script requires the port reported by MCPStatus and does not scan a port range.

## Tests and build

- RhinoAI MCP autostart and RhinoStandards targeted regression set: 34 passed.
- Client-neutral project contract tests: 5 passed.
- Four PowerShell scripts parse successfully: source patch, install, rollback and exact-endpoint verify.
- RhinoAI Release/net8.0 plugin and Windows x64 router build: 0 errors. One pre-existing unrelated CS1998 warning was allowed for the isolated build; unrelated upstream source was not changed.

## Promotion boundary

The new RhinoAI RHP and router are built and staged as individual files in RhinoAI_MCP/Build. The replacement RHP has not been installed over the active user Rhino runtime because that Rhino session was deliberately preserved. Installation and post-reload MCPStatus verification remain pending until all Rhino processes are closed and the guarded installer is run.

The RhinoStandards and RhinoAI MCP source folders are the canonical editable files. No ZIP archive is required for review, modification, installation or GitHub updates.
