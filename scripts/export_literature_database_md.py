"""
Export Research Radar local literature database documentation.

This script reads data/*.json and writes docs/literature-database.md.  The
generated Markdown is intended as a compact onboarding file for future Codex
sessions that need to search the already-collected literature before going to
the web.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_PATH = ROOT / "docs" / "literature-database.md"


CATEGORY_DESCRIPTIONS = {
    "旋转不稳定性 RI": (
        "轴流风扇、压气机中的 rotating instability、rotating instabilities、"
        "叶尖泄漏流诱导的周向非定常扰动、近失速旋转扰动和方位模态。"
    ),
    "非同步振动 NSV": (
        "nonsynchronous vibration、non-synchronous vibration、non-engine-order "
        "blade vibration、part-speed vibration、行波振动和节径相关叶片振动。"
    ),
    "RI-NSV机理": (
        "RI 扰动与叶片振动之间的耦合机制，包括气动激励频率、扰动传播速度、"
        "锁频、行波模态和叶片响应之间的关系。"
    ),
    "机匣处理与流动控制": (
        "casing treatment、casing groove、casing slot、shroud treatment、"
        "endwall treatment 等改变叶尖流动和近失速扰动的控制方式。"
    ),
    "叶片流致振动抑制/控制": (
        "叶片改型、气动或结构失谐、intentional mistuning、flutter margin 提升、"
        "振动抑制和流动-振动控制策略。"
    ),
    "声学诱导叶片振动": (
        "acoustic resonance、trapped acoustic modes、duct/intake acoustic modes、"
        "声反射、声衬和壁面声学阻抗对叶片振动的影响。"
    ),
    "风扇/压气机叶片气动弹性": (
        "fan/compressor blade aeroelasticity、flutter、forced response、"
        "aerodynamic damping、inter-blade phase angle、nodal diameter 等。"
    ),
    "叶片流致振动预测模型": (
        "NSV 半解析模型、降阶模型、线性模型、单自由度模型、Van der Pol 类模型、"
        "锁频预测和声学/气动弹性预测模型。"
    ),
    "实验测量": "级环境或叶栅实验、叶尖定时、非定常压力测量、应变测量、时间分辨测量和模态识别。",
    "数值仿真": "CFD、URANS、LES、大涡模拟、全环/扇区非定常模拟、流固耦合计算和参数扫描。",
    "解析/降阶模型": (
        "半解析模型、降阶模型、低阶模型、线性模型、Moore-Greitzer 类稳定性模型、"
        "叶尖泄漏流/叶尖涡模化和扰动传播速度模型。"
    ),
    "叶尖间隙": "tip clearance、tip leakage、tip leakage vortex、tip gap、叶尖泄漏流和叶尖间隙变化的影响。",
    "失速/喘振机理": (
        "rotating stall、stall inception、surge、stall margin、spike、modal wave、"
        "stall cell 和失速恢复。"
    ),
    "稳定性建模": (
        "actuator disk、body force model、throughflow、streamline curvature、"
        "Moore-Greitzer 和三维稳定性模型。"
    ),
    "畸变进气": "inlet distortion、circumferential distortion、radial distortion、total pressure distortion 和非均匀进气。",
    "其他": "与风扇、压气机、叶轮机械振动或稳定性有一定关系，但无法明确归入上述类别的论文。",
}


CURRENT_JOURNALS = [
    ("Journal of Turbomachinery", "0889-504X", "ASME 叶轮机械核心期刊。"),
    ("Journal of Engineering for Gas Turbines and Power", "0742-4795", "燃气轮机与推进系统期刊。"),
    ("Journal of Propulsion and Power", "0748-4658", "AIAA 推进期刊。"),
    ("AIAA Journal", "0001-1452", "航空航天综合基础期刊。"),
    ("Journal of Sound and Vibration", "0022-460X", "声学与振动核心期刊。"),
    ("Progress in Aerospace Sciences", "0376-0421", "航空航天综述期刊。"),
    ("Chinese Journal of Aeronautics", "1000-9361", "航空领域综合期刊。"),
    ("Journal of Fluid Mechanics", "0022-1120", "流体力学基础期刊。"),
    ("Applied Acoustics", "0003-682X", "应用声学期刊。"),
    ("Journal of Fluids and Structures", "0889-9746", "流固耦合与流致振动核心期刊。"),
]


HISTORICAL_JOURNALS = [
    ("Journal of Engineering for Power", "0022-0825", "Journal of Engineering for Gas Turbines and Power 的历史前身之一。"),
    ("Journal of Basic Engineering", "0021-9223", "ASME 早期基础工程期刊。"),
]


KEY_TARGET_TITLES = [
    "Non-synchronous vibration in axial compressors: Lock-in mechanism and semi-analytical model",
]


def load_json(name: str, fallback: Any) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value if v)
    text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("|", r"\|")


def year_of(paper: dict[str, Any]) -> str:
    year = paper.get("year")
    if year:
        return clean(year)
    date = str(paper.get("date") or "")
    return clean(date[:4]) if len(date) >= 4 else ""


def year_range(papers: list[dict[str, Any]]) -> str:
    years: list[int] = []
    for paper in papers:
        try:
            years.append(int(year_of(paper)))
        except ValueError:
            continue
    if not years:
        return ""
    return f"{min(years)}-{max(years)}"


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(cell) for cell in row) + " |")
    return "\n".join(lines)


def link(url: str) -> str:
    url = clean(url)
    if not url:
        return ""
    return f"[link]({url})"


def counts_table(counter: Counter[str], limit: int | None = None) -> str:
    rows = counter.most_common(limit)
    return table(["项目", "数量"], [[k or "(empty)", v] for k, v in rows])


def current_index_rows(papers: list[dict[str, Any]]) -> list[list[Any]]:
    ordered = sorted(papers, key=lambda p: (str(p.get("date") or ""), str(p.get("title") or "")), reverse=True)
    return [
        [
            year_of(paper),
            paper.get("venue", ""),
            paper.get("title", ""),
            paper.get("authors", []),
            paper.get("tags", []),
            paper.get("relevance", ""),
            link(paper.get("url", "")),
        ]
        for paper in ordered
    ]


def historical_index_rows(papers: list[dict[str, Any]]) -> list[list[Any]]:
    ordered = sorted(papers, key=lambda p: (year_of(p), str(p.get("date") or ""), str(p.get("title") or "")))
    return [
        [
            year_of(paper),
            paper.get("venue", ""),
            paper.get("title", ""),
            paper.get("authors", []),
            paper.get("topics_matched", []),
            link(paper.get("url", "")),
        ]
        for paper in ordered
    ]


def key_target_rows(papers: list[dict[str, Any]], historical: list[dict[str, Any]]) -> list[list[Any]]:
    all_papers = papers + historical
    rows = []
    for title in KEY_TARGET_TITLES:
        matches = [
            paper for paper in all_papers
            if clean(paper.get("title", "")).casefold() == title.casefold()
        ]
        if matches:
            paper = matches[0]
            rows.append([
                title,
                "已精确入库",
                year_of(paper),
                paper.get("venue", ""),
                link(paper.get("url", "")),
            ])
        else:
            rows.append([
                title,
                "未在当前 JSON 中精确命中；建议后续用 OpenAlex 或新增关键词复查",
                "",
                "",
                "",
            ])
    return rows


def main() -> None:
    papers = load_json("papers.json", [])
    historical = load_json("papers-historical.json", [])
    timeline = load_json("timeline.json", {})
    groups = load_json("groups.json", [])
    categories = load_json("categories.json", [])
    meta = load_json("meta.json", [])

    current_tags = Counter(tag for paper in papers for tag in paper.get("tags", []))
    historical_topics = Counter(topic for paper in historical for topic in paper.get("topics_matched", []))
    current_venues = Counter(paper.get("venue", "") for paper in papers)
    historical_venues = Counter(paper.get("venue", "") for paper in historical)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pipeline_time = meta[0].get("last_updated", "") if meta else ""
    timeline_time = timeline.get("generated_at", "") if isinstance(timeline, dict) else ""

    sections: list[str] = []
    sections.append("# Research Radar 文献数据库说明\n")
    sections.append(
        "本文档由 `scripts/export_literature_database_md.py` 生成，用于让新的 Codex 对话快速了解本仓库已经检索到的文献、"
        "数据结构和分类方式。进行文献调研时，应优先检索本文档和 `data/*.json`，再考虑联网补充。"
    )
    sections.append("\n## 数据库概况\n")
    sections.append(
        table(
            ["项目", "当前值"],
            [
                ["生成时间 UTC", generated_at],
                ["流水线更新时间", pipeline_time],
                ["Timeline 生成时间", timeline_time],
                ["当前论文数量", len(papers)],
                ["历史论文数量", len(historical)],
                ["当前论文年份范围", year_range(papers)],
                ["历史论文年份范围", year_range(historical)],
                ["分类数量", len(categories)],
                ["研究组数量", len(groups)],
                ["当前论文数据源", "OpenAlex + DeepSeek"],
                ["历史论文数据源", "OpenAlex"],
            ],
        )
    )

    sections.append("\n## 数据文件结构\n")
    sections.append(
        table(
            ["文件", "用途", "主要字段"],
            [
                [
                    "data/papers.json",
                    "2015 年至今论文；包含 DeepSeek 分析结果和 Papers 页面显示所需字段。",
                    "id, title, abstract, authors, affiliations, date, year, venue, url, tags, relevance, relevance_reason, summary_zh, method, innovation, conclusions, limitations, groups",
                ],
                [
                    "data/papers-historical.json",
                    "历史论文；用于 Timeline 和历史背景检索。",
                    "id, title, abstract, authors, affiliations, date, year, venue, url, keywords, topics_matched",
                ],
                ["data/timeline.json", "按话题和 5 年时间段统计论文，并保存 AI 综述。", "generated_at, periods, topics"],
                ["data/groups.json", "按研究组聚合论文数量和相关论文。", "name, institution, papers, count"],
                ["data/categories.json", "Papers Filter 固定分类。", "分类名称列表"],
                ["data/meta.json", "流水线更新时间。", "last_updated"],
            ],
        )
    )

    sections.append("\n## 分类方式\n")
    sections.append(
        table(
            ["分类", "说明"],
            [[category, CATEGORY_DESCRIPTIONS.get(category, "")] for category in categories],
        )
    )

    sections.append("\n## 当前检索期刊范围\n")
    sections.append("当前论文库使用当前监控期刊，抓取 2015 年至今；历史论文库使用当前监控期刊加历史补充期刊。OpenAlex 过滤字段为 `locations.source.issn`。")
    sections.append("\n### 当前监控期刊\n")
    sections.append(table(["期刊", "ISSN", "说明"], CURRENT_JOURNALS))
    sections.append("\n### 历史补充期刊\n")
    sections.append(table(["期刊", "ISSN", "说明"], HISTORICAL_JOURNALS))

    sections.append("\n## 统计分布\n")
    sections.append("\n### 当前论文标签统计\n")
    sections.append(counts_table(current_tags))
    sections.append("\n### 历史论文话题统计\n")
    sections.append(counts_table(historical_topics))
    sections.append("\n### 当前论文期刊统计\n")
    sections.append(counts_table(current_venues))
    sections.append("\n### 历史论文期刊统计\n")
    sections.append(counts_table(historical_venues))

    sections.append("\n## 检索建议\n")
    sections.append(
        "- 优先用标题、摘要、`tags`、`topics_matched`、`relevance_reason` 进行本地检索。\n"
        "- 查当前论文的 AI 摘要、方法、创新点和相关性理由时读取 `data/papers.json`。\n"
        "- 查 2014 年及以前的背景文献和 Timeline 话题时读取 `data/papers-historical.json`。\n"
        "- ASME 等网页缺少可直接联网获取的摘要时，优先使用本地 JSON 已保存的 OpenAlex 摘要。\n"
        "- 经典 NSV 预测模型可检索 `lock-in mechanism`、`semi-analytical model`、`non-synchronous vibration in axial compressors`。"
    )

    sections.append("\n## 关键检索目标与缺口\n")
    sections.append(
        "本节列出对当前课题很重要、但需要特别核对是否已经进入本地数据库的目标文献。"
        "状态由脚本按标题精确匹配 `papers.json` 和 `papers-historical.json` 得到。"
    )
    sections.append(table(["目标文献", "状态", "Year", "Venue", "URL"], key_target_rows(papers, historical)))

    sections.append("\n## 当前论文完整索引\n")
    sections.append(
        table(
            ["Year", "Venue", "Title", "Authors", "Tags", "Relevance", "URL"],
            current_index_rows(papers),
        )
    )

    sections.append("\n## 历史论文完整索引\n")
    sections.append(
        table(
            ["Year", "Venue", "Title", "Authors", "Topics", "URL"],
            historical_index_rows(historical),
        )
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} with {len(papers)} current papers and {len(historical)} historical papers.")


if __name__ == "__main__":
    main()
