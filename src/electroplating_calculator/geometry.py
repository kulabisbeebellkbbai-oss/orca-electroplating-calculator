"""Triangle mesh area with explicit affine transforms and bounded temporary arrays."""
from dataclasses import dataclass
from numbers import Integral
import math
import numpy as np


class CalculationCancelled(Exception):
    """A caller cancelled measurement; no partial result is returned."""


@dataclass(frozen=True)
class MeshMeasure:
    area_mm2: float
    triangle_count: int
    degenerate_count: int


def measure_mesh(vertices, triangles, transform, *, chunk_size=65536, progress=None):
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, Integral) or chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer")
    v, t = np.asarray(vertices), np.asarray(triangles)
    m = np.asarray(transform, dtype=np.float64)
    if v.ndim != 2 or v.shape[1] != 3 or not len(v) or v.dtype.kind not in "iuf":
        raise ValueError("Vertices must be a nonempty numeric N x 3 array")
    if t.ndim != 2 or t.shape[1] != 3 or not len(t) or t.dtype.kind not in "iu":
        raise ValueError("Faces must be a nonempty integer M x 3 array")
    if t.min() < 0 or t.max() >= len(v):
        raise ValueError("Face index is outside the vertex array")
    if m.shape != (4,4) or not np.isfinite(m).all() or not np.array_equal(m[3], [0,0,0,1]):
        raise ValueError("Transform must be a finite affine 4 x 4 matrix")
    if np.linalg.slogdet(m[:3,:3])[0] == 0:
        raise ValueError("Transform must not collapse a model dimension")
    for start in range(0, len(v), chunk_size):
        if not np.isfinite(v[start:start+chunk_size]).all():
            raise ValueError("Vertices must be finite")
    total, compensation, degenerate = 0., 0., 0
    try:
        with np.errstate(over="raise", invalid="raise"):
            for start in range(0, len(t), chunk_size):
                if progress is not None and not progress(start, len(t)):
                    raise CalculationCancelled()
                points = np.asarray(v[t[start:start+chunk_size]], dtype=np.float64)
                points = points @ m[:3,:3].T + m[:3,3]
                if not np.isfinite(points).all():
                    raise ValueError("Transformed coordinates are not finite")
                cross = np.cross(points[:,1] - points[:,0], points[:,2] - points[:,0])
                areas = np.hypot(np.hypot(cross[:,0], cross[:,1]), cross[:,2]) * 0.5
                if not np.isfinite(areas).all():
                    raise ValueError("Triangle area overflowed")
                degenerate += int(np.count_nonzero(areas == 0))
                value = float(np.sum(areas, dtype=np.float64)) - compensation
                updated = total + value
                compensation = (updated - total) - value
                total = updated
    except FloatingPointError as exc:
        raise ValueError("Coordinates or areas overflowed double precision") from exc
    if not math.isfinite(total):
        raise ValueError("Total area overflowed double precision")
    if progress is not None and not progress(len(t), len(t)):
        raise CalculationCancelled()
    return MeshMeasure(total, len(t), degenerate)
