import pytest
from pycroner.parser import CronParser

@pytest.fixture
def parser(): 
    return CronParser()

# ---------------------------------- # 
#           Valid cases              # 
# ---------------------------------- # 

def test_parse_all_wildcards(parser):
    result = parser.parse("* * * * *")
    assert result["minute"] == set(range(60))
    assert result["hour"] == set(range(24))
    assert result["day"] == set(range(1, 32))
    assert result["month"] == set(range(1, 13))
    assert result["weekday"] == set(range(7))

def test_parse_step_values(parser):
    result = parser.parse("*/15 * * * *")
    assert result["minute"] == {0, 15, 30, 45}

def test_parse_ranges_and_lists(parser):
    result = parser.parse("0,30 6-8 10-12 1,6,12 1-3")
    assert result["minute"] == {0, 30}
    assert result["hour"] == {6, 7, 8}
    assert result["day"] == {10, 11, 12}
    assert result["month"] == {1, 6, 12}
    assert result["weekday"] == {1, 2, 3}

def test_parse_mixed_step_and_explicit(parser):
    result = parser.parse("1-3,5,*/20 10 15 2 0")
    expected_minutes = {1, 2, 3, 5} | set(range(0, 60, 20))
    assert result["minute"] == expected_minutes
    assert result["hour"] == {10}
    assert result["day"] == {15}
    assert result["month"] == {2}
    assert result["weekday"] == {0}

# ---------------------------------- # 
#      Cases with invalid crons      # 
# ---------------------------------- # 

def test_too_few_fields(parser):
    with pytest.raises(ValueError):
        parser.parse("* * *")

def test_too_many_fields(parser):
    with pytest.raises(ValueError):
        parser.parse("* * * * * *")

def test_invalid_minute_range(parser):
    with pytest.raises(ValueError):
        parser.parse("61 * * * *")

def test_invalid_hour_range(parser):
    with pytest.raises(ValueError):
        parser.parse("* 24 * * *")

def test_invalid_day_range(parser):
    with pytest.raises(ValueError):
        parser.parse("* * 0 * *")

def test_invalid_month_range(parser):
    with pytest.raises(ValueError):
        parser.parse("* * * 13 *")

def test_invalid_weekday_range(parser):
    with pytest.raises(ValueError):
        parser.parse("* * * * 7")

def test_invalid_step_value(parser):
    with pytest.raises(ValueError):
        parser.parse("*/X * * * *")

def test_reversed_range(parser):
    with pytest.raises(ValueError):
        parser.parse("10-5 * * * *")
