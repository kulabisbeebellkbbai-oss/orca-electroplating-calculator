from dataclasses import replace
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from electroplating_calculator.calculation import AreaRow, RowChoice, calculate
from electroplating_calculator.settings import default_settings
from electroplating_calculator.dialog import render_dialog, format_report


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        instance = p.chromium.launch()
        yield instance
        instance.close()


@pytest.fixture
def page(browser):
    page = browser.new_page(viewport={"width":1050,"height":850})
    rows = [AreaRow("0:0:0",'Cube </script><script>alert("雪")</script>',600),AreaRow("0:1:0","Cube copy 2",600)]
    page.set_content(render_dialog(rows,default_settings()))
    yield page
    page.close()


def test_unit_switch_preserves_current_and_selection(page):
    before = page.locator("#running-result").inner_text()
    for _ in range(3):
        page.get_by_label("Density unit",exact=True).select_option("A/dm2")
        page.get_by_label("Density unit",exact=True).select_option("A/in2")
    assert page.locator("#running-result").inner_text() == before
    page.get_by_label("Include Cube copy 2",exact=True).uncheck()
    assert page.locator("#total").inner_text().startswith("6 cm²")


def test_invalid_and_starting_independence(page):
    page.get_by_label("Running density",exact=True).fill("-1")
    assert page.get_by_role("button",name="Copy report",exact=True).is_disabled()
    assert "Enter" in page.locator("#validation").inner_text()
    page.get_by_label("Running density",exact=True).fill("0.1")
    run = page.locator("#running-result").inner_text()
    page.get_by_label("Use starting density",exact=True).check()
    page.get_by_label("Starting density",exact=True).fill("0.02")
    assert page.locator("#running-result").inner_text() == run
    assert page.locator("#starting-result").inner_text() != "—"


def test_profile_apply_converts_silver_asf_and_keeps_voltage_limit_distinct(page):
    page.locator('#profile').select_option('silver_nc')
    page.get_by_role('button', name='Use profile settings', exact=True).click()
    # 12 cm² = 1.86000372 in²; 10 ASF = 10/144 A/in².
    assert float(page.locator('#running-result').inner_text().split()[0]) == pytest.approx(.12916693)
    assert page.locator('#voltage').input_value() == ''
    page.locator('#power-mode').select_option('constant_voltage')
    page.get_by_role('button', name='Use profile settings', exact=True).click()
    assert page.locator('#voltage').input_value() == '1.5'
    page.locator('#voltage').fill('2.8')
    assert float(page.locator('#running-result').inner_text().split()[0]) == pytest.approx(.12916693)
    assert 'Voltage setpoint: 2.8 V' in page.locator('#report').input_value()


def test_electroless_suppresses_stale_copper_settings_and_saves_area_only(page):
    page.locator('#profile').select_option('electroless_nickel')
    assert page.locator('#running').is_disabled()
    assert page.locator('#voltage').is_disabled()
    assert page.locator('#running-result').inner_text() == 'Not applicable'
    assert '12 cm²' in page.locator('#report').input_value()
    page.evaluate('window.orca={submit:p=>window.submitted=p}')
    page.locator('#save').click()
    from electroplating_calculator.dialog import parse_submission
    payload = page.evaluate('window.submitted')
    _, _, saved = parse_submission(payload, [AreaRow('0:0:0','one',600),AreaRow('0:1:0','two',600)])
    assert saved.running_adm2 is None and saved.voltage_v is None


def test_unverified_profile_clears_values_on_apply_and_can_save_manual_inputs(page):
    page.locator('#profile').select_option('zinc_alkaline')
    page.get_by_role('button', name='Use profile settings', exact=True).click()
    assert page.locator('#running').input_value() == ''
    assert page.locator('#voltage').input_value() == ''
    assert 'not set' in page.locator('#report').input_value()
    assert page.locator('#save').is_enabled()
    page.locator('#running').fill('.2')
    page.locator('#voltage').fill('4')
    page.locator('#power-mode').select_option('constant_voltage')
    # A voltage limit must not silently become a setpoint.
    assert page.locator('#voltage').input_value() == ''


@pytest.mark.parametrize('mode', ['constant_current', 'constant_voltage'])
def test_every_profile_browser_report_and_saved_settings_match_python(page, mode):
    from electroplating_calculator.profiles import PROFILES
    from electroplating_calculator.dialog import parse_submission
    rows = [AreaRow('0:0:0','Cube </script><script>alert("雪")</script>',600),AreaRow('0:1:0','Cube copy 2',600)]
    page.evaluate('window.orca={submit:p=>window.submitted=p}')
    for profile in PROFILES:
        page.locator('#profile').select_option(profile)
        if page.locator('#power-mode').is_enabled():
            page.locator('#power-mode').select_option(mode)
        page.locator('#use-profile').click()
        page.locator('#save').click()
        _, choices, s = parse_submission(page.evaluate('window.submitted'), rows)
        result = calculate(rows, choices, running_adm2=s.running_adm2, starting_adm2=s.starting_adm2)
        assert page.locator('#report').input_value() == format_report(rows, choices, s, result), profile


def test_saved_voltage_mode_and_manual_value_survive_reopen(page):
    from electroplating_calculator.settings import decode_settings, encode_settings
    from electroplating_calculator.dialog import parse_submission
    rows = [AreaRow('0:0:0','one',600),AreaRow('0:1:0','two',600)]
    page.locator('#power-mode').select_option('constant_voltage')
    page.locator('#voltage').fill('2.75')
    page.evaluate('window.orca={submit:p=>window.submitted=p}')
    page.locator('#save').click()
    _, choices, saved = parse_submission(page.evaluate('window.submitted'), rows)
    page.set_content(render_dialog(rows, decode_settings(encode_settings(saved)), choices=choices))
    assert page.locator('#power-mode').input_value() == 'constant_voltage'
    assert page.locator('#voltage').input_value() == '2.75'
    assert 'Voltage setpoint: 2.75 V' in page.locator('#report').input_value()


@pytest.mark.parametrize('field', ['running', 'voltage'])
def test_incomplete_number_cannot_silently_save_as_blank(page, field):
    page.locator('#'+field).fill('')
    page.locator('#'+field).press_sequentially('1e')
    assert page.locator('#'+field).evaluate('e=>e.validity.badInput')
    assert page.locator('#save').is_disabled()
    assert page.locator('#copy').is_disabled()
    page.locator('#'+field).fill('')
    assert page.locator('#save').is_enabled()


def test_report_matches_python_and_literal_names(page):
    rows = [AreaRow("0:0:0",'Cube </script><script>alert("雪")</script>',600),AreaRow("0:1:0","Cube copy 2",600)]
    choices = [RowChoice(r.row_id) for r in rows]
    settings = default_settings()
    result = calculate(rows,choices,running_adm2=settings.running_adm2)
    assert page.locator("#report").input_value() == format_report(rows,choices,settings,result)
    assert page.locator("tbody tr").count() == 2


def test_copy_fallback_and_valid_save_payload(page):
    page.evaluate("window.orca={submit:p=>window.submitted=p}; Object.defineProperty(navigator,'clipboard',{value:undefined});")
    page.get_by_role("button",name="Copy report",exact=True).click()
    assert "selected" in page.locator("#copy-status").inner_text()
    page.get_by_label("Plated percentage for Cube copy 2",exact=True).fill("50")
    page.get_by_role("button",name="Save settings",exact=True).click()
    from electroplating_calculator.dialog import parse_submission
    payload = page.evaluate("window.submitted")
    action, choices, settings = parse_submission(payload,[AreaRow("0:0:0","one",600),AreaRow("0:1:0","two",600)])
    assert action == "save" and choices[1].plated_percent == 50


def test_light_dark_screenshots(page):
    destination = Path("artifacts/screenshots")
    destination.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(destination/"calculator-light.png"),full_page=True)
    page.emulate_media(color_scheme="dark")
    page.screenshot(path=str(destination/"calculator-dark.png"),full_page=True)


def test_template_tokens_are_literal(browser):
    page=browser.new_page()
    page.set_content(render_dialog([AreaRow('x','__SCRIPT__ __DATA__ 雪',600)],replace(default_settings(),bath_label='Bath __SCRIPT__')))
    assert page.locator('tbody tr').count()==1
    assert '__SCRIPT__ __DATA__ 雪' in page.locator('tbody').inner_text()
    assert 'Bath __SCRIPT__' in page.locator('#report').input_value()
    page.close()


@pytest.mark.parametrize('host_theme,os_theme,bg,fg',[
    ('dark','light','#191e23','#e5edef'),('light','dark','#ffffff','#182c30')])
def test_host_theme_overrides_os_consistently(browser,host_theme,os_theme,bg,fg):
    page=browser.new_page(color_scheme=os_theme)
    page.set_content(render_dialog([AreaRow('x','Cube',600)],default_settings()))
    page.evaluate("([theme,bg,fg])=>{document.documentElement.dataset.orcaTheme=theme;document.documentElement.style.setProperty('--orca-bg',bg);document.documentElement.style.setProperty('--orca-fg',fg);}",[host_theme,bg,fg])
    colors=page.locator('#running').evaluate("e=>({bg:getComputedStyle(e).backgroundColor,fg:getComputedStyle(e).color,hostBg:getComputedStyle(document.body).backgroundColor,hostFg:getComputedStyle(document.body).color})")
    assert colors['bg']==colors['hostBg']
    assert colors['fg']==colors['hostFg']
    page.close()


def test_edit_after_save_marks_settings_unsaved(browser):
    page=browser.new_page()
    page.set_content(render_dialog([AreaRow('x','Cube',600)],default_settings(),message='Settings saved.'))
    page.get_by_label('Running density',exact=True).fill('0.1')
    assert 'Settings saved.' not in page.locator('#message').inner_text()
    assert 'unsaved' in page.locator('#message').inner_text().lower()
    page.close()
