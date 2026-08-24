<template>
  <div class="vv-wrapper">
    <div v-if="isLoading" class="vv-loading text-center py-5 text-secondary">
      <span class="spinner-border spinner-border-sm me-2"></span>Loading volunteering & assigned tasks...
    </div>

    <div v-else-if="liveTasks.length === 0" class="vv-empty">
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
      <h3 class="vv-empty-title">No Assigned Volunteer Tasks Yet</h3>
      <p class="vv-empty-text">Apply to open campus bounties or event volunteer roles to receive assigned work and build verified experience.</p>
      <button class="vv-empty-btn" @click="$emit('browse-events')"><i class="bi bi-compass me-2"></i>Browse Opportunities</button>
    </div>

    <div v-else class="vv-grid">
      <div v-for="task in liveTasks" :key="task.id" class="vv-card" :class="'vv-' + task.status">
        <div class="vv-card-body">
          <div class="d-flex align-items-start justify-content-between gap-2 mb-2">
            <div>
              <span class="badge bg-primary-subtle text-primary mb-1" style="font-size: 0.72rem;">
                <i class="bi bi-briefcase-fill me-1"></i>{{ task.bountyTitle || task.eventName || 'Campus Bounty' }}
              </span>
              <h4 class="vv-event-name m-0">{{ task.title }}</h4>
            </div>
            <span class="vv-badge" :class="'vv-badge-' + task.status">{{ statusLabel(task.status) }}</span>
          </div>

          <p class="vv-task-desc text-secondary small">{{ task.task_description }}</p>

          <div class="vv-meta mb-3">
            <span><i class="bi bi-calendar3 me-1 text-info"></i>Deadline: {{ formatDisplayDate(task.deadline) }}</span>
            <span v-if="task.eventName"><i class="bi bi-geo-alt me-1 text-warning"></i>{{ task.eventName }}</span>
          </div>

          <!-- Deliverables Checklist -->
          <div v-if="task.deliverables?.length" class="vv-checklist-box mb-3">
            <span class="vv-checklist-title"><i class="bi bi-list-check me-1"></i>Deliverables Checklist</span>
            <div class="vv-checklist">
              <div
                v-for="d in task.deliverables"
                :key="d.id"
                class="vv-check-item"
                :class="{ done: d.status === 'completed' }"
                @click="toggleDeliverable(task, d)"
              >
                <i class="bi" :class="d.status === 'completed' ? 'bi-check-circle-fill text-success' : 'bi-circle'"></i>
                <span>{{ d.title }}</span>
                <span class="badge ms-auto" :class="d.status === 'completed' ? 'bg-success' : 'bg-secondary'">{{ d.status }}</span>
              </div>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="vv-actions mt-auto d-flex justify-content-between align-items-center flex-wrap gap-2">
            <button class="vv-btn vv-btn-outline" @click="openDetails(task)">
              <i class="bi bi-eye me-1"></i>View Details
            </button>
            <button
              v-if="task.status !== 'completed'"
              class="vv-btn vv-btn-primary"
              :disabled="isUpdating"
              @click="confirmComplete(task)"
            >
              <i class="bi bi-check-lg me-1"></i>Mark Task Completed
            </button>
            <span v-else class="text-success small fw-bold">
              <i class="bi bi-patch-check-fill me-1"></i>Completed
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="selectedTask" class="vv-modal-overlay" @click.self="selectedTask = null">
      <div class="vv-modal">
        <div class="vv-modal-header">
          <h3 class="vv-modal-title">Task & Volunteering Details</h3>
          <button class="vv-modal-close" @click="selectedTask = null"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="vv-modal-body">
          <div class="vv-modal-section">
            <h4>Task Information</h4>
            <div class="vv-modal-grid">
              <div><span class="vv-modal-label">Title</span><span>{{ selectedTask.title }}</span></div>
              <div><span class="vv-modal-label">Status</span><span class="badge bg-primary">{{ (selectedTask.status || '').toUpperCase() }}</span></div>
              <div><span class="vv-modal-label">Deadline</span><span>{{ formatDisplayDate(selectedTask.deadline) }}</span></div>
              <div v-if="selectedTask.bountyTitle"><span class="vv-modal-label">Bounty</span><span>{{ selectedTask.bountyTitle }}</span></div>
            </div>
            <div class="mt-3">
              <span class="vv-modal-label">Task Description</span>
              <p class="text-light mt-1">{{ selectedTask.task_description }}</p>
            </div>
          </div>

          <div v-if="selectedTask.deliverables?.length" class="vv-modal-section">
            <h4>Deliverables Checklist</h4>
            <div class="vv-checklist">
              <div
                v-for="d in selectedTask.deliverables"
                :key="d.id"
                class="vv-check-item"
                :class="{ done: d.status === 'completed' }"
                @click="toggleDeliverable(selectedTask, d)"
              >
                <i class="bi" :class="d.status === 'completed' ? 'bi-check-circle-fill text-success' : 'bi-circle'"></i>
                <span>{{ d.title }}</span>
                <span class="badge ms-auto" :class="d.status === 'completed' ? 'bg-success' : 'bg-secondary'">{{ d.status }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="vv-modal-footer">
          <button class="vv-btn vv-btn-secondary" @click="selectedTask = null">Close</button>
          <button
            v-if="selectedTask.status !== 'completed'"
            class="vv-btn vv-btn-primary"
            @click="confirmComplete(selectedTask)"
          >
            <i class="bi bi-check-lg me-1"></i>Mark Task Completed
          </button>
        </div>
      </div>
    </div>

    <!-- Confirm Complete Modal -->
    <div v-if="showConfirm" class="vv-confirm-overlay" @click.self="showConfirm = false">
      <div class="vv-confirm">
        <div class="vv-confirm-icon"><i class="bi bi-question-circle-fill"></i></div>
        <h4 class="vv-confirm-title">Mark Task as Completed?</h4>
        <p class="vv-confirm-text">Have you finished all required deliverables for this assigned task?</p>
        <div class="vv-confirm-actions">
          <button class="vv-btn vv-btn-secondary" @click="showConfirm = false">Cancel</button>
          <button class="vv-btn vv-btn-primary" :disabled="isUpdating" @click="doComplete">
            <span v-if="isUpdating" class="spinner-border spinner-border-sm me-2"></span>
            Confirm Completed
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast" class="vv-toast glass-toast">
      <i class="bi bi-check-circle-fill me-2" style="color: #4ade80;"></i>{{ toast }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { store } from '../../store/mockData';
import { fetchMyWorkApi, updateAssignedWorkApi } from '../../api/bounty';

const emit = defineEmits(['browse-events']);

const props = defineProps({
  applications: { type: Array, default: () => [] },
});

const liveTasks = ref([]);
const isLoading = ref(false);
const isUpdating = ref(false);

const selectedTask = ref(null);
const showConfirm = ref(false);
const pendingCompleteTask = ref(null);
const toast = ref('');

const getToken = () => store.token || localStorage.getItem('driven_token');

onMounted(async () => {
  await loadMyWorkTasks();
});

const loadMyWorkTasks = async () => {
  isLoading.value = true;
  try {
    const data = await fetchMyWorkApi(getToken());
    if (data && data.length) {
      liveTasks.value = data.map(w => ({
        id: w.id,
        application_id: w.application_id,
        title: w.title,
        task_description: w.task_description,
        deadline: w.deadline,
        status: w.status,
        deliverables: w.deliverables || [],
        eventName: w.event?.name,
        bountyTitle: w.application?.bounty_title,
      }));
    } else if (props.applications && props.applications.length) {
      liveTasks.value = props.applications.map(a => ({
        id: a.id,
        application_id: a.id,
        title: a.assignedTask || 'Volunteering Task',
        task_description: a.taskDescription || 'Event Volunteer Assignment',
        deadline: a.reportingTime || a.date,
        status: a.status || 'assigned',
        deliverables: (a.checklist || []).map((c, i) => ({ id: i, title: c.label, status: c.completed ? 'completed' : 'pending' })),
        eventName: a.eventName,
        bountyTitle: a.clubName,
      }));
    } else {
      liveTasks.value = [];
    }
  } catch (err) {
    console.error('Failed to load my work:', err);
    if (props.applications && props.applications.length) {
      liveTasks.value = props.applications.map(a => ({
        id: a.id,
        application_id: a.id,
        title: a.assignedTask || 'Volunteering Task',
        task_description: a.taskDescription || 'Event Volunteer Assignment',
        deadline: a.reportingTime || a.date,
        status: a.status || 'assigned',
        deliverables: (a.checklist || []).map((c, i) => ({ id: i, title: c.label, status: c.completed ? 'completed' : 'pending' })),
        eventName: a.eventName,
        bountyTitle: a.clubName,
      }));
    }
  } finally {
    isLoading.value = false;
  }
};

const statusLabel = (status) => {
  const labels = { assigned: 'Assigned', in_progress: 'In Progress', completed: 'Completed', accepted: 'Accepted' };
  return labels[status] || status;
};

const formatDisplayDate = (d) => {
  if (!d) return 'TBD';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const openDetails = (task) => {
  selectedTask.value = task;
};

const toggleDeliverable = async (task, deliverable) => {
  const newStatus = deliverable.status === 'completed' ? 'in_progress' : 'completed';
  try {
    await updateAssignedWorkApi(
      task.application_id || task.id,
      {
        deliverables: [{ id: deliverable.id, status: newStatus }],
      },
      getToken()
    );
    deliverable.status = newStatus;
  } catch (err) {
    console.error('Failed to update deliverable:', err);
  }
};

const confirmComplete = (task) => {
  pendingCompleteTask.value = task;
  showConfirm.value = true;
};

const doComplete = async () => {
  if (!pendingCompleteTask.value) return;
  isUpdating.value = true;
  try {
    await updateAssignedWorkApi(
      pendingCompleteTask.value.application_id || pendingCompleteTask.value.id,
      { status: 'completed' },
      getToken()
    );
    pendingCompleteTask.value.status = 'completed';
    if (selectedTask.value) {
      selectedTask.value.status = 'completed';
    }
    toast.value = 'Task marked as completed successfully!';
    setTimeout(() => { toast.value = ''; }, 3000);
  } catch (err) {
    console.error('Failed to mark task completed:', err);
  } finally {
    isUpdating.value = false;
    showConfirm.value = false;
    pendingCompleteTask.value = null;
  }
};
</script>

<style scoped>
.vv-wrapper {
  position: relative;
}

.vv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.vv-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}
.vv-card:hover {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(129, 140, 248, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.vv-card-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.vv-event-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #f1f5f9;
}

.vv-badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.2rem 0.65rem;
  border-radius: 6px;
  text-transform: uppercase;
}
.vv-badge-assigned, .vv-badge-accepted { background: rgba(99, 102, 241, 0.2); color: #c7d2fe; border: 1px solid rgba(129, 140, 248, 0.3); }
.vv-badge-in_progress { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.vv-badge-completed { background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }

.vv-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.78rem;
  color: #94a3b8;
  flex-wrap: wrap;
}

.vv-checklist-box {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
}
.vv-checklist-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #cbd5e1;
  display: block;
  margin-bottom: 0.5rem;
}
.vv-checklist {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.vv-check-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #e2e8f0;
  cursor: pointer;
}
.vv-check-item.done {
  color: #94a3b8;
  text-decoration: line-through;
}

.vv-btn {
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  border: none;
}
.vv-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
}
.vv-btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}
.vv-btn-outline {
  background: transparent;
  border: 1px solid rgba(129, 140, 248, 0.35);
  color: #c7d2fe;
}
.vv-btn-outline:hover {
  background: rgba(99, 102, 241, 0.15);
  color: #ffffff;
}
.vv-btn-secondary {
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}

/* Modals */
.vv-modal-overlay, .vv-confirm-overlay {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1050; padding: 1.5rem;
}
.vv-modal, .vv-confirm {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  width: 100%; max-width: 550px;
  max-height: 90vh; display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}
.vv-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex; align-items: center; justify-content: space-between;
}
.vv-modal-header h3 { font-size: 1.15rem; font-weight: 800; color: #f1f5f9; margin: 0; }
.vv-modal-close { background: transparent; border: none; color: #94a3b8; font-size: 1rem; cursor: pointer; }
.vv-modal-body { padding: 1.5rem; overflow-y: auto; flex: 1; }
.vv-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex; justify-content: flex-end; gap: 0.75rem;
}

.vv-modal-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-top: 0.5rem;
}
.vv-modal-label {
  font-size: 0.75rem;
  color: #94a3b8;
  display: block;
}

.vv-confirm { max-width: 420px; padding: 1.5rem; text-align: center; }
.vv-confirm-icon { font-size: 2.5rem; color: #818cf8; margin-bottom: 0.75rem; }
.vv-confirm-title { font-size: 1.15rem; font-weight: 800; color: #f1f5f9; margin: 0 0 0.5rem; }
.vv-confirm-text { font-size: 0.88rem; color: #94a3b8; margin: 0 0 1.25rem; }
.vv-confirm-actions { display: flex; justify-content: center; gap: 0.75rem; }

.vv-empty {
  text-align: center;
  padding: 3.5rem 1.5rem;
  color: #64748b;
}
.vv-empty-title { font-size: 1.2rem; font-weight: 800; color: #f1f5f9; margin: 1rem 0 0.4rem; }
.vv-empty-text { font-size: 0.88rem; color: #94a3b8; margin: 0 0 1.5rem; }
.vv-empty-btn {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none; border-radius: 10px;
  padding: 0.6rem 1.2rem; color: #ffffff;
  font-size: 0.88rem; font-weight: 700; cursor: pointer;
}

.vv-toast {
  position: fixed; bottom: 2rem; right: 2rem;
  padding: 0.75rem 1.25rem; border-radius: 12px;
  background: #1e293b; border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff; font-size: 0.88rem; font-weight: 600;
  display: flex; align-items: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 1100;
}
</style>
