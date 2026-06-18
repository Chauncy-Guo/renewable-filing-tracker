# 架构设计

## 整体流程

```
┌─────────────────────────────────────────────────────────────────────┐
│ ① 查公告                                                          │
│    query_api.js ──POST──▶ /api/tyrz/uca/notice/list2               │
│    ▲ 分页 pageNo=1..N  / 筛选 (不含户用光伏) / 时间范围            │
│    └─→ output/api_records_target.json                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ② 下文件                                                           │
│    download_word.js                                                │
│    ▲ 解析公告页 HTML 提取附件 href (相对路径自动转绝对)            │
│    ▲ HEAD 校验: 504B0304 → .docx  /  D0CF11E0 → .doc               │
│    └─→ output/PDFs/YY年M月份全国新能源装机建档立卡数据.{docx,doc}   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ③ 抽数据                                                           │
│    extract_all.py  (extract.py)                                    │
│    ├─ PDF: pdf_extract.mjs (pdfjs-dist) → tokens →                 │
│    │       pdf_parser._parse_pdf_text_to_table                     │
│    │       写入 output/Excel/工商业分布式/月度文件.xlsx             │
│    │                                                              │
│    └─ Word:                                                       │
│         .docx → python-docx 直读                                   │
│         .doc  → word_extract.mjs (word-extractor) → JSON           │
│         detect_type()  按项目编码前缀分类                           │
│         写入 output/Excel/{风机|集中式光伏|生物质}/月度文件.xlsx    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ④ 汇 总                                                            │
│    merge_excel.py  (merge.py)                                      │
│    ├─ 扫描 output/Excel/ 中所有 xlsx                               │
│    ├─ 按文件名解析 (年, 月) → 排序: 最新 → 最旧                     │
│    ├─ 同类型多张表合并, 附加"项目月份"列                           │
│    └─→ output/汇总/汇总_{类型}.xlsx                                │
└─────────────────────────────────────────────────────────────────────┘
```

## 输出目录约定 (output/)

所有运行时产物集中在 `output/`, 业务代码 (`src/` `scripts/`) 永远不写它以外的位置:

```
output/
├── PDFs/            原始 PDF/Word 源文件          (下载/输入)
├── Excel/           单月 xlsx                    (中间产物)
├── 汇总/            4 类汇总 xlsx                (最终交付)
├── api_records_target.json
└── docs/            项目文档                      (本目录)
```

`config.py` 通过 `__file__` 推算项目根, 拼出 `output/PDFs` `output/Excel` `output/汇总`,
所以无论从哪里执行 `scripts/extract_all.py` 都能写到正确位置。

> 跨平台注意: `output/` 下的中文目录 (`汇总`) 在不同文件系统下编码需一致;
> 仓库内统一使用 UTF-8, Windows + Git 默认会自动处理。

## Python 模块边界

```
renewable_extract/
│
├── config.py            纯常量, 不依赖任何业务模块
│   ├── 路径 (PDF_DIR / XLSX_DIR / SUMMARY_DIR / DOCS_DIR)
│   ├── 标头 (HEADER)
│   ├── 文件名清单 (INDUSTRIAL_PDFS / WORD_FILES)
│
├── excel_writer.py      工具层 — 不读业务, 只写 xlsx
│   └── save_xlsx(rows, path, sheet_name)
│
├── detect_type.py       纯函数 — 输入表格行, 返回类型字符串
│   └── detect_type(tbl) -> '风机' | '集中式光伏' | '工商业分布式' | '生物质' | None
│
├── pdf_parser.py        跨进程 — 调用 Node 解析 PDF
│   └── extract_pdf_to_rows(path) -> 5 列标准表
│       内部按 x 坐标聚类:
│         60-100   序号
│         110-200  项目编码 (正则 [A-Z]{2,3}\d{8,}[A-Z0-9]*)
│         220-540  项目名称 (跨多 token 拼接)
│         540-620  装机容量 (排除 4 位年份)
│         630-800  项目所在地
│
├── word_parser.py       单文件解析
│   ├── extract_docx_tables(path)      # python-docx
│   ├── extract_doc_tables(path)       # Node word-extractor
│   ├── normalize_table_header(tbl)    # 表头规整为 5 列
│   └── parse_row_cells(cells)         # 单元格行 -> 5 列表
│
├── extract.py           端到端流程 (组合以上模块)
│   ├── extract_pdfs()                 # 工商业分布式
│   ├── extract_words()                # 风机 / 集中式光伏 / 生物质
│   └── extract_all()
│
└── merge.py             汇总层
    ├── parse_month(filename)          # (年, 月) 二元组
    ├── _merge_category(name, pred, with_month_col)
    └── merge_all()                    # 4 类依次合并
```

## Node 脚本边界

| 脚本 | 职责 | 输入 | 输出 |
| --- | --- | --- | --- |
| `query_api.js` | 调 SSO 公告 API + 过滤 | `process.argv` 时间范围 | `output/api_records_target.json` |
| `download_word.js` | 下载 + 文件头校验 | `output/api_records_target.json` | `output/PDFs/YY年M月...{docx,doc}` |
| `pdf_extract.mjs` | pdfjs 提取 token 列表 | `pdf_path` | `out_json` |
| `word_extract.mjs` | word-extractor 解析 .doc | `doc_path` | `out_json` (含 sections) |

后两个脚本是被 Python 以子进程方式调用的, 不直接面向用户。

## 扩展点

### 新增一种新能源类型 (例如储能)

1. 在 `config.py` 中追加文件名清单;
2. 在 `detect_type.py` 增加编码前缀规则;
3. 在 `merge.py` 增加一个 `is_xxx()` 谓词和一次 `merge_all()` 调用。

### 接入新公告源 (非 SSO 系统)

1. 复用 `extract.py` 中的 `extract_words` / `extract_pdfs` 流程;
2. 自行实现一个 `query_api.js` 替代品, 输出符合 `{year, month, url}` 的 JSON。

## 错误恢复策略

| 场景 | 行为 |
| --- | --- |
| 公告页相对路径附件 | `download_word.js` 用 `new URL(pageUrl).origin + pathname` 拼接 |
| 附件文件类型不匹配扩展名 | 通过文件头前 8 字节重命名为正确扩展名 |
| Word 表格内表头被合并单元格搞乱 | `normalize_table_header` 强制覆盖为标准 5 列 |
| 25 年 3 月起 Word 只剩 3 个表 | `detect_type` 按编码前缀动态判断, 不再依赖固定顺序 |
| PDF 表格项目名称换行 | `_parse_pdf_row` 收集编码与容量之间的所有 token 拼接 |
| 项目所在省 + 详细地址分成两行 | 同样拼接, 用 y 坐标聚类容差 Y_TOL=8 合并 |
