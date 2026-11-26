import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { runInNewContext } from 'node:vm';

const site = new URL('../site/', import.meta.url);
const read = name => readFileSync(new URL(name, site), 'utf8');
const loader = read('dataflare.js');

function sdkRequests(pathname, navigator = {}) {
  const scripts = [];
  const window = {};
  const document = {
    currentScript: { dataset: { enabled: 'true' } },
    createElement: () => ({ addEventListener() {} }),
    head: { append: element => scripts.push(element.src) },
  };
  runInNewContext(loader, { window, document, location: { pathname }, navigator });
  return { scripts, config: window.dataflare._internal.CONFIG };
}

test('only the product page includes the first-party loader', () => {
  assert.match(read('index.html'), /<script defer src="\/dataflare\.js" data-enabled="true"><\/script>/);
  assert.doesNotMatch(read('overlay.html'), /dataflare\.js|observe\.gmac\.io/);
  const { scripts, config } = sdkRequests('/');
  assert.deepEqual(scripts, ['https://observe.gmac.io/s.js']);
  assert.equal(config.project, 'shuffledeck');
  assert.equal(config.persistence, 'cookieless');
  assert.equal(config.identify, false);
});

test('the overlay, device paths, and browser privacy signals suppress the SDK', () => {
  for (const pathname of ['/overlay', '/overlay.html', '/device/sample']) {
    assert.deepEqual(sdkRequests(pathname).scripts, []);
  }
  assert.deepEqual(sdkRequests('/', { doNotTrack: '1' }).scripts, []);
  assert.deepEqual(sdkRequests('/', { globalPrivacyControl: true }).scripts, []);
});
