using Rhino.UI;
using Rhino.Input;
using Rhino.Commands;
using Rhino.Input.Custom;

namespace Rhino.AI;

public class MCPStartCommand : Command
{

    public override string EnglishName => LOC.COMMANDNAME("MCPStart");

    protected override string CommandContextHelpUrl => DocsLinks.Homepage;

    protected override Result RunCommand(RhinoDoc doc, RunMode mode)
    {
        GetInteger go = new ();
        go.SetCommandPrompt("MCPStart Port");
        go.AcceptNothing(true);
        go.AcceptEnterWhenDone(true);
        bool hasDefault = RhinoAIHost.TryGetNextPort(out int suggestedPort);
        if (hasDefault)
            go.SetDefaultInteger(suggestedPort);
        go.SetLowerLimit(1, false);
        go.SetUpperLimit(65535, false);
        GetResult res = go.Get();
        // Nothing means Enter pressed; only valid when a default was actually set, otherwise go.Number() yields 0.
        if (res is GetResult.Nothing && !hasDefault) return Result.Cancel;
        if (res is not (GetResult.Number or GetResult.Nothing)) return Result.Cancel;

        if (res is GetResult.Nothing)
        {
            if (!RhinoAIHost.StartOnNextAvailablePort(doc, out int selectedPort))
                return Result.Failure;

            // Verify the listener is registered to this exact Rhino document.
            // A successful command call or an occupied port alone is not proof
            // that this document owns a live MCP listener.
            if (!RhinoAIHost.TryGetPortFor(doc, out int registeredPort)
                || registeredPort != selectedPort)
            {
                RhinoApp.WriteLine(
                    $"[RhinoAI] MCP start postcondition failed for this document; requested {selectedPort}, registered {registeredPort}.");
                return Result.Failure;
            }

            RhinoApp.WriteLine($"[RhinoAI] MCP server currently running on http://localhost:{registeredPort}/ (in-Rhino agents use /agent)");
            return Result.Success;
        }

        int port = go.Number();
        if (RhinoAIHost.StartOrRestart(doc, port))
        {
            if (!RhinoAIHost.TryGetPortFor(doc, out int registeredPort)
                || registeredPort != port)
            {
                RhinoApp.WriteLine(
                    $"[RhinoAI] MCP start postcondition failed for this document; requested {port}, registered {registeredPort}.");
                return Result.Failure;
            }

            RhinoApp.WriteLine($"[RhinoAI] MCP server currently running on http://localhost:{registeredPort}/ (in-Rhino agents use /agent)");
            return Result.Success;
        }

        return Result.Failure;
    }
}
