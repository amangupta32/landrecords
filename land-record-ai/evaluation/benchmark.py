"""Benchmark runner for automated OCR & field extraction evaluation."""

import json
import os
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from evaluation.metrics import calculate_cer, calculate_field_f1, calculate_wer


class BenchmarkSample(BaseModel):
    """Single benchmark ground-truth test case."""
    sample_id: str
    image_path: Optional[str] = None
    ground_truth_text: str
    ground_truth_fields: Dict[str, Any] = Field(default_factory=dict)


class BenchmarkSummary(BaseModel):
    """Consolidated benchmark run summary metrics."""
    total_samples: int
    average_cer: float
    average_wer: float
    field_precision: float
    field_recall: float
    field_f1: float
    average_latency_ms: float
    details: List[Dict[str, Any]] = Field(default_factory=list)


class BenchmarkRunner:
    """Runs automated benchmarks over sample land record datasets."""

    def __init__(self, samples: Optional[List[BenchmarkSample]] = None):
        self.samples = samples or self._create_default_benchmark_samples()

    def _create_default_benchmark_samples(self) -> List[BenchmarkSample]:
        """Provides default synthetic ground-truth benchmark suite for test reproducibility."""
        return [
            BenchmarkSample(
                sample_id="sample_jamabandi_up_01",
                ground_truth_text="अधिकार अभिलेख (जमाबंदी) वर्ष: 2024 ग्राम: रामपुर तहसील: रामपुर तहसील जिला: रामपुर राज्य: उत्तर प्रदेश खसरा संख्या: 245/1 खाता संख्या: 89 खाता धारक का नाम: रमेश कुमार शर्मा पिता का नाम: हरीश चंद्र शर्मा कुल क्षेत्रफल: 4.25 एकड़ उत्परिवर्तन क्रमांक: MUT-2023-882",
                ground_truth_fields={
                    "khasra_number": "245/1",
                    "khata_number": "89",
                    "owner_name": "Ramesh Kumar Sharma",
                    "land_area": 4.25,
                    "village": "Rampur",
                    "mutation_ref": "MUT-2023-882"
                }
            ),
            BenchmarkSample(
                sample_id="sample_mutation_up_02",
                ground_truth_text="दाखिल खारिज नामांतरण पंजी: MUT-2022-104 दिनांक: 10/06/2022 ग्राम: चांदपुर तहसील: रामपुर तहसील जिला: रामपुर खसरा संख्या: 118 खाता संख्या: 42 खातेदार का नाम: प्रिया देवी पति का नाम: महेश सिंह क्षेत्रफल: 2.50 हेक्टेयर",
                ground_truth_fields={
                    "khasra_number": "118",
                    "khata_number": "42",
                    "owner_name": "Priya Devi",
                    "land_area": 2.50,
                    "village": "Chandpur",
                    "mutation_ref": "MUT-2022-104"
                }
            )
        ]

    def evaluate_predictions(
        self,
        predictions: List[Dict[str, Any]]  # List of dicts with {"sample_id", "text", "fields", "latency_ms"}
    ) -> BenchmarkSummary:
        """Evaluate predictions against ground-truth samples."""
        pred_map = {p["sample_id"]: p for p in predictions}
        
        cer_list = []
        wer_list = []
        f1_list = []
        prec_list = []
        rec_list = []
        latency_list = []
        details = []

        for sample in self.samples:
            pred = pred_map.get(sample.sample_id, {})
            pred_text = pred.get("text", "")
            pred_fields = pred.get("fields", {})
            lat = pred.get("latency_ms", 50.0)

            cer = calculate_cer(sample.ground_truth_text, pred_text)
            wer = calculate_wer(sample.ground_truth_text, pred_text)
            f1_res = calculate_field_f1(sample.ground_truth_fields, pred_fields)

            cer_list.append(cer)
            wer_list.append(wer)
            f1_list.append(f1_res["f1"])
            prec_list.append(f1_res["precision"])
            rec_list.append(f1_res["recall"])
            latency_list.append(lat)

            details.append({
                "sample_id": sample.sample_id,
                "cer": cer,
                "wer": wer,
                "f1": f1_res["f1"],
                "precision": f1_res["precision"],
                "recall": f1_res["recall"],
                "latency_ms": lat
            })

        n = len(self.samples)
        return BenchmarkSummary(
            total_samples=n,
            average_cer=round(sum(cer_list) / n, 4) if n else 0.0,
            average_wer=round(sum(wer_list) / n, 4) if n else 0.0,
            field_precision=round(sum(prec_list) / n, 4) if n else 0.0,
            field_recall=round(sum(rec_list) / n, 4) if n else 0.0,
            field_f1=round(sum(f1_list) / n, 4) if n else 0.0,
            average_latency_ms=round(sum(latency_list) / n, 2) if n else 0.0,
            details=details
        )
