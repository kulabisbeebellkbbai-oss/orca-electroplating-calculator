import numpy as np
import pytest
from electroplating_calculator.geometry import measure_mesh, CalculationCancelled
from tests.fixtures.mesh_fixtures import cube


def test_10mm_cube_area():
    result = measure_mesh(*cube(), np.eye(4))
    assert result.area_mm2 == pytest.approx(600)
    assert result.triangle_count == 12
    assert result.degenerate_count == 0


@pytest.mark.parametrize("scale, expected", [([2,2,2],2400), ([2,3,4],5200), ([-1,1,1],600)])
def test_transformed_box_area(scale, expected):
    matrix = np.diag([*scale,1.])
    assert measure_mesh(*cube(), matrix).area_mm2 == pytest.approx(expected)


def test_rotation_translation_invariance_and_chunking():
    matrix = np.array([[0,-1,0,1e5],[1,0,0,-1e5],[0,0,1,1e4],[0,0,0,1.]])
    assert measure_mesh(*cube(), matrix, chunk_size=1).area_mm2 == pytest.approx(600,rel=1e-12)
    assert measure_mesh(*cube(), matrix, chunk_size=65536).area_mm2 == pytest.approx(600,rel=1e-12)


@pytest.mark.parametrize("bad", [float("nan"),float("inf")])
def test_nonfinite_vertices_rejected(bad):
    v,t = cube(); v[0,0] = bad
    with pytest.raises(ValueError):
        measure_mesh(v,t,np.eye(4))


@pytest.mark.parametrize("faces", [[[0,1,8]], [[-1,0,1]], [[0.,1.5,2.]], [[True,False,True]], [], [[0,1]]])
def test_bad_triangles_rejected(faces):
    with pytest.raises(ValueError):
        measure_mesh(cube()[0],faces,np.eye(4))


@pytest.mark.parametrize("matrix", [np.zeros((4,4)),np.eye(3),
                                    np.diag([1,0,1,1]),np.diag([1,1,np.inf,1]),
                                    np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,1,1]])])
def test_bad_transform_rejected(matrix):
    with pytest.raises(ValueError):
        measure_mesh(*cube(),matrix)


def test_wrong_vertex_dimension():
    with pytest.raises(ValueError):
        measure_mesh([[0,1],[2,3],[4,5]],[[0,1,2]],np.eye(4))


def test_degenerate_faces_counted():
    result = measure_mesh([[0,0,0],[0,0,0],[1,1,1]],[[0,1,2]],np.eye(4))
    assert result.area_mm2 == 0
    assert result.degenerate_count == 1


def test_cancelled_chunk_has_no_result():
    with pytest.raises(CalculationCancelled):
        measure_mesh(*cube(),np.eye(4),chunk_size=1,progress=lambda done,total: False)


def test_overflow_rejected():
    v,t = cube(); v *= 1e200
    with pytest.raises(ValueError):
        measure_mesh(v,t,np.eye(4))


@pytest.mark.parametrize("size",[0,-1,True,1.5])
def test_invalid_chunk_size(size):
    with pytest.raises(ValueError):
        measure_mesh(*cube(),np.eye(4),chunk_size=size)
