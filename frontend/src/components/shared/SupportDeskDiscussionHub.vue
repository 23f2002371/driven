<template>
  <div class="sdh-container">
    <!-- Header Section -->
    <div class="sdh-header">
      <div>
        <h3 class="sdh-title">
          <i class="bi bi-chat-square-text-fill me-2 text-primary"></i>Support Desk & Event Discussions
        </h3>
        <p class="sdh-subtitle">
          Browse event discussion forums, collaborate with organizers & participants, ask questions, and share updates.
        </p>
      </div>

      <!-- Action Button for Club Admin -->
      <div v-if="isAdmin" class="sdh-header-actions">
        <button class="sdh-btn-create" @click="openCreateModal">
          <i class="bi bi-plus-circle-fill me-2"></i>Create Discussion
        </button>
      </div>
    </div>

    <!-- Search & Filter Bar -->
    <div class="sdh-filter-bar">
      <div class="sdh-search-wrap">
        <i class="bi bi-search sdh-search-icon"></i>
        <input
          v-model="searchQuery"
          type="text"
          class="sdh-search-input"
          placeholder="Search discussion threads or events..."
        />
        <button v-if="searchQuery" class="sdh-search-clear" @click="searchQuery = ''"><i class="bi bi-x-lg"></i></button>
      </div>

      <div class="sdh-filter-right">
        <span class="sdh-thread-count">{{ filteredThreads.length }} Forum{{ filteredThreads.length !== 1 ? 's' : '' }}</span>
        <button class="sdh-btn-refresh" :disabled="isLoading" @click="loadData" title="Refresh discussions">
          <i class="bi bi-arrow-clockwise" :class="{ 'spin-anim': isLoading }"></i>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="sdh-loading">
      <div class="spinner-border text-primary mb-3" role="status"></div>
      <h5>Loading Discussion Forums...</h5>
      <p class="text-secondary small">Fetching active threads and event channels.</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredThreads.length === 0" class="sdh-empty">
      <div class="sdh-empty-icon">
        <i class="bi bi-chat-square-dots"></i>
      </div>
      <h4 class="sdh-empty-title">
        {{ searchQuery ? 'No matching discussion threads found' : 'No discussion threads created yet' }}
      </h4>
      <p class="sdh-empty-desc">
        {{
          isAdmin
            ? 'Click "Create Discussion" above to start an event discussion forum for your club events.'
            : 'Event organizers will start discussion threads here soon. Check back shortly!'
        }}
      </p>
      <div v-if="isAdmin && !searchQuery" class="mt-3">
        <button class="sdh-btn-create" @click="openCreateModal">
          <i class="bi bi-plus-circle-fill me-2"></i>Create First Discussion
        </button>
      </div>
    </div>

    <!-- Threads Row List -->
    <div v-else class="sdh-list">
      <div
        v-for="thread in filteredThreads"
        :key="thread.id"
        class="sdh-row-item"
        :class="{ 'sdh-row-active': activeThread?.id === thread.id }"
        @click="openSidePanel(thread)"
      >
        <!-- Left Icon -->
        <div class="sdh-row-icon">
          <i class="bi bi-chat-square-text-fill"></i>
        </div>

        <!-- Main Content -->
        <div class="sdh-row-main">
          <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
            <h4 class="sdh-row-title m-0">{{ thread.title }}</h4>
            <span class="sdh-event-badge">{{ getEventCategory(thread) }}</span>
          </div>

          <div class="sdh-row-meta">
            <span class="sdh-meta-event"><i class="bi bi-calendar-event me-1 text-primary"></i>{{ getEventName(thread) }}</span>
            <span class="sdh-meta-dot">•</span>
            <span class="sdh-meta-author"><i class="bi bi-person me-1"></i>Host: {{ thread.creator_name || 'Club Lead' }}</span>
            <span class="sdh-meta-dot">•</span>
            <span class="sdh-meta-time"><i class="bi bi-clock me-1"></i>{{ formatTimeAgo(thread.created_at) }}</span>
          </div>
        </div>

        <!-- Right Actions -->
        <div class="sdh-row-actions">
          <button class="sdh-btn-open-panel" @click.stop="openSidePanel(thread)">
            <i class="bi bi-chat-dots-fill me-2"></i>Open Discussion
          </button>

          <!-- Admin Delete Thread Button -->
          <button
            v-if="isAdmin"
            class="sdh-btn-delete-thread"
            title="Delete discussion thread"
            @click.stop="confirmDeleteThread(thread)"
          >
            <i class="bi bi-trash3"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- ── Slide-Out Discussion Side Panel ── -->
    <Transition name="sdh-panel">
      <div v-if="activeThread" class="sdh-panel-overlay" @click.self="closeSidePanel">
        <div class="sdh-panel">
          <!-- Panel Header -->
          <div class="sdh-panel-header">
            <div class="sdh-panel-header-left">
              <span class="sdh-panel-event-tag">
                <i class="bi bi-calendar-event me-1"></i>{{ getEventName(activeThread) }}
              </span>
              <h3 class="sdh-panel-title">{{ activeThread.title }}</h3>
              <div class="sdh-panel-sub-meta">
                <span><i class="bi bi-person-fill me-1"></i>Created by {{ activeThread.creator_name || 'Club Admin' }}</span>
                <span>•</span>
                <span>{{ formatFullDate(activeThread.created_at) }}</span>
              </div>
            </div>
            <button class="sdh-panel-close" @click="closeSidePanel" title="Close Panel">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <!-- Panel Body: Embeds EventDiscussionThread -->
          <div class="sdh-panel-body">
            <EventDiscussionThread
              :key="activeThread.id"
              :event-id="String(activeThread.event_id)"
              :event-name="getEventName(activeThread)"
              :is-admin="isAdmin"
            />
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── Create Discussion Modal (Club Admin) ── -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="sdh-modal-backdrop" @click.self="closeCreateModal">
        <div class="sdh-modal-card">
          <div class="sdh-modal-header">
            <div class="d-flex align-items-center gap-2">
              <div class="sdh-modal-icon"><i class="bi bi-chat-square-plus-fill"></i></div>
              <div>
                <h4 class="sdh-modal-title m-0">Create Event Discussion</h4>
                <span class="sdh-modal-sub">Start a dedicated discussion thread for a club event</span>
              </div>
            </div>
            <button class="sdh-modal-close" @click="closeCreateModal"><i class="bi bi-x-lg"></i></button>
          </div>

          <div class="sdh-modal-body">
            <!-- Event Picker -->
            <div class="mb-3">
              <label class="sdh-form-label"><i class="bi bi-calendar-event me-1 text-primary"></i>Choose Event *</label>
              <select v-model="createForm.eventId" class="sdh-form-select" @change="onEventSelectChange">
                <option value="" disabled>-- Select an Event --</option>
                <option v-for="ev in availableEvents" :key="ev.id" :value="String(ev.id)">
                  {{ ev.name }} ({{ ev.venue || 'Campus' }})
                </option>
              </select>
              <span v-if="availableEvents.length === 0" class="text-warning small mt-1 d-block">
                No events found. Please create an event first.
              </span>
            </div>

            <!-- Title Input -->
            <div class="mb-3">
              <label class="sdh-form-label"><i class="bi bi-type-h1 me-1 text-primary"></i>Discussion Forum Title *</label>
              <input
                v-model="createForm.title"
                type="text"
                class="sdh-form-input"
                placeholder="e.g. IoT Architecture Workshop - Q&A & Discussion"
                maxlength="200"
              />
              <span class="sdh-form-hint">A clear title to help participants identify the discussion thread.</span>
            </div>

            <div v-if="createModalError" class="alert alert-danger py-2 px-3 rounded-3 small">
              <i class="bi bi-exclamation-circle me-1"></i>{{ createModalError }}
            </div>
          </div>

          <div class="sdh-modal-footer">
            <button class="sdh-btn-modal-cancel" :disabled="isSubmittingCreate" @click="closeCreateModal">
              Cancel
            </button>
            <button
              class="sdh-btn-modal-submit"
              :disabled="isSubmittingCreate || !createForm.eventId || !createForm.title.trim()"
              @click="submitCreateThread"
            >
              <span v-if="isSubmittingCreate" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="bi bi-check-circle-fill me-1"></i>
              {{ isSubmittingCreate ? 'Creating Thread...' : 'Create Discussion' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Delete Thread Confirmation Modal ── -->
    <Teleport to="body">
      <div v-if="showDeleteModal && threadToDelete" class="sdh-modal-backdrop" @click.self="showDeleteModal = false">
        <div class="sdh-modal-card sdh-modal-confirm">
          <div class="sdh-confirm-icon-wrap">
            <i class="bi bi-trash3-fill"></i>
          </div>
          <h4 class="sdh-modal-title">Delete Discussion Thread?</h4>
          <p class="sdh-confirm-desc">
            Are you sure you want to permanently delete <strong>"{{ threadToDelete.title }}"</strong> and all associated messages? This action cannot be undone.
          </p>
          <div class="sdh-modal-footer p-0 border-0 d-flex gap-2">
            <button class="sdh-btn-modal-cancel flex-fill" :disabled="isDeletingThread" @click="showDeleteModal = false">
              Cancel
            </button>
            <button class="sdh-btn-modal-delete flex-fill" :disabled="isDeletingThread" @click="executeDeleteThread">
              <span v-if="isDeletingThread" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="bi bi-trash3 me-1"></i>
              {{ isDeletingThread ? 'Deleting...' : 'Yes, Delete Thread' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { store } from '../../store/mockData';
import { fetchEventsApi } from '../../api/events';
import {
  fetchDiscussionThreadsApi,
  createDiscussionThreadApi,
  deleteDiscussionThreadApi,
  getDiscussionThreadApi,
} from '../../api/discussion';
import EventDiscussionThread from './EventDiscussionThread.vue';

const props = defineProps({
  isAdmin: { type: Boolean, default: false },
});

const threads = ref([]);
const events = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');
const activeThread = ref(null);

// Create Modal State
const showCreateModal = ref(false);
const isSubmittingCreate = ref(false);
const createModalError = ref('');
const createForm = ref({
  eventId: '',
  title: '',
});

// Delete Modal State
const showDeleteModal = ref(false);
const threadToDelete = ref(null);
const isDeletingThread = ref(false);

const loadData = async () => {
  isLoading.value = true;
  const token = store.token || localStorage.getItem('driven_token');

  try {
    // 1. Fetch live events list
    const evList = await fetchEventsApi(token).catch(() => []);
    events.value = Array.isArray(evList) && evList.length > 0 ? evList : (store.events || []);

    // 2. Fetch live discussion threads
    const thList = await fetchDiscussionThreadsApi(token).catch(() => []);
    if (Array.isArray(thList) && thList.length > 0) {
      threads.value = thList;
    } else {
      // Fallback check per event if threads endpoint returns empty
      const threadsAcc = [];
      for (const ev of events.value.slice(0, 8)) {
        try {
          const t = await getDiscussionThreadApi(ev.id, token);
          if (t && !threadsAcc.some(x => x.id === t.id)) {
            threadsAcc.push(t);
          }
        } catch {}
      }
      threads.value = threadsAcc;
    }
  } catch (err) {
    console.error('Failed to load support desk data:', err);
  } finally {
    isLoading.value = false;
  }
};

const availableEvents = computed(() => {
  return events.value || [];
});

const filteredThreads = computed(() => {
  let list = [...threads.value];
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim();
    list = list.filter(t => {
      const evName = getEventName(t).toLowerCase();
      const title = (t.title || '').toLowerCase();
      const creator = (t.creator_name || '').toLowerCase();
      return evName.includes(q) || title.includes(q) || creator.includes(q);
    });
  }
  return list;
});

const getEventForThread = (thread) => {
  if (!thread || !thread.event_id) return null;
  return events.value.find(e => String(e.id) === String(thread.event_id)) || null;
};

const getEventName = (thread) => {
  const ev = getEventForThread(thread);
  return ev ? ev.name : (thread.title || 'Club Event');
};

const getEventCategory = (thread) => {
  const ev = getEventForThread(thread);
  return ev ? (ev.category || 'Workshop') : 'Discussion';
};

const getEventImage = (thread) => {
  const ev = getEventForThread(thread);
  return ev?.cover_image_url || ev?.image || 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=600&h=300&fit=crop';
};

const getInitials = (name) => {
  if (!name) return 'CL';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
};

const formatTimeAgo = (d) => {
  if (!d) return 'Recently';
  const date = new Date(d);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);
  if (diffSec < 60) return 'Just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHrs = Math.floor(diffMin / 60);
  if (diffHrs < 24) return `${diffHrs}h ago`;
  const diffDays = Math.floor(diffHrs / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const formatFullDate = (d) => {
  if (!d) return '';
  const date = new Date(d);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/* ── Side Panel Drawer ── */
const openSidePanel = (thread) => {
  activeThread.value = thread;
};

const closeSidePanel = () => {
  activeThread.value = null;
};

/* ── Create Modal ── */
const openCreateModal = () => {
  createModalError.value = '';
  createForm.value = {
    eventId: availableEvents.value.length > 0 ? String(availableEvents.value[0].id) : '',
    title: availableEvents.value.length > 0 ? `${availableEvents.value[0].name} Discussion` : '',
  };
  showCreateModal.value = true;
};

const onEventSelectChange = () => {
  const ev = availableEvents.value.find(e => String(e.id) === String(createForm.value.eventId));
  if (ev) {
    createForm.value.title = `${ev.name} Discussion`;
  }
};

const closeCreateModal = () => {
  showCreateModal.value = false;
};

const submitCreateThread = async () => {
  if (!createForm.value.eventId || !createForm.value.title.trim()) return;
  const token = store.token || localStorage.getItem('driven_token');

  isSubmittingCreate.value = true;
  createModalError.value = '';

  try {
    const res = await createDiscussionThreadApi(
      createForm.value.eventId,
      createForm.value.title.trim(),
      token
    );
    threads.value.unshift(res);
    closeCreateModal();
    // Automatically open the side panel for the created thread
    openSidePanel(res);
  } catch (err) {
    createModalError.value = err.message || 'Failed to create discussion thread.';
  } finally {
    isSubmittingCreate.value = false;
  }
};

/* ── Delete Thread ── */
const confirmDeleteThread = (thread) => {
  threadToDelete.value = thread;
  showDeleteModal.value = true;
};

const executeDeleteThread = async () => {
  if (!threadToDelete.value) return;
  const token = store.token || localStorage.getItem('driven_token');

  isDeletingThread.value = true;
  try {
    await deleteDiscussionThreadApi(threadToDelete.value.id, token);
    threads.value = threads.value.filter(t => t.id !== threadToDelete.value.id);
    if (activeThread.value?.id === threadToDelete.value.id) {
      closeSidePanel();
    }
    showDeleteModal.value = false;
    threadToDelete.value = null;
  } catch (err) {
    alert(err.message || 'Failed to delete discussion thread');
  } finally {
    isDeletingThread.value = false;
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.sdh-container {
  animation: sdhFadeIn 0.3s ease;
  position: relative;
}

.sdh-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.sdh-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #f8fafc;
  margin: 0;
}

.sdh-subtitle {
  font-size: 0.86rem;
  color: #94a3b8;
  margin: 0.25rem 0 0;
}

.sdh-btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 12px;
  padding: 0.7rem 1.4rem;
  color: #ffffff;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}
.sdh-btn-create:hover {
  filter: brightness(1.1);
  transform: translateY(-2px);
}

/* Filter Bar */
.sdh-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  backdrop-filter: blur(14px);
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
}

.sdh-search-wrap {
  position: relative;
  flex: 1;
  min-width: 240px;
  max-width: 420px;
}

.sdh-search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.85rem;
  pointer-events: none;
}

.sdh-search-input {
  width: 100%;
  padding: 0.55rem 0.85rem 0.55rem 2.3rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #f1f5f9;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s;
}
.sdh-search-input:focus {
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  background: rgba(255, 255, 255, 0.07);
}

.sdh-search-clear {
  position: absolute;
  right: 0.65rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #64748b;
  font-size: 0.65rem;
  cursor: pointer;
}

.sdh-filter-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sdh-thread-count {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 600;
}

.sdh-btn-refresh {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.sdh-btn-refresh:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

/* Loading & Empty */
.sdh-loading,
.sdh-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 5rem 1.5rem;
  color: #94a3b8;
}

.sdh-empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: #64748b;
  margin-bottom: 1.25rem;
}

.sdh-empty-title {
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.4rem;
}

.sdh-empty-desc {
  max-width: 440px;
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0;
}

/* Row Format List */
.sdh-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.sdh-row-item {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}
.sdh-row-item:hover {
  background: rgba(15, 23, 42, 0.95);
  border-color: rgba(129, 140, 248, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}
.sdh-row-active {
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3);
}

.sdh-row-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #818cf8;
  flex-shrink: 0;
}

.sdh-row-main {
  flex: 1;
  min-width: 0;
}

.sdh-row-title {
  font-size: 1.02rem;
  font-weight: 800;
  color: #f1f5f9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sdh-event-badge {
  background: rgba(99, 102, 241, 0.2);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #c7d2fe;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  text-transform: uppercase;
}

.sdh-row-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #94a3b8;
  flex-wrap: wrap;
}

.sdh-meta-event {
  color: #cbd5e1;
  font-weight: 600;
}
.sdh-meta-dot {
  color: #475569;
}
.sdh-meta-author {
  color: #94a3b8;
}
.sdh-meta-time {
  color: #64748b;
}

.sdh-row-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.sdh-btn-open-panel {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.3);
  border-radius: 10px;
  padding: 0.55rem 1rem;
  color: #c7d2fe;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  display: inline-flex;
  align-items: center;
}
.sdh-btn-open-panel:hover {
  background: rgba(99, 102, 241, 0.3);
  color: #ffffff;
}

.sdh-btn-delete-thread {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 10px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.2s;
}
.sdh-btn-delete-thread:hover {
  background: rgba(239, 68, 68, 0.25);
  color: #ffffff;
}

/* ── Slide-Out Side Panel Drawer ── */
.sdh-panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(6px);
  z-index: 999;
  display: flex;
  justify-content: flex-end;
}

.sdh-panel {
  width: 600px;
  max-width: 90vw;
  height: 100vh;
  background: #090f1d;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  box-shadow: -10px 0 40px rgba(0, 0, 0, 0.7);
  overflow: hidden;
}

.sdh-panel-header {
  padding: 1.5rem 1.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.95);
}

.sdh-panel-event-tag {
  font-size: 0.75rem;
  font-weight: 700;
  color: #818cf8;
  text-transform: uppercase;
}

.sdh-panel-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0.2rem 0;
  line-height: 1.3;
}

.sdh-panel-sub-meta {
  font-size: 0.76rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sdh-panel-close {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.sdh-panel-close:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
}

.sdh-panel-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0;
}

/* ── Modals ── */
.sdh-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.sdh-modal-card {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  max-width: 520px;
  width: 100%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  animation: sdhScaleIn 0.2s ease;
  overflow: hidden;
}

.sdh-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sdh-modal-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.2);
  border: 1px solid rgba(129, 140, 248, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #818cf8;
  font-size: 1.2rem;
}

.sdh-modal-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #f1f5f9;
}

.sdh-modal-sub {
  font-size: 0.78rem;
  color: #94a3b8;
}

.sdh-modal-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
}
.sdh-modal-close:hover {
  color: #ffffff;
}

.sdh-modal-body {
  padding: 1.5rem;
}

.sdh-form-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #cbd5e1;
  margin-bottom: 0.4rem;
  display: block;
}

.sdh-form-select,
.sdh-form-input {
  width: 100%;
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
  transition: all 0.2s;
}
.sdh-form-select:focus,
.sdh-form-input:focus {
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.sdh-form-hint {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 0.35rem;
  display: block;
}

.sdh-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sdh-btn-modal-cancel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.6rem 1.2rem;
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}
.sdh-btn-modal-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.sdh-btn-modal-submit {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1.4rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.sdh-btn-modal-submit:hover {
  filter: brightness(1.1);
}
.sdh-btn-modal-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Confirm Delete Modal */
.sdh-modal-confirm {
  max-width: 420px;
  padding: 2rem;
  text-align: center;
}

.sdh-confirm-icon-wrap {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: #ef4444;
  margin: 0 auto 1.25rem;
}

.sdh-confirm-desc {
  font-size: 0.88rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.sdh-btn-modal-delete {
  background: #dc2626;
  border: none;
  border-radius: 10px;
  padding: 0.65rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s;
}
.sdh-btn-modal-delete:hover {
  background: #b91c1c;
}
.sdh-btn-modal-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-anim {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

@keyframes sdhFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes sdhScaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* Panel slide transition */
.sdh-panel-enter-active,
.sdh-panel-leave-active {
  transition: opacity 0.3s ease;
}
.sdh-panel-enter-active .sdh-panel,
.sdh-panel-leave-active .sdh-panel {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.sdh-panel-enter-from,
.sdh-panel-leave-to {
  opacity: 0;
}
.sdh-panel-enter-from .sdh-panel,
.sdh-panel-leave-to .sdh-panel {
  transform: translateX(100%);
}
</style>
