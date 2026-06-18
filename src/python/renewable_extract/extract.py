# -*- coding: utf-8 -*-
"""端到端提取流程: PDF + Word -> Excel。"""
import os
import re
from typing import List

from .config import PDF_DIR, XLSX_DIR, INDUSTRIAL_PDFS, WORD_FILES
from .pdf_parser import extract_pdf_to_rows
from .word_parser import (
    extract_docx_tables, extract_doc_tables, normalize_table_header,
)
from .detect_type import detect_type
from .excel_writer import save_xlsx


def _get_ym(name: str):
    """从文件名提取 (yy, mm) 二元组。失败返回 (None, None)。"""
    m = re.search(r"(\d{2})年(\d+)月", name)
    if m:
        return m.group(1), int(m.group(2))
    return None, None


def extract_pdfs(verbose: bool = True) -> List[str]:
    """提取所有工商业分布式 PDF -> Excel。"""
    out_paths = []
    if verbose:
        print("===== 处理 PDF: 工商业分布式光伏 =====", flush=True)
    for pdf in INDUSTRIAL_PDFS:
        fp = os.path.join(PDF_DIR, pdf)
        if not os.path.exists(fp):
            if verbose:
                print(f"  ! 缺失: {pdf}", flush=True)
            continue
        yy, mm = _get_ym(pdf)
        if verbose:
            print(f"处理: {pdf}  (年月: {yy}年{mm}月)", flush=True)
        rows = extract_pdf_to_rows(fp)
        if verbose:
            print(f"  解析出 {len(rows)} 行数据 (含表头)", flush=True)
        out_name = f"{yy}年{mm}月份工商业分布式光伏建档立卡数据.xlsx"
        out_path = os.path.join(XLSX_DIR, out_name)
        save_xlsx(rows, out_path, sheet_name="工商业分布式")
        if verbose:
            print(f"  已保存: {out_path}", flush=True)
        out_paths.append(out_path)
    return out_paths


def extract_words(verbose: bool = True) -> List[str]:
    """提取所有全国新能源装机 Word -> 按类型 Excel。"""
    out_paths = []
    if verbose:
        print("\n===== 处理 Word: 全国新能源装机 =====", flush=True)
    for name, kind in WORD_FILES:
        fp = os.path.join(PDF_DIR, name)
        if not os.path.exists(fp):
            if verbose:
                print(f"  ! 缺失: {name}", flush=True)
            continue
        yy, mm = _get_ym(name)
        if verbose:
            print(f"处理: {name}  (年月: {yy}年{mm}月)", flush=True)

        if kind == "docx":
            tables = extract_docx_tables(fp)
        else:
            tables = extract_doc_tables(fp)

        if not tables:
            if verbose:
                print("  ! 未提取到表格", flush=True)
            continue

        if verbose:
            print(f"  提取到 {len(tables)} 个表", flush=True)

        type_to_tbl = {}
        for tbl in tables:
            tbl = normalize_table_header(tbl)
            if len(tbl) < 2:
                continue
            t = detect_type(tbl)
            if t:
                type_to_tbl.setdefault(t, []).append(tbl)

        for label, tbl_list in type_to_tbl.items():
            merged = tbl_list[0]
            for extra in tbl_list[1:]:
                merged = merged + extra[1:]  # 跳过额外表的表头
            out_name = f"{yy}年{mm}月份{label}建档立卡数据.xlsx"
            out_path = os.path.join(XLSX_DIR, out_name)
            save_xlsx(merged, out_path, sheet_name=label[:31])
            if verbose:
                print(f"    已保存 {label}: {len(merged)} 行 -> {out_name}", flush=True)
            out_paths.append(out_path)
    return out_paths


def extract_all(verbose: bool = True) -> List[str]:
    """主入口: 一次跑完所有 PDF + Word -> Excel。"""
    pdfs = extract_pdfs(verbose=verbose)
    words = extract_words(verbose=verbose)
    if verbose:
        print("\n===== 全部完成 =====", flush=True)
        print("\nExcel 文件夹内容:", flush=True)
        for f in sorted(os.listdir(XLSX_DIR)):
            fp = os.path.join(XLSX_DIR, f)
            size_kb = os.path.getsize(fp) / 1024
            print(f"  {f}  ({size_kb:.2f} KB)", flush=True)
    return pdfs + words
