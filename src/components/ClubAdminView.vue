<template>
    <div class="d-flex">
      <aside class="sidebar">
        <div class="sidebar-brand">DRIVEN</div>
        <nav class="mt-2 flex-grow-1">
          <div class="nav-item-custom" :class="{ active: currentTab === 'dashboard' }" @click="currentTab = 'dashboard'">
            <span>📊</span> Dashboard
          </div>
          <div class="nav-item-custom" :class="{ active: currentTab === 'events' }" @click="currentTab = 'events'">
            <span>📅</span> Events
          </div>
          <div class="nav-item-custom" :class="{ active: currentTab === 'create_event' }" @click="currentTab = 'create_event'">
            <span>➕</span> Create Event
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
  
      <main class="main-content flex-grow-1">
        <header class="top-header">
          <h4 class="fw-bold m-0 text-dark">Club Admin Portal</h4>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-primary bg-opacity-10 text-primary px-3 py-2 rounded-pill">Club Lead</span>
            <div class="bg-dark text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 38px; height: 38px; font-weight: bold;">CA</div>
          </div>
        </header>
  
        <div v-if="currentTab === 'dashboard'">
          <div class="row g-4 mb-4">
            <div class="col-md-4">
              <div class="stat-card">
                <div>
                  <span class="text-muted small fw-bold text-uppercase">Upcoming Events</span>
                  <div class="stat-value">{{ store.events.length }}</div>
                </div>
                <span class="fs-4">📅</span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="stat-card">
                <div>
                  <span class="text-muted small fw-bold text-uppercase">Inventory Items</span>
                  <div class="stat-value">{{ totalInventory }}</div>
                </div>
                <span class="fs-4">📦</span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="stat-card">
                <div>
                  <span class="text-muted small fw-bold text-uppercase">Pending Tickets</span>
                  <div class="stat-value">{{ openTicketsCount }}</div>
                </div>
                <span class="fs-4">💬</span>
              </div>
            </div>
          </div>
  
          <div class="d-flex gap-2 mb-4">
            <button class="btn btn-primary rounded-pill px-4" @click="currentTab = 'create_event'">+ Create Event</button>
            <button class="btn btn-outline-secondary rounded-pill px-4" @click="currentTab = 'inventory'">Manage Inventory</button>
          </div>
  
          <div class="card-custom p-4">
            <h6 class="fw-bold mb-3">Recent Events</h6>
            <div class="list-group list-group-flush">
              <div v-for="event in store.events" :key="event.id" class="list-group-item px-0 py-3 d-flex justify-content-between align-items-center border-bottom">
                <div>
                  <h6 class="mb-1 fw-bold">{{ event.name }}</h6>
                  <small class="text-muted">{{ event.date }} &bull; {{ event.venue }}</small>
                </div>
                <span class="badge-status" :class="event.status === 'Approved' ? 'badge-approved' : 'badge-pending'">{{ event.status }}</span>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Events to be linked across all (Admin creates -> Reflect in all) -->
        <div v-else-if="currentTab === 'events'">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="fw-bold m-0">All Club Events</h5>
            <button class="btn btn-primary btn-sm rounded-pill px-3" @click="currentTab = 'create_event'">+ New Event</button>
          </div>
          <div class="row g-4">
            <div v-for="event in store.events" :key="event.id" class="col-md-6">
              <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between">
                <div>
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="fw-bold m-0 fs-5">{{ event.name }}</h6>
                    <span class="badge-status" :class="event.status === 'Approved' ? 'badge-approved' : 'badge-pending'">{{ event.status }}</span>
                  </div>
                  <p class="text-muted small mb-3">{{ event.description }}</p>
                </div>
                <div class="bg-light p-3 rounded-3 d-flex justify-content-between text-muted small">
                  <span>📍 {{ event.venue }}</span>
                  <span>🗓️ {{ event.date }}</span>
                  <span>👥 {{ event.participants }} Max</span>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Event to be created here -> Handoff for persmission to Lab Admin (AJ) -->
        <div v-else-if="currentTab === 'create_event'" class="card-custom p-4 max-w-lg">
          <div class="d-flex align-items-center gap-2 mb-4">
            <button class="btn btn-sm btn-light border" @click="currentTab = 'dashboard'">← Back</button>
            <h5 class="fw-bold m-0">Create New Event</h5>
          </div>
          <form @submit.prevent="submitNewEvent">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label small fw-bold">Event Name</label>
                <input v-model="formEvent.name" type="text" class="form-control" placeholder="e.g. IoT Workshop" required />
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold">Category</label>
                <select v-model="formEvent.category" class="form-select">
                  <option>Workshop</option>
                  <option>Seminar</option>
                  <option>Hackathon</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold">Venue / Lab Selection</label>
                <select v-model="formEvent.venue" class="form-select">
                  <option>Lab A</option>
                  <option>Lab B</option>
                  <option>Auditorium</option>
                  <option>Seminar Hall</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold">Date</label>
                <input v-model="formEvent.date" type="text" class="form-control" placeholder="e.g. Jul 30, 2026" required />
              </div>
              <div class="col-12">
                <label class="form-label small fw-bold">Expected Participants</label>
                <input v-model="formEvent.participants" type="number" class="form-control" placeholder="50" required />
              </div>
              <div class="col-12">
                <label class="form-label small fw-bold">Description</label>
                <textarea v-model="formEvent.description" class="form-control" rows="3" placeholder="Brief description of the event..." required></textarea>
              </div>
              <div class="col-12 mt-4">
                <button type="submit" class="btn btn-primary rounded-pill px-4 py-2">Request Approval (Send to Lab Admin)</button>
              </div>
            </div>
          </form>
        </div>
  
        <!-- Inventory Updation to be done from here by admin (Also must reflect for everyone) -->
        <div v-else-if="currentTab === 'inventory'">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="fw-bold m-0">Inventory Management</h5>
            <button class="btn btn-outline-primary btn-sm rounded-pill px-3" @click="showAddInventory = !showAddInventory">+ Add New Item</button>
          </div>
  
          <!-- Allow the admin to add items and should show up for the students -> Handoff updated items to Students (Navanit) -->
          <div v-if="showAddInventory" class="card-custom p-4 mb-4 bg-light">
            <h6 class="fw-bold mb-3">Add Equipment to Stock</h6>
            <form @submit.prevent="addNewInventoryItem" class="row g-2 align-items-end">
              <div class="col-md-4">
                <label class="form-label small">Equipment Name</label>
                <input v-model="newItem.name" type="text" class="form-control form-control-sm" required />
              </div>
              <div class="col-md-3">
                <label class="form-label small">Category</label>
                <input v-model="newItem.category" type="text" class="form-control form-control-sm" placeholder="e.g. Hardware" required />
              </div>
              <div class="col-md-2">
                <label class="form-label small">Qty</label>
                <input v-model="newItem.available" type="number" class="form-control form-control-sm" required />
              </div>
              <div class="col-md-3">
                <button type="submit" class="btn btn-primary btn-sm w-100 rounded-pill">Add Item</button>
              </div>
            </form>
          </div>
  
          <div class="card-custom p-4 mb-4">
            <h6 class="fw-bold mb-3 text-success">Available Inventory</h6>
            <table class="table table-hover align-middle">
              <thead>
                <tr class="text-muted small">
                  <th>Equipment</th>
                  <th>Category</th>
                  <th>Available</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in store.inventory" :key="item.id">
                  <td class="fw-bold">{{ item.name }}</td>
                  <td><span class="badge bg-light text-dark border">{{ item.category }}</span></td>
                  <td class="fw-bold text-success">{{ item.available }}</td>
                  <td>
                    <button class="btn btn-sm btn-success px-3 rounded-pill" :disabled="item.available === 0" @click="borrowItem(item)">Borrow</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
  
          <div class="card-custom p-4">
            <h6 class="fw-bold mb-3 text-warning">Borrowed Inventory</h6>
            <table class="table table-hover align-middle">
              <thead>
                <tr class="text-muted small">
                  <th>Equipment</th>
                  <th>Category</th>
                  <th>Borrowed Qty</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in store.inventory.filter(i => i.borrowed > 0)" :key="'b-'+item.id">
                  <td class="fw-bold">{{ item.name }}</td>
                  <td><span class="badge bg-light text-dark border">{{ item.category }}</span></td>
                  <td class="fw-bold text-danger">{{ item.borrowed }}</td>
                  <td>
                    <button class="btn btn-sm btn-warning px-3 rounded-pill text-dark fw-bold" @click="returnItem(item)">Return</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- Get handoff from StudentsTab (Navanit) -> Support Desk functionality should allow admins to responds and resolve  -->
        <div v-else-if="currentTab === 'support'" class="card-custom p-4">
          <h5 class="fw-bold mb-4">Support Desk Queue</h5>
          <div v-for="ticket in store.tickets" :key="ticket.id" class="border rounded-3 p-3 mb-3" :class="ticket.status === 'Resolved' ? 'bg-light' : 'bg-white'">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div>
                <span class="fw-bold me-2">{{ ticket.student }}</span>
                <span class="badge" :class="ticket.priority === 'High' ? 'bg-danger-subtle text-danger' : 'bg-warning-subtle text-warning'">{{ ticket.priority }}</span>
              </div>
              <span class="badge-status" :class="ticket.status === 'Resolved' ? 'badge-resolved' : 'badge-open'">{{ ticket.status }}</span>
            </div>
            <p class="mb-2 text-dark">{{ ticket.subject }}</p>
            
            <!-- Reply and respond to resolve user query -> Send response to Students (Navanit) -->
            <div v-if="ticket.reply" class="bg-white p-2 rounded border-start border-primary border-3 small text-muted mt-2">
              <strong>Admin Reply:</strong> {{ ticket.reply }}
            </div>
            <div v-else class="mt-3 d-flex gap-2">
              <input v-model="replyText[ticket.id]" type="text" class="form-control form-control-sm" placeholder="Type response to resolve ticket..." />
              <button class="btn btn-sm btn-primary px-3 rounded-pill" @click="sendReply(ticket.id)">Reply & Resolve</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, reactive } from 'vue';
  import { store } from '../store/mockData';
  
  const currentTab = ref('dashboard');
  const showAddInventory = ref(false);
  const replyText = reactive({});
  
  const formEvent = reactive({ name: '', category: 'Workshop', venue: 'Lab A', date: '', participants: '', description: '' });
  const newItem = reactive({ name: '', category: '', available: 1 });
  
  const totalInventory = computed(() => store.inventory.reduce((acc, item) => acc + item.available + item.borrowed, 0));
  const openTicketsCount = computed(() => store.tickets.filter(t => t.status === 'Open').length);
  
  const submitNewEvent = () => {
    store.addEvent({ ...formEvent });
    formEvent.name = ''; formEvent.date = ''; formEvent.description = '';
    currentTab.value = 'events';
  };
  
  const addNewInventoryItem = () => {
    store.inventory.push({ id: Date.now(), name: newItem.name, category: newItem.category, available: newItem.available, borrowed: 0 });
    newItem.name = ''; newItem.category = ''; newItem.available = 1;
    showAddInventory.value = false;
  };
  
  const borrowItem = (item) => {
    if (item.available > 0) { item.available--; item.borrowed++; }
  };
  
  const returnItem = (item) => {
    if (item.borrowed > 0) { item.borrowed--; item.available++; }
  };
  
  const sendReply = (id) => {
    if (replyText[id]) {
      store.resolveTicket(id, replyText[id]);
      replyText[id] = '';
    }
  };
  </script>