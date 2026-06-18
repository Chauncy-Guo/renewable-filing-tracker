# -*- coding: utf-8 -*-
"""路径与文件名常量集中管理。"""
import os

# 项目根目录 (config.py 所在包的上两级)
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PACKAGE_DIR)))

# 输出根目录: 所有数据产物 (原始 / 中间 / 汇总 / 文档) 都放在这里
OUT_ROOT = os.path.join(ROOT_DIR, "output")

# 数据目录
PDF_DIR = os.path.join(OUT_ROOT, "PDFs")      # 原始 PDF/Word 源文件
XLSX_DIR = os.path.join(OUT_ROOT, "Excel")    # 提取后的 Excel
SUMMARY_DIR = os.path.join(OUT_ROOT, "汇总")  # 汇总结果
DOCS_DIR = os.path.join(OUT_ROOT, "docs")    # 项目文档 (与代码解耦)

# 临时文件 (Node.js 调用)
NODE_DIR = os.path.join(ROOT_DIR, "src", "node")
PDF_EXTRACT_MJS = os.path.join(NODE_DIR, "pdf_extract.mjs")
DOC_EXTRACT_MJS = os.path.join(NODE_DIR, "word_extract.mjs")

# 别名 (向下兼容)
OUT_DIR = SUMMARY_DIR

# 确保输出目录存在
for d in (OUT_ROOT, PDF_DIR, XLSX_DIR, SUMMARY_DIR):
    os.makedirs(d, exist_ok=True)

# 标准表头
HEADER = ["序号", "项目编码", "项目名称", "装机容量(MW)", "项目所在地", "项目月份"]

# 工商业分布式光伏 PDF 文件名 (按时间顺序)
INDUSTRIAL_PDFS = [
    "24年9月份工商业分布式光伏建档立卡数据.pdf",
    "24年10月份工商业分布式光伏建档立卡数据.pdf",
    "24年11月份工商业分布式光伏建档立卡数据.pdf",
    "24年12月份工商业分布式光伏建档立卡数据.pdf",
    "25年1月份分布式光伏建档立卡数据.pdf",
    "25年2月份工商业分布式光伏建档立卡数据.pdf",
]

# 全国新能源装机 Word 文件 (按时间顺序)
WORD_FILES = [
    ("24年5月份全国新能源装机建档立卡数据.doc", "doc"),
    ("24年6月份全国新能源装机建档立卡数据.docx", "docx"),
    ("24年7月份全国新能源装机建档立卡数据.docx", "docx"),
    ("24年8月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年3月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年4月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年5月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年6月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年7月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年8月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年9月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年10月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年11月份全国新能源装机建档立卡数据.docx", "docx"),
    ("25年12月份全国新能源装机建档立卡数据.docx", "docx"),
    ("26年1月份全国新能源装机建档立卡数据.docx", "docx"),
    ("26年3月份全国新能源装机建档立卡数据.docx", "docx"),
    ("26年4月份全国新能源装机建档立卡数据.docx", "docx"),
]
