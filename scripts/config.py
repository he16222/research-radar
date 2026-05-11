# ─────────────────────────────────────────────
#  研究雷达 · 配置文件
#  按需修改关键词和分类标签
# ─────────────────────────────────────────────

# 搜索关键词（每个词会在所有目标期刊中搜索）
# 原则：先用短词广搜，再用长词精搜，靠 AI 评分过滤不相关的
KEYWORDS = [
    # ── 叶尖间隙 ──
    "tip clearance",
    "tip leakage",
    "compressor tip clearance",
    # ── 机匣处理 ──
    "casing treatment",
    "stall margin",
    # ── 失速 / 喘振 / 稳定性 ──
    "rotating stall",
    "compressor surge",
    "stall inception",
    "compressor stability",
    # ── 稳定性建模 ──
    "actuator disk",
    "body force model",
    "Moore Greitzer",
    "streamline curvature",
    # ── 进气畸变 ──
    "distortion",
    "inlet distortion",
    "circumferential distortion",
    "radial distortion",
    # ── RI 与 RI-NSV 机理 ──
    "rotating instability",
    "rotating instabilities",
    "rotating instability axial compressor",
    "rotating instability axial fan",
    "tip leakage flow rotating instability",
    "tip clearance rotating instability",
    "azimuthal mode rotating instability",
    "casing groove rotating instability",
    "prestall rotating disturbance compressor",
    # ── 非同步振动 NSV ──
    "nonsynchronous vibration",
    "non-synchronous vibration",
    "non synchronous vibration",
    "non-engine order blade vibration",
    "part speed vibration",
    "nonsynchronous blade vibration",
    "non-synchronous blade vibration",
    # ── 风扇/压气机叶片气动弹性 ──
    "fan blade aeroelasticity",
    "compressor blade aeroelasticity",
    "aeroelastic stability fan blade",
    "aeroelastic stability compressor blade",
    "fan blade flutter",
    "compressor blade flutter",
    "fan blade forced response",
    "compressor blade forced response",
    "aerodynamic damping fan blade",
    "aerodynamic damping compressor blade",
    "travelling wave mode compressor blade",
    "traveling wave mode compressor blade",
    "inter-blade phase angle flutter",
    "nodal diameter fan flutter",
    # ── 流动-振动控制 ──
    "intentional mistuning non-synchronous vibration",
    "aerodynamic mistuning non-synchronous vibration",
    "structural mistuning non-synchronous vibration",
    "casing treatment non-synchronous vibration",
    "axial slot casing treatment non-synchronous blade vibration",
    "casing treatment blade vibration compressor",
    "casing treatment rotating instability",
    "acoustic treatment fan flutter",
    "acoustic impedance fan flutter",
    "wall impedance fan flutter",
    "liner fan flutter stability",
    "fan blade flutter margin",
    "improving flutter margin fan blade",
    # ── 声学诱导叶片振动 ──
    "acoustic resonance non-synchronous blade vibration",
    "trapped acoustic modes blade vibration",
    "trapped acoustic modes compressor",
    "acoustic modes non-synchronous vibration",
    "acoustic reflections fan flutter",
    "intake acoustic reflections fan blade",
    "intake acoustics fan flutter",
    "duct acoustic modes blade vibration",
    "aeroacoustic blade vibration compressor",
    # ── 叶片流致振动预测模型 ──
    "non-synchronous vibration semi-analytical model",
    "convective non-synchronous vibration model",
    "lock-in mechanism non-synchronous vibration compressor",
    "linear model non-synchronous vibration compressor",
    "single-degree-of-freedom non-synchronous vibration",
    "reduced-order model nonsynchronous vibration turbomachinery",
    "Van der Pol nonsynchronous vibration turbomachinery",
    "aeroelastic reduced-order model fan blade",
    "flutter reduced order model fan blade",
    "acoustic treatment fan flutter analytical model",
]

# 目标期刊（AIAA / ASME），按 ISSN 精准过滤
TARGET_JOURNALS = [
    {"name": "Journal of Turbomachinery",          "issn": "0889-504X"},
    {"name": "J. Eng. Gas Turbines and Power",     "issn": "0742-4795"},
    {"name": "Journal of Propulsion and Power",    "issn": "0748-4658"},
    {"name": "AIAA Journal",                        "issn": "0001-1452"},
    {"name": "Journal of Sound and Vibration",      "issn": "0022-460X"},
    {"name": "Progress in Aerospace Sciences",      "issn": "0376-0421"},
    {"name": "Chinese Journal of Aeronautics",      "issn": "1000-9361"},
]

# 历史期刊（前身），仅 fetch_papers_historical 使用
HISTORICAL_JOURNALS = [
    {"name": "J. Eng. for Power (→JEGTP前身)",     "issn": "0022-0825"},
    {"name": "J. Basic Engineering",                "issn": "0021-9223"},
]

# 只抓近几年的论文
FETCH_FROM_YEAR = 2020

# 历史论文起始年份（fetch_papers_historical.py 使用）
FETCH_FROM_YEAR_HISTORICAL = 1960

# GitHub 搜索词
GITHUB_KEYWORDS = [
    "turbomachinery CFD",
    "compressor stability",
    "actuator disk turbomachinery",
    "OpenFOAM turbomachinery",
    "axial compressor simulation",
]

# 分类标签（DeepSeek 从这里选，可自由扩展）
CATEGORIES = [
    "旋转不稳定性 RI",
    "非同步振动 NSV",
    "RI-NSV 机理",
    "机匣处理与流动控制",
    "叶片流致振动抑制/控制",
    "声学诱导叶片振动",
    "风扇/压气机叶片气动弹性",
    "叶片流致振动预测模型",
    "实验测量",
    "数值仿真",
    "解析/降阶模型",
    "叶尖间隙",
    "失速/喘振机理",
    "稳定性建模",
    "畸变进气",
    "其他",
]

# 每次最多抓取数量
MAX_PAPERS_PER_QUERY = 50   # 每个关键词每本期刊
MAX_REPOS = 20               # GitHub 仓库数

# 相关度阈值：低于此分数不写入最终 JSON
MIN_RELEVANCE = 2

# 重点追踪的课题组（PI 姓名列表用于匹配作者字段）
# 可自由添加，name 字段会显示在网页上
RESEARCH_GROUPS = [
    # ── 北美 ──
    {
        "name": "MIT GTL",
        "institution": "MIT",
        "pis": ["Greitzer", "Spakovszky", "C. S. Tan", "Choon Tan", "Paduano"],
    },
    {
        "name": "Purdue Compressor Lab",
        "institution": "Purdue University",
        "pis": ["Nicole Key", "Nicole L. Key", "Berdanier", "Sanford Fleeter", "Yujun Leng"],
    },
    {
        "name": "NASA Glenn",
        "institution": "NASA Glenn Research Center",
        "pis": ["Chunill Hah", "Adamczyk"],
    },
    {
        "name": "Polytechnique Montreal",
        "institution": "Polytechnique Montreal",
        "pis": ["Huu Duc Vo", "Alain Batailly"],
    },
    # ── 欧洲 ──
    {
        "name": "Cambridge Whittle Lab",
        "institution": "University of Cambridge",
        "pis": ["Cumpsty", "Hodson", "I. J. Day", "Cesare A. Hall", "Paul G. Tucker"],
    },
    {
        "name": "Oxford Thermofluids",
        "institution": "University of Oxford",
        "pis": ["L. He", "Thomas Povey"],
    },
    {
        "name": "Imperial Aeroelasticity",
        "institution": "Imperial College London",
        "pis": [
            "Mehdi Vahdati",
            "Sina Stapelfeldt",
            "Loic Salles",
            "Fanzhou Zhao",
            "Venkatesh Suriyanarayanan",
        ],
    },
    {
        "name": "ETH Zurich LEC",
        "institution": "ETH Zurich",
        "pis": ["Reza S. Abhari"],
    },
    {
        "name": "Ecole Centrale Lyon LMFA",
        "institution": "Ecole Centrale de Lyon",
        "pis": ["Xavier Ottavy", "Christoph Brandstetter", "Fabrice Thouverez"],
    },
    {
        "name": "TU Dresden",
        "institution": "TU Dresden",
        "pis": ["Ronald Mailach", "Konrad Vogeler", "Xiangyi Chen", "Martin Lange"],
    },
    {
        "name": "TU Darmstadt GLR",
        "institution": "Technical University of Darmstadt",
        "pis": [
            "Schiffer",
            "Heinz-Peter Schiffer",
            "H.-P. Schiffer",
            "F. Holzinger",
            "Holzinger",
            "Maximilian Jungst",
            "Christoph Brandstetter",
        ],
        "aliases": [
            "TU Darmstadt",
            "Technical University of Darmstadt",
            "Technische Universitat Darmstadt",
            "Institute of Gas Turbines and Aerospace Propulsion",
            "Gas Turbines and Aerospace Propulsion",
            "GLR",
        ],
    },
    {
        "name": "DLR",
        "institution": "German Aerospace Center",
        "pis": [
            "F. Holste",
            "Holste",
            "Frank Kameier",
            "Kameier",
            "Neise",
            "Benjamin Pardowitz",
            "Pardowitz",
            "Marz",
            "M. Baumgartner",
            "Baumgartner",
        ],
        "aliases": [
            "DLR",
            "German Aerospace Center",
            "Deutsches Zentrum fur Luft- und Raumfahrt",
            "Engine Acoustics Department",
            "Institute of Propulsion Technology",
            "Institute of Aeroelasticity",
            "Fan and Compressor",
        ],
    },
    {
        "name": "TU Berlin Aero Engines",
        "institution": "Technische Universitat Berlin",
        "pis": ["Mario Eck", "Dieter Peitsch", "Victor Bicalho Civinelli de Almeida"],
        "aliases": [
            "Technische Universitat Berlin",
            "Technical University of Berlin",
            "TU Berlin",
            "Institute of Aeronautics and Astronautics",
            "Chair for Aero Engines",
        ],
    },
    {
        "name": "Duke Aeroelasticity",
        "institution": "Duke University",
        "pis": ["Hall", "Kielb", "Spiker", "Richard Hollenbach", "Clark", "Dowell"],
        "aliases": [
            "Duke University",
            "Thomas Lord Department of Mechanical Engineering",
            "Department of Mechanical Engineering and Material Science",
        ],
    },
    {
        "name": "University of Pennsylvania",
        "institution": "University of Pennsylvania",
        "pis": [],
        "aliases": ["University of Pennsylvania", "Penn Engineering"],
    },
    {
        "name": "Cranfield Propulsion",
        "institution": "Cranfield University",
        "pis": ["David G. MacManus", "Vassilios Pachidis"],
    },
    {
        "name": "Bath Sealing Group",
        "institution": "University of Bath",
        "pis": ["James A. Scobie", "Gary D. Lock", "Carl M. Sangan"],
    },
    {
        "name": "ITP Aero / UPM",
        "institution": "ITP Aero / Univ. Politecnica de Madrid",
        "pis": ["Roque Corral"],
    },
    # ── 中国 ──
    {
        "name": "Beihang BUAA",
        "institution": "Beihang University",
        "pis": ["Xiaofeng Sun", "Dakun Sun", "Xu Dong"],
    },
    {
        "name": "Tsinghua Turbo Lab",
        "institution": "Tsinghua University",
        "pis": ["Xinqian Zheng"],
    },
    {
        "name": "CAS IET",
        "institution": "Chinese Academy of Sciences",
        "pis": ["Juan Du"],
    },
    {
        "name": "Peking University",
        "institution": "Peking University",
        "pis": ["Chao Zhou"],
    },
    {
        "name": "BIT Wu Group",
        "institution": "Beijing Institute of Technology",
        "pis": ["Yanhui Wu"],
    },
    {
        "name": "SJTU Teng Group",
        "institution": "Shanghai Jiao Tong University",
        "pis": ["Jinfang Teng", "Mingmin Zhu"],
    },
    # ── 工业界 ──
    {
        "name": "Penn State (historical)",
        "institution": "Penn State University",
        "pis": ["Lakshminarayana"],
    },
    {
        "name": "Ferrara / Parma",
        "institution": "Univ. Ferrara / Univ. Parma",
        "pis": ["Michele Pinelli", "Mirko Morini"],
    },
    {
        "name": "GE Aviation",
        "institution": "GE Aviation",
        "pis": ["A. R. Wadia"],
    },
    {
        "name": "Mitsubishi Heavy Industries",
        "institution": "Mitsubishi Heavy Industries",
        "pis": ["Ryosuke Seki"],
        "aliases": [
            "Mitsubishi Heavy Industries",
            "Turbomachinery Research Department",
            "Research & Innovation Center",
        ],
    },
    {
        "name": "Waseda / IHI",
        "institution": "Waseda University / IHI",
        "pis": ["Fujisawa", "Yutaka Ohta"],
        "aliases": [
            "Waseda University",
            "Department of Applied Mechanics and Aerospace Engineering",
            "IHI",
        ],
    },
    {
        "name": "CSIR-NAL Propulsion",
        "institution": "CSIR-National Aerospace Laboratories",
        "pis": [],
        "aliases": [
            "CSIR-National Aerospace Laboratories",
            "National Aerospace Laboratories",
            "Propulsion Division",
        ],
    },
    {
        "name": "IISc Aerospace",
        "institution": "Indian Institute of Science",
        "pis": ["Jyoti Ranjan Majhi", "Kartik Venkatraman"],
        "aliases": [
            "Indian Institute of Science",
            "IISc",
            "Department of Aerospace Engineering",
        ],
    },
    {
        "name": "Kurz & Brun (Industrial GT)",
        "institution": "Solar Turbines / Elliott Group",
        "pis": ["Rainer Kurz", "Klaus Brun"],
    },
]
