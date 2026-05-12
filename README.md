# Research Radar

**面向特定研究方向的文献追踪网站**：按期刊和关键词从 OpenAlex 抓取论文，使用 DeepSeek 生成中文摘要、方法、创新点、结论、相关度评分和分类标签，并在 GitHub Pages 上展示 Papers、Groups、Timeline 和 AI Chat。

本仓库基于 `treeEnergy/research-radar` 修改，当前配置面向以下课题：

> 风扇/压气机中旋转不稳定性 RI 导致的非同步振动 NSV，以及基于机匣处理、叶片改型、失谐、声学阻抗调控等方式的流动-振动控制；重点使用实验测量、数值仿真、解析/降阶模型研究 RI-NSV机理、预测与控制。

访问地址：

`https://he16222.github.io/research-radar/`

---

## 功能

- 双主题网页界面，支持 Papers、Groups、Timeline、AI Chat、标注和愿望清单。
- 从 OpenAlex 按 `关键词 × 期刊 ISSN` 抓取论文，当前配置为 92 个论文检索关键词、10 本当前监控期刊和 2 本历史前身期刊。
- DeepSeek 对新论文生成中文综述、研究方法、创新点、主要结论、局限性、分类标签、`relevance` 和 `relevance_reason`。
- Papers Filter 固定读取 `data/categories.json`，当前包含 16 个分类标签。
- Groups 页面根据作者姓名和 OpenAlex 单位信息匹配课题组，当前配置 32 个研究组。
- Timeline 使用 15 个默认研究话题，按 5 年时间段统计并生成 AI 综述。
- GitHub Actions 每周自动运行，也支持 Actions 页面手动触发和网页按钮触发。
- 网页端 AI Chat 使用浏览器 localStorage 中的 DeepSeek API Key，不经过项目后端服务器。

---

## 当前数据状态

数据文件由 GitHub Actions 流水线生成并提交回仓库。

当前仓库包含最近一次 `Research Radar Pipeline` 生成的数据文件：

- `data/papers.json`
- `data/papers-historical.json`
- `data/timeline.json`
- `data/groups.json`
- `data/repos.json`
- `data/meta.json`

克隆仓库后可以直接读取这些静态数据。修改检索方向、期刊范围或分类体系后，需要重新运行 `Research Radar Pipeline` 才能让数据和页面同步更新。全量重建会重新调用 DeepSeek，仓库的 `Actions secrets` 或本地环境变量中必须配置 `DEEPSEEK_API_KEY`。

---

## 本地安装与使用

本项目是静态网页加 Python 数据流水线。只浏览现有数据时，本地不需要数据库和后端服务；需要重新抓取和分析论文时，才需要配置 Python 环境和 DeepSeek API Key。

### 1. 克隆仓库

```bash
git clone https://github.com/he16222/research-radar.git
cd research-radar
```

### 2. 创建 Python 环境

建议使用 Python 3.11。Windows PowerShell 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r scripts\requirements.txt
```

macOS 或 Linux 示例：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

### 3. 本地打开网页

不要直接双击 `index.html`，因为浏览器在 `file://` 模式下可能阻止读取 `data/*.json`。建议在仓库根目录启动本地静态服务器：

```bash
python -m http.server 8000
```

然后在浏览器打开：

```text
http://localhost:8000
```

此时网页会读取本地 `data/*.json`。如果这些文件已经包含数据，Papers、Groups 和 Timeline 可以直接浏览。

### 4. 本地运行论文更新流水线

需要重新检索论文、调用 DeepSeek 生成中文摘要和评分时，先设置 `DEEPSEEK_API_KEY`。

Windows PowerShell：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
cd scripts
python run_pipeline.py
```

macOS 或 Linux：

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
cd scripts
python run_pipeline.py
```

流水线会更新仓库根目录下的 `data/*.json`。本地运行产生的数据只保存在本机，提交和推送后才会同步到 GitHub Pages。

### 5. 本地个性化修改

常见修改位置：

- `scripts/config.py`：修改检索关键词、监控期刊、分类标签和研究组。
- `data/topics.json`：网页同步出来的自定义 Timeline 话题词；存在时会追加到主检索关键词。
- `data/categories.json`：Papers Filter 固定分类，由流水线根据 `CATEGORIES` 写出。
- `index.html`：修改页面展示、筛选、Timeline、Groups 和 AI Chat 交互。

修改检索关键词、期刊或分类后，建议重新运行 `python run_pipeline.py`。已有论文如果需要重新评分和重新分类，需要清空对应的 `data/*.json` 后再全量重建。

---

## 快速部署

### 1. Fork 或使用当前仓库

Fork 后建议仓库名保持 `research-radar`。GitHub Pages 默认访问地址为：

`https://你的用户名.github.io/research-radar/`

### 2. 配置 DeepSeek API Key

进入仓库：

`Settings -> Secrets and variables -> Actions -> New repository secret`

添加：

- Name: `DEEPSEEK_API_KEY`
- Value: 你的 DeepSeek API Key

### 3. 启用 GitHub Pages

进入仓库：

`Settings -> Pages`

设置：

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/ (root)`

保存后等待 GitHub Pages 发布。

### 4. 首次运行流水线

进入：

`Actions -> Research Radar Pipeline -> Run workflow`

运行完成后，流水线会更新 `data/*.json` 并自动提交到仓库。

本地运行方式：

```bash
cd scripts
python run_pipeline.py
```

本地运行前需要在 `.env` 或环境变量中设置 `DEEPSEEK_API_KEY`。

---

## 网页按钮触发更新

右上角“更新检索”按钮会在浏览器中调用 GitHub API 触发 `workflow_dispatch`。浏览器不能自动继承你的 GitHub 登录权限，因此需要输入 GitHub Personal Access Token。

建议使用 Fine-grained token：

- Repository access：只选择 `he16222/research-radar`
- Actions：`Read and write`
- Contents：`Read and write`

其中 `Actions: Read and write` 用于触发 GitHub Actions；`Contents: Read and write` 用于网页把自定义话题同步到 `data/topics.json`。

Token 会保存在当前浏览器的 localStorage。它不会上传到本项目后端服务器，但同源网页脚本可以读取 localStorage，因此应使用最小权限和合理过期时间。

如果需要重新输入 token，可以在浏览器 Console 执行：

```js
localStorage.removeItem('rr_github_token')
```

---

## 技术架构

```text
GitHub Pages
├── index.html
├── data/papers.json
├── data/papers-historical.json
├── data/timeline.json
├── data/groups.json
├── data/categories.json
└── scripts/

浏览器 -> fetch data/*.json
浏览器 -> DeepSeek API              AI Chat，Key 存 localStorage
浏览器 -> GitHub API                可选，触发 Actions 或同步 data/topics.json
GitHub Actions -> OpenAlex API      按关键词和期刊 ISSN 抓取论文
GitHub Actions -> DeepSeek API      论文分析和 Timeline 综述
GitHub Actions -> commit data/*.json
```

当前论文抓取逻辑：

1. 读取 `scripts/config.py` 的 `KEYWORDS`。
2. 如果存在 `data/topics.json`，追加其中的 `terms` 并去重。
3. 对每个 `关键词 × TARGET_JOURNALS[*].issn` 调用 OpenAlex。
4. 按标题 ID 去重。
5. 对新增论文调用 DeepSeek。
6. `relevance < MIN_RELEVANCE` 的论文不写入 `papers.json`。

`relevance_reason` 只用于页面展示；真正影响入库的是 `relevance` 分数。

---

## 当前配置重点

| 配置项 | 位置 | 当前含义 |
|---|---|---|
| 论文检索关键词 | `scripts/config.py` -> `KEYWORDS` | RI、NSV、气动弹性、声学诱导振动、流动-振动控制、解析/降阶模型 |
| 当前监控期刊 | `scripts/config.py` -> `TARGET_JOURNALS` | 10 本期刊 |
| 历史前身期刊 | `scripts/config.py` -> `HISTORICAL_JOURNALS` | 2 本期刊 |
| AI 分类标签 | `scripts/config.py` -> `CATEGORIES` | 16 个固定 Filter 标签 |
| 课题组 | `scripts/config.py` -> `RESEARCH_GROUPS` | 32 个研究组，支持 `pis` 和 `aliases` 匹配 |
| AI 论文分析提示词 | `scripts/process_with_ai.py` -> `BASE_SYSTEM_PROMPT`、`RELEVANCE_GUIDE` | 围绕 RI-NSV机理、预测与控制评分 |
| Timeline 默认话题 | `scripts/fetch_papers_historical.py` 和 `index.html` -> `DEFAULT_TOPICS` | 15 个话题 |
| 自动更新频率 | `.github/workflows/pipeline.yml` -> `cron` | 每周自动运行 |

当前核心分类：

| 分类 | 覆盖内容 | 与当前课题的关系 |
|---|---|---|
| `旋转不稳定性 RI` | 轴流风扇、压气机中的 rotating instability、rotating instabilities、叶尖泄漏流诱导的周向非定常扰动、近失速旋转扰动、方位模态等。 | 用于识别 NSV 的主要流动激励来源，尤其关注叶尖间隙、机匣槽、近失速工况下的 RI 形成与传播。 |
| `非同步振动 NSV` | nonsynchronous vibration、non-synchronous vibration、non-engine-order blade vibration、part-speed vibration、行波振动和节径相关叶片振动。 | 对应当前课题的主要振动对象，强调区别于转速整数阶强迫响应的自激或流致振动现象。 |
| `RI-NSV机理` | RI 扰动与叶片振动之间的耦合机制，包括气动激励频率、扰动传播速度、锁频、行波模态和叶片响应之间的关系。 | 属于最核心类别，用于筛选直接讨论“RI 如何导致 NSV”以及如何预测这种耦合关系的论文。 |
| `机匣处理与流动控制` | casing treatment、casing groove、casing slot、shroud treatment、endwall treatment 等改变叶尖流动和近失速扰动的控制方式。 | 用于追踪通过机匣结构或端壁处理改变 RI、叶尖泄漏流和失速裕度，进而影响 NSV 或流致振动的研究。 |
| `叶片流致振动抑制/控制` | 叶片改型、气动或结构失谐、 intentional mistuning、flutter margin 提升、振动抑制和流动-振动控制策略。 | 用于收集面向叶片颤振、NSV、强迫响应或其他流致振动问题的抑制方法。 |
| `声学诱导叶片振动` | acoustic resonance、trapped acoustic modes、duct/intake acoustic modes、声反射、声衬和壁面声学阻抗对叶片振动的影响。 | 用于追踪声学模态与叶片振动耦合的论文，尤其是声学反馈、进气道反射和阻抗调控对风扇/压气机叶片稳定性的影响。 |
| `风扇/压气机叶片气动弹性` | fan/compressor blade aeroelasticity、flutter、forced response、aerodynamic damping、inter-blade phase angle、nodal diameter 等。 | 用于收集风扇和压气机叶片气动弹性稳定性论文，作为 NSV、颤振和强迫响应分析的上位背景类别。 |
| `叶片流致振动预测模型` | NSV 半解析模型、降阶模型、线性模型、单自由度模型、Van der Pol 类模型、锁频预测和声学/气动弹性预测模型。 | 用于追踪能直接预测叶片流致振动幅值、频率、锁频条件或稳定边界的模型类论文。 |
| `实验测量` | 级环境或叶栅实验、叶尖定时、非定常压力测量、应变测量、时间分辨测量和模态识别。 | 用于标记提供实验数据、验证机制或支持模型校核的论文。 |
| `数值仿真` | CFD、URANS、LES、大涡模拟、全环/扇区非定常模拟、流固耦合计算和参数扫描。 | 用于标记通过数值手段研究 RI、NSV、气动弹性、叶尖泄漏流和控制措施的论文。 |
| `解析/降阶模型` | 半解析模型、降阶模型、低阶模型、线性模型、Moore-Greitzer 类稳定性模型、叶尖泄漏流/叶尖涡模化和扰动传播速度模型。 | 该分类强调研究方法本身，常与 `叶片流致振动预测模型` 同时出现，用于保留可解释、计算成本较低的理论和模型研究。 |
| `叶尖间隙` | tip clearance、tip leakage、tip leakage vortex、tip gap、叶尖泄漏流和叶尖间隙变化的影响。 | 叶尖间隙是 RI、近失速扰动和部分 NSV 问题的重要流动来源，该分类用于保留相关基础流动研究。 |
| `失速/喘振机理` | rotating stall、stall inception、surge、stall margin、spike、modal wave、stall cell 和失速恢复。 | 用于保留风扇/压气机稳定性背景文献，特别是与 RI、叶尖泄漏流和近失速非定常扰动有关的研究。 |
| `稳定性建模` | actuator disk、body force model、throughflow、streamline curvature、Moore-Greitzer 和三维稳定性模型。 | 用于收集风扇/压气机系统稳定性和流动稳定性建模论文，为 RI 与控制研究提供理论背景。 |
| `畸变进气` | inlet distortion、circumferential distortion、radial distortion、total pressure distortion 和非均匀进气。 | 用于保留进气畸变对压气机稳定性、非定常流动和叶片响应影响的论文。 |
| `其他` | 与风扇、压气机、叶轮机械振动或稳定性有一定关系，但无法明确归入上述类别的论文。 | 作为兜底标签，避免有参考价值但分类边界不清的论文被完全排除。 |

### 当前检索期刊范围

当前论文库使用 `TARGET_JOURNALS`，抓取 2015 年至今的论文；历史论文库使用 `TARGET_JOURNALS + HISTORICAL_JOURNALS`，抓取 1960 年至 2014 年的论文。OpenAlex 查询使用 `locations.source.issn` 过滤，原因是部分期刊的 print ISSN 不一定出现在 `primary_location.source.issn`，例如 Journal of Fluid Mechanics。

当前监控期刊：

| 期刊 | ISSN | 纳入原因 |
|---|---|---|
| Journal of Turbomachinery | `0889-504X` | ASME 叶轮机械核心期刊，覆盖压气机、涡轮、风扇、非定常流动、叶尖泄漏流、稳定性和气动弹性。 |
| Journal of Engineering for Gas Turbines and Power | `0742-4795` | 燃气轮机与推进系统期刊，覆盖压气机/风扇部件、稳定性、失速、试验和工程应用。 |
| Journal of Propulsion and Power | `0748-4658` | AIAA 推进期刊，覆盖航空发动机推进部件、风扇/压气机气动、非定常流动和推进系统相关振动问题。 |
| AIAA Journal | `0001-1452` | 航空航天综合基础期刊，覆盖气动弹性、流固耦合、声学、非定常流动和计算方法。 |
| Journal of Sound and Vibration | `0022-460X` | 声学与振动核心期刊，覆盖叶片振动、声学模态、结构响应、非线性振动和流致振动。 |
| Progress in Aerospace Sciences | `0376-0421` | 航空航天综述期刊，适合捕捉气动弹性、推进系统、非定常气动和流动控制方向的综述性工作。 |
| Chinese Journal of Aeronautics | `1000-9361` | 航空领域综合期刊，覆盖压气机、风扇、非定常流动、气动弹性和国内相关研究进展。 |
| Journal of Fluid Mechanics | `0022-1120` | 流体力学基础期刊，覆盖涡结构、剪切流、非定常流动、流动稳定性和可用于解释 RI/叶尖泄漏流的基础研究。 |
| Applied Acoustics | `0003-682X` | 应用声学期刊，覆盖管道声学、声学阻抗、声衬、声反射和声振耦合问题。 |
| Journal of Fluids and Structures | `0889-9746` | 流固耦合与流致振动核心期刊，覆盖流致振动、气动弹性、结构响应和非线性耦合。 |

历史补充期刊：

| 期刊 | ISSN | 纳入原因 |
|---|---|---|
| Journal of Engineering for Power | `0022-0825` | Journal of Engineering for Gas Turbines and Power 的历史前身之一，覆盖早期燃气轮机、压气机和叶轮机械研究。 |
| Journal of Basic Engineering | `0021-9223` | ASME 早期基础工程期刊，可能包含早期流体机械、流动稳定性和叶轮机械基础论文。 |

---

## 数据文件说明

- `data/papers.json`：2015 年至今论文，经过 DeepSeek 分析，按日期倒序。
- `data/papers-historical.json`：1960 年至 2014 年历史论文，包含 OpenAlex 元数据和 `topics_matched`。
- `data/timeline.json`：Timeline 热力图数据和 AI 综述。
- `data/groups.json`：课题组统计，合并历史论文和当前论文。
- `data/categories.json`：Papers Filter 固定分类。
- `data/topics.json`：可选文件，由网页“同步到流水线”生成；存在时会追加到主检索关键词。
- `data/annotations.json`：仓库级标注记忆，会被流水线读取并影响后续 AI 判断。
- 浏览器 localStorage：保存已读状态、网页端评价、愿望清单、AI Chat Key、GitHub Token 等本地状态。

---

## 维护说明

修改检索方向时，通常需要同步调整：

1. `KEYWORDS`
2. `CATEGORIES`
3. `BASE_SYSTEM_PROMPT` 和 `RELEVANCE_GUIDE`
4. Python 与前端两份 `DEFAULT_TOPICS`
5. `data/categories.json`
6. 必要时清空旧的 `papers.json`、`papers-historical.json`、`timeline.json`、`groups.json`、`repos.json`、`meta.json` 后重建

修改后建议运行：

```bash
python -m py_compile scripts/*.py
python -m pytest scripts/tests -q
```

---

## 更新日志

### v1.5（2026-05-11）

- 当前论文抓取起始年份从 2020 年改为 2015 年，历史论文覆盖 1960 年至 2014 年。
- 新增 Journal of Fluid Mechanics、Applied Acoustics、Journal of Fluids and Structures 三本当前监控期刊。
- 增加叶尖泄漏流模化、降阶模型和经典 NSV 半解析模型相关检索词。
- 统一 `RI-NSV机理` 标签，兼容旧数据中的空格版本，避免 Papers Filter 重复。
- 修正 Timeline 年份解析，使只有 `date` 字段的当前论文也能进入 2020s 和 2025s heatmap。
- 将 OpenAlex 期刊过滤字段改为 `locations.source.issn`，以保证 Journal of Fluid Mechanics 的 print ISSN 能被正确检索。

### v1.4（2026-05-11）

- 将仓库方向校准为 RI 导致 NSV、流动-振动控制、实验/仿真/解析模型。
- 重构论文检索关键词，删除宽泛词和易误匹配缩写。
- 重构 Papers Filter 分类和 Timeline 默认话题。
- 修改 DeepSeek 评分规则，使 `relevance` 围绕 RI-NSV机理、预测或控制。
- 修正 `data/topics.json` 逻辑：网页话题词追加到主关键词，不再覆盖主关键词。
- 删除旧的“叶尖畸变下稳定裕度”标注偏置。
- 清空旧数据文件，等待按新方向全量重建。

### v1.3（2026-03-31）

- 双主题系统、论文列表分页、Timeline 视觉优化、Markdown AI 综述。
- 项目手册 `docs/manual.md`。

### v1.2（2026-03-30）

- Timeline 改为 5 年间隔。
- 增加历史论文抓取和历史前身期刊。
- 增加课题组统计和相关度排序。

### v1.1（2026-03-30）

- 新增时间轴热力图、文献愿望清单、历史论文抓取。

### v1.0（2026-03-28）

- 初始发布：论文抓取、AI 分析、课题组追踪、标注系统、AI 问答。

---

## License

MIT，自由使用、修改和分发。
