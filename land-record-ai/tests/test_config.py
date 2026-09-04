"""Tests for YAML configuration files loading and schema correctness."""

from pathlib import Path
import yaml
import pytest


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class TestConfigurations:
    """Test validity and required keys in YAML configs."""

    def test_thresholds_yaml(self):
        threshold_file = CONFIG_DIR / "thresholds.yaml"
        assert threshold_file.exists()
        with open(threshold_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert "quality" in cfg
        assert "blur_threshold" in cfg["quality"]
        assert "acceptable_threshold" in cfg["quality"]
        assert "confidence_weights" in cfg
        assert cfg["confidence_weights"]["ocr"] == 0.40
        assert cfg["confidence_weights"]["extraction"] == 0.30
        assert cfg["confidence_weights"]["validation"] == 0.20
        assert cfg["confidence_weights"]["context"] == 0.10

    def test_languages_yaml(self):
        lang_file = CONFIG_DIR / "languages.yaml"
        assert lang_file.exists()
        with open(lang_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert "languages" in cfg
        assert "indic_numerals" in cfg
        assert "devanagari" in cfg["indic_numerals"]
        assert cfg["indic_numerals"]["devanagari"]["१"] == "1"

    def test_fields_yaml(self):
        fields_file = CONFIG_DIR / "fields.yaml"
        assert fields_file.exists()
        with open(fields_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert "fields" in cfg
        fields = cfg["fields"]
        assert "owner_names" in fields
        assert "khasra_numbers" in fields
        assert "khata_numbers" in fields
        assert "land_area" in fields
        assert "location" in fields
        assert "mutation" in fields

    def test_state_rules(self):
        state_rules_dir = CONFIG_DIR / "state_rules"
        assert state_rules_dir.exists()
        for rule_file in state_rules_dir.glob("*.yaml"):
            with open(rule_file, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            assert "state_name" in cfg
            assert "supported_units" in cfg
