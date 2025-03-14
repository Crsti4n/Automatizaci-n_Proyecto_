import { test, expect } from '@playwright/test';

test('Verificar que los mensajes de RabbitMQ aparecen en las tablas', async ({ page }) => {
  await page.goto('http://localhost:5173');  // Asegúrate de que la página esté cargada

  // Esperar que ambas tablas tengan al menos 1 fila
  const tableConsumer1 = await page.locator('.consumer1-table .p-datatable tbody tr');
  const tableConsumer2 = await page.locator('.consumer2-table .p-datatable tbody tr');

  // Verificar que ambas tablas tienen al menos 1 fila
  await expect(tableConsumer1).toHaveCount(1, { timeout: 5000 });
  await expect(tableConsumer2).toHaveCount(1, { timeout: 5000 });
});
