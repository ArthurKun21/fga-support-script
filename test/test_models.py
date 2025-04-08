from models import (
    Assets,
    BaseData,
    CraftEssenceData,
    ServantData,
    _cleanup_name,
    _preprocess_name,
)


class TestPreprocessName:
    def test_normal_string(self):
        assert _preprocess_name("TestString") == "TestString"

    def test_accented_characters(self):
        assert _preprocess_name("áéíóú") == "aeiou"

    def test_mixed_characters(self):
        assert _preprocess_name("Hélló Wörld") == "Hello World"

    def test_empty_string(self):
        assert _preprocess_name("") == ""


class TestCleanupName:
    def test_normal_string(self):
        assert _cleanup_name("TestString") == "TestString"

    def test_invalid_characters(self):
        assert _cleanup_name("File:Name?") == "File Name"

    def test_with_path_separators(self):
        assert _cleanup_name("path/to\\file") == "path to file"

    def test_trailing_spaces(self):
        assert _cleanup_name(" TestString  ") == "TestString"

    def test_accented_characters(self):
        assert _cleanup_name("Sérvànt") == "Servant"

    def test_mixed_characters_with_white_space(self):
        assert _cleanup_name(" Hélló Wörld ") == "Hello World"

    def test_empty_string(self):
        assert _cleanup_name("") == ""


class TestAssets:
    def test_initialization(self):
        asset = Assets(key="test_key", url="https://example.com/image.jpg")
        assert asset.key == "test_key"
        assert asset.url == "https://example.com/image.jpg"

    def test_url_file_name(self):
        asset = Assets(key="test_key", url="https://example.com/image.jpg")
        assert asset.url_file_name == "image.jpg"

    def test_url_file_name_complex_url(self):
        asset = Assets(
            key="test_key", url="https://example.com/path/to/image.jpg?param=value"
        )
        assert asset.url_file_name == "image.jpg"

    def test_url_file_name_no_filename(self):
        asset = Assets(key="test_key", url="https://example.com/")
        assert asset.url_file_name == ""


class TestBaseData:
    def test_initialization(self):
        base_data = BaseData(idx=1, name="Test", rarity=5)
        assert base_data.idx == 1
        assert base_data.name == "Test"
        assert base_data.rarity == 5
        assert base_data.assets == []

    def test_post_init_sanitization(self):
        base_data = BaseData(idx=1, name="Tést:Name", rarity=5)
        assert base_data.name == "Test Name"

    def test_sanitized_name(self):
        base_data = BaseData(idx=1, name="Test", rarity=5)
        # Change the name after initialization to test the property
        base_data.name = "Tést:Name"
        assert base_data.sanitized_name == "Test Name"

    def test_is_empty_true(self):
        base_data = BaseData(idx=1, name="Test", rarity=5)
        assert base_data.is_empty is True

    def test_is_empty_false(self):
        asset = Assets(key="test", url="https://example.com/image.jpg")
        base_data = BaseData(idx=1, name="Test", rarity=5, assets=[asset])
        assert base_data.is_empty is False


class TestServantData:
    def test_initialization(self):
        servant = ServantData(idx=1, name="Test Servant", rarity=5)
        assert servant.idx == 1
        assert servant.name == "Test Servant"
        assert servant.rarity == 5
        assert servant.assets == []
        assert servant.class_name == ""

    def test_inheritance(self):
        servant = ServantData(idx=1, name="Test Servant", rarity=5)
        assert isinstance(servant, BaseData)

    def test_with_class_name(self):
        servant = ServantData(idx=1, name="Test Servant", rarity=5, class_name="Saber")
        assert servant.class_name == "Saber"


class TestCraftEssenceData:
    def test_initialization(self):
        ce = CraftEssenceData(idx=1, name="Test CE", rarity=5)
        assert ce.idx == 1
        assert ce.name == "Test CE"
        assert ce.rarity == 5
        assert ce.assets == []

    def test_inheritance(self):
        ce = CraftEssenceData(idx=1, name="Test CE", rarity=5)
        assert isinstance(ce, BaseData)

    def test_with_assets(self):
        asset = Assets(key="test", url="https://example.com/image.jpg")
        ce = CraftEssenceData(idx=1, name="Test CE", rarity=5, assets=[asset])
        assert ce.assets[0].key == "test"
        assert ce.assets[0].url == "https://example.com/image.jpg"
