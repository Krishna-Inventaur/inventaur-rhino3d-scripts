"""Self-contained invariants for the client-neutral RhinoAI MCP repair."""
from __future__ import annotations
import hashlib
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class RhinoAIMcpContractTests(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_mcpstart_checks_document_listener_ownership(self):
        source = self.read("Source/RhinoAI/MCPStartCommand.cs")
        self.assertEqual(source.count("RhinoAIHost.TryGetPortFor(doc, out int registeredPort)"), 2)
        self.assertIn("registeredPort != selectedPort", source)
        self.assertIn("registeredPort != port", source)

    def test_patched_and_prechange_sources_are_available(self):
        patched = ROOT / "Source/RhinoAI/MCPStartCommand.cs"
        before = ROOT / "Source/RhinoAI/MCPStartCommand.cs.before.cs"
        patch = ROOT / "Source/RhinoAI/MCPStartCommand.cs.patch"
        self.assertTrue(patched.is_file())
        self.assertTrue(before.is_file())
        self.assertTrue(patch.is_file())
        self.assertNotEqual(hashlib.sha256(patched.read_bytes()).digest(), hashlib.sha256(before.read_bytes()).digest())

    def test_build_outputs_are_open_files(self):
        for rel in (
            "Build/RhinoAI/net8.0/RhinoAI.rhp",
            "Build/RhinoAI/net8.0/Acp.dll",
            "Build/RhinoAI/router/win-x64/rhino-mcp-router.exe",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_guarded_install_rollback_and_exact_verify_exist(self):
        for rel in (
            "Scripts/INSTALL.ps1",
            "Scripts/ROLLBACK.ps1",
            "Scripts/VERIFY.ps1",
            "Scripts/APPLY_RHINOAI_SOURCE_PATCH.ps1",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)
        verify = self.read("Scripts/VERIFY.ps1")
        self.assertIn("[Parameter(Mandatory=$true)]", verify)
        self.assertNotIn("10500..10600", verify)

    def test_readme_describes_client_neutral_mcpconnect(self):
        readme = self.read("README.md")
        self.assertIn("MCPConnect", readme)
        self.assertIn("client-neutral", readme.lower())
        self.assertNotIn("IvyGPT", readme)
        self.assertIn("rhino-mcp-router", readme)

if __name__ == "__main__":
    unittest.main(verbosity=2)
