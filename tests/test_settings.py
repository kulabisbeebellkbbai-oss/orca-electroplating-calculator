from dataclasses import replace
import json
import pytest
from electroplating_calculator.settings import default_settings,decode_settings,encode_settings


def test_missing_config_uses_defaults():
    s=decode_settings("{}")
    assert s.profile == "caswell_acid_copper"
    assert s.running_adm2 == pytest.approx(1.08500217000434)
    assert s.starting_adm2 is None
    assert s.density_unit == "A/in2" and s.area_unit == "cm2"


def test_settings_save_contains_no_model_state():
    s=replace(default_settings(),bath_label="My bath",coating_label="My coating",running_adm2=2,starting_adm2=.3)
    encoded=encode_settings(s)
    assert decode_settings(encoded) == s
    assert "choices" not in json.loads(encoded)
    assert "rows" not in json.loads(encoded)


@pytest.mark.parametrize("raw",["{", "null", "[]", '{"running_adm2":NaN}', '{"schema_version":999}',
                              '{"profile":"evil"}','{"running_adm2":true}'])
def test_bad_json_or_schema_reports_error(raw):
    with pytest.raises(ValueError):
        decode_settings(raw)


def test_unknown_schema_reports_error():
    with pytest.raises(ValueError):
        encode_settings(replace(default_settings(),schema_version=99))


def test_disabled_start_versus_zero():
    with pytest.raises(ValueError):
        encode_settings(replace(default_settings(),starting_adm2=0))


def test_custom_density_preserved():
    s=replace(default_settings(),profile="custom",running_adm2=.123)
    assert decode_settings(encode_settings(s)).running_adm2 == .123
