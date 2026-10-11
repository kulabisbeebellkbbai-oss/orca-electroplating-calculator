from dataclasses import dataclass, asdict
import json
from .calculation import density_in, finite_number, AREA_FACTORS, DENSITY_FACTORS
from .profiles import PROFILES, CASWELL_SOURCE, DENSITY_TO_ADM2

CASWELL_RANGE_AIN2 = (0.07, 0.20)


@dataclass(frozen=True)
class Settings:
    profile: str
    bath_label: str
    coating_label: str
    density_unit: str
    running_adm2: float | None
    starting_adm2: float | None
    area_unit: str
    schema_version: int = 2
    power_mode: str = 'constant_current'
    voltage_v: float | None = None


def default_settings():
    return Settings("caswell_acid_copper", "Acid copper with Caswell A/B additives",
                    "MG Chemicals 843AR", "A/in2", density_in(.07,"A/in2","A/dm2"),None,"cm2")


def validate_settings(settings):
    if type(settings.schema_version) is not int or settings.schema_version != 2:
        raise ValueError("Unsupported settings schema version")
    if not isinstance(settings.profile, str) or settings.profile not in PROFILES:
        raise ValueError("Unknown bath profile")
    if settings.area_unit not in AREA_FACTORS or settings.density_unit not in DENSITY_FACTORS:
        raise ValueError("Unknown display unit")
    for label in (settings.bath_label,settings.coating_label):
        if not isinstance(label,str) or len(label) > 300:
            raise ValueError("Profile labels must be text of at most 300 characters")
    if settings.power_mode not in ('constant_current', 'constant_voltage'):
        raise ValueError('Unknown power supply mode')
    if not PROFILES[settings.profile].electrical and any(value is not None for value in (settings.running_adm2, settings.starting_adm2, settings.voltage_v)):
        raise ValueError('Electrical settings do not apply to this bath')
    if settings.voltage_v is not None:
        finite_number(settings.voltage_v,'Voltage',positive=True)
    if settings.running_adm2 is not None:
        finite_number(settings.running_adm2,"Running current density",positive=True)
    if settings.starting_adm2 is not None:
        finite_number(settings.starting_adm2,"Starting current density",positive=True)
    return settings


def decode_settings(raw):
    try:
        values = json.loads(raw or "{}")
    except (ValueError,TypeError) as exc:
        raise ValueError("Saved settings are not valid JSON") from exc
    if not isinstance(values,dict):
        raise ValueError("Saved settings must be a JSON object")
    defaults = asdict(default_settings())
    if set(values) - defaults.keys():
        raise ValueError("Unknown saved settings fields")
    version = values.get('schema_version', 1)
    if type(version) is not int or version not in (1, 2):
        raise ValueError('Unsupported settings schema version')
    values['schema_version'] = 2
    return validate_settings(Settings(**(defaults | values)))


def encode_settings(settings):
    return json.dumps(asdict(validate_settings(settings)),ensure_ascii=False,allow_nan=False)


def reference_notice(settings):
    profile = PROFILES[settings.profile]
    if settings.running_adm2 is None or not profile.density_range:
        return ""
    density = settings.running_adm2 / DENSITY_TO_ADM2[profile.density_unit]
    low, high = profile.density_range
    if density < low * (1 - 1e-12) or density > high * (1 + 1e-12):
        return "Selected running density is outside this profile's published reference range."
    return ""
