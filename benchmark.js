import { JSDOM } from 'jsdom';

const dom = new JSDOM(`<!DOCTYPE html>
<html>
<body>
  <div class="goose">Goose</div>
  <div class="geese">Geese</div>
</body>
</html>`);
const document = dom.window.document;

const gooseBtnCached = document.querySelector('.goose');

const ITERATIONS = 100000;

let start1 = performance.now();
for (let i = 0; i < ITERATIONS; i++) {
  const btn = document.querySelector('.goose');
  btn.classList.add('bounce');
  btn.classList.remove('bounce');
}
let end1 = performance.now();
console.log(`Uncached querySelector: ${end1 - start1} ms`);

let start2 = performance.now();
for (let i = 0; i < ITERATIONS; i++) {
  const btn = gooseBtnCached;
  btn.classList.add('bounce');
  btn.classList.remove('bounce');
}
let end2 = performance.now();
console.log(`Cached variable: ${end2 - start2} ms`);
