# -*- coding: utf-8 -*-
"""PDF 文本提取与表格解析。"""
import json
import re
import subprocess
import os
from typing import List, Optional

from .config import PDF_EXTRACT_MJS


# ===== PDF 表格列 x 范围 (基于 pdfjs-dist 文本坐标) =====
COL_SERIAL_X = (60, 100)    # 序号
COL_CODE_X = (110, 200)     # 项目编码
COL_NAME_X = (220, 540)     # 项目名称 (宽列, 跨多 token)
COL_CAP_X = (540, 620)      # 装机容量
COL_LOC_X = (630, 800)      # 项目所在地


def extract_pdf_to_rows(pdf_path: str, json_out: Optional[str] = None) -> List[List[str]]:
    """调用 Node.js pdf_extract.mjs 解析 PDF, 返回标准 5 列表格 (含表头)。

    Args:
        pdf_path: PDF 源文件路径。
        json_out: 临时 JSON 输出路径, 默认在 PDF 同目录生成 _tmp_pdf.json。

    Returns:
        二维列表, 第一行为表头, 后续为数据行。
    """
    if json_out is None:
        json_out = os.path.join(os.path.dirname(pdf_path), "_tmp_pdf.json")

    res = subprocess.run(
        ["node", PDF_EXTRACT_MJS, os.path.abspath(pdf_path), json_out],
        capture_output=True, text=True, encoding="utf-8", timeout=300,
    )
    if res.returncode != 0:
        raise RuntimeError(f"pdfjs 解析失败: {res.stderr[:300]}")

    try:
        rows = _parse_pdf_text_to_table(json_out)
    finally:
        if os.path.exists(json_out):
            os.unlink(json_out)
    return rows


def _parse_pdf_text_to_table(json_path: str) -> List[List[str]]:
    """把 Node.js 输出的 token 列表重组为表格行。"""
    with open(json_path, "r", encoding="utf-8") as f:
        rows_raw = json.load(f)
    rows = []
    in_data = False
    for entry in rows_raw:
        if entry.get("pageBreak"):
            in_data = False
            continue
        tokens = entry.get("tokens", [])
        if not tokens:
            continue
        joined = "|".join(t["str"] for t in tokens)
        if "序号" in joined and "项目编码" in joined:
            in_data = True
            if not rows:
                rows.append(["序号", "项目编码", "项目名称", "装机容量(MW)", "项目所在地"])
            continue
        if not in_data:
            continue
        if len(tokens) == 1 and re.match(r"^\d{1,4}$", tokens[0]["str"].strip()):
            continue
        row = _parse_pdf_row(tokens)
        if row:
            rows.append(row)
    return rows


def _parse_pdf_row(tokens: List[dict]) -> Optional[List[str]]:
    """根据 x 坐标从 token 列表中提取 [序号, 编码, 名称, 容量, 地址]。"""
    serial = None
    serial_idx = -1
    for i, t in enumerate(tokens):
        if COL_SERIAL_X[0] <= t["x"] <= COL_SERIAL_X[1] and re.match(r"^\d{1,5}$", t["str"].strip()):
            serial = t["str"].strip()
            serial_idx = i
            break
    if serial is None:
        return None

    code = None
    code_idx = -1
    for i, t in enumerate(tokens):
        if COL_CODE_X[0] <= t["x"] <= COL_CODE_X[1] and re.match(r"^[A-Z]{2,3}\d{10,}[A-Z0-9]*$", t["str"].strip()):
            code = t["str"].strip()
            code_idx = i
            break
    if code is None:
        return None

    cap = None
    cap_idx = -1
    for i, t in enumerate(tokens):
        v = t["str"].strip()
        if not (COL_CAP_X[0] <= t["x"] <= COL_CAP_X[1]):
            continue
        if not re.match(r"^\d+(\.\d+)?$", v):
            continue
        if re.match(r"^\d{4}$", v) and 2020 <= int(v) <= 2039:
            continue
        cap = v
        cap_idx = i
        break
    if cap is None:
        return None

    name_parts = []
    for i, t in enumerate(tokens):
        if code_idx < i < cap_idx and COL_NAME_X[0] <= t["x"] <= COL_NAME_X[1]:
            v = t["str"].strip()
            if v:
                name_parts.append(v)
    name = "".join(name_parts)

    loc_parts = []
    for i, t in enumerate(tokens):
        if i > cap_idx and COL_LOC_X[0] <= t["x"] <= COL_LOC_X[1]:
            v = t["str"].strip()
            if v:
                loc_parts.append(v)
    loc = "".join(loc_parts)

    return [serial, code, name, cap, loc]
