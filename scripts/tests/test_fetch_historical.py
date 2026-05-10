"""Tests for fetch_papers_historical utility functions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fetch_papers_historical import DEFAULT_TOPICS, matches_topic, compute_topics_matched, reconstruct_abstract


def test_matches_topic_title():
    paper = {"title": "Casing Treatment Stall Margin Improvement", "abstract": "", "keywords": []}
    assert matches_topic(paper, ["casing treatment"]) is True


def test_matches_topic_abstract():
    paper = {"title": "Compressor study", "abstract": "tip clearance effect on stage efficiency", "keywords": []}
    assert matches_topic(paper, ["tip clearance effect"]) is True


def test_matches_topic_keywords():
    paper = {"title": "Axial compressor", "abstract": "stability analysis", "keywords": ["compressor surge"]}
    assert matches_topic(paper, ["compressor surge"]) is True


def test_matches_topic_case_insensitive():
    paper = {"title": "INLET DISTORTION COMPRESSOR STUDY", "abstract": "", "keywords": []}
    assert matches_topic(paper, ["inlet distortion compressor"]) is True


def test_matches_topic_no_match():
    paper = {"title": "Heat exchanger design", "abstract": "thermal hydraulics", "keywords": []}
    assert matches_topic(paper, ["tip clearance", "casing treatment"]) is False


def test_compute_topics_matched_single():
    paper = {"title": "Casing treatment stall margin", "abstract": "", "keywords": []}
    topics = [
        {"label": "机匣处理", "terms": ["casing treatment"]},
        {"label": "叶尖间隙", "terms": ["tip clearance"]},
    ]
    result = compute_topics_matched(paper, topics)
    assert result == ["机匣处理"]


def test_compute_topics_matched_multiple():
    paper = {"title": "tip clearance casing treatment effects", "abstract": "", "keywords": []}
    topics = [
        {"label": "机匣处理", "terms": ["casing treatment"]},
        {"label": "叶尖间隙", "terms": ["tip clearance"]},
    ]
    result = compute_topics_matched(paper, topics)
    assert set(result) == {"机匣处理", "叶尖间隙"}


def test_new_default_topics_match_requested_areas():
    topic_labels = {t["label"] for t in DEFAULT_TOPICS}
    assert "非同步振动 NSV" in topic_labels
    assert "气动弹性" in topic_labels
    assert "转子振动控制" in topic_labels
    assert "旋转流动不稳定性 RI" in topic_labels
    assert "转子叶片振动预测解析模型" in topic_labels

    paper = {
        "title": "Nonsynchronous vibration and rotating instability in a transonic compressor",
        "abstract": "An aeroelastic reduced order model predicts rotor blade vibration.",
        "keywords": ["flutter", "harmonic balance"],
    }
    result = set(compute_topics_matched(paper, DEFAULT_TOPICS))
    assert "非同步振动 NSV" in result
    assert "气动弹性" in result
    assert "旋转流动不稳定性 RI" in result
    assert "转子叶片振动预测解析模型" in result


def test_reconstruct_abstract_empty():
    assert reconstruct_abstract(None) == ""
    assert reconstruct_abstract({}) == ""


def test_reconstruct_abstract():
    inv = {"Hello": [0], "world": [1]}
    result = reconstruct_abstract(inv)
    assert result == "Hello world"
