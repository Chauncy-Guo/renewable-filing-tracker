# -*- coding: utf-8 -*-
"""Word 表格类型识别 (根据首行项目编码前缀)。"""
from typing import Optional, List


def detect_type(tbl: List[List[str]]) -> Optional[str]:
    """根据表中数据行的项目编码前缀判断该表属于哪一类。

    编码前缀规则 (来自国能新能〔xxxx〕xx 号建档立卡项目编码):
        PW...    -> 风机
        PPD...   -> 工商业分布式光伏
        PPC/PPS  -> 集中式光伏
        PB...    -> 生物质 (含垃圾焚烧/沼气)

    Args:
        tbl: 二维列表, 第一行为表头, 后续为数据行, 第二列为项目编码。

    Returns:
        '风机' | '工商业分布式' | '集中式光伏' | '生物质' | None
    """
    for row in tbl[1:6]:
        if not row or len(row) < 2:
            continue
        code = str(row[1] or "").strip()
        if not code:
            continue
        up = code.upper()
        if up.startswith("PPD"):
            return "工商业分布式"
        if up.startswith("PPC") or up.startswith("PPS") or up.startswith("PP"):
            return "集中式光伏"
        if up.startswith("PW"):
            return "风机"
        if up.startswith("PB"):
            return "生物质"
        break
    return None
