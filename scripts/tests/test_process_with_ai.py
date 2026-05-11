"""Tests for AI tag normalization helpers."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from process_with_ai import normalize_tags


def test_normalize_tags_unifies_ri_nsv_aliases():
    assert normalize_tags(["RI-NSV 机理", "RI-NSV机理", "RI/NSV机理"]) == ["RI-NSV机理"]


def test_normalize_tags_maps_unknown_to_other():
    assert normalize_tags(["unconfigured tag"]) == ["其他"]


def test_normalize_tags_keeps_configured_labels():
    assert normalize_tags(["非同步振动 NSV", "解析/降阶模型"]) == ["非同步振动 NSV", "解析/降阶模型"]
