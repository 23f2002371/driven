<template>
  <div class="copilot-rec">
    <div class="copilot-rec-header">
      <div class="copilot-rec-badge">
        <i :class="'bi bi-' + icon"></i>
        <span>{{ title }}</span>
      </div>
      <i class="bi bi-stars copilot-rec-sparkle"></i>
    </div>
    <p class="copilot-rec-message">{{ message }}</p>
    <button class="copilot-rec-btn" @click="$emit('action')">
      {{ action }}
      <i class="bi bi-arrow-right-short"></i>
    </button>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  icon: String,
  message: String,
  action: String,
});
defineEmits(['action']);
</script>

<style scoped>
.copilot-rec {
  background: linear-gradient(135deg, rgba(79,70,229,0.08), rgba(124,58,237,0.04));
  border: 1px solid rgba(129,140,248,0.12);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.75rem;
  position: relative;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
}
.copilot-rec:hover {
  border-color: rgba(129,140,248,0.25);
  background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(124,58,237,0.06));
}
.copilot-rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}
.copilot-rec-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: #818cf8;
}
.copilot-rec-badge i {
  font-size: 0.7rem;
}
.copilot-rec-sparkle {
  font-size: 0.75rem;
  color: #a78bfa;
  opacity: 0.6;
}
.copilot-rec-message {
  margin: 0 0 0.6rem;
  font-size: 0.82rem;
  color: #cbd5e1;
  line-height: 1.45;
}
.copilot-rec-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
  padding: 0.3rem 0.75rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 700;
  font-family: inherit;
  border: 1px solid rgba(129,140,248,0.15);
  background: rgba(129,140,248,0.08);
  color: #a5b4fc;
  cursor: pointer;
  transition: all 0.2s;
}
.copilot-rec-btn:hover {
  background: rgba(129,140,248,0.15);
  border-color: rgba(129,140,248,0.25);
}
.copilot-rec-btn i {
  font-size: 0.85rem;
  transition: transform 0.2s;
}
.copilot-rec-btn:hover i {
  transform: translateX(2px);
}
</style>
