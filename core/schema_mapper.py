"""
Schema Mapper - Intelligent column name matching for PizzaOps Intelligence.

Maps varied column names from different data sources to a standardized schema.
Uses fuzzy matching and keyword detection to handle naming variations.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ColumnMapping:
    """Represents a mapping from source column to standard column."""
    source_name: str
    standard_name: str
    confidence: float  # 0.0 to 1.0
    match_type: str  # 'exact', 'fuzzy', 'keyword', 'manual'


# Standard schema for PizzaOps Intelligence
STANDARD_SCHEMA = {
    # Required columns
    "order_id": {
        "type": "id",
        "required": True,
        "keywords": ["pizza", "order", "id", "no", "number", "ref", "reference"],
        "patterns": [r"pizza\s*no", r"order\s*id", r"order\s*no", r"order\s*number"],
    },
    "order_date": {
        "type": "datetime",
        "required": True,
        "keywords": ["order", "date", "day"],
        "patterns": [r"order\s*date", r"date"],
    },
    "order_time": {
        "type": "time",
        "required": False,
        "keywords": ["order", "time"],
        "patterns": [r"order\s*time", r"time"],
    },

    # Timing columns (stages)
    "order_receipt_time": {
        "type": "numeric",
        "required": False,
        "keywords": ["order", "receipt", "receive", "intake"],
        "patterns": [r"order\s*receipt", r"receipt\s*time", r"intake"],
    },
    "dough_prep_time": {
        "type": "numeric",
        "required": False,
        "keywords": ["dough", "base", "prep", "preparation"],
        "patterns": [r"dough\s*prep", r"base\s*prep", r"dough\s*time"],
    },
    "styling_time": {
        "type": "numeric",
        "required": False,
        "keywords": ["styling", "style", "topping", "top"],
        "patterns": [r"styling", r"style\s*time", r"topping\s*time"],
    },
    "oven_time": {
        "type": "numeric",
        "required": False,
        "keywords": ["oven", "cook", "cooking", "bake", "baking"],
        "patterns": [r"oven\s*time", r"cooking\s*time", r"cook\s*time", r"bake"],
    },
    "boxing_time": {
        "type": "numeric",
        "required": False,
        "keywords": ["box", "boxing", "pack", "packaging"],
        "patterns": [r"boxing", r"box\s*time", r"pack"],
    },
    "delivery_duration": {
        "type": "numeric",
        "required": False,
        "keywords": ["delivery", "deliver", "duration", "transit"],
        "patterns": [r"delivery\s*\(?mins?\)?", r"delivery\s*time", r"deliver\s*duration"],
    },
    "total_process_time": {
        "type": "numeric",
        "required": False,
        "keywords": ["total", "ord", "del", "process", "overall"],
        "patterns": [r"ord\s*-?\s*del", r"total\s*time", r"total\s*process", r"overall"],
    },

    # Order details
    "order_mode": {
        "type": "categorical",
        "required": False,
        "keywords": ["order", "mode", "channel", "source", "type"],
        "patterns": [r"order\s*mode", r"order\s*channel", r"order\s*type", r"order\s*source"],
    },
    "pizza_size": {
        "type": "categorical",
        "required": False,
        "keywords": ["size", "pizza"],
        "patterns": [r"size", r"pizza\s*size"],
    },
    "delivery_area": {
        "type": "categorical",
        "required": False,
        "keywords": ["area", "zone", "region", "location", "delivery"],
        "patterns": [r"area", r"zone", r"delivery\s*area", r"region"],
    },

    # Staff columns
    "order_taker": {
        "type": "categorical",
        "required": False,
        "keywords": ["order", "taker", "receiver", "intake"],
        "patterns": [r"order\s*taker", r"receiver"],
    },
    "dough_prep_staff": {
        "type": "categorical",
        "required": False,
        "keywords": ["dough", "prep", "staff", "maker"],
        "patterns": [r"dough\s*prep", r"dough\s*maker"],
    },
    "chef_name": {
        "type": "categorical",
        "required": False,
        "keywords": ["stylist", "chef", "cook", "topper"],
        "patterns": [r"stylist", r"chef", r"cook"],
    },
    "oven_operator": {
        "type": "categorical",
        "required": False,
        "keywords": ["oven", "operator", "baker"],
        "patterns": [r"oven", r"baker"],
    },
    "boxer": {
        "type": "categorical",
        "required": False,
        "keywords": ["boxer", "packer", "packaging"],
        "patterns": [r"boxer", r"packer"],
    },
    "driver_name": {
        "type": "categorical",
        "required": False,
        "keywords": ["driver", "deliverer", "delivery", "courier"],
        "patterns": [r"driver", r"deliverer", r"courier"],
    },

    # Quality columns
    "complaint": {
        "type": "boolean",
        "required": False,
        "keywords": ["complaint", "complain", "issue", "problem", "cust"],
        "patterns": [r"complaint", r"cust.*complaint", r"customer.*complaint"],
    },
    "complaint_reason": {
        "type": "categorical",
        "required": False,
        "keywords": ["reason", "complaint", "cause", "issue"],
        "patterns": [r"reason", r"complaint\s*reason", r"cause"],
    },

    # Equipment
    "oven_temperature": {
        "type": "numeric",
        "required": False,
        "keywords": ["oven", "temp", "temperature", "heat"],
        "patterns": [r"oven\s*temp", r"temperature"],
    },
}


class SchemaMapper:
    """
    Intelligent schema mapper that matches source columns to standard schema.

    Uses multiple matching strategies:
    1. Exact match (case-insensitive)
    2. Pattern matching (regex)
    3. Keyword matching (fuzzy)
    """

    def __init__(self, custom_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize schema mapper.

        Args:
            custom_mappings: Optional dict of {source_col: standard_col} for manual overrides
        """
        self.schema = STANDARD_SCHEMA
        self.custom_mappings = custom_mappings or {}
        self.mappings: List[ColumnMapping] = []

    def _normalize(self, text: str) -> str:
        """Normalize column name for matching."""
        # Convert to lowercase
        text = text.lower().strip()
        # Remove special characters except spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def _exact_match(self, source_col: str) -> Optional[Tuple[str, float]]:
        """Try exact match (case-insensitive, normalized)."""
        normalized = self._normalize(source_col)

        for standard_name in self.schema:
            if normalized == standard_name.replace('_', ' '):
                return standard_name, 1.0
        return None

    def _pattern_match(self, source_col: str) -> Optional[Tuple[str, float]]:
        """Try regex pattern matching."""
        normalized = self._normalize(source_col)

        best_match = None
        best_confidence = 0.0

        for standard_name, config in self.schema.items():
            for pattern in config.get("patterns", []):
                if re.search(pattern, normalized):
                    # Confidence based on pattern specificity
                    confidence = 0.9 if len(pattern) > 10 else 0.8
                    if confidence > best_confidence:
                        best_match = standard_name
                        best_confidence = confidence

        return (best_match, best_confidence) if best_match else None

    def _keyword_match(self, source_col: str) -> Optional[Tuple[str, float]]:
        """Try keyword-based fuzzy matching."""
        normalized = self._normalize(source_col)
        words = set(normalized.split())

        best_match = None
        best_score = 0.0

        for standard_name, config in self.schema.items():
            keywords = set(config.get("keywords", []))
            if not keywords:
                continue

            # Calculate overlap score
            overlap = len(words & keywords)
            if overlap > 0:
                score = overlap / max(len(words), len(keywords))
                # Boost score if multiple keywords match
                if overlap >= 2:
                    score = min(score + 0.1, 0.75)

                if score > best_score:
                    best_match = standard_name
                    best_score = score

        # Only return if confidence is reasonable
        return (best_match, best_score) if best_score >= 0.3 else None

    def map_column(self, source_col: str) -> Optional[ColumnMapping]:
        """
        Map a single source column to standard schema.

        Args:
            source_col: The source column name

        Returns:
            ColumnMapping if match found, None otherwise
        """
        # Check custom mappings first
        if source_col in self.custom_mappings:
            return ColumnMapping(
                source_name=source_col,
                standard_name=self.custom_mappings[source_col],
                confidence=1.0,
                match_type="manual"
            )

        # Try exact match
        result = self._exact_match(source_col)
        if result:
            return ColumnMapping(
                source_name=source_col,
                standard_name=result[0],
                confidence=result[1],
                match_type="exact"
            )

        # Try pattern match
        result = self._pattern_match(source_col)
        if result:
            return ColumnMapping(
                source_name=source_col,
                standard_name=result[0],
                confidence=result[1],
                match_type="pattern"
            )

        # Try keyword match
        result = self._keyword_match(source_col)
        if result:
            return ColumnMapping(
                source_name=source_col,
                standard_name=result[0],
                confidence=result[1],
                match_type="keyword"
            )

        return None

    def map_dataframe(self, columns: List[str]) -> Dict[str, ColumnMapping]:
        """
        Map all columns in a dataframe to standard schema.

        Args:
            columns: List of source column names

        Returns:
            Dict of {source_col: ColumnMapping}
        """
        mappings = {}
        used_standards = set()  # Track already-mapped standard names

        # First pass: high confidence matches
        for col in columns:
            mapping = self.map_column(col)
            if mapping and mapping.confidence >= 0.8:
                if mapping.standard_name not in used_standards:
                    mappings[col] = mapping
                    used_standards.add(mapping.standard_name)

        # Second pass: lower confidence matches for unmapped columns
        for col in columns:
            if col not in mappings:
                mapping = self.map_column(col)
                if mapping and mapping.standard_name not in used_standards:
                    mappings[col] = mapping
                    used_standards.add(mapping.standard_name)

        self.mappings = list(mappings.values())
        return mappings

    def get_rename_dict(self, columns: List[str]) -> Dict[str, str]:
        """
        Get a simple rename dictionary for pandas.

        Args:
            columns: List of source column names

        Returns:
            Dict of {source_col: standard_col} for renaming
        """
        mappings = self.map_dataframe(columns)
        return {
            source: mapping.standard_name
            for source, mapping in mappings.items()
        }

    def get_mapping_report(self, columns: List[str]) -> Dict:
        """
        Generate a detailed mapping report.

        Args:
            columns: List of source column names

        Returns:
            Dict with mapping statistics and details
        """
        mappings = self.map_dataframe(columns)

        mapped_cols = list(mappings.keys())
        unmapped_cols = [c for c in columns if c not in mappings]

        # Check for missing required columns
        mapped_standards = {m.standard_name for m in mappings.values()}
        missing_required = [
            name for name, config in self.schema.items()
            if config.get("required") and name not in mapped_standards
        ]

        return {
            "total_columns": len(columns),
            "mapped_columns": len(mapped_cols),
            "unmapped_columns": len(unmapped_cols),
            "mapping_rate": len(mapped_cols) / len(columns) if columns else 0,
            "mappings": [
                {
                    "source": m.source_name,
                    "target": m.standard_name,
                    "confidence": m.confidence,
                    "match_type": m.match_type,
                }
                for m in mappings.values()
            ],
            "unmapped": unmapped_cols,
            "missing_required": missing_required,
            "warnings": [
                f"Missing required column: {col}" for col in missing_required
            ],
        }


def auto_map_columns(df) -> Tuple[dict, dict]:
    """
    Convenience function to auto-map a dataframe's columns.

    Args:
        df: pandas DataFrame

    Returns:
        Tuple of (rename_dict, report_dict)
    """
    mapper = SchemaMapper()
    rename_dict = mapper.get_rename_dict(list(df.columns))
    report = mapper.get_mapping_report(list(df.columns))
    return rename_dict, report
