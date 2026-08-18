"""Unit tests for training metrics calculation."""
import os
import sys
import numpy as np
import pytest

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from training.metrics import compute_accuracy, compute_precision_recall_f1, compute_metrics

def test_compute_accuracy():
    preds = np.array([0, 1, 2, 1])
    targets = np.array([0, 1, 2, 0])
    acc = compute_accuracy(preds, targets)
    assert acc == 0.75

def test_compute_precision_recall_f1():
    preds = np.array([0, 1, 2, 0])
    targets = np.array([0, 1, 2, 0])
    prec, rec, f1 = compute_precision_recall_f1(preds, targets, num_classes=3)
    assert prec == 1.0
    assert rec == 1.0
    assert f1 == 1.0

def test_compute_metrics_dictionary():
    metrics = compute_metrics(
        loss=0.45,
        accuracy=0.85,
        total_samples=100,
        precision=0.82,
        recall=0.84,
        f1_score=0.83,
    )
    assert metrics["loss"] == 0.45
    assert metrics["accuracy"] == 0.85
    assert metrics["num_samples"] == 100
    assert metrics["precision"] == 0.82
    assert metrics["recall"] == 0.84
    assert metrics["f1_score"] == 0.83
