"""Read-only adapter for the verified Orca host model API."""
import numpy as np
from .calculation import AreaRow
from .geometry import measure_mesh, CalculationCancelled


class UnsupportedHostError(RuntimeError):
    pass


def required_method(obj, name, label):
    method = getattr(obj, name, None)
    if not callable(method):
        raise UnsupportedHostError(f"Missing Orca capability: {label}.{name}")
    return method


def require_host(orca_module):
    host = getattr(orca_module, "host", None)
    required_method(host, "model", "orca.host")
    ui = getattr(host, "ui", None)
    for name in ("create_window", "create_progress_dialog"):
        required_method(ui, name, "orca.host.ui")
    base = getattr(getattr(orca_module, "script", None), "ScriptPluginCapabilityBase", None)
    for name in ("get_config", "save_config"):
        required_method(base, name, "script")
    for name in ("WINDOW_MODAL","PD_CAN_ABORT","PD_APP_MODAL"):
        if not hasattr(ui,name):
            raise UnsupportedHostError(f"Missing Orca capability: orca.host.ui.{name}")


def collect_rows(model, *, progress=None):
    rows = []
    objects = required_method(model,"objects","model")()
    for oi, obj in enumerate(objects):
        volumes = list(required_method(obj,"volumes","object")())
        instances = list(required_method(obj,"instances","object")())
        for vol in volumes:
            for name in ("is_model_part", "is_negative_volume"):
                required_method(vol, name, "volume")
        parts = [(vi,v) for vi,v in enumerate(volumes) if v.is_model_part()]
        warnings = []
        if len(parts) > 1 or any(v.is_negative_volume() for v in volumes):
            warnings.append("Multipart mesh: hidden interfaces may be counted; no boolean union is applied.")
        if any(v.is_negative_volume() for v in volumes):
            warnings.append("Negative volumes are excluded, but their cuts are not applied to the measured mesh.")
        for ii, instance in enumerate(instances):
            required_method(instance,"matrix","instance")
            for vi, vol in parts:
                for name in ("matrix","mesh"):
                    required_method(vol,name,"volume")
                row_warnings = list(warnings)
                label = f"{getattr(obj,'name','Object')} · copy {ii+1} · {getattr(vol,'name','Part')}"
                area, error = 0., None
                try:
                    mesh = vol.mesh()
                    for name in ("vertices","triangles","is_manifold"):
                        required_method(mesh,name,"mesh")
                    if not mesh.is_manifold():
                        row_warnings.append("Mesh is not manifold; inspect open or overlapping surfaces.")
                    transform = np.asarray(instance.matrix(),dtype=np.float64) @ np.asarray(vol.matrix(),dtype=np.float64)
                    measure = measure_mesh(mesh.vertices(),mesh.triangles(),transform,progress=progress)
                    area = measure.area_mm2
                    if measure.degenerate_count:
                        row_warnings.append(f"{measure.degenerate_count} zero-area triangles were ignored.")
                except (CalculationCancelled,UnsupportedHostError):
                    raise
                except Exception as exc:
                    error = f"Cannot measure this mesh: {exc}"
                rows.append(AreaRow(f"{oi}:{ii}:{vi}",label,area,tuple(row_warnings),error))
    return rows
