<template>
  <aside class="sidebar">
    <div class="sidebar-brand">DRIVEN</div>
    <nav class="sidebar-nav">
      <div
        v-for="item in navItems"
        :key="item.key"
        class="nav-item"
        :class="{ active: activeTab === item.key }"
        @click="$emit('update:activeTab', item.key)"
      >
        <i class="bi nav-icon" :class="'bi-' + item.icon"></i>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
      </div>
    </nav>
    <div class="sidebar-footer">
      <button
        class="btn-sidebar-copilot"
        :class="{ active: store.isCopilotOpen }"
        @click="store.toggleCopilot()"
        title="Open DRIVEN Copilot"
      >
        <div class="copilot-btn-glow"></div>
        <div class="copilot-icon-wrap">
          <svg class="copilot-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <span class="copilot-label">DRIVEN Copilot</span>
        <span class="copilot-pill">AI</span>
      </button>

      <button class="btn-logout" @click="store.logout()">
        <i class="bi bi-box-arrow-right me-2"></i>Logout
      </button>
    </div>
  </aside>
</template>

<script setup>
import { store } from '../../store/mockData';

defineProps({
  navItems: { type: Array, required: true },
  activeTab: { type: String, required: true }
});

defineEmits(['update:activeTab']);
</script>

<style scoped>
.sidebar {
  width: 240px;
  min-height: 100vh;
  background: #0b111f;
  border-right: 1px solid rgba(255,255,255,0.05);
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  z-index: 1000;
}
.sidebar-brand {
  font-size: 1.4rem;
  font-weight: 800;
  padding: 1.5rem 1.5rem 1.25rem;
  letter-spacing: -0.5px;
  color: #ffffff;
}
.sidebar-nav {
  flex: 1;
  padding: 0.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4,0,0.2,1);
  position: relative;
  color: #8892a8;
  margin-bottom: 1px;
  font-weight: 500;
}
.nav-item:hover {
  background: rgba(255,255,255,0.05);
  color: #e2e8f0;
}
.nav-item.active {
  background: rgba(99,102,241,0.1);
  color: #c7d2fe;
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: -0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 0 3px 3px 0;
  background: linear-gradient(180deg, #818cf8, #a78bfa);
}
.nav-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
  color: #64748b;
}
.nav-item:hover .nav-icon {
  color: #94a3b8;
}
.nav-item.active .nav-icon {
  color: #a5b4fc;
}
.nav-label {
  font-size: 0.85rem;
  font-weight: 500;
}
.nav-item.active .nav-label {
  font-weight: 600;
}
.nav-badge {
  margin-left: auto;
  background: rgba(244,63,94,0.15);
  color: #fb7185;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  min-width: 18px;
  text-align: center;
  line-height: 1.4;
}
.sidebar-footer {
  padding: 0.75rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  margin: 0 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.btn-sidebar-copilot {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.15) 100%);
  border: 1px solid rgba(129, 140, 248, 0.28);
  color: #e0e7ff;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.btn-sidebar-copilot:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.22) 0%, rgba(168, 85, 247, 0.28) 100%);
  border-color: rgba(168, 85, 247, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.25);
  color: #ffffff;
}
.btn-sidebar-copilot.active {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(79, 70, 229, 0.45);
}
.copilot-btn-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, transparent 65%);
  pointer-events: none;
}
.copilot-icon-wrap {
  width: 24px;
  height: 24px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.btn-sidebar-copilot.active .copilot-icon-wrap {
  background: rgba(255, 255, 255, 0.2);
}
.copilot-svg-icon {
  width: 15px;
  height: 15px;
  color: #a78bfa;
}
.btn-sidebar-copilot.active .copilot-svg-icon {
  color: #ffffff;
}
.copilot-label {
  flex: 1;
  text-align: left;
  font-size: 0.82rem;
  letter-spacing: -0.2px;
}
.copilot-pill {
  font-size: 0.62rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: rgba(168, 85, 247, 0.3);
  border: 1px solid rgba(192, 132, 252, 0.4);
  color: #e9d5ff;
}
.btn-sidebar-copilot.active .copilot-pill {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
}
.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem;
  border: 1px solid rgba(239,68,68,0.12);
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #f87171;
  background: rgba(239,68,68,0.06);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-logout:hover {
  background: rgba(239,68,68,0.12);
  border-color: rgba(239,68,68,0.25);
  transform: translateY(-1px);
}
</style>
