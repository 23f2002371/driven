<template>
  <header class="top-header">
    <h5 class="top-header-title">{{ title }}</h5>
    <div class="top-header-right">
      <div class="notification-btn" @click="$emit('notif-click')">
        <i class="bi bi-bell"></i>
        <span v-if="notifCount > 0" class="notification-badge">{{ notifCount > 99 ? '99+' : notifCount }}</span>
      </div>
      <span class="role-badge">{{ badgeText }}</span>
      <div class="avatar-circle">
        {{ avatarInitials }}
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  badgeText: { type: String, required: true },
  badgeClass: { type: String, default: '' },
  avatarInitials: { type: String, required: true },
  notifCount: { type: Number, default: 0 }
});

defineEmits(['notif-click']);
</script>

<style scoped>
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0;
  border-bottom: none;
}
.top-header-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: -0.3px;
}
.top-header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.notification-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8892a8;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.notification-btn:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.15);
  color: #e2e8f0;
}
.notification-badge {
  position: absolute;
  top: -4px; right: -4px;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #fb7185;
  border: 2px solid #090B16;
  color: #fff;
  font-size: 0.55rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
  line-height: 1;
}
.role-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: rgba(109,93,246,0.12);
  color: #a5b4fc;
  border: 1px solid rgba(109,93,246,0.15);
  letter-spacing: 0.2px;
}
.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6D5DF6, #8B5CF6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.7rem;
  box-shadow: 0 2px 8px rgba(109,93,246,0.3);
  letter-spacing: 0.5px;
}
</style>
