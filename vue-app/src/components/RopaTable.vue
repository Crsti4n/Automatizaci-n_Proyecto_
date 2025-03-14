<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const ropaLista1 = ref([]);
const ropaLista2 = ref([]);

window.ropaLista1 = ropaLista1;  // 🔹 Hacer accesibles en consola
window.ropaLista2 = ropaLista2;

console.log("📌 ropaLista1 inicial:", ropaLista1.value);
console.log("📌 ropaLista2 inicial:", ropaLista2.value);

function conectarWebSocket(url, lista) {
    const socket = new WebSocket(url);

    socket.onmessage = (event) => {
        console.log(`📩 Mensaje recibido de ${url}:`, event.data);
        try {
            const producto = JSON.parse(event.data);
            console.log("✅ Producto parseado correctamente:", producto);

            // 🔹 Agregar ruta de imagen basada en el tipo de producto
            producto.imagen = `/images/${producto.tipo.toLowerCase()}.png`;

            lista.value.unshift(producto);
            console.log("🔄 Estado de la lista actualizada:", lista.value);
        } catch (error) {
            console.error("❌ Error al procesar el mensaje:", error);
        }
    };

    socket.onopen = () => console.log(`Conectado a ${url}`);
    socket.onerror = (error) => console.error(`Error en WebSocket ${url}:`, error);
    socket.onclose = () => {
        console.warn(`WebSocket ${url} cerrado. Reintentando...`);
        setTimeout(() => conectarWebSocket(url, lista), 3000);
    };
}

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
