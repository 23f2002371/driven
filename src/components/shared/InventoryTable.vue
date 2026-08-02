<template>
  <div class="card-glass p-4 mb-4">
    <h6 class="fw-bold mb-3" :class="titleClass">{{ title }}</h6>
    <div class="table-responsive">
      <table class="table table-dark table-dark-custom align-middle mb-0" :class="{ 'table-hover-custom': hover }">
        <thead>
          <tr class="text-muted small">
            <th>Equipment</th>
            <th>Category</th>
            <th>{{ countLabel }}</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id || item.key" class="table-row-hover">
            <td class="fw-bold text-light">{{ item.name }}</td>
            <td>
              <span class="category-tag">{{ item.category }}</span>
            </td>
            <td :class="countClass">{{ getValue(item) }}</td>
            <td>
              <slot name="actions" :item="item" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  items: { type: Array, required: true },
  title: { type: String, required: true },
  valueKey: { type: String, default: 'available' },
  countLabel: { type: String, default: 'Available' },
  countClass: { type: String, default: 'fw-bold text-success' },
  titleClass: { type: String, default: 'text-success' },
  hover: { type: Boolean, default: true }
});

const getValue = (item) => item[props.valueKey] ?? 0;
</script>
