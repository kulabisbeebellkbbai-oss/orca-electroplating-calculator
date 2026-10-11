from dataclasses import asdict
import pytest
from electroplating_calculator.calculation import AreaRow, RowChoice, calculate
from electroplating_calculator.settings import default_settings
from electroplating_calculator.dialog import render_dialog, parse_submission, format_report

NAME = '</script><script>alert("雪")</script>'
ROWS = [AreaRow("0:0:0",NAME,600)]


def payload():
    return dict(action="save", choices=[asdict(RowChoice("0:0:0"))],settings=asdict(default_settings()))


def test_safe_embedding_and_literal_report():
    html = render_dialog(ROWS,default_settings())
    assert NAME not in html
    assert "\\u003c/script" in html
    result = calculate(ROWS,[RowChoice("0:0:0")],running_adm2=1)
    assert NAME in format_report(ROWS,[RowChoice("0:0:0")],default_settings(),result)


def test_submission_uses_trusted_area():
    action, choices, settings = parse_submission(payload(),ROWS)
    assert action == "save" and choices[0].selected
    assert settings == default_settings()


@pytest.mark.parametrize("mutate",[
    lambda p:p.update(action="upload"),
    lambda p:p["choices"][0].update(area_mm2=123),
    lambda p:p["choices"][0].update(row_id="unknown"),
    lambda p:p["choices"][0].update(plated_percent=float("nan")),
    lambda p:p["choices"].clear(),
    lambda p:p["settings"].update(running_adm2=False),
])
def test_untrusted_payload_rejected(mutate):
    p = payload(); mutate(p)
    with pytest.raises(ValueError): parse_submission(p,ROWS)


def test_close_needs_no_valid_form():
    assert parse_submission({"action":"close"},ROWS)[0] == "close"
