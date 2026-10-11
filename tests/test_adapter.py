from types import SimpleNamespace as NS
import numpy as np
import pytest
from tests.fixtures.mesh_fixtures import cube
from electroplating_calculator.orca_adapter import collect_rows, UnsupportedHostError
from electroplating_calculator.geometry import CalculationCancelled


def volume(kind="part", matrix=None, vertices=None):
    v, t = cube()
    return NS(name="Cube", is_model_part=lambda: kind == "part",
              is_negative_volume=lambda: kind == "negative",
              matrix=lambda: np.eye(4) if matrix is None else matrix,
              mesh=lambda: NS(vertices=lambda: v if vertices is None else vertices,
                              triangles=lambda: t, is_manifold=lambda: True))


def model(volumes=None, matrices=None):
    return NS(objects=lambda: [NS(name="Box", volumes=lambda: volumes or [volume()],
              instances=lambda: [NS(matrix=lambda m=m: m) for m in (matrices or [np.eye(4)])])])


def test_instance_transform_follows_volume_transform():
    rotation = np.array([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
    rows = collect_rows(model([volume(matrix=rotation)], [np.diag([2,3,4,1]), np.eye(4)]))
    assert [r.area_mm2 for r in rows] == pytest.approx([5200,600])
    assert [r.row_id for r in rows] == ["0:0:0","0:1:0"]


def test_nonparts_excluded_and_cut_warning_survives():
    rows = collect_rows(model([volume(),volume("negative"),volume("modifier"),volume("support")]))
    assert len(rows) == 1
    assert any("Negative" in w for w in rows[0].warnings)
    assert any("interfaces" in w for w in rows[0].warnings)


def test_missing_classification_fails_precisely():
    v = volume()
    del v.is_model_part
    with pytest.raises(UnsupportedHostError,match="is_model_part"):
        collect_rows(model([v]))


def test_bad_mesh_visible_with_error():
    rows = collect_rows(model([volume(vertices=[])]))
    assert rows[0].error and rows[0].area_mm2 == 0


def test_cancellation_propagates():
    with pytest.raises(CalculationCancelled):
        collect_rows(model(),progress=lambda *args: False)
