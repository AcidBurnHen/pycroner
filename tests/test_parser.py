import pytest
from pycroner.parser import CronParser


def mask_from_values(vals):
    m = 0
    for v in vals:
        m |= 1 << v
    return m


def mask_range(start, end, step=1):
    return mask_from_values(range(start, end + 1, step))


@pytest.fixture
def parser():
    return CronParser()

# ---------------------------------- # 
#           Valid cases              # 
# ---------------------------------- # 

def test_parse_all_wildcards(parser):
    result = parser.parse("* * * * *")
    assert result["minute"] == mask_range(0, 59)
    assert result["hour"] == mask_range(0, 23)
    assert result["day"] == mask_range(1, 31)
    assert result["month"] == mask_range(1, 12)
    assert result["weekday"] == mask_range(0, 6)

def test_parse_step_values(parser):
    result = parser.parse("*/15 * * * *")
    assert result["minute"] == mask_from_values([0, 15, 30, 45])

def test_parse_ranges_and_lists(parser):
    result = parser.parse("0,30 6-8 10-12 1,6,12 1-3")
    assert result["minute"] == mask_from_values([0, 30])
    assert result["hour"] == mask_from_values([6, 7, 8])
    assert result["day"] == mask_from_values([10, 11, 12])
    assert result["month"] == mask_from_values([1, 6, 12])
    assert result["weekday"] == mask_from_values([1, 2, 3])

def test_parse_mixed_step_and_explicit(parser):
    result = parser.parse("1-3,5,*/20 10 15 2 0")
    expected_minutes = mask_from_values([1, 2, 3, 5]) | mask_range(0, 59, 20)
    assert result["minute"] == expected_minutes
    assert result["hour"] == mask_from_values([10])
    assert result["day"] == mask_from_values([15])
    assert result["month"] == mask_from_values([2])
    assert result["weekday"] == mask_from_values([0])


def test_parse_on_start(parser):
    assert parser.parse("on_start") == "on_start"

def test_parse_on_exit(parser):
    assert parser.parse("on_exit") == "on_exit"

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
