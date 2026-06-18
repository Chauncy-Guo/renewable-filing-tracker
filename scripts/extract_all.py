#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
入口: 一键提取所有 PDF + Word -> Excel/

用法:
    python scripts/extract_all.py
"""
import io
import sys
from pathlib import Path

# 把 src/python 加入路径
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

# 修复 Windows 控制台编码
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from renewable_extract.extract import extract_all

if __name__ == "__main__":
    extract_all()
