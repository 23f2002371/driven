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
      <button class="btn-logout" @click="store.currentUserRole = 'home'">
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
