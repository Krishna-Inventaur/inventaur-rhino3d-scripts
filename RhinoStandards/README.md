## RhinoAI MCP startup integration

AutoLayer delegates Rhino 9 listener allocation to RhinoAI through _MCPStart _Enter. It performs no port-range scan or synchronous TCP/JSON-RPC probe during Rhino startup. RhinoAI owns listener allocation and document-scoped registration. Rhino 8 remains on its separate MCP-only 10508 path.

The client-neutral RhinoAI source patch, RHP/router build, guarded installer, rollback, tests and E2E evidence are maintained as editable files at ../../RhinoAI_MCP/. The built RHP is staged; plugin promotion remains separate from an already-running Rhino session.


# Inventaur Rhino Standards — canonical source

The user-facing, bundle-based installer and clean distribution are in the Distribution/ folder.

## Build / release
- Distribution/ — clean product package source; Core, Modules, Bundles, Docs, Examples and Tests.
- Build_RhinoStandards_Release.ps1 — builds the versioned ZIP, manifest, hashes and integrity report.
- Releases/ — immutable, dated release snapshots.

## Core implementation source
- Installer/ — Rhino 9 drafting standards runtime and document policy.
- AutoLayer/ — Rhino startup router; Rhino 9 standards startup and existing Rhino 8 MCP-only branch.
- Commands/ — user commands for dynamic annotation controls.
- Template/ — canonical metric template.
- HatchLibrary/ and LinetypeLibrary/ — source libraries.
- Examples/ — annotation demonstration model.
- Tests/ and Reports/ — regression runners and verification evidence.
- Archive/ and Backups/ — retained historical snapshots; not included wholesale in public packages.

## Design rule

Core Standards is installed as a coordinated set because the layer, annotation, lineweight, hatch, linetype and template rules share validation. Independent features live under Distribution/Modules and are selectable through the bundle catalog.

Original third-party MultiView Capture ownership is credited in Distribution/THIRD_PARTY_CREDITS.md. Its RHP is never modified.

## 2026-11-24 template readback hardening

The canonical Installer source, Distribution/Core installer and deployed Documents installer are synchronized after the Rhino 9 File3dm table-indexing fix. Template generation is candidate-first and rollback-safe. Regression tests are in Tests/test_file3dm_readback_and_template_commit.py; isolated Rhino E2E evidence is in testing/INSTALLER_FIX_RHINO_E2E_20261124/Reports/Installer_Fix_Rhino_E2E.json.

The 2026-11-24 File3dmFix release snapshot is separate from the earlier E2E snapshot. The earlier snapshot is retained unchanged.

