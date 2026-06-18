#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
入口: 把 Excel/ 中的单月文件按类型汇总到 汇总/

用法:
    python scripts/merge_excel.py
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from renewable_extract.merge import merge_all

if __name__ == "__main__":
    merge_all()
