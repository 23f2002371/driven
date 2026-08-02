<template>
  <div>
    <div class="calendar-grid mb-2 text-center text-muted small fw-bold">
      <div>S</div><div>M</div><div>T</div><div>W</div><div>T</div><div>F</div><div>S</div>
    </div>
    <div class="calendar-grid">
      <div
        v-for="day in 31"
        :key="day"
        class="calendar-day"
        :class="isBooked(day) ? 'day-booked' : 'day-available'"
        @click="$emit('toggle-date', day)"
      >
        {{ day }}
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  bookedDates: { type: Array, default: () => [] }
});

defineEmits(['toggle-date']);

const isBooked = (day) => props.bookedDates.includes(day);
</script>
