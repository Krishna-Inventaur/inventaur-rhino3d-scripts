# Rhino startup entrypoint.
# Rhino 9: load Inventaur drafting standards, then start RhinoAI MCP on port 10500.
# Rhino 8: MCP autostart only, on port 10508. The standards installer is Rhino 9-targeted.
import Rhino, traceback, os, codecs, time, System

try:
    _INV_DOCUMENTS_DIR = str(System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyDocuments))
except Exception:
    _INV_DOCUMENTS_DIR = os.path.join(os.path.expanduser("~"), "Documents")
_INV_INSTALLER_PATH = os.path.join(
    _INV_DOCUMENTS_DIR, "Inventaur", "Rhino Standards",
    "Inventaur_RhinoStandards_Install.py"
)
_INV_BOOTSTRAP_STARTED = time.time()
_INV_BOOTSTRAP_PHASES = {}
try:
    _inv_process = System.Diagnostics.Process.GetCurrentProcess()
    _INV_BOOTSTRAP_PHASES["rhino_process_age_ms"] = (
        (System.DateTime.Now - _inv_process.StartTime).TotalMilliseconds)
    _INV_BOOTSTRAP_PHASES["rhino_process_start"] = str(_inv_process.StartTime)
except Exception:
    _INV_BOOTSTRAP_PHASES["rhino_process_age_ms"] = -1
_INV_RHINO_MAJOR = 9
try:
    _INV_RHINO_MAJOR = int(Rhino.RhinoApp.Version.Major)
except Exception:
    try:
        _INV_RHINO_MAJOR = int(str(Rhino.RhinoApp.Version).split(".", 1)[0])
    except Exception:
        pass

_INV_MCP_PORT = 10508 if _INV_RHINO_MAJOR == 8 else 10500
_INV_BOOTSTRAP_LOG_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "Inventaur", "RhinoStandards", "logs", "Inventaur_RhinoBootstrap.log"
)

def _inv_ensure_directory(path):
    """Create a directory on both IronPython 2.7 and CPython 3."""
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

_inv_ensure_directory(os.path.dirname(_INV_BOOTSTRAP_LOG_PATH))

def _inv_bootstrap_log(message):
    try:
        with codecs.open(_INV_BOOTSTRAP_LOG_PATH, "a", "utf-8") as stream:
            stream.write("[{0}] {1}\n".format(
                time.strftime("%Y-%m-%dT%H:%M:%S"), str(message)))
    except Exception:
        pass

# Keep Rhino 8's MCP bootstrap independent from the Rhino 9-only installer.
_inv_phase_started = time.time()
_inv_bootstrap_log("BOOTSTRAP_START rhino_major={0} pid={1}".format(_INV_RHINO_MAJOR, os.getpid()))
if _INV_RHINO_MAJOR == 9:
    try:
        _inv_read_started = time.time()
        with codecs.open(_INV_INSTALLER_PATH, "r", "utf-8") as stream:
            _inv_installer_source = stream.read()
        _INV_BOOTSTRAP_PHASES["installer_read_ms"] = (time.time() - _inv_read_started) * 1000.0
        _inv_exec_started = time.time()
        eval(compile(_inv_installer_source, _INV_INSTALLER_PATH, "exec"), globals(), globals())
        _INV_BOOTSTRAP_PHASES["installer_exec_ms"] = (time.time() - _inv_exec_started) * 1000.0
        _inv_bootstrap_log("STANDARDS_BOOTSTRAP_OK version={0} read_ms={1:.1f} exec_ms={2:.1f}".format(
            str(globals().get("VERSION", "unknown")),
            _INV_BOOTSTRAP_PHASES.get("installer_read_ms", 0.0),
            _INV_BOOTSTRAP_PHASES.get("installer_exec_ms", 0.0)))
    except Exception:
        _INV_BOOTSTRAP_PHASES["installer_exec_ms"] = (time.time() - _inv_phase_started) * 1000.0
        _inv_bootstrap_log("STANDARDS_BOOTSTRAP_ERROR\n" + traceback.format_exc())
else:
    _inv_bootstrap_log(
        "STANDARDS_BOOTSTRAP_SKIPPED rhino_major={0}; MCP autostart continues".format(
            _INV_RHINO_MAJOR
        )
    )

# Delegate port arbitration and listener ownership to RhinoAI. MCPStart's
# Enter/default path calls StartOnNextAvailablePort(doc), which binds a free
# port and registers that listener against this exact Rhino document. Do not
# scan the port range in this startup script: synchronous probing can block
# Rhino's UI thread on unrelated or non-responsive listeners.
_inv_mcp_started = time.time()
try:
    if _INV_RHINO_MAJOR >= 9:
        _inv_mcp_command = "_MCPStart _Enter"
    else:
        # Preserve the Rhino 8 legacy fixed-port contract.
        _inv_mcp_command = "_MCPStart {0} ".format(_INV_MCP_PORT)

    _inv_mcp_start_result = Rhino.RhinoApp.RunScript(_inv_mcp_command, False)
    _inv_bootstrap_log(
        "MCPSTART_RUNSCRIPT_RETURN={0} command={1}".format(
            repr(_inv_mcp_start_result), repr(_inv_mcp_command)
        )
    )
    if _inv_mcp_start_result:
        _inv_bootstrap_log(
            "MCPSTART_COMMAND_ACCEPTED document_scoped_listener_postcondition_in_plugin"
        )
    else:
        _inv_bootstrap_log(
            "MCPSTART_COMMAND_NOT_ACCEPTED command={0}".format(
                repr(_inv_mcp_command)
            )
        )
except Exception:
    _inv_bootstrap_log("MCPSTART_ERROR\\n" + traceback.format_exc())

_INV_BOOTSTRAP_PHASES["mcp_ms"] = (time.time() - _inv_mcp_started) * 1000.0
_INV_BOOTSTRAP_PHASES["total_ms"] = (time.time() - _INV_BOOTSTRAP_STARTED) * 1000.0
_inv_summary = ("INVENTAUR RHINO BOOTSTRAP: RhinoStart-to-script={0:.0f} ms | "
                "standards={1:.0f} ms | MCP={2:.0f} ms | total={3:.0f} ms | log={4}").format(
    _INV_BOOTSTRAP_PHASES.get("rhino_process_age_ms", -1.0),
    _INV_BOOTSTRAP_PHASES.get("installer_exec_ms", 0.0),
    _INV_BOOTSTRAP_PHASES.get("mcp_ms", 0.0),
    _INV_BOOTSTRAP_PHASES.get("total_ms", 0.0),
    _INV_BOOTSTRAP_LOG_PATH)
_inv_bootstrap_log("PERF " + repr(_INV_BOOTSTRAP_PHASES))
try:
    Rhino.RhinoApp.WriteLine(_inv_summary)
except Exception:
    print(_inv_summary)
