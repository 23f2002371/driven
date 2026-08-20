<template>
  <div class="oauth-callback">
    <div class="oauth-callback-card">
      <div class="spinner-border text-primary mb-3" role="status"></div>
      <h5>{{ status }}</h5>
      <p v-if="error" class="oauth-error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { store } from '../store/mockData';
import * as api from '../api/auth';

const route = useRoute();
const router = useRouter();
const status = ref('Completing your sign in...');
const error = ref('');

const roleHome = {
  student: '/student-dashboard',
  club_admin: '/clubAdmin-dashboard',
  lab_admin: '/labAdmin-dashboard'
};

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : null;

  if (!token) {
    error.value = 'Missing authentication token.';
    status.value = 'Sign in failed';
    setTimeout(() => {
      if (window.opener && !window.opener.closed) {
        window.close();
      } else {
        router.replace('/home');
      }
    }, 2000);
    return;
  }

  // If opened as a popup window:
  if (window.opener && !window.opener.closed) {
    try {
      window.opener.postMessage({ type: 'OAUTH_SUCCESS', token }, '*');
      window.close();
      return;
    } catch {
      // If postMessage fails, fallback to direct in-window redirect below
    }
  }

  try {
    const user = await api.me(token);
    store.setAuth(token, user);
    window.history.pushState(null, '', window.location.href);
    router.replace(roleHome[user.role] || '/home');
  } catch (err) {
    status.value = 'Sign in failed';
    error.value = err.message;
    setTimeout(() => router.replace('/home'), 2500);
  }
});
</script>

<style scoped>
.oauth-callback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0b111f;
}
.oauth-callback-card {
  text-align: center;
  color: #e2e8f0;
  padding: 2.5rem 3rem;
  border-radius: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
}
.oauth-callback-card h5 {
  margin: 0;
  font-size: 1rem;
}
.oauth-error {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #f87171;
}
</style>