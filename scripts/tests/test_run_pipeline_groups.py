"""Tests for group matching and category export in the pipeline."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import run_pipeline


def test_tag_groups_matches_pi(monkeypatch):
    monkeypatch.setattr(run_pipeline, "load_all_groups", lambda: [
        {
            "name": "TU Darmstadt GLR",
            "institution": "Technical University of Darmstadt",
            "pis": ["Schiffer"],
            "aliases": [],
        }
    ])
    papers = [{"authors": ["H.-P. Schiffer"], "affiliations": []}]

    run_pipeline.tag_groups(papers)

    assert papers[0]["groups"] == ["TU Darmstadt GLR"]


def test_tag_groups_matches_affiliation_alias(monkeypatch):
    monkeypatch.setattr(run_pipeline, "load_all_groups", lambda: [
        {
            "name": "DLR",
            "institution": "German Aerospace Center",
            "pis": [],
            "aliases": ["German Aerospace Center", "Engine Acoustics Department"],
        }
    ])
    papers = [{
        "authors": ["A. Researcher"],
        "affiliations": ["Engine Acoustics Department, German Aerospace Center"],
    }]

    run_pipeline.tag_groups(papers)

    assert papers[0]["groups"] == ["DLR"]


def test_write_categories_exports_configured_labels(tmp_path, monkeypatch):
    monkeypatch.setattr(run_pipeline, "DATA_DIR", tmp_path)
    monkeypatch.setattr(run_pipeline, "CATEGORIES", ["非同步振动 NSV", "旋转不稳定性 RI"])

    run_pipeline.write_categories()

    data = json.loads((tmp_path / "categories.json").read_text(encoding="utf-8"))
    assert data == ["非同步振动 NSV", "旋转不稳定性 RI"]


def test_load_pipeline_keywords_merges_config_and_topics(tmp_path, monkeypatch):
    monkeypatch.setattr(run_pipeline, "DATA_DIR", tmp_path)
    monkeypatch.setattr(run_pipeline, "KEYWORDS", [
        "rotating instability",
        "non-synchronous vibration",
    ])
    (tmp_path / "topics.json").write_text(json.dumps([
        {"label": "自定义", "terms": ["rotating instability", "fan blade flutter"]},
    ], ensure_ascii=False), encoding="utf-8")

    keywords = run_pipeline.load_pipeline_keywords()

    assert keywords == [
        "rotating instability",
        "non-synchronous vibration",
        "fan blade flutter",
    ]
