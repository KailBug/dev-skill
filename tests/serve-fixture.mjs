import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript' };
const allowed = new Set([
  '/tests/fixtures/website.html',
  '/skills/website/minimal-product-website/assets/design-system.css',
  '/skills/website/minimal-product-website/assets/reveal.js',
]);
const server = http.createServer((request, response) => {
  const name = new URL(request.url, 'http://127.0.0.1').pathname;
  if (!allowed.has(name)) {
    response.writeHead(404);
    response.end('Not found');
    return;
  }
  const file = path.join(root, name.slice(1));
  response.writeHead(200, { 'Content-Type': types[path.extname(file)] });
  fs.createReadStream(file).pipe(response);
});
server.listen(4173, '127.0.0.1');
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.close(() => process.exit(0)));
