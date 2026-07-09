<template>
  <div class="d-flex">
   
    <aside class="sidebar">
      <div class="sidebar-brand">DRIVEN</div>
      <nav class="mt-2 flex-grow-1">
        <div class="nav-item-custom" :class="{ active: currentTab === 'dashboard' }" @click="currentTab = 'dashboard'">
          <span>📊</span> Dashboard
        </div>
        <div class="nav-item-custom" :class="{ active: currentTab === 'approvals' }" @click="currentTab = 'approvals'">
          <span>✅</span> Event Approvals
        </div>
        <div class="nav-item-custom" :class="{ active: currentTab === 'calendar' }" @click="currentTab = 'calendar'">
          <span>📅</span> Slot Calendar
        </div>
      </nav>
      <div class="p-3 border-top">
        <button class="btn btn-outline-danger w-100 btn-sm rounded-pill" @click="store.currentUserRole = 'home'">Logout</button>
      </div>
    </aside>

    
    <main class="main-content flex-grow-1">
      <header class="top-header">
        <h4 class="fw-bold m-0 text-dark">Lab Administrator Portal</h4>
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-warning bg-opacity-10 text-warning px-3 py-2 rounded-pill">Facility Controller</span>
          <div class="bg-dark text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 38px; height: 38px; font-weight: bold;">LA</div>
        </div>
      </header>

      <!-- Dashboard view condition -->
      <div v-if="currentTab === 'dashboard'">
        <div class="row g-4 mb-4">
          <div class="col-md-4">
            <div class="stat-card">
              <div><span class="text-muted small fw-bold">Pending Requests</span><div class="stat-value">{{ pendingEvents.length }}</div></div>
              <span>🕒</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="stat-card">
              <div><span class="text-muted small fw-bold">Approved Events</span><div class="stat-value">3</div></div>
              <span>🗓️</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="stat-card">
              <div><span class="text-muted small fw-bold">Total Slots Booked</span><div class="stat-value">0
                
              </div></div>
              <span>📩</span>
            </div>
          </div>
        </div>

        <div class="card-custom p-4">
          <h6 class="fw-bold mb-3">Pending Approval Requests</h6>
          <div v-if="pendingEvents.length === 0" class="text-muted small py-3">All caught up! No events pending review.</div>
          
          <div v-for="event in pendingEvents" :key="event.id" class="d-flex justify-content-between align-items-center py-3 border-bottom">
            <div>
              <h6 class="fw-bold m-0">{{ event.name }}</h6>
              <small class="text-muted">{{ event.venue }} &bull; {{ event.date }} ({{ event.participants }} Expected)</small>
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-success px-3 rounded-pill" @click="store.approveEvent(event.id)">Approve</button>
              <button class="btn btn-sm btn-outline-danger px-3 rounded-pill" @click="rejectEvent(event.id)">Reject</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Approvals and Rejection option -->
      <div v-else-if="currentTab === 'approvals'">
        <div class="row g-4">
          
          <!-- Approvals Table -->
          <div class="col-md-8">
            <div class="card-custom p-4 h-100">
              <h5 class="fw-bold mb-4">Event Approval Workflow</h5>
              <table class="table align-middle">
                <thead>
                  <tr class="text-muted small">
                    <th>Event Name</th>
                    <th>Venue Requested</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="event in store.events" :key="event.id">
                    <td class="fw-bold">{{ event.name }}</td>
                    <td>{{ event.venue }}</td>
                    <td>{{ event.date }}</td>
                    <td><span class="badge-status" :class="event.status === 'Approved' ? 'badge-approved' : 'badge-pending'">{{ event.status }}</span></td>
                    <td>
                      <div v-if="event.status === 'Pending'" class="d-flex gap-2">
                        <button class="btn btn-sm btn-success px-3 rounded-pill" @click="store.approveEvent(event.id)">Approve</button>
                        <button class="btn btn-sm btn-outline-danger px-3 rounded-pill" @click="rejectEvent(event.id)">Reject</button>
                      </div>
                      <span v-else class="text-muted small">No action needed</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Venue Checker -->
          <div class="col-md-4">
            <div class="card-custom p-4 bg-light h-100 border-0">
              <h6 class="fw-bold mb-1 text-primary">Cross-Check Availability</h6>
              <p class="text-muted small mb-3">View specific venue schedules before approving.</p>
              
              <select v-model="selectedVenue" class="form-select mb-4 shadow-sm border-0">
                <option v-for="venue in venues" :key="venue" :value="venue">{{ venue }}</option>
              </select>

              <div class="calendar-grid mb-2 text-center text-muted small fw-bold" style="gap: 4px;">
                <div>S</div><div>M</div><div>T</div><div>W</div><div>T</div><div>F</div><div>S</div>
              </div>
              
              <div class="calendar-grid" style="gap: 4px;">
                <div v-for="day in 31" :key="day"
                     class="calendar-day small py-1 shadow-sm"
                     :class="isBooked(day) ? 'day-booked' : 'day-available'"
                     @click="toggleDateStatus(day)">
                  {{ day }}
                </div>
              </div>
              <small class="text-muted d-block mt-3 text-center" style="font-size: 0.75rem;">*Click to toggle slot status for {{ selectedVenue }}</small>
            </div>
          </div>

        </div>
      </div>

      <!-- SLOT CALENDAR -->
      <div v-else-if="currentTab === 'calendar'">
        <div class="row g-4">
          <div class="col-md-7">
            <div class="card-custom p-4">
              
              <div class="d-flex justify-content-between align-items-start mb-4">
                <div>
                  <h5 class="fw-bold m-0 mb-2">Slot Calendar</h5>
                  <select v-model="selectedVenue" class="form-select shadow-sm bg-light" style="width: 200px;">
                    <option v-for="venue in venues" :key="venue" :value="venue">{{ venue }}</option>
                  </select>
                </div>
                <div class="d-flex gap-3 small fw-bold mt-2">
                  <span class="d-flex align-items-center gap-1"><span class="d-inline-block rounded" style="width:12px; height:12px; background:#ef4444;"></span> Booked</span>
                  <span class="d-flex align-items-center gap-1"><span class="d-inline-block rounded" style="width:12px; height:12px; background:#22c55e;"></span> Available</span>
                </div>
              </div>

              <!-- Days Header -->
              <div class="calendar-grid mb-2 text-center text-muted small fw-bold">
                <div>S</div><div>M</div><div>T</div><div>W</div><div>T</div><div>F</div><div>S</div>
              </div>
              <!-- Calendar Grid (31 Days of July) -->
              <div class="calendar-grid">
                <div v-for="day in 31" :key="day"
                     class="calendar-day"
                     :class="isBooked(day) ? 'day-booked' : 'day-available'"
                     @click="toggleDateStatus(day)">
                  {{ day }}
                </div>
              </div>
              <small class="text-muted d-block mt-3 text-center">*Viewing data for <strong>{{ selectedVenue }}</strong></small>
            </div>
          </div>

          <!-- Side List of Bookings -->
          <div class="col-md-5">
            <div class="card-custom p-4">
              <h6 class="fw-bold mb-3">Recent Bookings ({{ selectedVenue }})</h6>
              <div class="list-group list-group-flush" v-if="isBooked(15) || isBooked(22) || isBooked(28)">
                <div v-if="isBooked(15)" class="list-group-item px-0 py-2 border-bottom">
                  <strong class="d-block text-dark">IoT Workshop</strong>
                  <small class="text-muted">{{ selectedVenue }} &bull; Jul 15 &bull; 09:00 - 12:00</small>
                </div>
                <div v-if="isBooked(22)" class="list-group-item px-0 py-2 border-bottom">
                  <strong class="d-block text-dark">Hackathon 2026</strong>
                  <small class="text-muted">{{ selectedVenue }} &bull; Jul 22 &bull; All Day</small>
                </div>
                <div v-if="isBooked(28)" class="list-group-item px-0 py-2">
                  <strong class="d-block text-dark">Python Bootcamp</strong>
                  <small class="text-muted">{{ selectedVenue }} &bull; Jul 28 &bull; 14:00 - 17:00</small>
                </div>
              </div>
              <div v-else class="text-muted small py-3">No confirmed events for this venue yet.</div>
            </div>
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
const pendingEvents = computed(() => store.events.filter(e => e.status === 'Pending'));

// Reject action removes the event entirely from the queue
const rejectEvent = (id) => {
  const index = store.events.findIndex(e => e.id === id);
  if (index !== -1) store.events.splice(index, 1);
};

// --- VENUE TRACKING LOGIC ---
const venues = ['Lab A', 'Lab B', 'Auditorium', 'Seminar Hall'];
const selectedVenue = ref('Lab A');

// Reactive mapping for which dates are booked inside which venue
const venueBookings = reactive({
  'Lab A': [15],
  'Lab B': [28],
  'Auditorium': [22],
  'Seminar Hall': [12, 18, 26]
});

// Helper function to dynamically color days Red (Booked) or Green (Available)
const isBooked = (day) => {
  return venueBookings[selectedVenue.value] && venueBookings[selectedVenue.value].includes(day);
};

// Toggle function now updates specifically for the chosen venue
const toggleDateStatus = (day) => {
  if (!venueBookings[selectedVenue.value]) {
    venueBookings[selectedVenue.value] = [];
  }
  
  const venueArray = venueBookings[selectedVenue.value];
  const index = venueArray.indexOf(day);
  
  if (index === -1) {
    venueArray.push(day);
  } else {
    venueArray.splice(index, 1);
  }
};
</script>