# -*- coding: utf-8 -*-
"""Word (.doc / .docx) 表格解析。"""
import json
import os
import re
import subprocess
from typing import List, Optional

from docx import Document

from .config import DOC_EXTRACT_MJS


def extract_docx_tables(path: str) -> List[List[List[str]]]:
    """用 python-docx 解析 .docx 文件, 返回每张表为一个二维列表。

    单元格内的换行会被替换为空格。
    """
    doc = Document(path)
    tables = []
    for t in doc.tables:
        rows = []
        for row in t.rows:
            cells = [c.text.strip().replace("\n", " ").replace("\r", "") for c in row.cells]
            rows.append(cells)
        tables.append(rows)
    return tables


def extract_doc_tables(path: str) -> List[List[List[str]]]:
    """解析老版本 .doc 文件, 通过 Node.js word_extract.mjs 调用 word-extractor。"""
    json_out = os.path.join(os.path.dirname(path), "_tmp_doc.json")
    res = subprocess.run(
        ["node", DOC_EXTRACT_MJS, os.path.abspath(path), json_out],
        capture_output=True, text=True, encoding="utf-8", timeout=300,
    )
    if res.returncode != 0:
        raise RuntimeError(f"word-extractor 失败: {res.stderr[:300]}")
    try:
        with open(json_out, "r", encoding="utf-8") as f:
            data = json.load(f)
        sections = data.get("sections", {})
        order = ["风机", "集中式光伏", "工商业分布式", "生物质"]
        return [sections[k] for k in order if k in sections]
    finally:
        if os.path.exists(json_out):
            os.unlink(json_out)


def normalize_table_header(tbl: List[List[str]]) -> List[List[str]]:
    """把任意表头规范为 5 列标准表头。"""
    if not tbl:
        return tbl
    if not tbl[0] or "序号" not in str(tbl[0][0]):
        return [["序号", "项目编码", "项目名称", "装机容量(MW)", "项目所在地"]] + tbl
    tbl[0] = ["序号", "项目编码", "项目名称", "装机容量(MW)", "项目所在地"]
    return tbl


def parse_row_cells(cells: List[str]) -> Optional[List[str]]:
    """从 Word 单元格行解析 [序号, 编码, 名称, 容量, 地址]。"""
    if not cells:
        return None
    if not re.match(r"^\d{1,4}$", cells[0]):
        return None
    serial = cells[0]

    code = None
    code_idx = -1
    for i in range(1, len(cells)):
        if re.match(r"^[A-Z]{2,3}\d{10,}[A-Z0-9]*$", cells[i]):
            code = cells[i]
            code_idx = i
            break
    if code_idx == -1:
        return None

    cap = None
    cap_idx = -1
    for i in range(code_idx + 1, len(cells)):
        v = cells[i]
        if not re.match(r"^\d+(\.\d+)?$", v):
            continue
        if re.match(r"^\d{4}$", v) and 2020 <= int(v) <= 2039:
            continue
        cap = v
        cap_idx = i
        break
    if cap_idx == -1:
        return None

    name = "".join(cells[code_idx + 1: cap_idx]) if cap_idx > code_idx + 1 else ""
    loc = "".join(cells[cap_idx + 1:]) if cap_idx + 1 < len(cells) else ""
    return [serial, code, name, cap, loc]
