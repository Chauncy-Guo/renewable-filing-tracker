/**
 * Word (.doc) 文本提取 (word-extractor)
 *
 * 调用方式: node word_extract.mjs <doc_path> <out_json>
 *
 * 输出: JSON 对象 { file, sections: { '风机': [[表头],[数据]...], ... } }
 */
import fs from 'node:fs';
import WordExtractor from 'word-extractor';

const file = process.argv[2];
const outFile = process.argv[3];
const extractor = new WordExtractor();
const doc = await extractor.extract(file);
const text = doc.getBody();
const lines = text.split(/\r?\n/);

const SECTION_KEYS = ['风机', '集中式光伏', '工商业分布式', '生物质'];

// 找所有"表头"行 (序号 + 项目编码)
const tableHeaderLines = [];
for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (/序号/.test(line) && /项目编码/.test(line)) {
        tableHeaderLines.push(i);
    }
}

const tables = [];
for (let i = 0; i < tableHeaderLines.length; i++) {
    const start = tableHeaderLines[i] + 1;
    const end = i + 1 < tableHeaderLines.length ? tableHeaderLines[i + 1] : lines.length;
    tables.push({ header: tableHeaderLines[i], start, end });
}

function parseData(start, end) {
    const data = [];
    for (let i = start; i < end; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        if (/^备注/.test(line) || /^注[:：]/.test(line)) break;
        if (/项目编码.{0,3}内涵|由.{0,10}位字符|项目编码组成|项目编码含义/.test(line)) break;
        const re = /(\d{1,4})\s+(P[A-Z]{2,3}\d{8,}[A-Z0-9]*)\s+(\S(?:[\s\S]*?\S)?)\s+(\d+(?:\.\d+)?)\s+(\S(?:[\s\S]*?\S)?)(?=\s+\d{1,4}\s+P[A-Z]{2,3}\d{8,}|$)/g;
        let m;
        while ((m = re.exec(line)) !== null) {
            const num = m[1];
            const code = m[2];
            let name = m[3].trim().replace(/[,，;；]+$/, '').trim();
            const cap = m[4];
            let loc = m[5].trim().replace(/[,，;；]+$/, '').trim();
            if (/备注|^注/.test(name) || /项目编码/.test(name)) break;
            data.push([num, code, name, cap, loc]);
        }
    }
    return data;
}

const out = { file, sections: {} };
for (let i = 0; i < SECTION_KEYS.length && i < tables.length; i++) {
    const key = SECTION_KEYS[i];
    const t = tables[i];
    const data = parseData(t.start, t.end);
    out.sections[key] = [['序号', '项目编码', '项目名称', '装机容量(MW)', '项目所在地']].concat(data);
}
fs.writeFileSync(outFile, JSON.stringify(out), 'utf8');
