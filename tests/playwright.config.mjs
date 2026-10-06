import { defineConfig } from '@playwright/test';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  testDir: '.',
  testMatch: 'assets.spec.mjs',
  fullyParallel: false,
  workers: 1,
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  use: {
    browserName: 'chromium',
    baseURL: 'http://127.0.0.1:4173',
    viewport: { width: 1440, height: 900 },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    launchOptions: process.env.SKILL_TEST_BROWSER_PATH
      ? { executablePath: process.env.SKILL_TEST_BROWSER_PATH, args: ['--no-proxy-server'] }
      : {},
  },
  webServer: {
    command: 'node tests/serve-fixture.mjs',
    cwd: fileURLToPath(new URL('../', import.meta.url)),
    url: 'http://127.0.0.1:4173/tests/fixtures/website.html',
    reuseExistingServer: false,
    timeout: 10_000,
  },
});
