"""Static contract regression tests for Rhino MCP startup/port routing.

These tests intentionally verify source wiring without Rhino/.NET runtime dependencies.
They complement, but do not replace, compiled plugin and live multi-instance tests.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def source(path):
    return (ROOT / path).read_text(encoding="utf-8")

class McpAutostartContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = source("rhino/plugin/AISettings.cs")
        cls.auto = source("rhino/plugin/AIAutoLoad.cs")
        cls.plugin = source("rhino/plugin/RhinoAIPlugin.cs")
        cls.host = source("rhino/plugin/RhinoAIHost.ai.cs")
        cls.server = source("rhino/plugin/McpServer.ai.cs")
        cls.start = source("rhino/plugin/Commands/MCPStartCommand.cs")
        cls.status = source("rhino/plugin/Commands/MCPStatusCommand.cs")
        cls.spawn = source("rhino/plugin/Commands/MCPSpawnCommand.cs")
        cls.router_control = source("rhino/plugin/Internal/RouterControlTool.ai.cs")
        cls.agent_dispatch = source("rhino/plugin/Agents/AgentDispatch.ai.cs")
        cls.docs = source("rhino/README.md")
        cls.plugin_project = source("rhino/plugin/RhinoAI.csproj")
        cls.close_doc = source("rhino/plugin/Tools/CloseDocTool.cs")
        cls.autolayer = (ROOT.parent / "Rhino3D_Scripts" / "RhinoStandards" / "AutoLayer" / "Inventaur_RhinoAutoLayer.py").read_text(encoding="utf-8")

    def test_autoload_defaults_enabled_and_is_provider_independent(self):
        self.assertIn("GetBool(nameof(AutoLoadMCP), true)", self.settings)
        self.assertIn("return WasStartedViaAgent || AISettings.AutoLoadMCP;", self.auto)

    def test_plugin_load_registers_new_open_close_and_adopts_existing_docs(self):
        self.assertIn("RhinoAIHost.RegisterDocumentWatcher();", self.plugin)
        for hook in ("RhinoDoc.CloseDocument += CloseServer", "RhinoDoc.NewDocument += OpenNewServer", "RhinoDoc.EndOpenDocument += OpenServer"):
            self.assertIn(hook, self.host)
        self.assertIn("foreach (RhinoDoc doc in RhinoDoc.OpenDocuments())", self.host)

    def test_independent_processes_arbitrate_by_actual_listener_start(self):
        self.assertIn("PreferredPortScanWidth = 100", self.host)
        self.assertIn("Start(doc, candidate, quiet: true)", self.host)
        self.assertLess(self.host.index("for (int candidate = first; candidate <= last; candidate++)"), self.host.index("for (int attempt = 0; attempt < 5; attempt++)"))
        self.assertIn("Start(doc, ephemeral, quiet: true)", self.host)

    def test_collision_failures_are_quiet_and_failed_server_entry_is_removed(self):
        self.assertIn("if (!quiet)", self.server)
        self.assertIn("Servers.Remove(doc.RuntimeSerialNumber);", self.host)

    def test_mcpstart_default_and_explicit_custom_port_paths_are_distinct(self):
        self.assertIn("StartOnNextAvailablePort(doc, out int selectedPort)", self.start)
        self.assertIn("StartOrRestart(doc, port)", self.start)

    def test_mcpstatus_yes_uses_the_collision_aware_allocator(self):
        self.assertIn("StartOnNextAvailablePort(doc, out int nextPort)", self.status)

    def test_router_reserved_and_spawned_ports_remain_explicit(self):
        self.assertIn("StartOrRestart(doc, port)", self.spawn)
        self.assertIn("RhinoAIHost.Start(newDoc, port)", self.router_control)
        self.assertIn("RhinoAIHost.StartOrRestart(doc, nextPort)", self.agent_dispatch)

    def test_windows_close_uses_documented_open_replacement_and_verifies_close_and_rebind(self):
        self.assertIn("OperatingSystem.IsWindows()", self.close_doc)
        self.assertIn("using (File3dm blank = new())", self.close_doc)
        self.assertIn("blank.Write(replacementPath, RhinoApp.ExeVersion)", self.close_doc)
        self.assertIn("RhinoApp.InvokeAndWait", self.close_doc)
        self.assertIn("RhinoDoc.Open(replacementPath, out bool wasAlreadyOpen)", self.close_doc)
        self.assertIn("RhinoDoc.CloseDocument += onClose", self.close_doc)
        self.assertIn("e.DocumentSerialNumber == closingSerial", self.close_doc)
        self.assertIn("RhinoDoc.OpenDocuments().Any(d => d.RuntimeSerialNumber == closingSerial)", self.close_doc)
        self.assertIn("RhinoAIHost.TryGetPortFor(replacement, out int reboundPort)", self.close_doc)
        self.assertIn("reboundPort != previousPort", self.close_doc)
        self.assertIn("RhinoAIHost.HasStarted(replacement)", self.close_doc)
        self.assertIn("DeleteReplacementWhenClosed(replacement, replacementPath)", self.close_doc)
        self.assertIn("Windows close was not verified", self.close_doc)

    def test_close_tool_does_not_report_success_from_an_unverified_run_script(self):
        self.assertIn("if (!commandAccepted)", self.close_doc)
        self.assertIn("return Failure(ToolError.Failed", self.close_doc)

    def test_nested_router_publish_restores_only_the_requested_runtime_identifier(self):
        self.assertIn("-p:RuntimeIdentifiers=%(_RouterRid.Identity)", self.plugin_project)
        self.assertIn("-p:WarningsNotAsErrors=$(WarningsNotAsErrors)", self.plugin_project)

    def test_readme_documents_startup_range_custom_port_and_router_compatibility(self):
        for token in ("Load MCP server at startup", "10500–10600", "MCPStart", "explicit reserved-port path", "already open"):
            self.assertIn(token, self.docs)

    def test_autolayer_does_not_poll_or_scan_ports_synchronously_during_boot(self):
        self.assertIn('_inv_mcp_command = "_MCPStart _Enter"', self.autolayer)
        self.assertNotIn("socket", self.autolayer.lower())
        self.assertNotIn("TcpClient", self.autolayer)
        self.assertNotIn("HttpWebRequest", self.autolayer)
        self.assertNotIn("tools/list", self.autolayer)
        self.assertNotIn("_inv_tcp_candidate_open", self.autolayer)
        self.assertNotIn("_inv_discover_mcp_endpoints", self.autolayer)
        self.assertIn("MCPSTART_RUNSCRIPT_RETURN", self.autolayer)
        self.assertIn("document_scoped_listener_postcondition_in_plugin", self.autolayer)

    def test_rhino9_autolayer_delegates_port_selection_to_collision_aware_allocator(self):
        self.assertIn('_inv_mcp_command = "_MCPStart _Enter"', self.autolayer)
        self.assertIn("StartOnNextAvailablePort(doc, out int selectedPort)", self.start)
        self.assertNotIn("10500", self.autolayer.split("# Keep Rhino 8")[1].split("_INV_BOOTSTRAP_PHASES[\"mcp_ms\"]")[0])

    def test_mcpstart_success_requires_current_document_port_registration(self):
        self.assertEqual(self.start.count("RhinoAIHost.TryGetPortFor(doc, out int registeredPort)"), 2)
        self.assertIn("registeredPort != selectedPort", self.start)
        self.assertIn("registeredPort != port", self.start)
        self.assertIn("MCP start postcondition failed for this document", self.start)

    def test_rhino8_legacy_fixed_port_contract_is_preserved(self):
        self.assertIn('_INV_MCP_PORT = 10508 if _INV_RHINO_MAJOR == 8 else 10500', self.autolayer)
        self.assertIn('_inv_mcp_command = "_MCPStart {0} ".format(_INV_MCP_PORT)', self.autolayer)

    def test_autolayer_copies_are_byte_identical(self):
        from pathlib import Path
        import hashlib
        standards = ROOT.parent / "Rhino3D_Scripts" / "RhinoStandards"
        source_path = standards / "AutoLayer" / "Inventaur_RhinoAutoLayer.py"
        distribution_path = standards / "Distribution" / "Core" / "AutoLayer" / "Inventaur_RhinoAutoLayer.py"
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).digest(), hashlib.sha256(distribution_path.read_bytes()).digest())
        runtime_path = Path.home() / "OneDrive" / "Documents" / "Inventaur" / "Rhino Standards" / "Inventaur_RhinoAutoLayer.py"
        if runtime_path.exists():
            self.assertEqual(hashlib.sha256(source_path.read_bytes()).digest(), hashlib.sha256(runtime_path.read_bytes()).digest())

if __name__ == "__main__":
    unittest.main(verbosity=2)
