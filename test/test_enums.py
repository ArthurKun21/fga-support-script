import pytest

from enums import SupportKind


def test_support_kind_values():
    """Test that SupportKind enum has the expected values."""
    assert SupportKind.SERVANT == "servant"
    assert SupportKind.CRAFT_ESSENCE == "ce"


def test_support_kind_string_representation():
    """Test the string representation of SupportKind enum values."""
    assert str(SupportKind.SERVANT) == "servant"
    assert str(SupportKind.CRAFT_ESSENCE) == "ce"


def test_support_kind_comparison():
    """Test that SupportKind enum values can be compared with strings."""
    assert SupportKind.SERVANT == "servant"
    assert "servant" == SupportKind.SERVANT  # noqa: SIM300
    assert SupportKind.CRAFT_ESSENCE == "ce"
    assert "ce" == SupportKind.CRAFT_ESSENCE  # noqa: SIM300


def test_support_kind_identity():
    """Test identity of SupportKind enum values."""
    assert SupportKind.SERVANT is SupportKind.SERVANT
    assert SupportKind.CRAFT_ESSENCE is SupportKind.CRAFT_ESSENCE
    assert SupportKind.SERVANT is not SupportKind.CRAFT_ESSENCE


def test_support_kind_from_string():
    """Test creating SupportKind from strings."""
    assert SupportKind("servant") == SupportKind.SERVANT
    assert SupportKind("ce") == SupportKind.CRAFT_ESSENCE


def test_support_kind_invalid_value():
    """Test that creating SupportKind with invalid value raises ValueError."""
    with pytest.raises(ValueError):
        SupportKind("invalid")
