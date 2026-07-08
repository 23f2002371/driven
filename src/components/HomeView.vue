<template>
    <div class="container-fluid min-vh-100 d-flex flex-column justify-content-between bg-white">
      <header class="d-flex justify-content-between align-items-center p-4 border-bottom">
        <h3 class="fw-bold text-primary m-0">DRIVEN</h3>
        <div>
          <button class="btn btn-outline-primary me-2 px-4 rounded-pill" @click="showAuthModal('login')">Login</button>
          <button class="btn btn-primary px-4 rounded-pill" @click="showAuthModal('register')">Register</button>
        </div>
      </header>
  
      <main class="container my-auto py-5">
        <div class="row align-items-center">
          <div class="col-lg-6 mb-4 mb-lg-0">
            <h1 class="display-4 fw-bold mb-3" style="background: linear-gradient(135deg, #0f172a 0%, #4f46e5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1.5px;">
  Manage Your Messy Tasks, Seamlessly
</h1>
            <p class="lead text-muted mb-4">A unified platform for club admins, lab administrators, and students to manage events, inventory, and support all in one place.</p>
            <div class="d-flex gap-3">
              <button class="btn btn-primary btn-lg px-4 rounded-pill shadow-sm" @click="showAuthModal('login')">Get Started</button>
              <button class="btn btn-outline-secondary btn-lg px-4 rounded-pill" @click="showAuthModal('login')">Login</button>
            </div>
          </div>
          <div class="col-lg-6 text-center">
            <div class="card-custom p-4 bg-light border-0">
              <img src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80" alt="Students collaborating" class="img-fluid rounded-3 shadow">
            </div>
          </div>
        </div>
  
        <div class="row mt-5 pt-4 text-center">
          <div class="col-md-4 mb-3">
            <div class="p-4 rounded-3 card-custom h-100">
              <div class="d-inline-block p-3 bg-primary bg-opacity-10 text-primary rounded-circle mb-3">📅</div>
              <h5 class="fw-bold">Event Management</h5>
              <p class="text-muted small m-0">Create, approve, and manage club events with seamless lab slot booking.</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="p-4 rounded-3 card-custom h-100">
              <div class="d-inline-block p-3 bg-success bg-opacity-10 text-success rounded-circle mb-3">📦</div>
              <h5 class="fw-bold">Inventory Tracking</h5>
              <p class="text-muted small m-0">Borrow and return lab equipment with full visibility on stock levels.</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="p-4 rounded-3 card-custom h-100">
              <div class="d-inline-block p-3 bg-warning bg-opacity-10 text-warning rounded-circle mb-3">💬</div>
              <h5 class="fw-bold">Support Desk</h5>
              <p class="text-muted small m-0">Direct ticket routing for equipment issues and general technical help.</p>
            </div>
          </div>
        </div>
      </main>


  
      <footer class="text-center py-3 border-top text-muted small">
        &copy; 2026 DRIVEN Platform.
      </footer>


  
      <!--Mock authentication model : As discussed with Navanit and in our last team meet -->

      
      <div v-if="activeModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content card-custom p-3">
            <div class="modal-header border-0">
              <h5 class="modal-title fw-bold">{{ activeModal === 'login' ? 'Welcome Back' : 'Create Account' }}</h5>
              <button type="button" class="btn-close" @click="activeModal = null"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label small text-muted">Select Demo Role to Login:</label>
                <select v-model="selectedRole" class="form-select">
                  <option value="club_admin">Club Admin</option>
                  <option value="student">Student</option>
                  <option value="lab_admin">Lab Admin</option>
                </select>
              </div>
              <button class="btn btn-primary w-100 rounded-pill py-2" @click="handleAuth">Continue to Dashboard</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { store } from '../store/mockData';
  
  const activeModal = ref(null);
  const selectedRole = ref('club_admin');
  
  const showAuthModal = (type) => {
    activeModal.value = type;
  };
  
  const handleAuth = () => {
    store.currentUserRole = selectedRole.value;
    activeModal.value = null;
  };
  </script>