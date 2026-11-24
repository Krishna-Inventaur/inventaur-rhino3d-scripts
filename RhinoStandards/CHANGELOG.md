## RhinoAI-owned listener allocation

- Removed synchronous TCP port enumeration and JSON-RPC discovery from AutoLayer startup.
- Rhino 9 delegates port selection to RhinoAI through _MCPStart _Enter.
- RhinoAI MCPStart verifies that the active RhinoDoc owns the listener before reporting success.
- Rhino 8 retains its explicitly separate MCP-only startup contract.
- Client-neutral RhinoAI source, RHP/router build, installation scripts and reports are maintained as editable files under tools/RhinoAI_MCP/.
- The rebuilt plugin remains staged until all Rhino instances can be closed and guarded installation/reload can be performed.


# Changelog

## 2026-11-24 — Bundle installer and modular distribution

- Added clean Distribution/ package layout with Core, Modules, Bundles, Docs, Examples and Tests.
- Added Essential, Professional, Complete and Custom bundle choices.
- Added native RhinoCommon path-based MultiView Capture installation.
- Added optional standalone STEP Export module deployment.
- Added a private install-root override for isolated tests.
- Added hash-aware idempotent deployment, install state and a machine-readable install report.
- Kept the core runtime version at 1.9.0 and retained its existing regression evidence.
- Preserved the supplied MultiView Capture RHP byte-for-byte and retained DIG.Tools attribution.