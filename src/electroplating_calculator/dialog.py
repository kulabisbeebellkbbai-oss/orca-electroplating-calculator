"""Offline rendering, strict form validation, and plain-text reports."""
from dataclasses import asdict
from importlib.resources import files
import json
import re
from .calculation import RowChoice, calculate, area_in, density_in
from .settings import Settings, validate_settings, CASWELL_SOURCE, reference_notice
from .profiles import PROFILES, profile_data, VOLTAGE_GUIDANCE

LIMITATION = "Measured triangle mesh area includes modeled cavities and hidden surfaces. Adjust for masking and bath exposure; print texture and conductive-coating coverage are not measured."


def render_dialog(rows, settings, *, message="", choices=None):
    validate_settings(settings)
    if choices is None:
        choices = [RowChoice(row.row_id,selected=not bool(row.error)) for row in rows]
    data = dict(rows=[asdict(r) for r in rows],choices=[asdict(c) for c in choices],
                settings=asdict(settings),message=message,limitation=LIMITATION,
                profiles=profile_data(),voltage_guidance=VOLTAGE_GUIDANCE)
    embedded = json.dumps(data,ensure_ascii=False,allow_nan=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    resources = files("electroplating_calculator").joinpath("resources")
    slots = {"__DATA__":embedded,"__SCRIPT__":resources.joinpath("calculator.js").read_text(encoding="utf-8")}
    return re.sub("__DATA__|__SCRIPT__",lambda match:slots[match.group()],resources.joinpath("calculator.html").read_text(encoding="utf-8"))


def parse_submission(payload, rows):
    if not isinstance(payload,dict) or payload.get("action") not in ("save","close"):
        raise ValueError("Unknown calculator action")
    if payload["action"] == "close":
        return "close",[],None
    if set(payload) != {"action","choices","settings"}:
        raise ValueError("Unknown submitted fields")
    raw_choices, values = payload["choices"], payload["settings"]
    if not isinstance(raw_choices,list) or not isinstance(values,dict):
        raise ValueError("Malformed calculator form")
    if set(values) != set(Settings.__dataclass_fields__):
        raise ValueError("Unknown or missing settings fields")
    choices = []
    for choice in raw_choices:
        if not isinstance(choice,dict) or set(choice) != set(RowChoice.__dataclass_fields__):
            raise ValueError("Unknown or missing row fields")
        if not isinstance(choice["row_id"],str):
            raise ValueError("Row IDs must be text")
        choices.append(RowChoice(**choice))
    if {c.row_id for c in choices} != {r.row_id for r in rows}:
        raise ValueError("Form must contain exactly the measured rows")
    settings = validate_settings(Settings(**values))
    calculate(rows,choices,running_adm2=settings.running_adm2,starting_adm2=settings.starting_adm2)
    return "save",choices,settings


def number(value):
    return format(value,".8g")


def format_report(rows, choices, settings, result):
    validate_settings(settings)
    profile = PROFILES[settings.profile]
    lines = ["Electroplating Calculator",f"Bath: {settings.bath_label}",f"Coating: {settings.coating_label}",
             "Measured mesh area / adjusted plated estimate:"]
    for row in rows:
        if row.row_id in result.adjusted_mm2:
            lines.append(f"{row.label}: {number(area_in(row.area_mm2,'cm2'))} cm² / {number(area_in(result.adjusted_mm2[row.row_id],'cm2'))} cm²")
        elif row.error:
            lines.append(f"Excluded invalid mesh: {row.label}: {row.error}")
    lines.append("Total adjusted plated estimate: " + " / ".join(f"{number(area_in(result.total_mm2,u))} {s}" for u,s in (("cm2","cm²"),("dm2","dm²"),("in2","in²"))))
    if profile.electrical:
        lines.append(f"Selected running density: {number(settings.running_adm2)} A/dm² ({number(density_in(settings.running_adm2,'A/dm2','A/in2'))} A/in²)" if settings.running_adm2 is not None else 'Selected running density: not set; supplier value required')
        if settings.starting_adm2 is not None:
            lines.append(f"Selected starting density: {number(settings.starting_adm2)} A/dm²")
        lines.append("Calculated current at your selected density: " + (f"running {number(result.running_a)} A" if result.running_a is not None and settings.running_adm2 is not None else ('no plated area selected' if result.total_mm2 == 0 else 'density not set')))
        if result.starting_a is not None and settings.starting_adm2 is not None:
            lines.append(f"Calculated starting current: {number(result.starting_a)} A")
        cc = settings.power_mode == 'constant_current'
        lines.append('Power supply mode: ' + ('constant current' if cc else 'constant voltage'))
        lines.append(('Voltage limit: ' if cc else 'Voltage setpoint: ') + (f'{number(settings.voltage_v)} V' if settings.voltage_v is not None else 'not set'))
        lines.append(VOLTAGE_GUIDANCE)
    else:
        lines.append('Current and voltage: not applicable (area-only process)')
    lines.extend(result.warnings)
    lines.append(LIMITATION)
    lines.append(profile.reference())
    if profile.source: lines.append('Source (reviewed 2026-10-10): ' + profile.source)
    if reference_notice(settings): lines.append(reference_notice(settings))
    return "\n".join(lines)
