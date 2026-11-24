# RhinoAI MCP — verification results

## Build

- Rhino 9 Windows x64 / net8.0 Release build: PASS.
- Errors: 0.
- One pre-existing unrelated CS1998 warning in the upstream router was allowed for the isolated build; no unrelated source was changed.
- The built RHP, runtime dependencies and stdio router are committed as individual files in Build/RhinoAI/.

## Runtime and MCP

- Fresh Rhino 9.1.26314.9001 disposable process used the no-scan AutoLayer startup entrypoint.
- Startup bootstrap: approximately 1.03 seconds; MCPStart phase: approximately 303 ms.
- Fresh endpoint returned JSON-RPC tools/list HTTP 200 with 44 tools.
- The OS assigned port 53318 in the concurrent-instance test; no claim is made that preferred port 10501 was selected.
- The disposable Rhino process and endpoint exited cleanly.
- The existing user Rhino session on port 10500 was not closed or modified.
- The standard stdio router initialized, listed the same 44 tools and adopted the already-running Rhino instance through list_slots. It exited cleanly without closing Rhino.

## Source and deployment safeguards

- MCPStart source patch is guarded by exact preimage and postimage SHA-256 values.
- Applying the patch to a disposable source copy and running the patcher a second time both passed.
- Plugin installer checks for open Rhino processes, backs up the current plugin folders, verifies the staged RHP and rolls back on failure.
- Rollback is separate and also refuses to run while Rhino is open.
- Verification requires the exact port reported by MCPStatus; it does not scan a range.
- Save/discard dialogs and unknown native prompts are not automatically accepted.

## Outstanding promotion step

The replacement RHP is built and staged. It has not yet been installed over the active Rhino runtime because the user's Rhino process was intentionally preserved. After all Rhino instances are closed, run Scripts/INSTALL.ps1 -ConfirmInstall, start Rhino manually and verify the actual endpoint with MCPStatus and Scripts/VERIFY.ps1 -Port <reported-port>.
