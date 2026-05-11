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

当前仓库已经清空旧数据，等待按 RI-NSV 新方向全量重建：

- `data/papers.json`
- `data/papers-historical.json`
- `data/timeline.json`
- `data/groups.json`
- `data/repos.json`
- `data/meta.json`

运行 `Research Radar Pipeline` 后，上述文件会重新生成。由于全量重建会重新调用 DeepSeek，仓库的 `Actions secrets` 必须配置 `DEEPSEEK_API_KEY`。

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

- `旋转不稳定性 RI`
- `非同步振动 NSV`
- `RI-NSV机理`
- `机匣处理与流动控制`
- `叶片流致振动抑制/控制`
- `声学诱导叶片振动`
- `风扇/压气机叶片气动弹性`
- `叶片流致振动预测模型`
- `实验测量`
- `数值仿真`
- `解析/降阶模型`
- `叶尖间隙`
- `失速/喘振机理`
- `稳定性建模`
- `畸变进气`
- `其他`

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
