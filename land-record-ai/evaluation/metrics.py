"""Evaluation metrics: Character Error Rate (CER), Word Error Rate (WER), and Field F1."""

from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple, Union


def levenshtein_distance(seq1: Union[str, List[str]], seq2: Union[str, List[str]]) -> int:
    """Compute Levenshtein edit distance between two sequences (chars or words)."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )

    return dp[m][n]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Compute Character Error Rate: CER = Levenshtein(ref, hyp) / len(ref).
    Returns 0.0 for exact match, clamped to max 1.0.
    """
    ref_clean = reference.strip()
    hyp_clean = hypothesis.strip()

    if not ref_clean and not hyp_clean:
        return 0.0
    if not ref_clean:
        return 1.0

    dist = levenshtein_distance(ref_clean, hyp_clean)
    cer = dist / len(ref_clean)
    return round(float(min(1.0, cer)), 4)


def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Compute Word Error Rate: WER = Levenshtein_words(ref, hyp) / len(ref_words).
    """
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()

    if not ref_words and not hyp_words:
        return 0.0
    if not ref_words:
        return 1.0

    dist = levenshtein_distance(ref_words, hyp_words)
    wer = dist / len(ref_words)
    return round(float(min(1.0, wer)), 4)


def calculate_field_f1(
    ground_truth: Dict[str, Any],
    predictions: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calculate Precision, Recall, and F1-score for extracted fields.
    """
    tp = 0
    fp = 0
    fn = 0

    all_keys = set(ground_truth.keys()).union(set(predictions.keys()))

    for key in all_keys:
        gt_val = ground_truth.get(key)
        pred_val = predictions.get(key)

        if gt_val is not None and pred_val is not None:
            # Check match
            gt_str = str(gt_val).strip().lower()
            pred_str = str(pred_val).strip().lower()
            if gt_str == pred_str or gt_str in pred_str or pred_str in gt_str:
                tp += 1
            else:
                fp += 1
                fn += 1
        elif gt_val is not None and pred_val is None:
            fn += 1
        elif gt_val is None and pred_val is not None:
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if fn == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn
    }
