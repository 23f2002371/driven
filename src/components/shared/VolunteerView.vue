<template>
  <div class="vv-wrapper">
    <div v-if="applications.length === 0" class="vv-empty">
      <div class="vv-empty-ill">
        <svg viewBox="0 0 200 160" fill="none">
          <circle cx="100" cy="60" r="30" stroke="rgba(129,140,248,0.15)" stroke-width="1.5" fill="rgba(129,140,248,0.03)"/>
          <path d="M85 55l10 10 20-20" stroke="rgba(129,140,248,0.3)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="55" y="100" width="90" height="8" rx="4" fill="rgba(255,255,255,0.04)"/>
          <rect x="65" y="115" width="70" height="6" rx="3" fill="rgba(255,255,255,0.03)"/>
          <rect x="75" y="128" width="50" height="6" rx="3" fill="rgba(255,255,255,0.02)"/>
          <path d="M60 140c0-8 6-14 14-14h52c8 0 14 6 14 14" stroke="rgba(129,140,248,0.08)" stroke-width="1" fill="none"/>
        </svg>
      </div>
      <h3 class="vv-empty-title">No Volunteer Activities Yet</h3>
      <p class="vv-empty-text">Apply as a volunteer for upcoming events to contribute and build experience.</p>
      <button class="vv-empty-btn" @click="$emit('browse-events')"><i class="bi bi-calendar-event me-2"></i>Browse Events</button>
    </div>

    <div v-else class="vv-grid">
      <div v-for="app in applications" :key="app.id" class="vv-card" :class="'vv-' + app.status">
        <div class="vv-card-banner" :style="{ backgroundImage: `url(${app.image})` }">
          <div class="vv-banner-overlay">
            <span class="vv-badge" :class="'vv-badge-' + app.status">{{ statusLabel(app.status) }}</span>
          </div>
        </div>
        <div class="vv-card-body">
          <div class="vv-card-top">
            <h4 class="vv-event-name">{{ app.eventName }}</h4>
            <span class="vv-club-name"><i class="bi bi-building me-1"></i>{{ app.clubName }}</span>
          </div>
          <div class="vv-meta">
            <span><i class="bi bi-calendar3 me-1"></i>{{ app.date }}</span>
            <span><i class="bi bi-geo-alt me-1"></i>{{ app.venue }}</span>
          </div>
          <div v-if="app.role" class="vv-role-tag">{{ app.role }}</div>

          <div v-if="app.status === 'pending'" class="vv-status-msg">
            <i class="bi bi-clock-history me-2"></i>Application Submitted. Waiting for club approval.
          </div>

          <div v-else-if="app.status === 'rejected'" class="vv-status-msg vv-rejected-msg">
            <i class="bi bi-x-circle me-2"></i>Application Not Selected
            <p v-if="app.feedback" class="vv-feedback">{{ app.feedback }}</p>
          </div>

          <div v-else-if="app.status === 'completed'" class="vv-status-msg vv-completed-msg">
            <div class="vv-completed-top">
              <i class="bi bi-check-circle-fill text-success me-2"></i>Task Completed
              <span class="vv-completion-date">{{ app.completionDate }}</span>
            </div>
            <p v-if="app.thankYouMessage" class="vv-thanks">{{ app.thankYouMessage }}</p>
            <div class="vv-cert-placeholder">
              <i class="bi bi-award me-1"></i>Certificate will be generated after backend integration.
            </div>
          </div>

          <div v-else-if="app.status === 'accepted'" class="vv-accepted-section">
            <div class="vv-task-card">
              <div class="vv-task-header">
                <span class="vv-task-label">Assigned Task</span>
                <span class="vv-priority" :class="'vv-priority-' + app.priority">{{ app.priority }}</span>
              </div>
              <h5 class="vv-task-name">{{ app.assignedTask }}</h5>
              <p class="vv-task-desc">{{ app.taskDescription }}</p>
              <div class="vv-task-meta">
                <div><span class="vv-meta-label">Assigned By</span><span>{{ app.assignedBy }}</span></div>
                <div><span class="vv-meta-label">Reporting Time</span><span>{{ app.reportingTime }}</span></div>
                <div><span class="vv-meta-label">Volunteer Lead</span><span>{{ app.volunteerLead }}</span></div>
              </div>
            </div>
            <div class="vv-actions">
              <button class="vv-btn vv-btn-outline" @click="openDetails(app)"><i class="bi bi-eye me-1"></i>View Details</button>
              <button class="vv-btn vv-btn-primary" @click="confirmComplete(app)"><i class="bi bi-check-lg me-1"></i>Mark Task Completed</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedApp" class="vv-modal-overlay" @click.self="selectedApp = null">
      <div class="vv-modal">
        <div class="vv-modal-header">
          <h3 class="vv-modal-title">Volunteer Details</h3>
          <button class="vv-modal-close" @click="selectedApp = null"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="vv-modal-body">
          <div class="vv-modal-section">
            <h4>Event Information</h4>
            <div class="vv-modal-grid">
              <div><span class="vv-modal-label">Event</span><span>{{ selectedApp.eventName }}</span></div>
              <div><span class="vv-modal-label">Role</span><span>{{ selectedApp.role }}</span></div>
              <div><span class="vv-modal-label">Assigned Task</span><span>{{ selectedApp.assignedTask }}</span></div>
              <div><span class="vv-modal-label">Reporting Time</span><span>{{ selectedApp.reportingTime }}</span></div>
              <div><span class="vv-modal-label">Venue</span><span>{{ selectedApp.venue }}</span></div>
              <div><span class="vv-modal-label">Coordinator</span><span>{{ selectedApp.volunteerLead }}</span></div>
            </div>
          </div>
          <div class="vv-modal-section">
            <h4>Task Checklist</h4>
            <div class="vv-checklist">
              <div v-for="item in selectedApp.checklist" :key="item.id" class="vv-check-item" :class="{ done: item.completed }">
                <i class="bi" :class="item.completed ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                <span>{{ item.label }}</span>
              </div>
            </div>
          </div>
          <div v-if="selectedApp.dressCode" class="vv-modal-section">
            <h4>Dress Code</h4>
            <p class="vv-modal-text">{{ selectedApp.dressCode }}</p>
          </div>
          <div v-if="selectedApp.notes" class="vv-modal-section">
            <h4>Notes</h4>
            <p class="vv-modal-text">{{ selectedApp.notes }}</p>
          </div>
        </div>
        <div class="vv-modal-footer">
          <button class="vv-btn vv-btn-secondary" @click="selectedApp = null">Close</button>
          <button v-if="selectedApp.status === 'accepted'" class="vv-btn vv-btn-primary" @click="confirmComplete(selectedApp)"><i class="bi bi-check-lg me-1"></i>Mark Task Completed</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirm" class="vv-confirm-overlay" @click.self="showConfirm = false">
      <div class="vv-confirm">
        <div class="vv-confirm-icon"><i class="bi bi-question-circle-fill"></i></div>
        <h4 class="vv-confirm-title">Mark Task as Completed?</h4>
        <p class="vv-confirm-text">Once confirmed, the task status will be updated to completed. This action cannot be undone.</p>
        <div class="vv-confirm-actions">
          <button class="vv-btn vv-btn-secondary" @click="showConfirm = false">Cancel</button>
          <button class="vv-btn vv-btn-primary" @click="doComplete">Confirm</button>
        </div>
      </div>
    </div>

    <div v-if="toast" class="vv-toast glass-toast"><i class="bi bi-check-circle-fill me-2" style="color: #4ade80;"></i>{{ toast }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { store } from '../../store/mockData';

const emit = defineEmits(['browse-events']);

const props = defineProps({
  applications: { type: Array, default: () => [] },
});

const selectedApp = ref(null);
const showConfirm = ref(false);
const pendingCompleteId = ref(null);
const toast = ref('');

const statusLabel = (status) => {
  const labels = { pending: 'Pending', accepted: 'Accepted', rejected: 'Rejected', completed: 'Completed' };
  return labels[status] || status;
};

const openDetails = (app) => {
  selectedApp.value = app;
};

const confirmComplete = (app) => {
  pendingCompleteId.value = app.id;
  showConfirm.value = true;
};

const doComplete = () => {
  if (pendingCompleteId.value) {
    store.markVolunteerTaskComplete(pendingCompleteId.value);
    selectedApp.value = null;
    toast.value = 'Task marked as completed.';
    setTimeout(() => { toast.value = ''; }, 3000);
  }
  showConfirm.value = false;
  pendingCompleteId.value = null;
};
</script>
