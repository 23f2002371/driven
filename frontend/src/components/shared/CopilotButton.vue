<template>
  <button class="copilot-fab" @click="$emit('toggle')" :class="{ active: open }">
    <div class="copilot-fab-glow"></div>
    <div class="copilot-fab-inner">
      <svg v-if="!open" class="copilot-fab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        <path d="M2 17l10 5 10-5"/>
        <path d="M2 12l10 5 10-5"/>
      </svg>
      <svg v-else class="copilot-fab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </div>
    <span class="copilot-fab-label">Copilot</span>
  </button>
</template>

<script setup>
defineProps({ open: Boolean });
defineEmits(['toggle']);
</script>

<style scoped>
.copilot-fab {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.1rem 0.7rem 0.9rem;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(79, 70, 229, 0.45);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}
.copilot-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(79, 70, 229, 0.6);
}
.copilot-fab.active {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}
.copilot-fab.active:hover {
  background: rgba(255, 255, 255, 0.12);
}
.copilot-fab-glow {
  position: absolute;
  inset: -4px;
  border-radius: 999px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  opacity: 0.35;
  filter: blur(12px);
  animation: fabPulse 2.5s ease-in-out infinite;
  pointer-events: none;
}
.copilot-fab.active .copilot-fab-glow {
  display: none;
}
@keyframes fabPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.08); }
}
.copilot-fab-inner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}
.copilot-fab-icon {
  width: 20px;
  height: 20px;
}
.copilot-fab-label {
  position: relative;
  font-size: 0.82rem;
  letter-spacing: 0.3px;
}
</style>
