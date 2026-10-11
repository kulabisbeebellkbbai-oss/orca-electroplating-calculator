from dataclasses import dataclass
import math
from numbers import Real

AREA_FACTORS = {"cm2": 100., "dm2": 10000., "in2": 645.16}
DENSITY_FACTORS = {"A/dm2": 1., "A/in2": 10000. / 645.16}


def finite_number(value, name, *, minimum=0., positive=False):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    value = float(value)
    if value < minimum or (positive and value <= minimum):
        raise ValueError(f"{name} must be {'greater than' if positive else 'at least'} {minimum:g}")
    return value


@dataclass(frozen=True)
class AreaRow:
    row_id: str
    label: str
    area_mm2: float
    warnings: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class RowChoice:
    row_id: str
    selected: bool = True
    plated_percent: float = 100
    excluded_cm2: float = 0


@dataclass(frozen=True)
class CurrentResult:
    adjusted_mm2: dict[str, float]
    total_mm2: float
    running_a: float | None
    starting_a: float | None
    warnings: tuple[str, ...]


def area_in(area_mm2, unit):
    if unit not in AREA_FACTORS:
        raise ValueError("Unknown area unit")
    return finite_number(area_mm2, "Area") / AREA_FACTORS[unit]


def density_in(value, from_unit, to_unit):
    if from_unit not in DENSITY_FACTORS or to_unit not in DENSITY_FACTORS:
        raise ValueError("Unknown density unit")
    converted = finite_number(value, "Current density", positive=True) * DENSITY_FACTORS[from_unit] / DENSITY_FACTORS[to_unit]
    return finite_number(converted, "Converted current density", positive=True)


def calculate(rows, choices, *, running_adm2, starting_adm2=None):
    running = None if running_adm2 is None else finite_number(running_adm2, "Running current density", positive=True)
    starting = None if starting_adm2 is None else finite_number(starting_adm2, "Starting current density", positive=True)
    by_id = {row.row_id: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Duplicate measured row IDs")
    seen, adjusted = set(), {}
    warnings = list(dict.fromkeys(warning for row in rows for warning in row.warnings))
    for choice in choices:
        if choice.row_id not in by_id or choice.row_id in seen:
            raise ValueError("Unknown or duplicate row choice")
        seen.add(choice.row_id)
        if type(choice.selected) is not bool:
            raise ValueError("Selection must be boolean")
        if not choice.selected:
            continue
        row = by_id[choice.row_id]
        if row.error:
            raise ValueError(f"{row.label}: {row.error}")
        area = finite_number(row.area_mm2, "Measured area")
        percent = finite_number(choice.plated_percent, "Plated percentage")
        if percent > 100:
            raise ValueError("Plated percentage must not exceed 100")
        excluded = finite_number(choice.excluded_cm2, "Excluded area") * 100.
        plated = area * (percent / 100.)
        if not math.isfinite(excluded) or excluded > plated:
            raise ValueError("Excluded area exceeds the percentage-adjusted mesh area")
        adjusted[choice.row_id] = plated - excluded
    try:
        total = math.fsum(adjusted.values())
    except OverflowError as exc:
        raise ValueError("Total plated area overflowed") from exc
    finite_number(total, "Total plated area")
    if total == 0:
        return CurrentResult(adjusted, 0., None, None, tuple(warnings))
    run_a = None if running is None else finite_number(total / 10000. * running, "Calculated running current", positive=True)
    start_a = None if starting is None else finite_number(total / 10000. * starting, "Calculated starting current", positive=True)
    return CurrentResult(adjusted, total, run_a, start_a, tuple(warnings))
