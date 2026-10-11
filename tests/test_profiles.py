from dataclasses import asdict, replace
import json
import pytest
from electroplating_calculator.settings import default_settings, decode_settings, encode_settings
from electroplating_calculator.calculation import AreaRow, RowChoice, calculate
from electroplating_calculator.dialog import parse_submission, format_report


def test_upgrade_preserves_actual_copper_settings_without_inventing_voltage():
    old = dict(profile='caswell_acid_copper', bath_label='Acid copper',
               coating_label='MG Chemicals 843AR', density_unit='A/dm2',
               running_adm2=1.08500217000434, starting_adm2=.5, area_unit='dm2', schema_version=1)
    upgraded = decode_settings(json.dumps(old))
    assert upgraded.schema_version == 2
    for key, value in old.items():
        if key != 'schema_version': assert getattr(upgraded, key) == value
    assert upgraded.voltage_v is None and upgraded.power_mode == 'constant_current'
    assert decode_settings(encode_settings(upgraded)) == upgraded


@pytest.mark.parametrize('value', [0, -1, True, float('inf'), float('nan'), '3'])
def test_bad_voltage_cannot_be_saved(value):
    with pytest.raises(ValueError):
        encode_settings(replace(default_settings(), voltage_v=value))


def test_voltage_does_not_change_area_based_current():
    rows, choices = [AreaRow('a', 'Cube', 2400)], [RowChoice('a')]
    s = replace(default_settings(), power_mode='constant_voltage', voltage_v=3)
    payload = dict(action='save', choices=[asdict(c) for c in choices], settings=asdict(s))
    _, _, saved = parse_submission(payload, rows)
    result = calculate(rows, choices, running_adm2=saved.running_adm2)
    assert result.running_a == pytest.approx(.2604005208010416)
    report = format_report(rows, choices, saved, result)
    assert 'Voltage setpoint: 3 V' in report
    assert 'not predicted from voltage' in report


def test_electroless_rejects_forged_electrical_settings():
    with pytest.raises(ValueError):
        encode_settings(replace(default_settings(), profile='electroless_nickel'))


def test_area_only_report_has_no_current_even_if_caller_passes_stale_result():
    rows, choices = [AreaRow('a', 'Cube', 2400)], [RowChoice('a')]
    s = replace(default_settings(), profile='electroless_nickel', running_adm2=None,
                starting_adm2=None, voltage_v=None)
    stale = calculate(rows, choices, running_adm2=2, starting_adm2=.5)
    report = format_report(rows, choices, s, stale)
    assert '24 cm²' in report
    assert 'Current and voltage: not applicable' in report
    assert '0.48 A' not in report and '0.12 A' not in report


def test_missing_density_keeps_area_without_fabricating_current():
    result = calculate([AreaRow('a', 'Cube', 2400)], [RowChoice('a')], running_adm2=None)
    assert result.total_mm2 == 2400 and result.running_a is None
