const { test, expect, chromium } = require('@playwright/test');

test('OpenGlaze UI smoke', async () => {
  const url = process.env.OPENGLAZE_URL || 'http://localhost:18771';
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', (err) => errors.push(`pageerror: ${err.message}`));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(`console error: ${msg.text()}`);
  });
  page.on('response', (response) => {
    if (response.status() >= 400) errors.push(`http ${response.status()}: ${response.url()}`);
  });

  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: '/tmp/openglaze-home.png', fullPage: true });
  await expect(page.locator('.logo')).toContainText('OpenGlaze');
  await expect(page).toHaveTitle(/OpenGlaze/);

  const apiGlazes = await page.evaluate(async () => {
    const r = await fetch('/api/glazes');
    const data = await r.json();
    return { ok: r.ok, count: data.length, blue: data.filter(g => g.family === 'blue').length };
  });
  expect(apiGlazes.ok).toBeTruthy();
  expect(apiGlazes.count).toBeGreaterThan(0);

  // Regression (audit ledger row 11): with the family-key mismatch, the All
  // Glazes view rendered nothing even though the API served every seeded
  // glaze. The view must list everything the API returns, and a family
  // filter must match the API's singular lowercase family values.
  await page.click('[data-view="glazes"]');
  await page.waitForTimeout(250);
  const familySections = await page.locator('.glaze-family-section').count();
  const renderedCards = await page.locator('.glaze-detail-card').count();
  expect(familySections).toBeGreaterThan(0);
  expect(renderedCards).toEqual(apiGlazes.count);

  expect(apiGlazes.blue).toBeGreaterThan(0);
  await page.click('.family-filter[data-family="Blues"]');
  await page.waitForTimeout(250);
  const blueCards = await page.locator('.glaze-detail-card').count();
  expect(blueCards).toEqual(apiGlazes.blue);
  await page.click('.family-filter[data-family="all"]');
  await page.waitForTimeout(250);

  for (const view of [
    'glazes',
    'photos',
    'studio',
    'progress',
    'predictions',
    'tips',
    'canvas',
  ]) {
    await page.click(`[data-view="${view}"]`);
    await page.waitForTimeout(250);
  }

  await page.click('.search-trigger');
  await page.waitForTimeout(250);
  await page.keyboard.press('Escape');

  await page.click('button:has-text("Ask Kama")');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/openglaze-kama.png', fullPage: true });

  const visibleText = await page.locator('body').innerText();
  for (const expected of ['OpenGlaze', 'Combinations', 'All Glazes']) {
    expect(visibleText).toContain(expected);
  }
  expect(errors).toEqual([]);
  await browser.close();
  console.log(
    JSON.stringify({
      apiGlazes: apiGlazes.count,
      screenshots: ['/tmp/openglaze-home.png', '/tmp/openglaze-kama.png'],
    })
  );
});
