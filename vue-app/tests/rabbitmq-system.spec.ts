import { test, expect } from '@playwright/test';

test('Verificar el flujo completo de RabbitMQ y la Base de Datos', async ({ request }) => {
  console.log("🚀 Iniciando prueba de RabbitMQ y BD");

  const backendUrl = 'http://host.docker.internal:8000';

  // 1️⃣ Enviar un mensaje al backend
  const mensaje = {
    tipo: "Chaqueta",
    color: "Negro",
    talla: "M",
    precio: 79.99
  };

  console.log("📤 Enviando mensaje al backend...");
  const response = await request.post(`${backendUrl}/productos/`, {
    headers: {
      "Content-Type": "application/json"
    },
    data: mensaje
  });

  expect(response.ok()).toBeTruthy();
  console.log("✅ Mensaje enviado correctamente");

  // 2️⃣ Esperar unos segundos para permitir el procesamiento en RabbitMQ
  await new Promise(res => setTimeout(res, 5000));

  // 3️⃣ Consultar la base de datos
  console.log("🔍 Consultando la base de datos...");
  const consulta = await request.get(`${backendUrl}/productos/`);
  const datos = await consulta.json();

  console.log("📥 Datos recibidos:", datos);

  // 4️⃣ Asegurar que el producto está en la BD
  expect(datos).toContainEqual(expect.objectContaining(mensaje));
  console.log("✅ Producto encontrado en la BD");
});
