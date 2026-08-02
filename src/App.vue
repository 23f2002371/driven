<template>
  <div id="app">
    <router-view />
    <CopilotButton :open="copilotOpen" @toggle="copilotOpen = !copilotOpen" />
    <CopilotPanel :open="copilotOpen" @close="copilotOpen = false" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { store } from './store/mockData';
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

watch(() => store.currentUserRole, (role) => {
  if (route.name === 'event-details') return;
  const name = routeMap[role];
  if (name && route.name !== name) {
    router.push({ name });
  }
}, { immediate: true });
</script>
