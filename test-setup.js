import { readFileSync } from 'fs';
import { resolve } from 'path';

const html = readFileSync(resolve(process.cwd(), 'index.html'), 'utf-8');
document.documentElement.innerHTML = html;
