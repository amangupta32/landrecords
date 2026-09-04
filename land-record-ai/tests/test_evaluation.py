"""Unit tests for Evaluation metrics and benchmark runner."""

import pytest
from evaluation.benchmark import BenchmarkRunner, BenchmarkSample
from evaluation.metrics import calculate_cer, calculate_field_f1, calculate_wer, levenshtein_distance


class TestEvaluationMetrics:
    def test_levenshtein_distance_exact(self):
        assert levenshtein_distance("खसरा", "खसरा") == 0

    def test_levenshtein_distance_edit(self):
        assert levenshtein_distance("kitten", "sitting") == 3

    def test_calculate_cer_exact(self):
        assert calculate_cer("खसरा संख्या 245/1", "खसरा संख्या 245/1") == 0.0

    def test_calculate_cer_substitution(self):
        cer = calculate_cer("खसरा 245", "खसरा 246")
        assert 0.0 < cer < 0.3

    def test_calculate_wer_exact(self):
        assert calculate_wer("खसरा संख्या 245/1", "खसरा संख्या 245/1") == 0.0

    def test_calculate_wer_single_word_diff(self):
        wer = calculate_wer("Khasra No 245/1", "Khasra No 245/2")
        assert wer == round(1.0 / 3.0, 4)

    def test_field_f1_perfect(self):
        gt = {"khasra": "245/1", "owner": "Ramesh"}
        pred = {"khasra": "245/1", "owner": "Ramesh"}
        res = calculate_field_f1(gt, pred)
        assert res["f1"] == 1.0
        assert res["precision"] == 1.0
        assert res["recall"] == 1.0

    def test_field_f1_partial(self):
        gt = {"khasra": "245/1", "owner": "Ramesh", "area": "4.25"}
        pred = {"khasra": "245/1", "owner": "Suresh"}
        res = calculate_field_f1(gt, pred)
        assert 0.0 < res["f1"] < 1.0


class TestBenchmarkRunner:
    def test_benchmark_runner_evaluation(self):
        runner = BenchmarkRunner()
        preds = [
            {
                "sample_id": "sample_jamabandi_up_01",
                "text": "अधिकार अभिलेख (जमाबंदी) वर्ष: 2024 ग्राम: रामपुर तहसील: रामपुर तहसील जिला: रामपुर राज्य: उत्तर प्रदेश खसरा संख्या: 245/1 खाता संख्या: 89 खाता धारक का नाम: रमेश कुमार शर्मा पिता का नाम: हरीश चंद्र शर्मा कुल क्षेत्रफल: 4.25 एकड़ उत्परिवर्तन क्रमांक: MUT-2023-882",
                "fields": {
                    "khasra_number": "245/1",
                    "khata_number": "89",
                    "owner_name": "Ramesh Kumar Sharma",
                    "land_area": 4.25,
                    "village": "Rampur",
                    "mutation_ref": "MUT-2023-882"
                },
                "latency_ms": 35.0
            },
            {
                "sample_id": "sample_mutation_up_02",
                "text": "दाखिल खारिज नामांतरण पंजी: MUT-2022-104 दिनांक: 10/06/2022 ग्राम: चांदपुर तहसील: रामपुर तहसील जिला: रामपुर खसरा संख्या: 118 खाता संख्या: 42 खातेदार का नाम: प्रिया देवी पति का नाम: महेश सिंह क्षेत्रफल: 2.50 हेक्टेयर",
                "fields": {
                    "khasra_number": "118",
                    "khata_number": "42",
                    "owner_name": "Priya Devi",
                    "land_area": 2.50,
                    "village": "Chandpur",
                    "mutation_ref": "MUT-2022-104"
                },
                "latency_ms": 40.0
            }
        ]

        summary = runner.evaluate_predictions(preds)
        assert summary.total_samples == 2
        assert summary.average_cer == 0.0
        assert summary.field_f1 == 1.0
        assert summary.average_latency_ms < 100.0
