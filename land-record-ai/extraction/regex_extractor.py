"""Regex pattern-based extractor for Khasra, Khata, Land Area, Dates, and Mutations."""

from datetime import datetime
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import yaml

from schemas.fields import AreaField, DateField, KhasraField, KhataField, MutationField
from schemas.ocr import OCREngineResult, OCRWord


class RegexFieldExtractor:
    """Extracts land record fields using multi-lingual regular expressions and keyword anchors."""

    def __init__(self, fields_config_path: Optional[str] = None):
        self.config = self._load_config(fields_config_path)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        path = config_path or os.path.join(os.path.dirname(__file__), "..", "config", "fields.yaml")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def extract_khasra_numbers(self, text: str, words: Optional[List[OCRWord]] = None) -> List[KhasraField]:
        """Extract Khasra / Survey numbers from text."""
        results: List[KhasraField] = []
        seen = set()

        # Specific labeled pattern: e.g. "खसरा संख्या: 245/1" or "Khasra No: 245/1" or "312/B"
        labeled_pattern = r'(?i)(?:खसरा\s*(?:संख्या|नं\.?|सं\.?)?|गाटा\s*(?:संख्या|सं\.?)?|भूखण्ड\s*संख्या|khasra\s*(?:no|number)?|survey\s*(?:no|number)?|plot\s*no\.?)\s*[:\-\s]*([0-9]+(?:[\/\-][0-9A-Za-z\u0900-\u097F]+)*(?:\s*[क-हA-Za-z])?)'
        
        for m in re.finditer(labeled_pattern, text):
            raw_val = m.group(1).strip()
            # Clean spaces around slashes: "245 / 1" -> "245/1"
            clean_val = re.sub(r'\s*[\/\-]\s*', '/', raw_val)
            if clean_val and clean_val not in seen:
                seen.add(clean_val)
                bbox = self._find_word_bbox(clean_val, words)
                results.append(KhasraField(
                    value=clean_val,
                    raw_text=m.group(0).strip(),
                    confidence=0.95,
                    tier="VERY_HIGH",
                    bbox=bbox
                ))

        # Fallback standalone slash pattern e.g. "245/1" or "312/B"
        if not results:
            standalone_pattern = r'\b([0-9]{1,5}\/[0-9]{1,4}(?:\/[0-9]{1,4})*(?:[A-Za-z])?)\b'
            for m in re.finditer(standalone_pattern, text):
                val = m.group(1).strip()
                if val not in seen:
                    seen.add(val)
                    bbox = self._find_word_bbox(val, words)
                    results.append(KhasraField(
                        value=val,
                        raw_text=m.group(0).strip(),
                        confidence=0.85,
                        tier="HIGH",
                        bbox=bbox
                    ))

        return results

    def extract_khata_numbers(self, text: str, words: Optional[List[OCRWord]] = None) -> List[KhataField]:
        """Extract Khata / Khatauni account numbers from text."""
        results: List[KhataField] = []
        seen = set()

        pattern = r'(?i)(?:खाता\s*(?:संख्या|नं\.?|सं\.?)?|खतौनी\s*(?:संख्या|नं\.?|सं\.?)?|khata\s*(?:no|number)?|khewat\s*(?:no|number)?|account\s*no\.?)\s*[:\-\s]*([0-9]+(?:[\/\-][0-9]+)?)'
        for m in re.finditer(pattern, text):
            raw_val = m.group(1).strip()
            clean_val = re.sub(r'\s*[\/\-]\s*', '/', raw_val)
            if clean_val and clean_val not in seen:
                seen.add(clean_val)
                bbox = self._find_word_bbox(clean_val, words)
                results.append(KhataField(
                    value=clean_val,
                    raw_text=m.group(0).strip(),
                    confidence=0.92,
                    tier="VERY_HIGH",
                    bbox=bbox
                ))

        return results

    def extract_land_area(self, text: str, words: Optional[List[OCRWord]] = None) -> AreaField:
        """Extract land area numeric value and unit."""
        unit_aliases = {
            "hectare": ["हेक्टेयर", "हेक्टे.", "हे.", "hectare", "hectares", "ha", "hac"],
            "acre": ["एकड़", "एकड", "acre", "acres", "ac"],
            "bigha": ["बीघा", "बीघे", "विघा", "bigha", "bighas"],
            "biswa": ["बिस्वा", "बिस्वे", "biswa", "biswas"],
            "sq_meter": ["वर्ग मीटर", "वर्ग मी.", "व.मी.", "square meter", "sqm", "sq m", "sq.m."]
        }

        # Match labeled area e.g. "रकबा: 4.25 एकड़" or "Land Area: 2.50 Hectares"
        area_pattern = r'(?i)(?:रकबा|क्षेत्रफल|विस्तार|land\s*area|area|extent|measurement)\s*[:\-\s]*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z\u0900-\u097F\.\s]+)?'
        match = re.search(area_pattern, text)

        if match:
            num_str = match.group(1)
            raw_unit = (match.group(2) or "").strip()
            val_float = float(num_str)

            # Match unit
            identified_unit = None
            for std_unit, aliases in unit_aliases.items():
                for alias in aliases:
                    if alias.lower() in raw_unit.lower():
                        identified_unit = std_unit
                        break
                if identified_unit:
                    break

            bbox = self._find_word_bbox(num_str, words)
            return AreaField(
                value=val_float,
                unit=identified_unit or "acre",
                raw_text=match.group(0).strip(),
                confidence=0.92,
                tier="VERY_HIGH",
                bbox=bbox
            )

        # Standalone number + unit search: e.g. "4.25 Acres" or "2.50 हेक्टेयर"
        fallback_pattern = r'([0-9]+(?:\.[0-9]+)?)\s*(हेक्टेयर|हेक्टे\.|एकड़|बीघा|बिस्वा|वर्ग मीटर|hectares?|acres?|bighas?|sqm)'
        m_fallback = re.search(fallback_pattern, text, re.IGNORECASE)
        if m_fallback:
            val_float = float(m_fallback.group(1))
            raw_u = m_fallback.group(2).lower()
            u_name = "acre"
            if any(k in raw_u for k in ["हेक्टे", "hectare"]):
                u_name = "hectare"
            elif any(k in raw_u for k in ["बीघा", "bigha"]):
                u_name = "bigha"
            elif any(k in raw_u for k in ["बिस्वा", "biswa"]):
                u_name = "biswa"
            elif any(k in raw_u for k in ["वर्ग", "sqm", "meter"]):
                u_name = "sq_meter"

            bbox = self._find_word_bbox(m_fallback.group(1), words)
            return AreaField(
                value=val_float,
                unit=u_name,
                raw_text=m_fallback.group(0).strip(),
                confidence=0.85,
                tier="HIGH",
                bbox=bbox
            )

        return AreaField(confidence=0.0, tier="LOW")

    def extract_mutation_reference(self, text: str, words: Optional[List[OCRWord]] = None) -> Optional[MutationField]:
        """Extract mutation reference identifier."""
        # Matches e.g. "MUT-2023-882", "MUT-2022-104", "MUT-PENDING", "नामांतरण पंजी: MUT-101"
        pattern = r'(?i)(?:नामांतरण|दाखिल\s*खारिज|इंतकाल|तब्दील\s*मलकीयत|फेरफार|mutation(?:\s*(?:number|no|ref))?)\s*[:\-\s]*([A-Za-z0-9\-]+)'
        m = re.search(pattern, text)
        if m:
            val = m.group(1).strip()
            bbox = self._find_word_bbox(val, words)
            return MutationField(
                mutation_number=val,
                raw_text=m.group(0).strip(),
                confidence=0.90,
                tier="VERY_HIGH",
                bbox=bbox
            )

        # Standalone MUT- pattern
        m_standalone = re.search(r'\b(MUT-[0-9A-Za-z\-]+)\b', text, re.IGNORECASE)
        if m_standalone:
            val = m_standalone.group(1).strip()
            bbox = self._find_word_bbox(val, words)
            return MutationField(
                mutation_number=val,
                raw_text=m_standalone.group(0).strip(),
                confidence=0.88,
                tier="HIGH",
                bbox=bbox
            )

        return None

    def extract_record_date(self, text: str, words: Optional[List[OCRWord]] = None) -> Optional[DateField]:
        """Extract record / order date and standardize to ISO format (YYYY-MM-DD)."""
        # DD/MM/YYYY or DD-MM-YYYY
        d_match = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b', text)
        if d_match:
            day, month, year = int(d_match.group(1)), int(d_match.group(2)), int(d_match.group(3))
            try:
                dt = datetime(year, month, day)
                iso_str = dt.strftime("%Y-%m-%d")
                bbox = self._find_word_bbox(d_match.group(0), words)
                return DateField(
                    iso_date=iso_str,
                    raw_date=d_match.group(0),
                    confidence=0.94,
                    tier="VERY_HIGH",
                    bbox=bbox
                )
            except ValueError:
                pass

        # YYYY-MM-DD or YYYY/MM/DD
        y_match = re.search(r'\b(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})\b', text)
        if y_match:
            year, month, day = int(y_match.group(1)), int(y_match.group(2)), int(y_match.group(3))
            try:
                dt = datetime(year, month, day)
                iso_str = dt.strftime("%Y-%m-%d")
                bbox = self._find_word_bbox(y_match.group(0), words)
                return DateField(
                    iso_date=iso_str,
                    raw_date=y_match.group(0),
                    confidence=0.94,
                    tier="VERY_HIGH",
                    bbox=bbox
                )
            except ValueError:
                pass

        return None

    def _find_word_bbox(self, target_text: str, words: Optional[List[OCRWord]]) -> Optional[List[int]]:
        """Find the bounding box of the matching word token if available."""
        if not words or not target_text:
            return None
        target_clean = target_text.lower().replace(" ", "")
        for word in words:
            w_text = (word.normalized_text or word.text).lower().replace(" ", "")
            if target_clean in w_text or w_text in target_clean:
                return word.bbox
        return None
