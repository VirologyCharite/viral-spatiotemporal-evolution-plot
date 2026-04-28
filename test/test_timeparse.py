"""Tests for time string parsing functionality."""

import math
import pytest

from vsep.timeparse import convert_x_value, parse_time_to_log10_seconds


class TestParseTimeToLog10Seconds:
    """Test cases for parse_time_to_log10_seconds function."""

    def test_milliseconds(self):
        """Test millisecond parsing."""
        assert parse_time_to_log10_seconds("1 ms") == pytest.approx(-3.0, abs=0.01)
        assert parse_time_to_log10_seconds("5 milliseconds") == pytest.approx(-2.30, abs=0.01)
        assert parse_time_to_log10_seconds("500 msec") == pytest.approx(-0.30, abs=0.01)

    def test_microseconds(self):
        """Test microsecond parsing."""
        assert parse_time_to_log10_seconds("1 microsecond") == pytest.approx(-6.0, abs=0.01)
        assert parse_time_to_log10_seconds("10 μs") == pytest.approx(-5.0, abs=0.01)
        assert parse_time_to_log10_seconds("100 us") == pytest.approx(-4.0, abs=0.01)

    def test_nanoseconds(self):
        """Test nanosecond parsing."""
        assert parse_time_to_log10_seconds("1 nanosecond") == pytest.approx(-9.0, abs=0.01)
        assert parse_time_to_log10_seconds("10 ns") == pytest.approx(-8.0, abs=0.01)

    def test_standard_units(self):
        """Test standard time units that pytimeparse handles."""
        assert parse_time_to_log10_seconds("1 second") == pytest.approx(0.0, abs=0.01)
        assert parse_time_to_log10_seconds("1 minute") == pytest.approx(1.78, abs=0.01)
        assert parse_time_to_log10_seconds("1 hour") == pytest.approx(3.56, abs=0.01)
        assert parse_time_to_log10_seconds("1 day") == pytest.approx(4.94, abs=0.01)
        assert parse_time_to_log10_seconds("1 week") == pytest.approx(5.78, abs=0.01)

    def test_years(self):
        """Test year parsing."""
        assert parse_time_to_log10_seconds("1 year") == pytest.approx(7.50, abs=0.01)
        assert parse_time_to_log10_seconds("2 years") == pytest.approx(7.80, abs=0.01)
        assert parse_time_to_log10_seconds("10 yr") == pytest.approx(8.50, abs=0.01)

    def test_decades_centuries_millennia(self):
        """Test longer time periods."""
        assert parse_time_to_log10_seconds("1 decade") == pytest.approx(8.50, abs=0.01)
        assert parse_time_to_log10_seconds("1 century") == pytest.approx(9.50, abs=0.01)
        assert parse_time_to_log10_seconds("1 millennium") == pytest.approx(10.50, abs=0.01)

    def test_geological_time(self):
        """Test geological time units."""
        assert parse_time_to_log10_seconds("1 Myr") == pytest.approx(13.50, abs=0.01)
        assert parse_time_to_log10_seconds("10 Myr") == pytest.approx(14.50, abs=0.01)
        assert parse_time_to_log10_seconds("1 Gyr") == pytest.approx(16.50, abs=0.1)  # Allow more tolerance for Gyr
        assert parse_time_to_log10_seconds("4 Gyr") == pytest.approx(17.10, abs=0.01)

    def test_billion_million_years_spelled_out(self):
        """Test spelled-out geological time."""
        assert parse_time_to_log10_seconds("1 million years") == pytest.approx(13.50, abs=0.01)
        assert parse_time_to_log10_seconds("100 million years") == pytest.approx(15.50, abs=0.01)
        assert parse_time_to_log10_seconds("1 billion years") == pytest.approx(16.50, abs=0.1)  # Allow more tolerance

    def test_fractional_values(self):
        """Test fractional time values."""
        assert parse_time_to_log10_seconds("2.5 hours") == pytest.approx(3.95, abs=0.01)
        assert parse_time_to_log10_seconds("4.5 Gyr") == pytest.approx(17.15, abs=0.01)

    def test_case_insensitive(self):
        """Test that parsing is case insensitive."""
        assert parse_time_to_log10_seconds("1 YEAR") == pytest.approx(7.50, abs=0.01)
        assert parse_time_to_log10_seconds("5 MYR") == pytest.approx(14.20, abs=0.01)
        assert parse_time_to_log10_seconds("2 GYR") == pytest.approx(16.80, abs=0.1)  # Allow more tolerance

    def test_invalid_strings(self):
        """Test that invalid strings return None."""
        assert parse_time_to_log10_seconds("not a time") is None
        assert parse_time_to_log10_seconds("") is None
        assert parse_time_to_log10_seconds("xyz") is None
        assert parse_time_to_log10_seconds("5") is None  # number without unit

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very small numbers
        assert parse_time_to_log10_seconds("0.1 ms") == pytest.approx(-4.0, abs=0.01)

        # Very large numbers
        assert parse_time_to_log10_seconds("1000 Myr") == pytest.approx(16.50, abs=0.01)


class TestConvertXValue:
    """Test cases for convert_x_value function."""

    def test_numeric_values(self):
        """Test that numeric values pass through unchanged."""
        assert convert_x_value(7.5) == 7.5
        assert convert_x_value(-3.0) == -3.0
        assert convert_x_value(0) == 0.0

    def test_string_values(self):
        """Test that string values are parsed correctly."""
        assert convert_x_value("1 year") == pytest.approx(7.50, abs=0.01)
        assert convert_x_value("1 ms") == pytest.approx(-3.0, abs=0.01)

    def test_invalid_string_values(self):
        """Test that invalid strings return None."""
        assert convert_x_value("invalid") is None
        assert convert_x_value("") is None

    def test_mixed_types(self):
        """Test various input types."""
        # Integer
        assert convert_x_value(5) == 5.0

        # Float
        assert convert_x_value(3.14) == 3.14

        # String that parses
        assert convert_x_value("1 day") == pytest.approx(4.94, abs=0.01)

        # String that doesn't parse
        assert convert_x_value("nonsense") is None


# Test data for parametrized tests
TIME_STRING_TEST_DATA = [
    # Format: (input_string, expected_log10_seconds, tolerance)
    ("1 ms", -3.0, 0.01),
    ("1 minute", 1.78, 0.01),
    ("1 hour", 3.56, 0.01),
    ("1 day", 4.94, 0.01),
    ("1 week", 5.78, 0.01),
    ("1 year", 7.50, 0.01),
    ("1 decade", 8.50, 0.01),
    ("1 century", 9.50, 0.01),
    ("10 Myr", 14.50, 0.01),
    ("4 Gyr", 17.10, 0.02),
]


@pytest.mark.parametrize("time_str,expected,tolerance", TIME_STRING_TEST_DATA)
def test_time_string_parsing_parametrized(time_str, expected, tolerance):
    """Parametrized test for time string parsing."""
    result = parse_time_to_log10_seconds(time_str)
    assert result == pytest.approx(expected, abs=tolerance)


def test_reference_values_from_toml():
    """Test that our parsing matches the reference values from the original TOML comments."""
    # From the original TOML comments:
    # -3.0 = 1 ms | 7.5 = 1 year | 17.1 = 4 Gyr
    assert parse_time_to_log10_seconds("1 ms") == pytest.approx(-3.0, abs=0.01)
    assert parse_time_to_log10_seconds("1 year") == pytest.approx(7.5, abs=0.01)
    assert parse_time_to_log10_seconds("4 Gyr") == pytest.approx(17.1, abs=0.02)

    # Additional reference values from TOML:
    # 1.78 = 1 min | 3.56 = 1 hr | 4.94 = 1 day
    assert parse_time_to_log10_seconds("1 minute") == pytest.approx(1.78, abs=0.01)
    assert parse_time_to_log10_seconds("1 hour") == pytest.approx(3.56, abs=0.01)
    assert parse_time_to_log10_seconds("1 day") == pytest.approx(4.94, abs=0.01)

    # 9.50 = 1 century | 11.50 = 10,000 yr | 13.50 = 1 Myr | 15.50 = 100 Myr
    assert parse_time_to_log10_seconds("1 century") == pytest.approx(9.50, abs=0.01)
    assert parse_time_to_log10_seconds("10000 years") == pytest.approx(11.50, abs=0.01)
    assert parse_time_to_log10_seconds("1 Myr") == pytest.approx(13.50, abs=0.01)
    assert parse_time_to_log10_seconds("100 Myr") == pytest.approx(15.50, abs=0.01)