<template>
  <div id="app">
    <router-view />
    <CopilotButton :open="copilotOpen" @toggle="copilotOpen = !copilotOpen" />
    <CopilotPanel :open="copilotOpen" @close="copilotOpen = false" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { store } from './store/mockData';
import * as api from './api/auth';
import CopilotButton from './components/shared/CopilotButton.vue';
import CopilotPanel from './components/shared/CopilotPanel.vue';

const router = useRouter();
const route = useRoute();
const copilotOpen = ref(false);

const routeMap = {
  home: 'home',
  club_admin: 'club-admin',
  student: 'student',
  lab_admin: 'lab-admin'
};

const ignoreRoutes = new Set(['event-details', 'oauth-success']);

watch(() => store.currentUserRole, (role) => {
  if (!route.name || ignoreRoutes.has(route.name)) return;
  const name = routeMap[role];
  if (name && route.name !== name) {
    router.push({ name });
  }
});

const getDashboardRouteName = () => {
  let role = store.currentUserRole;
  if (!role || role === 'home') {
    try {
      const u = JSON.parse(localStorage.getItem('driven_user') || '{}');
      role = u.role || 'student';
    } catch {
      role = 'student';
    }
  }
  return routeMap[role] || 'student';
};

const handlePopState = () => {
  const token = localStorage.getItem('driven_token') || store.token;
  if (token) {
    const target = getDashboardRouteName();
    window.history.pushState(null, '', window.location.href);
    router.replace({ name: target });
  }
};

watch(() => route.fullPath, () => {
  const token = localStorage.getItem('driven_token') || store.token;
  if (token) {
    window.history.pushState(null, '', window.location.href);
  }
}, { immediate: true });

onMounted(async () => {
  window.addEventListener('popstate', handlePopState);

  const token = localStorage.getItem('driven_token') || store.token;
  if (token) {
    window.history.pushState(null, '', window.location.href);
  }

  if (store.token && !store.currentUser) {
    try {
      const user = await api.me(store.token);
      store.setAuth(store.token, user);
    } catch {
      store.logout();
    }
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('popstate', handlePopState);
});
</script>