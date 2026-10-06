import { test, expect } from '@playwright/test';

const fixture = '/tests/fixtures/website.html';
async function load(page) {
  await page.goto(fixture);
  await page.waitForFunction(() => window.fixtureReady);
}

for (const width of [1440, 1024, 390, 320]) {
  test(`layout remains usable at ${width}px`, async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setViewportSize({ width, height: 900 });
    await load(page);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('h1')).toHaveCSS('opacity', '1');
    await expect(page.getByRole('link', { name: '开始使用' })).toBeVisible();
    expect((await page.getByRole('link', { name: '开始使用' }).boundingBox()).height).toBeGreaterThanOrEqual(44);
    await expect(page.locator('#hidden-control')).toBeHidden();
    const code = page.locator('.mpw-command-row code');
    if (width <= 390) {
      expect(await code.evaluate(element => element.scrollWidth > element.clientWidth)).toBe(true);
    }
    const command = await page.locator('.mpw-command').boundingBox();
    const copy = await page.getByRole('button', { name: '复制命令' }).boundingBox();
    expect(copy.x + copy.width).toBeLessThanOrEqual(command.x + command.width);
    expect(errors).toEqual([]);
  });
}

test('keyboard focus immediately reveals nested ancestors', async ({ page }) => {
  await load(page);
  await expect(page.locator('#details')).toHaveCSS('opacity', '0');
  await page.locator('#focus-target').focus();
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
  await expect(page.locator('#nested')).toHaveCSS('opacity', '1');
});

test('scrolling reveals content once', async ({ page }) => {
  await load(page);
  await expect(page.locator('#details')).toHaveCSS('opacity', '0');
  await page.locator('#details').scrollIntoViewIfNeeded();
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
  await page.evaluate(() => scrollTo(0, 0));
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
});

test('reduced motion, including a runtime preference change, keeps content visible', async ({ page }) => {
  await load(page);
  await expect(page.locator('#details')).toHaveCSS('opacity', '0');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
  await expect(page.locator('#details')).toHaveCSS('transform', 'none');
  await load(page);
  await expect(page.locator('.mpw-reveal.is-pending')).toHaveCount(0);
});

test('cleanup restores pending content', async ({ page }) => {
  await load(page);
  await page.evaluate(() => window.disposeFixture());
  await expect(page.locator('.mpw-reveal.is-pending')).toHaveCount(0);
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
});

test('missing IntersectionObserver leaves content visible', async ({ page }) => {
  await page.addInitScript(() => { delete window.IntersectionObserver; });
  await load(page);
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
  await expect(page.locator('.mpw-reveal.is-pending')).toHaveCount(0);
});

test('without JavaScript, content and native FAQ remain usable', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 320, height: 900 } });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:4173' + fixture);
  await expect(page.locator('#details')).toHaveCSS('opacity', '1');
  await expect(page.locator('#hidden-control')).toBeHidden();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.locator('summary').focus();
  await page.keyboard.press('Enter');
  expect(await page.locator('details').evaluate(element => element.open)).toBe(true);
  await context.close();
});
