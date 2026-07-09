<script setup>
  import { ref, computed, reactive } from 'vue';
  import { store } from '../store/mockData';
  
  const currentTab = ref('dashboard');
  const myRegisteredEvents = ref([]);
  const myBorrowedCount = ref(0); 
  
  // Item borrowed by student
  const myBorrowedItems = reactive({}); 
  const newTicket = reactive({ subject: '', priority: 'Medium' });
  
  
  const approvedEvents = computed(() => store.events.filter(e => e.status === 'Approved'));
  const activeTickets = computed(() => store.tickets.filter(t => t.status === 'Open'));
  const resolvedTickets = computed(() => store.tickets.filter(t => t.status === 'Resolved'));
  
  
  const selectedEvent = ref(null);
  
  //Function to open the modal and load event data
  const viewEventDetails = (event) => {
    selectedEvent.value = event;
  };
  
  //Function to close the modal
  const closeEventDetails = () => {
    selectedEvent.value = null;
  };
  
  //The registration logic now handles the modal state
  const confirmRegistration = (id) => {
    if (!myRegisteredEvents.value.includes(id)) {
      myRegisteredEvents.value.push(id);
      
      setTimeout(() => {
        closeEventDetails();
      }, 1500);
    }
  };
  
  const studentBorrow = (item) => {
    if (item.available > 0) {
      item.available--;
      item.borrowed++;
      myBorrowedCount.value++;
      // item added to the student's personal tracker
      myBorrowedItems[item.id] = (myBorrowedItems[item.id] || 0) + 1;
    }
  };
  
  // Return to reverse the borrowing process
  const studentReturn = (item) => {
    if (myBorrowedItems[item.id] > 0) {
      item.available++;
      item.borrowed--;
      myBorrowedCount.value--;
      myBorrowedItems[item.id]--;
    }
  };
  
  const submitStudentTicket = () => {
    store.addTicket({ subject: newTicket.subject, priority: newTicket.priority });
    newTicket.subject = '';
  };
  </script>





<template>
    <div class="d-flex">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-brand">DRIVEN</div>
        <nav class="mt-2 flex-grow-1">
          <div class="nav-item-custom" :class="{ active: currentTab === 'dashboard' }" @click="currentTab = 'dashboard'">
            <span>📊</span> Dashboard
          </div>
          <div class="nav-item-custom" :class="{ active: currentTab === 'events' }" @click="currentTab = 'events'">
            <span>📅</span> Browse Events
          </div>
          <div class="nav-item-custom" :class="{ active: currentTab === 'inventory' }" @click="currentTab = 'inventory'">
            <span>📦</span> Inventory
          </div>
          <div class="nav-item-custom" :class="{ active: currentTab === 'support' }" @click="currentTab = 'support'">
            <span>💬</span> Support Desk
          </div>
        </nav>
        <div class="p-3 border-top">
          <button class="btn btn-outline-danger w-100 btn-sm rounded-pill" @click="store.currentUserRole = 'home'">Logout</button>
        </div>
      </aside>
  
      <!-- Main Content Area -->
      <main class="main-content flex-grow-1">
        <header class="top-header">
          <h4 class="fw-bold m-0 text-dark">Student Portal</h4>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-success bg-opacity-10 text-success px-3 py-2 rounded-pill">Student Member</span>
            <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 38px; height: 38px; font-weight: bold;">AS</div>
          </div>
        </header>
  
        <!-- DASHBOARD TAB -->
        <div v-if="currentTab === 'dashboard'">
          <div class="row g-4 mb-4">
            <div class="col-md-3">
              <div class="stat-card">
                <div><span class="text-muted small fw-bold">Ongoing Events</span><div class="stat-value">3</div></div>
                <span>📅</span>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card">
                <div><span class="text-muted small fw-bold">Applied Events</span><div class="stat-value">{{ myRegisteredEvents.length }}</div></div>
                <span>✅</span>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card">
                <div><span class="text-muted small fw-bold">Closed Events</span><div class="stat-value">1</div></div>
                <span>🗄️</span>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card">
                <div><span class="text-muted small fw-bold">Borrowed Items</span><div class="stat-value">{{ myBorrowedCount }}</div></div>
                <span>📦</span>
              </div>
            </div>
          </div>
  
          <div class="d-flex gap-2 mb-4">
            <button class="btn btn-primary rounded-pill px-4" @click="currentTab = 'events'">Browse Events</button>
            <button class="btn btn-outline-secondary rounded-pill px-4" @click="currentTab = 'inventory'">Request Inventory</button>
          </div>
  
          <h6 class="fw-bold mb-3">Ongoing Club Events</h6>
          <div class="row g-3 mb-5">
            <div v-for="event in approvedEvents" :key="event.id" class="col-md-4">
              <div class="card-custom p-3 border-start border-primary border-4">
                <span class="badge bg-success-subtle text-success mb-2 d-inline-block w-auto">Ongoing</span>
                <h6 class="fw-bold">{{ event.name }}</h6>
                <p class="text-muted small m-0">{{ event.venue }} &bull; {{ event.date }}</p>
                <button class="btn btn-sm btn-outline-primary mt-3 w-100 rounded-pill" @click="viewEventDetails(event)">
                  {{ myRegisteredEvents.includes(event.id) ? 'View Details (Registered)' : 'View Details & Register' }}
                </button>
              </div>
            </div>
          </div>
  
          <h6 class="fw-bold mb-3 text-muted">Closed Events</h6>
          <div class="card-custom p-3 bg-light text-muted w-50">
            <div class="d-flex justify-content-between">
              <span class="fw-bold">AI/ML Seminar</span>
              <span class="badge bg-secondary">Closed</span>
            </div>
            <small>Seminar Hall &bull; Jun 20, 2026</small>
          </div>
        </div>
  
        <!-- EVENTS TAB -->
        <div v-else-if="currentTab === 'events'">
          <h5 class="fw-bold mb-4">Available Events for Registration</h5>
          <div class="row g-4">
            <div v-for="event in approvedEvents" :key="event.id" class="col-md-6">
              <div class="card-custom p-4 d-flex flex-column justify-content-between h-100">
                <div>
                  <h5 class="fw-bold text-primary">{{ event.name }}</h5>
                  <p class="text-muted small">{{ event.description }}</p>
                </div>
                <div class="border-top pt-3 mt-3 d-flex justify-content-between align-items-center">
                  <span class="small fw-bold text-muted">📍 {{ event.venue }} | 🗓️ {{ event.date }}</span>
                  <button class="btn btn-primary px-4 rounded-pill btn-sm" @click="viewEventDetails(event)">
                    {{ myRegisteredEvents.includes(event.id) ? 'Registered' : 'View Details' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
  
       <!-- TAB 3: INVENTORY -->
        <div v-else-if="currentTab === 'inventory'">
          <h5 class="fw-bold mb-4">Lab Equipment Borrowing</h5>
          <div class="card-custom p-4 mb-4">
            <h6 class="fw-bold mb-3">Available for Borrowing</h6>
            <table class="table align-middle">
              <thead>
                <tr class="text-muted small">
                  <th>Equipment</th>
                  <th>Category</th>
                  <th>In Stock</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in store.inventory" :key="item.id">
                  <td class="fw-bold">{{ item.name }}</td>
                  <td><span class="badge bg-light text-dark border">{{ item.category }}</span></td>
                  <td class="text-success fw-bold">{{ item.available }}</td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-success px-3 rounded-pill me-2" 
                      :disabled="item.available === 0" 
                      @click="studentBorrow(item)">
                      Borrow
                    </button>
                    
                    <!-- New Dynamic Return Button -->
                    <button 
                      v-if="myBorrowedItems[item.id]" 
                      class="btn btn-sm btn-outline-warning px-3 rounded-pill text-dark fw-bold" 
                      @click="studentReturn(item)">
                      Return ({{ myBorrowedItems[item.id] }})
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- SUPPORT DESK  -->
        <div v-else-if="currentTab === 'support'">
          <div class="row g-4">
            <!-- Left Column: Raise Ticket Form -->
            <div class="col-md-5">
              <div class="card-custom p-4 bg-light border-0">
                <h6 class="fw-bold mb-3 text-primary">Raise Support Ticket</h6>
                <form @submit.prevent="submitStudentTicket">
                  <div class="mb-3">
                    <label class="form-label small fw-bold">Subject / Issue</label>
                    <input v-model="newTicket.subject" type="text" class="form-control" placeholder="Describe issue briefly..." required />
                  </div>
                  <div class="mb-3">
                    <label class="form-label small fw-bold">Priority</label>
                    <select v-model="newTicket.priority" class="form-select">
                      <option>Low</option>
                      <option>Medium</option>
                      <option>High</option>
                    </select>
                  </div>
                  <button type="submit" class="btn btn-primary w-100 rounded-pill py-2">Submit Ticket</button>
                </form>
              </div>
            </div>
  
            <!-- Right Column: Split Active vs Resolved Tickets -->
            <div class="col-md-7">
              <!-- Active Tickets -->
              <h6 class="fw-bold mb-3 text-danger">🔴 Active Tickets (Pending Admin Response)</h6>
              <div v-if="activeTickets.length === 0" class="text-muted small mb-4">No active pending tickets.</div>
              <div v-for="ticket in activeTickets" :key="'act-'+ticket.id" class="card-custom p-3 mb-3 border-start border-danger border-3">
                <div class="d-flex justify-content-between">
                  <strong class="text-dark">{{ ticket.subject }}</strong>
                  <span class="badge bg-danger-subtle text-danger">{{ ticket.status }}</span>
                </div>
                <small class="text-muted">Priority: {{ ticket.priority }}</small>
              </div>
  
              <!-- Resolved Tickets (Moved into separate space as requested) -->
              <h6 class="fw-bold mb-3 mt-4 text-success">🟢 Resolved Tickets (Admin Handled)</h6>
              <div v-if="resolvedTickets.length === 0" class="text-muted small">No resolved tickets yet.</div>
              <div v-for="ticket in resolvedTickets" :key="'res-'+ticket.id" class="card-custom p-3 mb-3 bg-light border-start border-success border-3">
                <div class="d-flex justify-content-between mb-1">
                  <strong class="text-dark">{{ ticket.subject }}</strong>
                  <span class="badge-status badge-resolved">Resolved ✓</span>
                </div>
                <div class="bg-white p-2 rounded small text-muted border">
                  <strong>Admin Response:</strong> {{ ticket.reply }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedEvent" class="modal d-block" style="background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content card-custom border-0 shadow-lg overflow-hidden">
              <div class="modal-header border-bottom-0 bg-light pb-0 pt-4 px-4">
                <h5 class="modal-title fw-bold text-primary">Event Information</h5>
                <button type="button" class="btn-close" @click="closeEventDetails"></button>
              </div>
              <div class="modal-body p-4 pt-3">
                <h4 class="fw-bold mb-3">{{ selectedEvent.name }}</h4>
                
                <div class="d-flex flex-wrap gap-2 mb-4">
                  <span class="badge bg-primary bg-opacity-10 text-primary px-3 py-2 rounded-pill">📍 {{ selectedEvent.venue }}</span>
                  <span class="badge bg-secondary bg-opacity-10 text-secondary px-3 py-2 rounded-pill">🗓️ {{ selectedEvent.date }}</span>
                </div>
                
                <p class="text-muted mb-4" style="line-height: 1.6;">{{ selectedEvent.description }}</p>
  
                <div class="bg-light p-3 rounded-4 mb-4">
                  <div class="row text-center">
                    <div class="col-6 border-end">
                      <span class="d-block text-muted small fw-bold text-uppercase mb-1">Capacity</span>
                      <span class="fw-bold text-dark">{{ selectedEvent.participants }} Max</span>
                    </div>
                    <div class="col-6">
                      <span class="d-block text-muted small fw-bold text-uppercase mb-1">Status</span>
                      <span class="fw-bold text-success">{{ selectedEvent.status }}</span>
                    </div>
                  </div>
                </div>
  
                <button
                  class="btn w-100 rounded-pill py-3 fw-bold"
                  :class="myRegisteredEvents.includes(selectedEvent.id) ? 'btn-success' : 'btn-primary'"
                  @click="confirmRegistration(selectedEvent.id)"
                  :disabled="myRegisteredEvents.includes(selectedEvent.id)"
                >
                  {{ myRegisteredEvents.includes(selectedEvent.id) ? '✓ Successfully Registered' : 'Confirm Registration' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </template>