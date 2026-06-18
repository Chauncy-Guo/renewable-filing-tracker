# 全国新增建档立卡新能源装机数据提取工具

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docs: CC-BY-NC-4.0](https://img.shields.io/badge/Docs-CC--BY--NC--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![Node 20+](https://img.shields.io/badge/Node-20+-339933.svg?logo=node.js&logoColor=white)](https://nodejs.org)
[![GitHub repo](https://img.shields.io/badge/GitHub-Chauncy--Guo%2Frenewable--filing--tracker-181717.svg?logo=github)](https://github.com/Chauncy-Guo/renewable-filing-tracker)

> 自动化采集 [国能新能建档立卡系统](https://sso.renewable.org.cn/noticeHisroty?noticeType=1)
> 发布的《全国新增建档立卡新能源发电项目情况》公告,
> 把随附的 PDF / Word 文件解析为 Excel, 并按月份和类型汇总到统一表格。

## 功能概览

| 阶段 | 说明 | 入口 |
| --- | --- | --- |
| ① 查公告 | 调用 SSO API 列出目标时间范围内的公告 | `node src/node/query_api.js` |
| ② 下文件 | 从公告页解析附件链接, 下载 .doc / .docx 到 `output/PDFs/` | `node src/node/download_word.js` |
| ③ 抽数据 | 解析 PDF/Word 表格 → 单月 Excel, 写入 `output/Excel/` | `python scripts/extract_all.py` |
| ④ 汇 总 | 把同类型单月 Excel 合并, 增加"项目月份"列, 写入 `output/汇总/` | `python scripts/merge_excel.py` |

数据源分为两类:

- **全国新能源装机** (.docx) — 包含 **风机 / 集中式光伏 / 生物质** 三类项目
- **工商业分布式光伏** (.pdf) — 24 年起单独发布的 PDF 公告

## 目录结构

```
.
├── README.md                        # 本文档
├── package.json                     # Node.js 依赖与脚本
├── requirements.txt                 # Python 依赖
├── .gitignore                       # 临时文件 / 缓存忽略
│
├── src/                             # 核心代码
│   ├── node/                        # Node.js 脚本
│   │   ├── query_api.js             #   公告 API 查询
│   │   ├── download_word.js         #   Word 附件下载
│   │   ├── pdf_extract.mjs          #   PDF 文本提取 (pdfjs-dist)
│   │   └── word_extract.mjs         #   .doc 文本提取 (word-extractor)
│   └── python/                      # Python 包
│       └── renewable_extract/
│           ├── __init__.py
│           ├── config.py            #   路径与文件名常量
│           ├── excel_writer.py      #   通用 xlsx 输出
│           ├── detect_type.py       #   Word 表类型识别
│           ├── pdf_parser.py        #   PDF 表格解析
│           ├── word_parser.py       #   Word 表格解析
│           ├── extract.py           #   端到端提取流程
│           └── merge.py             #   汇总合并
│
├── scripts/                         # 用户级入口 (一行命令)
│   ├── download_new.js              #   一键: 查公告 + 下文件
│   ├── extract_all.py               #   一键: PDF + Word -> Excel
│   └── merge_excel.py               #   一键: Excel -> 汇总
│
└── output/                          # 所有数据产物
│   ├── PDFs/                        #   原始 PDF / Word 文件
│   ├── Excel/                       #   单月单类型 xlsx (中间产物)
│   ├── 汇总/                        #   4 类汇总 xlsx (最终交付)
│   ├── api_records_target.json      #   公告列表缓存
│   └── docs/                        #   详细文档 (不入仓, 副本在仓库根 docs/)
│
├── docs/                            # 入仓的详细文档 (供 GitHub Pages)
│   ├── architecture.md              #   架构与模块设计
│   ├── data-format.md               #   输入 / 输出数据格式
│   ├── faq.md                       #   常见问题与维护
│   └── .nojekyll                    #   跳过 Jekyll 渲染
│
└── LICENSE                          # AGPL-3.0 全文
```

> 全部数据产物统一放在 `output/`, 与代码 (`src/` / `scripts/`) 严格分离, 方便打包、清理、迁移。

## 快速开始

### 1. 环境依赖

- **Python 3.10+**
- **Node.js 20+**

```bash
# Python 依赖
pip install -r requirements.txt

# Node 依赖
npm install
```

### 2. 一键流程

```bash
# (可选) 拉取最新公告 -> output/PDFs/
node scripts/download_new.js 2025 3 2026 4

# 解析 output/PDFs/ -> output/Excel/
python scripts/extract_all.py

# 合并 output/Excel/ -> output/汇总/
python scripts/merge_excel.py
```

### 3. 单独运行某一步

```bash
# 只查公告 (输出控制台 + output/api_records_target.json)
node src/node/query_api.js 2025 3 2026 4

# 只下载 (依赖上一步生成的 output/api_records_target.json)
node src/node/download_word.js

# 只跑 PDF (工商业分布式)
python -c "import sys; sys.path.insert(0,'src/python'); from renewable_extract.extract import extract_pdfs; extract_pdfs()"

# 只跑 Word (风机/集中式光伏/生物质)
python -c "import sys; sys.path.insert(0,'src/python'); from renewable_extract.extract import extract_words; extract_words()"

# 只生成某一类汇总
python -c "import sys; sys.path.insert(0,'src/python'); from renewable_extract.merge import _merge_category, is_wind; _merge_category('风机', is_wind, True)"
```

## 输出结果

### `output/Excel/` 单月文件

```
24年9月份工商业分布式光伏建档立卡数据.xlsx
25年3月份风机建档立卡数据.xlsx
25年3月份集中式光伏建档立卡数据.xlsx
25年3月份生物质建档立卡数据.xlsx
...
```

### `output/汇总/` 4 类合并文件

| 文件名 | 数据来源 |
| --- | --- |
| `汇总_工商业分布式光伏.xlsx` | 各月工商业分布式 PDF |
| `汇总_集中式光伏.xlsx` | 各月 Word 文档中的集中式光伏表 |
| `汇总_风机.xlsx` | 各月 Word 文档中的风机表 |
| `汇总_生物质.xlsx` | 各月 Word 文档中的生物质表 |

每条记录都包含"项目月份"列, 方便后续筛选与溯源。

## 项目编码规则

提取逻辑通过项目编码前缀自动识别表格类型:

| 前缀 | 类型 |
| --- | --- |
| `PW` | 风机 |
| `PPC` / `PPS` | 集中式光伏 |
| `PPD` | 工商业分布式光伏 |
| `PB` | 生物质 (含垃圾焚烧/沼气) |

## 详细文档

- [架构设计](docs/architecture.md) — 模块划分、调用链、扩展点
- [数据格式](docs/data-format.md) — 输入公告、PDF、Word 与输出 Excel 字段
- [常见问题](docs/faq.md) — 文件头校验、相对路径、动态表类型等

> GitHub Pages 在线版: <https://chauncy-guo.github.io/renewable-filing-tracker/>

## License

本项目采用 **双重 license**, 根据内容性质分别适用:

| 内容 | License | 含义 |
| --- | --- | --- |
| 全部源码 (`src/` `scripts/`) | [AGPL-3.0](LICENSE) | 网络服务也必须开源; 商用需公开修改后的源代码 |
| 项目文档 (`docs/` `README.md`) | [CC-BY-NC-4.0](https://creativecommons.org/licenses/by-nc/4.0/) | 署名 + 禁止商业用途 |

简单说:

- 你可以自由使用、修改、分发
- **但**: 如果你把这个项目 (或其修改版) 用作网络服务 (SaaS / API) 提供给他人, 必须公开全部修改后的源代码
- **并且**: 项目文档禁止用于商业用途

Copyright (C) 2026 Chauncy-Guo
