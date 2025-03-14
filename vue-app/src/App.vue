<script setup>
import RopaTable from './components/RopaTable.vue';
</script>

<template>
  <div class="container mx-auto p-5">
    <h1 class="text-2xl font-bold mb-5">📦 Mensajes Recibidos de RabbitMQ</h1>
    <RopaTable />
  </div>
</template>

<style>
.container {
  max-width: 800px;
  margin: auto;
}
</style>
