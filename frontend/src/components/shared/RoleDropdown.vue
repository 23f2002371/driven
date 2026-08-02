<template>
  <div class="role-dropdown" ref="dropdownRef">
    <button type="button" class="role-dropdown-trigger" @click="open = !open">
      <i :class="roleIcon" class="role-icon"></i>
      <span>{{ roleLabel }}</span>
      <i class="bi bi-chevron-down" :class="{ rotated: open }"></i>
    </button>
    <div v-if="open" class="role-dropdown-menu">
      <button
        v-for="opt in options"
        :key="opt.value"
        type="button"
        class="role-dropdown-item"
        :class="{ selected: modelValue === opt.value }"
        @click="select(opt.value)"
      >
        <i :class="opt.icon" class="role-item-icon"></i>
        <div class="role-item-text">
          <span class="role-item-label">{{ opt.label }}</span>
          <span class="role-item-desc">{{ opt.desc }}</span>
        </div>
        <i v-if="modelValue === opt.value" class="bi bi-check-lg role-item-check"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: { type: String, default: 'student' }
});

const emit = defineEmits(['update:modelValue']);

const open = ref(false);
const dropdownRef = ref(null);

const options = [
  { value: 'student', label: 'Student', icon: 'bi bi-mortarboard-fill', desc: 'Explore & join clubs' },
  { value: 'club_admin', label: 'Club Admin', icon: 'bi bi-people-fill', desc: 'Manage your club' },
  { value: 'lab_admin', label: 'Lab Admin', icon: 'bi bi-laptop-fill', desc: 'Oversee lab access' },
];

const roleIcon = computed(() => options.find(o => o.value === props.modelValue)?.icon || 'bi bi-person-fill');
const roleLabel = computed(() => options.find(o => o.value === props.modelValue)?.label || 'Select role');

const select = (val) => {
  emit('update:modelValue', val);
  open.value = false;
};

const onClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    open.value = false;
  }
};

onMounted(() => document.addEventListener('click', onClickOutside));
onUnmounted(() => document.removeEventListener('click', onClickOutside));
</script>
