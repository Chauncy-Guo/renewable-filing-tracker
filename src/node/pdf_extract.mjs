/**
 * PDF 文本提取 (pdfjs-dist)
 *
 * 调用方式: node pdf_extract.mjs <pdf_path> <out_json>
 *
 * 输出: JSON 数组, 每项为
 *   { y, tokens: [{x, str}, ...] }   普通行
 *   { pageBreak: true }              分页
 */
import fs from 'node:fs';

const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
const data = new Uint8Array(fs.readFileSync(process.argv[2]));
const doc = await pdfjs.getDocument({
    data,
    useSystemFonts: true,
    disableFontFace: true,
}).promise;

const result = [];

// y 聚类容差: 相邻 y 差 <= 8 视为同一行
// PDF 表格中项目名称可能跨 2 行(自动换行),名称 y 与序号 y 差约 7-8
// 但同一行内 token 的 y 差通常 <= 0.5
// 相邻数据行的 y 差约 16-17, 容差 8 不会误合并
const Y_TOL = 8;

for (let p = 1; p <= doc.numPages; p++) {
    const page = await doc.getPage(p);
    const tc = await page.getTextContent();
    const allTokens = [];
    for (const it of tc.items) {
        allTokens.push({ x: it.transform[4], y: it.transform[5], str: it.str });
    }
    allTokens.sort((a, b) => b.y - a.y);
    const clusters = [];
    for (const tk of allTokens) {
        let placed = false;
        for (const c of clusters) {
            if (Math.abs(c.yRef - tk.y) <= Y_TOL) {
                c.items.push(tk);
                c.yRef = (c.yRef * (c.items.length - 1) + tk.y) / c.items.length;
                placed = true;
                break;
            }
        }
        if (!placed) clusters.push({ yRef: tk.y, items: [tk] });
    }
    for (const c of clusters) {
        c.items.sort((a, b) => a.x - b.x);
        result.push({ y: c.yRef, tokens: c.items.map(x => ({ x: x.x, str: x.str })) });
    }
    result.push({ pageBreak: true });
}

fs.writeFileSync(process.argv[3], JSON.stringify(result));
