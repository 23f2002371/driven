<template>
  <div class="stat-card glass">
    <div>
      <span class="text-muted small fw-bold text-uppercase tracking-wide">{{ title }}</span>
      <div class="stat-value gradient-text">{{ value }}</div>
    </div>
    <div class="stat-icon">
      <i class="bi" :class="'bi-' + icon"></i>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: [Number, String], required: true },
  icon: { type: String, default: 'bar-chart-fill' }
});
</script>
