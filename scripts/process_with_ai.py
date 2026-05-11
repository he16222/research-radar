"""
process_with_ai.py
调用 DeepSeek API 对论文做深度分析：
- 有全文 PDF：基于全文提取摘要、研究方法、创新点、主要结论、局限性
- 仅有摘要：从摘要尽量推断上述内容
"""

import os
import io
import json
import time
import logging
import requests
from typing import Optional
from openai import OpenAI
from config import CATEGORIES, MIN_RELEVANCE

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

TAG_ALIASES = {
    "ri-nsv 机理": "RI-NSV机理",
    "ri-nsv机理": "RI-NSV机理",
    "ri/nsv机理": "RI-NSV机理",
    "ri-nsv mechanism": "RI-NSV机理",
}
VALID_CATEGORIES = set(CATEGORIES)


def normalize_tag(tag: str) -> str:
    """Normalize historical and model-generated tag variants to canonical names."""
    text = str(tag or "").strip()
    if not text:
        return ""
    return TAG_ALIASES.get(text.casefold(), text)


def normalize_tags(tags) -> list[str]:
    """Normalize, deduplicate, and constrain AI tags to configured categories."""
    if isinstance(tags, list):
        raw_tags = tags
    elif tags:
        raw_tags = [tags]
    else:
        raw_tags = []

    result: list[str] = []
    seen: set[str] = set()
    for tag in raw_tags:
        normalized = normalize_tag(tag)
        if not normalized:
            continue
        if normalized not in VALID_CATEGORIES:
            normalized = "其他"
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    if not result:
        result.append("其他")
    return result[:3]

# ─────────────────────────────────────────────
#  DeepSeek 客户端
# ─────────────────────────────────────────────

def get_client() -> OpenAI:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("请设置环境变量 DEEPSEEK_API_KEY")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# ─────────────────────────────────────────────
#  PDF 全文提取
# ─────────────────────────────────────────────

def fetch_pdf_text(pdf_url: str, max_chars: int = 12000) -> str:
    """下载 PDF 并提取文本，返回前 max_chars 字符（含引言和结论区域）"""
    if not HAS_PDF or not pdf_url:
        return ""
    try:
        resp = requests.get(pdf_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return ""
        with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
            pages = pdf.pages
            # 优先提取：前3页（引言/方法）+ 最后2页（结论）
            target = list(pages[:3]) + list(pages[-2:]) if len(pages) > 5 else list(pages)
            text = "\n".join(p.extract_text() or "" for p in target)
        return text[:max_chars].strip()
    except Exception as e:
        log.debug(f"PDF 提取失败: {e}")
        return ""


# ─────────────────────────────────────────────
#  Prompt 模板
# ─────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """你是一个航空发动机风扇/压气机非定常气动、气动弹性与叶片振动领域的资深研究助手。
用户课题核心：风扇/压气机中旋转不稳定性 RI 导致的非同步振动 NSV，以及基于机匣处理、叶片改型、失谐、声学阻抗调控等方式的流动-振动控制；重点使用实验测量、数值仿真、解析/降阶模型研究 RI-NSV机理、预测与控制。
评分时优先判断论文与 RI-NSV机理、预测或控制的关系，不要沿用叶尖畸变下稳定裕度作为核心标准。
只输出 JSON，不要有任何其他文字或 markdown 代码块。"""

RELEVANCE_GUIDE = """relevance 评分标准：
5=直接研究 RI 导致 NSV，或 RI-NSV 预测、机理、控制；
4=研究 NSV、rotating instability、声学诱导叶片振动、风扇/压气机颤振、流致振动控制；
3=研究叶尖泄漏流、机匣处理、近失速扰动、气动弹性、强迫响应，但未直接连接 NSV；
2=泛化叶片振动、失谐、声学处理、流固耦合、转子动力学，与风扇/压气机流致振动有参考价值；
1=普通稳定性、普通结构振动、非叶轮机械对象；
0=无关。
relevance_reason 必须用一句话说明论文与 RI-NSV机理、预测或控制的关系。"""
RELEVANCE_GUIDE += """
“解析/降阶模型”包括半解析模型、降阶模型、低阶模型、线性模型、Van der Pol 类模型、叶尖泄漏流/叶尖涡模化、锁频与扰动传播速度预测模型。"""

def build_system_prompt(annotations: dict) -> str:
    """将用户历史标注整合进系统 prompt，形成个性化偏好记忆"""
    if not annotations:
        return BASE_SYSTEM_PROMPT
    notes = [f"- {v['note']}" for v in annotations.values() if v.get("note")]
    if not notes:
        return BASE_SYSTEM_PROMPT
    notes_text = "\n".join(notes[:20])  # 最多取 20 条
    return BASE_SYSTEM_PROMPT + f"""

用户过往评价记录（请据此校准相关度判断）：
{notes_text}"""

# 有全文时使用
FULLTEXT_TEMPLATE = """请基于以下论文全文进行深度分析：

标题：{title}
全文节选（引言 + 结论）：
{text}

返回以下 JSON（字段全部必填，不能为空字符串）：
{{
  "summary_zh": "100~150字中文综述，涵盖研究背景、方法和主要发现",
  "method": "40~70字，描述核心研究手段（数值模拟/实验/理论推导等）及关键参数",
  "innovation": "40~70字，与前人工作相比的核心创新点，尽量具体",
  "conclusions": "50~80字，列出2~3条最重要的定量或定性结论",
  "limitations": "20~40字，论文的主要局限或未来工作方向",
  "tags": ["标签1", "标签2"],
  "relevance": 3,
  "relevance_reason": "一句话说明评分理由"
}}

tags 从以下列表中选 1~3 个：{categories}
{relevance_guide}"""

# 仅有摘要时使用
ABSTRACT_TEMPLATE = """请基于以下论文摘要进行尽可能详尽的分析（无法获取全文，请从摘要最大化提取信息）：

标题：{title}
摘要：{abstract}

返回以下 JSON（字段全部必填，如摘要信息不足则基于领域知识合理推断，不能留空）：
{{
  "summary_zh": "80~120字中文综述，突出研究对象、方法和核心发现",
  "method": "30~60字，从摘要推断研究方法（数值/实验/理论）及主要工况参数",
  "innovation": "30~60字，与同类研究相比的创新点，如摘要未明确则推断",
  "conclusions": "40~70字，列出1~2条关键结论，尽量包含定量数据",
  "limitations": "20~40字，基于研究范围推断可能的局限",
  "tags": ["标签1", "标签2"],
  "relevance": 3,
  "relevance_reason": "一句话说明评分理由"
}}

tags 从以下列表中选 1~3 个：{categories}
{relevance_guide}"""


# ─────────────────────────────────────────────
#  单篇处理
# ─────────────────────────────────────────────

def load_annotations(data_dir: str = None) -> dict:
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    path = os.path.join(data_dir, 'annotations.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}


def process_one(
    client: OpenAI,
    title: str,
    abstract: str,
    pdf_url: str = "",
    system_prompt: str = None,
    retries: int = 3,
) -> Optional[dict]:
    # 尝试获取全文
    full_text = fetch_pdf_text(pdf_url) if pdf_url else ""
    has_fulltext = bool(full_text)

    if has_fulltext:
        prompt = FULLTEXT_TEMPLATE.format(
            title=title,
            text=full_text,
            categories="、".join(CATEGORIES),
            relevance_guide=RELEVANCE_GUIDE,
        )
        log.debug(f"  [全文模式] {title[:40]}")
    else:
        prompt = ABSTRACT_TEMPLATE.format(
            title=title,
            abstract=abstract[:3000],
            categories="、".join(CATEGORIES),
            relevance_guide=RELEVANCE_GUIDE,
        )

    if system_prompt is None:
        system_prompt = BASE_SYSTEM_PROMPT

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=800,
            )
            raw = resp.choices[0].message.content.strip()
            result = json.loads(raw)

            for field in ("summary_zh", "method", "innovation", "conclusions",
                          "limitations", "tags", "relevance"):
                assert field in result, f"缺少 {field}"

            result["tags"] = normalize_tags(result.get("tags", []))
            result["has_fulltext"] = has_fulltext
            return result

        except json.JSONDecodeError as e:
            log.warning(f"JSON 解析失败（第{attempt+1}次）: {e}")
        except AssertionError as e:
            log.warning(f"字段校验失败（第{attempt+1}次）: {e}")
        except Exception as e:
            log.warning(f"API 调用失败（第{attempt+1}次）: {e}")

        if attempt < retries - 1:
            time.sleep(2 ** attempt)

    log.error(f"论文处理彻底失败，跳过：{title[:60]}")
    return None


# ─────────────────────────────────────────────
#  批量处理
# ─────────────────────────────────────────────

def process_papers(
    raw_papers: list[dict],
    existing_ids: set[str],
    max_workers: int = 5,
) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    client      = get_client()
    annotations = load_annotations()
    sys_prompt  = build_system_prompt(annotations)
    if annotations:
        log.info(f"已加载 {len(annotations)} 条用户标注作为 AI 参考上下文")

    new_papers = [p for p in raw_papers if p["id"] not in existing_ids]
    skipped    = len(raw_papers) - len(new_papers)
    log.info(f"需处理 {len(new_papers)} 篇新论文（跳过 {skipped} 篇已存在），并发数 {max_workers}")

    def _process(paper: dict):
        return paper, process_one(
            client,
            paper["title"],
            paper["abstract"],
            pdf_url=paper.get("pdf_url", ""),
            system_prompt=sys_prompt,
        )

    results: list[dict] = []
    filtered = 0
    fulltext_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process, p): p for p in new_papers}
        done = 0
        for future in as_completed(futures):
            done += 1
            paper, ai = future.result()
            if ai is None:
                continue
            relevance = int(ai.get("relevance", 0))
            if relevance < MIN_RELEVANCE:
                filtered += 1
                log.info(f"[{done}/{len(new_papers)}] 相关度 {relevance}，过滤：{paper['title'][:50]}")
                continue
            if ai.get("has_fulltext"):
                fulltext_count += 1
            enriched = {**paper, **ai}
            results.append(enriched)
            log.info(f"[{done}/{len(new_papers)}] 相关度 {relevance}，{'全文' if ai.get('has_fulltext') else '摘要'}，标签：{ai.get('tags')} — {paper['title'][:50]}")

    log.info(
        f"处理完成：{len(results)} 篇入库（其中 {fulltext_count} 篇全文分析），"
        f"{skipped} 篇已存在，{filtered} 篇低相关度过滤"
    )
    # ASCII 统计行，供前端解析（中文字符在 Windows 下可能乱码）
    print(f"[STATS] new={len(results)} skipped={skipped} filtered={filtered}", flush=True)
    return results


# ─────────────────────────────────────────────
#  主入口（独立测试用）
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("../.env")
    client = get_client()
    result = process_one(
        client,
        "Effects of Non-Axisymmetric Tip Clearance on Compressor Stability",
        "This paper investigates the influence of circumferential tip clearance distortion "
        "on the stall margin of an axial compressor using full-annulus unsteady simulations.",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
