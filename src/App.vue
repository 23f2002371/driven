<template>
  <div id="app">
    <!-- Role Switcher for Demo Purposes -->
    <div class="bg-dark text-white py-1 px-3 d-flex justify-content-between align-items-center" style="font-size: 12px; z-index: 9999; position: relative;">
      <span>DRIVEN Demo Environment | Current Role: <strong>{{ store.currentUserRole.toUpperCase() }}</strong></span>
      <div>
        <button class="btn btn-sm btn-outline-light me-1 py-0" @click="store.currentUserRole = 'home'">Home</button>
        <button class="btn btn-sm btn-outline-light me-1 py-0" @click="store.currentUserRole = 'club_admin'">Club Admin</button>
        <button class="btn btn-sm btn-outline-light me-1 py-0" @click="store.currentUserRole = 'student'">Student</button>
        <button class="btn btn-sm btn-outline-light py-0" @click="store.currentUserRole = 'lab_admin'">Lab Admin</button>
      </div>
    </div>

    <HomeView v-if="store.currentUserRole === 'home'" />
    <ClubAdminView v-else-if="store.currentUserRole === 'club_admin'" />
    <StudentView v-else-if="store.currentUserRole === 'student'" />
    <LabAdminView v-else-if="store.currentUserRole === 'lab_admin'" />
  </div>
</template>

<script setup>
import { store } from './store/mockData';
import HomeView from './components/HomeView.vue';
import ClubAdminView from './components/ClubAdminView.vue';
import StudentView from './components/StudentView.vue';
import LabAdminView from './components/LabAdminView.vue';
</script>