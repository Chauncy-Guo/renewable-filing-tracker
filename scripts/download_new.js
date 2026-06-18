#!/usr/bin/env node
/**
 * 入口: 一键下载新一批全国新能源装机 Word 文档
 *
 * 步骤:
 *   1. 调用 src/node/query_api.js 获取目标公告列表
 *   2. 调用 src/node/download_word.js 下载所有附件
 *
 * 用法:
 *   node scripts/download_new.js [min_year] [min_month] [max_year] [max_month]
 */
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const NODE_DIR = path.join(ROOT, 'src', 'node');

const args = process.argv.slice(2);
if (args.length < 4) {
    // 默认 2025-03 ~ 2026-04
    args.push('2025', '3', '2026', '4');
}
console.log(`>>> 查询公告: ${args[0]}-${args[1]} ~ ${args[2]}-${args[3]}`);
const q1 = spawnSync('node', [path.join(NODE_DIR, 'query_api.js'), ...args], {
    stdio: 'inherit', cwd: ROOT,
});
if (q1.status !== 0) process.exit(q1.status);

console.log('\n>>> 下载附件');
const q2 = spawnSync('node', [path.join(NODE_DIR, 'download_word.js')], {
    stdio: 'inherit', cwd: ROOT,
});
process.exit(q2.status || 0);
