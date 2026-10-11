import pytest
from electroplating_calculator.calculation import AreaRow, RowChoice, calculate, area_in, density_in


@pytest.mark.parametrize("unit,want",[("cm2",6),("dm2",0.06),("in2",0.93000186000372)])
def test_exact_area_conversions(unit,want):
    assert area_in(600,unit) == pytest.approx(want,rel=1e-12)


def test_copper_reference_current():
    result = calculate([AreaRow("a","part",10000)],[RowChoice("a")],running_adm2=1.08500217000434)
    assert result.running_a == pytest.approx(1.08500217000434)
    assert result.starting_a is None


def test_area_adjustments():
    result = calculate([AreaRow("a","part",10000)],[RowChoice("a",True,50,10)],running_adm2=2)
    assert result.total_mm2 == 4000
    assert result.adjusted_mm2 == {"a":4000}
    assert result.running_a == pytest.approx(0.8)


def test_unchecked_instance_excluded_and_start_independent():
    rows = [AreaRow("a","one",600),AreaRow("b","two",600)]
    result = calculate(rows,[RowChoice("a"),RowChoice("b",False)],running_adm2=2,starting_adm2=0.5)
    assert result.total_mm2 == 600
    assert result.running_a == pytest.approx(.12)
    assert result.starting_a == pytest.approx(.03)


def test_density_round_trip():
    assert density_in(.07,"A/in2","A/dm2") == pytest.approx(1.08500217000434)
    assert density_in(1.08500217000434,"A/dm2","A/in2") == pytest.approx(.07,rel=1e-12)


@pytest.mark.parametrize("value",[float("nan"),float("inf"),0,-1,True])
def test_invalid_density(value):
    with pytest.raises(ValueError):
        calculate([AreaRow("a","part",600)],[RowChoice("a")],running_adm2=value)


@pytest.mark.parametrize("percent,excluded",[(101,0),(-1,0),(True,0),(50,31), (50,-1),(50,float("nan"))])
def test_invalid_adjustments(percent,excluded):
    with pytest.raises(ValueError):
        calculate([AreaRow("a","part",6000)],[RowChoice("a",True,percent,excluded)],running_adm2=2)


@pytest.mark.parametrize("choices",[[RowChoice("unknown")],[RowChoice("a"),RowChoice("a")]])
def test_unknown_duplicate_choices(choices):
    with pytest.raises(ValueError):
        calculate([AreaRow("a","part",600)],choices,running_adm2=2)


def test_invalid_selected_geometry_blocks_batch():
    rows = [AreaRow("a","valid",600),AreaRow("b","invalid",0,error="bad mesh")]
    with pytest.raises(ValueError):
        calculate(rows,[RowChoice("a"),RowChoice("b")],running_adm2=2)
    assert calculate(rows,[RowChoice("a"),RowChoice("b",False)],running_adm2=2).total_mm2 == 600


@pytest.mark.parametrize("choices", [[],[RowChoice("a",False)],[RowChoice("a",True,0)]])
def test_empty_result_is_not_actionable(choices):
    result = calculate([AreaRow("a","part",600)],choices,running_adm2=2,starting_adm2=.5)
    assert result.total_mm2 == 0
    assert result.running_a is None and result.starting_a is None


def test_reference_range_notice_not_rejection():
    result = calculate([AreaRow("a","part",10000)],[RowChoice("a")],running_adm2=.1)
    assert result.running_a == .1


def test_overflow_cannot_produce_current():
    with pytest.raises(ValueError):
        calculate([AreaRow("a","part",1e308)],[RowChoice("a")],running_adm2=1e308)
