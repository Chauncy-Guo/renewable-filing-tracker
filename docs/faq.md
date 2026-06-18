# 常见问题与维护

## Q1. 公告页的附件是相对路径怎么办?

`download_word.js` 检测到 `href` 不以 `http` 开头时会用以下规则拼接:

```js
attachUrl = new URL(t.url).origin + new URL(t.url).pathname.replace(/[^/]+$/, '') + attachPath
```

如未来公告域名变化, 只需调整 `query_api.js` 顶部的 `API` 常量。

## Q2. 下载的 .docx 文件其实是 .doc 怎么办?

部分老公告的附件扩展名是 `.docx`, 实际内容是 OLE2 格式。
`download_word.js` 通过文件头前 8 字节判断真实类型:

| 文件头 | 真实类型 |
| --- | --- |
| `504B0304` | .docx (ZIP) |
| `D0CF11E0` | .doc (OLE2) |
| 其它 | .bin (未识别, 保留原扩展名) |

识别后会自动重命名为正确的扩展名。

## Q3. 25 年 3 月起的 Word 表格变少了?

老格式 (24 年 5~8 月) Word 内有 4 张表 (风机 / 集中式光伏 / 工商业分布式 / 生物质),
新格式 (25 年 3 月起) 只剩 3 张表 (少了工商业分布式, 改为单独 PDF 发布)。

`detect_type` 改为按每张表的项目编码前缀动态判断, 不再依赖固定顺序:

| 编码前缀 | 类型 |
| --- | --- |
| `PW` | 风机 |
| `PPC` / `PPS` | 集中式光伏 |
| `PPD` | 工商业分布式 |
| `PB` | 生物质 |

## Q4. 工商业分布式数据来源切换?

- 24 年 5~8 月: 在 Word 内 (表 3)
- 24 年 9 月起: 单独 PDF 公告

`extract.py` 内的 `extract_pdfs` 处理 PDF 部分, `extract_words` 处理 Word 部分, 互不影响。

## Q5. PDF 表格里项目名称换行导致错位?

`pdf_extract.mjs` 按 y 坐标聚类 (容差 Y_TOL=8),
把同行的所有 token 合并到一条记录, `pdf_parser._parse_pdf_row` 再用 x 范围分列。

如果将来 PDF 模板变化, 只需调整 `pdf_parser.py` 顶部的 5 个 `COL_*_X` 常量。

## Q6. 控制台中文乱码?

Windows PowerShell 默认 GBK 编码。运行前先执行:

```powershell
$env:PYTHONIOENCODING = "utf-8"
chcp 65001 | Out-Null
```

或者改用 Windows Terminal / VS Code 集成终端。

## Q7. 怎么新增/移除一个汇总类别?

编辑 `src/python/renewable_extract/merge.py` 底部的 `merge_all` 列表:

```python
for name, pred, with_col in [
    ("工商业分布式光伏", is_industrial, True),
    ("集中式光伏", is_central, True),
    ("风机", is_wind, True),
    ("生物质", is_biomass, True),
    # 新增一行: ("新类型", is_xxx, True)
]:
    ...
```

并在文件顶部添加对应的谓词:

```python
def is_xxx(f: str) -> bool:
    return "新类型" in f
```

## Q8. 临时文件怎么清理?

`output/PDFs/_tmp_*.json` 是 Node 子进程与 Python 之间的中间产物, 每次运行结束会自动删除。
如果意外中断残留了, 可以手动:

```bash
del output\PDFs\_tmp_*.json
```

## Q9. 依赖升级注意事项

- `pdfjs-dist` 大版本升级时, `pdf_extract.mjs` 的 import 路径可能要改
  (本项目使用 `pdfjs-dist/legacy/build/pdf.mjs`)
- `word-extractor` 解析 OLE2 文档较慢, 24 年 5 月的 .doc 解析可能需 30s+
- `openpyxl` 升级到大版本 (>3.2) 需检查 `Font` / `PatternFill` API 是否变化

## Q10. 如果公告 API 加了鉴权?

需要在 `query_api.js` 的 `fetch` 调用中加 `headers: { Cookie, Authorization }`,
并把 cookie 放在 `.env` 中 (新增 `dotenv` 依赖)。

## Q11. 移动后根目录还残留一个空 `Excel/` 目录删不掉?

如果之前在 `Excel/` 里有大量文件, robocopy 移动过程中 Windows 资源管理器可能会缓存对
该目录的句柄, 导致 `Excel/` 成为不可删除的空目录 (PowerShell / .NET / cmd 都报"另一进程占用")。

此时可在文件资源管理器中右键 → 关闭占用 → 删除。
或者: 关闭所有打开 `Excel/` 的程序 (VS Code / Excel / 文件预览) 后再删除。

代码本身不受影响, 实际数据全部在 `output/Excel/` 下。

## Q12. 为什么 `output/` 下有 `.gitkeep`?

`output/` 目录的 4 个子目录 (`PDFs/` `Excel/` `汇总/` `docs/`) 都预先放了一个 `.gitkeep`
占位文件, 方便 `git clone` 后立刻有完整的目录结构。
当脚本真正生成数据时, 这些 `.gitkeep` 会与新文件共存, 不会干扰。

## Q13. `.gitignore` 为什么不跟踪 `output/` 下的文件?

按设计, `output/` 是**纯运行时产物**, 全部由脚本生成:

- `output/PDFs/` — 从公告系统下载, 重新跑一次会刷新
- `output/Excel/` — 由 `extract_all.py` 生成
- `output/汇总/` — 由 `merge_excel.py` 生成
- `output/docs/` — 项目说明文档, 放在此处方便和产物一起打包

如果把这些全入仓, 仓库会迅速膨胀且每次 commit 都有大量 diff。
`.gitignore` 排除了所有数据文件和文档, 仅保留 4 个 `.gitkeep` 让目录结构入仓。

如需把某类文档 (例如 `output/docs/architecture.md`) 加入版本管理, 在 `.gitignore` 中
加一行 `!output/docs/architecture.md` 即可 (白名单语法)。
