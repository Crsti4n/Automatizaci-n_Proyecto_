import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    headless: true, // 🔹 Forzar modo headless
    browserName: 'chromium', // O 'firefox', 'webkit' según lo que necesites
  },
});
