# Upstream source attribution

This repair modifies a narrow part of the McNeel RhinoAI source tree.
Upstream repository: https://github.com/mcneel/RhinoAI
Upstream branch inspected: rhino-9.x
Upstream licence: MIT; the original full licence is included in Licenses/McNeel_RhinoAI_MIT_LICENSE.txt.

The only plugin source file modified by this repair is:
- rhino/plugin/Commands/MCPStartCommand.cs

The accompanying static test and README changes are also included for traceability. This is a community repair package, not an official McNeel binary release and not an endorsement by McNeel.

Repair implementation notes and live evidence are in the package root README and Reports/REPAIR_E2E_REPORT.json. Only MCPStartCommand.cs is modified in the RhinoAI plugin source payload.
