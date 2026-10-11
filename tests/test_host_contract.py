from types import SimpleNamespace as NS
import numpy as np
from tools.probe_orca import probe_host


def host(objects):
    mesh = NS(vertices=lambda: np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
              triangles=lambda: np.array([[0, 1, 2]]), is_manifold=lambda: False)
    vol = NS(is_model_part=lambda: True, is_negative_volume=lambda: False,
             mesh=lambda: mesh, matrix=lambda: np.eye(4))
    graph = [NS(volumes=lambda: [vol], instances=lambda: [NS(matrix=lambda: np.eye(4))])] if objects else []
    base = type("Base", (), {"get_config": lambda s: "{}", "save_config": lambda s, c: True})
    return NS(host=NS(model=lambda: NS(objects=lambda: graph),
                      ui=NS(create_window=lambda **kw: None, create_progress_dialog=lambda **kw: None)),
              script=NS(ScriptPluginCapabilityBase=base), __version__="test")


def test_missing_host_reports_named_capability():
    result = probe_host(NS())
    assert "orca.host.model" in result["missing"]
    assert not result["geometry_verified"]


def test_empty_model_leaves_geometry_unverified():
    result = probe_host(host(False))
    assert result["missing"] == []
    assert not result["geometry_verified"]


def test_required_contract_accepts_fake_supported_host():
    result = probe_host(host(True))
    assert result["missing"] == []
    assert result["geometry_verified"]


def test_missing_classification_cannot_be_counted():
    h = host(True)
    del h.host.model().objects()[0].volumes()[0].is_model_part
    result = probe_host(h)
    assert any("is_model_part" in m for m in result["missing"])
    assert not result["geometry_verified"]
