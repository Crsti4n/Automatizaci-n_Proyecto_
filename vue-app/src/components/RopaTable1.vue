<script setup>
import { ref, onMounted } from 'vue';  // Importación de Vue para manejar estados reactivos y el ciclo de vida
import DataTable from 'primevue/datatable';  // Importación de PrimeVue DataTable
import Column from 'primevue/column'; // 🔹 Importación de PrimeVue Column (se había olvidado comentar)

// Definición de las listas reactivas para almacenar los datos recibidos de los WebSockets
const ropaLista1 = ref([]);
const ropaLista2 = ref([]);

// 🔹 Hacer accesibles las listas en la consola del navegador (útil para depuración)
window.ropaLista1 = ropaLista1;
window.ropaLista2 = ropaLista2;

console.log("📌 ropaLista1 inicial:", ropaLista1.value);
console.log("📌 ropaLista2 inicial:", ropaLista2.value);

// Función para conectar con WebSockets y recibir datos en tiempo real
function conectarWebSocket(url, lista) {
    const socket = new WebSocket(url);

    socket.onmessage = (event) => {
        console.log(`📩 Mensaje recibido de ${url}:`, event.data);
        try {
            const producto = JSON.parse(event.data);  // Convertir el mensaje JSON en un objeto
            console.log("✅ Producto parseado correctamente:", producto);

            // 🔹 Agregar ruta de imagen basada en el tipo de producto
            producto.imagen = `/images/${producto.tipo.toLowerCase()}.png`;

            lista.value.unshift(producto);  // Agregar el producto al inicio de la lista
            console.log("🔄 Estado de la lista actualizada:", lista.value);
        } catch (error) {
            console.error("❌ Error al procesar el mensaje:", error);
        }
    };

    // Evento cuando la conexión se abre correctamente
    socket.onopen = () => console.log(`Conectado a ${url}`);

    // Manejo de errores en la conexión
    socket.onerror = (error) => console.error(`Error en WebSocket ${url}:`, error);

    // Si la conexión se cierra, se reintenta la conexión después de 3 segundos
    socket.onclose = () => {
        console.warn(`WebSocket ${url} cerrado. Reintentando...`);
        setTimeout(() => conectarWebSocket(url, lista), 3000);
    };
}

// Iniciar la conexión WebSocket cuando el componente se monta
onMounted(() => {
    conectarWebSocket("ws://localhost:8000/ws/consumer1", ropaLista1);
    conectarWebSocket("ws://localhost:8000/ws/consumer2", ropaLista2);
});
</script>

<template>
  <div class="p-5">
    <h2 class="text-xl font-bold mb-3 text-center">📦 Mensajes Recibidos de RabbitMQ</h2>

    <div class="grid grid-cols-2 gap-8">
      <!-- Interfaz de Consumer 1 -->
      <div class="border p-4 rounded-lg shadow-lg bg-white">
        <h3 class="text-lg font-bold mb-2 text-blue-500 text-center">🟢 Datos de Consumer 1</h3>
        <DataTable :value="ropaLista1" stripedRows class="p-datatable-sm">
          <Column header="Imagen">
            <template #body="slotProps">
              <img
                :src="slotProps.data.imagen"
                alt="Imagen no encontrada"
                class="w-16 h-16 object-cover rounded-md"
                @error="(e) => e.target.src = '/images/default.png'"  <!-- 🔹 Imagen por defecto si no se encuentra -->
              />
            </template>
          </Column>
          <Column field="tipo" header="Tipo"></Column>
          <Column field="color" header="Color"></Column>
          <Column field="talla" header="Talla"></Column>
          <Column field="precio" header="Precio" :sortable="true"></Column> <!-- 🔹 Precio ordenable -->
        </DataTable>
      </div>

      <!-- Interfaz de Consumer 2 -->
      <div class="border p-4 rounded-lg shadow-lg bg-white">
        <h3 class="text-lg font-bold mb-2 text-green-500 text-center">🟢 Datos de Consumer 2</h3>
        <DataTable :value="ropaLista2" stripedRows class="p-datatable-sm">
          <Column header="Imagen">
            <template #body="slotProps">
              <img
                :src="slotProps.data.imagen"
                alt="Imagen no encontrada"
                class="w-16 h-16 object-cover rounded-md"
                @error="(e) => e.target.src = '/images/default.png'"
              />
            </template>
          </Column>
          <Column field="tipo" header="Tipo"></Column>
          <Column field="color" header="Color"></Column>
          <Column field="talla" header="Talla"></Column>
          <Column field="precio" header="Precio" :sortable="true"></Column>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<style scoped>
.p-datatable-sm {
  width: 100%;
  text-align: center;
}
</style>

