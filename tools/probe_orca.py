# /// script
# dependencies = []
# [tool.orcaslicer.plugin]
# name = "Surface Area Host Probe"
# description = "Read-only development probe for electroplating calculator APIs"
# version = "0.1.0"
# ///
"""Development-only capability probe. Does not modify meshes or presets."""
import json
import os
from pathlib import Path


def probe_host(orca_module):
    missing = []

    def check(obj, name, label):
        value = getattr(obj, name, None)
        if not callable(value):
            missing.append(label)
        return value

    host = getattr(orca_module, "host", None)
    model_fn = check(host, "model", "orca.host.model")
    ui = getattr(host, "ui", None)
    check(ui, "create_window", "orca.host.ui.create_window")
    check(ui, "create_progress_dialog", "orca.host.ui.create_progress_dialog")
    base = getattr(getattr(orca_module, "script", None), "ScriptPluginCapabilityBase", None)
    check(base, "get_config", "script.get_config")
    check(base, "save_config", "script.save_config")
    verified = False
    if model_fn is not None:
        try:
            model = model_fn()
            for obj in model.objects():
                volumes = list(obj.volumes())
                instances = list(obj.instances())
                for instance in instances:
                    check(instance, "matrix", "instance.matrix")
                for vol in volumes:
                    check(vol, "is_model_part", "volume.is_model_part")
                    check(vol, "is_negative_volume", "volume.is_negative_volume")
                    check(vol, "matrix", "volume.matrix")
                    mesh_fn = check(vol, "mesh", "volume.mesh")
                    if mesh_fn:
                        mesh = mesh_fn()
                        for name in ("vertices", "triangles", "is_manifold"):
                            check(mesh, name, "mesh." + name)
                verified = verified or bool(volumes and instances)
        except Exception as exc:
            missing.append("model inspection unavailable: " + str(exc))
    return {"missing": sorted(set(missing)), "geometry_verified": verified and not missing,
            "build": str(getattr(orca_module, "__version__", "not exposed"))}


try:
    import orca
except ImportError:
    orca = None

if orca is not None:
    class Probe(orca.script.ScriptPluginCapabilityBase):
        def get_name(self):
            return "Surface Area Host Probe"

        def execute(self):
            result = probe_host(orca)
            return orca.ExecutionResult.success(json.dumps(result), json.dumps(result))

        def on_load(self):
            # Explicitly supplied development output; normal installations write nothing.
            destination = os.environ.get("ORCA_SURFACE_PROBE_OUTPUT")
            if destination:
                Path(destination).write_text(json.dumps(probe_host(orca), indent=2), encoding="utf-8")

    @orca.plugin
    class ProbePackage(orca.base):
        def register_capabilities(self):
            orca.register_capability(Probe)
