<template>
  <div class="ssd-page">
    <section class="ssd-hero">
      <div class="ssd-hero-bg"></div>
      <div class="ssd-hero-inner">
        <div class="ssd-hero-left">
          <div class="ssd-hero-tag">Support</div>
          <h1 class="ssd-hero-title">Support Desk</h1>
          <p class="ssd-hero-sub">Need help with events, registrations, or inventory? Create a support request and track every conversation with the club administrators in one place.</p>
          <button class="ssd-hero-cta" @click="showNewTicketModal = true">
            <i class="bi bi-plus-lg me-2"></i>New Support Ticket
          </button>
        </div>
        <div class="ssd-hero-right">
          <div class="ssd-stat-card" v-for="stat in stats" :key="stat.label">
            <div class="ssd-stat-icon" :style="{ background: stat.iconBg, color: stat.iconColor }">
              <i :class="'bi bi-' + stat.icon"></i>
            </div>
            <div class="ssd-stat-body">
              <span class="ssd-stat-value">{{ stat.value }}</span>
              <span class="ssd-stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="ssd-toolbar">
      <div class="ssd-toolbar-left">
        <div class="ssd-search-wrap">
          <i class="bi bi-search ssd-search-icon"></i>
          <input v-model="searchQuery" type="text" class="ssd-search-input" placeholder="Search tickets..." />
          <button v-if="searchQuery" class="ssd-search-clear" @click="searchQuery = ''"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="ssd-filter-group">
          <div class="ssd-select-wrap">
            <i class="bi bi-circle-fill ssd-select-icon"></i>
            <select v-model="statusFilter" class="ssd-select">
              <option value="">All Status</option>
              <option value="Open">Open</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>
          <div class="ssd-select-wrap">
            <i class="bi bi-tag ssd-select-icon"></i>
            <select v-model="categoryFilter" class="ssd-select">
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div class="ssd-select-wrap">
            <i class="bi bi-flag ssd-select-icon"></i>
            <select v-model="priorityFilter" class="ssd-select">
              <option value="">All Priorities</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          <div class="ssd-select-wrap">
            <i class="bi bi-arrow-down-up ssd-select-icon"></i>
            <select v-model="sortBy" class="ssd-select">
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>
        </div>
      </div>
      <div class="ssd-toolbar-right">
        <span class="ssd-result-count">{{ filteredTickets.length }} tickets</span>
        <button class="ssd-btn-new" @click="showNewTicketModal = true">
          <i class="bi bi-plus-lg"></i><span>New Ticket</span>
        </button>
      </div>
    </div>

    <div v-if="filteredTickets.length > 0" class="ssd-grid">
      <div
        v-for="(ticket, index) in filteredTickets"
        :key="ticket.id"
        class="ssd-card"
        :class="{ 'ssd-card-unread': hasUnread(ticket), 'ssd-card-resolved': ticket.status === 'Resolved' }"
        :style="{ animationDelay: `${index * 0.05}s` }"
      >
        <div class="ssd-card-head">
          <div class="ssd-card-badges-top">
            <span class="ssd-badge-cat">{{ ticket.category || 'General' }}</span>
            <span class="ssd-badge-priority" :class="ticket.priority?.toLowerCase() || 'low'">{{ ticket.priority || 'Low' }}</span>
            <span class="ssd-badge-status" :class="ticket.status?.toLowerCase() || 'open'">{{ ticket.status || 'Open' }}</span>
          </div>
          <div v-if="hasUnread(ticket)" class="ssd-unread-dot" title="New reply"></div>
        </div>
        <h3 class="ssd-card-title">{{ ticket.subject }}</h3>
        <p class="ssd-card-preview">{{ ticket.description || ticket.subject }}</p>
        <div class="ssd-card-meta">
          <span><i class="bi bi-clock"></i>{{ ticket.createdAt }}</span>
          <span><i class="bi bi-arrow-repeat"></i>{{ ticket.lastUpdated }}</span>
          <span><i class="bi bi-chat-dots"></i>{{ ticket.messages?.length || 0 }} msgs</span>
        </div>
        <div class="ssd-card-actions">
          <button class="ssd-action-btn" @click="openConversation(ticket)"><i class="bi bi-chat-dots"></i>View Conversation</button>
          <button v-if="ticket.status === 'Open'" class="ssd-action-btn subtle" @click="openConversation(ticket)"><i class="bi bi-pencil"></i>Edit</button>
          <button v-if="ticket.status === 'Open'" class="ssd-action-btn danger" @click="closeTicket(ticket)"><i class="bi bi-x-lg"></i>Close</button>
        </div>
      </div>
    </div>

    <div v-else class="ssd-empty">
      <div class="ssd-empty-illustration">
        <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="40" y="30" width="120" height="90" rx="14" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
          <circle cx="100" cy="55" r="12" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
          <rect x="72" y="75" width="56" height="6" rx="3" fill="rgba(255,255,255,0.05)"/>
          <rect x="72" y="87" width="40" height="6" rx="3" fill="rgba(255,255,255,0.03)"/>
          <rect x="72" y="99" width="48" height="6" rx="3" fill="rgba(255,255,255,0.03)"/>
          <path d="M55 130h90" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M80 130l-8-8M80 130l8-8" stroke="rgba(129,140,248,0.2)" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="100" cy="145" r="3" fill="rgba(129,140,248,0.2)"/>
        </svg>
      </div>
      <h3 class="ssd-empty-title">No Support Tickets Yet</h3>
      <p class="ssd-empty-text">Need help? Create your first support request and our team will get back to you.</p>
      <button class="ssd-empty-btn" @click="showNewTicketModal = true">
        <i class="bi bi-plus-lg me-2"></i>New Ticket
      </button>
    </div>

    <Transition name="ssd-modal">
      <div v-if="showNewTicketModal" class="ssd-modal-overlay" @click.self="showNewTicketModal = false">
        <div class="ssd-modal">
          <div class="ssd-modal-header">
            <div>
              <h2 class="ssd-modal-title">New Support Ticket</h2>
              <p class="ssd-modal-sub">Describe your issue and our team will respond shortly.</p>
            </div>
            <button class="ssd-modal-close" @click="showNewTicketModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="ssd-modal-body">
            <div class="ssd-form-section">
              <h4 class="ssd-form-section-title">Ticket Information</h4>
              <div class="ssd-form-group">
                <label class="ssd-form-label">Subject <span class="required">*</span></label>
                <div class="ssd-input-wrap" :class="{ focus: focusSubject }">
                  <input v-model="newForm.subject" type="text" class="ssd-form-input" placeholder="e.g. Unable to register for Hackathon" @focus="focusSubject = true" @blur="focusSubject = false" />
                </div>
              </div>
              <div class="ssd-form-row">
                <div class="ssd-form-group">
                  <label class="ssd-form-label">Category <span class="required">*</span></label>
                  <div class="ssd-select-styled">
                    <select v-model="newForm.category" class="ssd-form-input">
                      <option value="" disabled>Select category</option>
                      <option value="Registration">Registration</option>
                      <option value="Inventory">Inventory</option>
                      <option value="Event">Event</option>
                      <option value="Technical">Technical</option>
                      <option value="Other">Other</option>
                    </select>
                    <i class="bi bi-chevron-down ssd-select-arrow"></i>
                  </div>
                </div>
                <div class="ssd-form-group">
                  <label class="ssd-form-label">Priority <span class="required">*</span></label>
                  <div class="ssd-select-styled">
                    <select v-model="newForm.priority" class="ssd-form-input">
                      <option value="" disabled>Select priority</option>
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                    </select>
                    <i class="bi bi-chevron-down ssd-select-arrow"></i>
                  </div>
                </div>
              </div>
              <div class="ssd-form-group">
                <label class="ssd-form-label">Related Event <span class="required">*</span></label>
                <div class="ssd-select-styled">
                  <select v-model="newForm.relatedEvent" class="ssd-form-input">
                    <option value="" disabled>Select an event</option>
                    <option v-for="event in ongoingEvents" :key="event.id" :value="event.name">{{ event.name }} — {{ event.date }}</option>
                  </select>
                  <i class="bi bi-chevron-down ssd-select-arrow"></i>
                </div>
              </div>
              <div class="ssd-form-group">
                <label class="ssd-form-label">Description <span class="required">*</span></label>
                <textarea v-model="newForm.description" class="ssd-form-textarea" rows="4" placeholder="Describe your issue in detail..."></textarea>
              </div>
              <div class="ssd-form-group">
                <label class="ssd-form-label">Attachment <span class="ssd-optional">(optional)</span></label>
                <div class="ssd-upload-zone" @click="attachInput?.click()" @dragover.prevent @drop.prevent="handleDrop">
                  <input ref="attachInput" type="file" hidden @change="handleAttach" />
                  <i class="bi bi-cloud-arrow-up ssd-upload-icon"></i>
                  <p class="ssd-upload-text">Drop files here or <span>Browse</span></p>
                  <div v-if="newForm.attachmentName" class="ssd-attach-preview">
                    <i class="bi bi-file-earmark"></i>
                    <span>{{ newForm.attachmentName }}</span>
                    <button class="ssd-attach-remove" @click.stop="newForm.attachmentName = ''; newForm.attachment = null"><i class="bi bi-x"></i></button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="ssd-modal-footer">
            <span class="ssd-footer-hint"><span class="required">*</span> Required fields</span>
            <div class="ssd-footer-actions">
              <button class="ssd-btn-ghost" @click="showNewTicketModal = false">Cancel</button>
              <button class="ssd-btn-ghost" @click="submitTicket">Save as Draft</button>
              <button class="ssd-btn-primary" :disabled="!formValid" @click="submitTicket">
                <i class="bi bi-send-fill me-1"></i>Submit Ticket
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="ssd-panel">
      <div v-if="conversationTicket" class="ssd-panel-overlay" @click.self="closeConversation">
        <div class="ssd-panel">
          <button class="ssd-panel-close" @click="closeConversation"><i class="bi bi-x-lg"></i></button>
          <div class="ssd-panel-scroll">
            <div class="ssd-panel-section">
              <div class="ssd-panel-head">
                <h2 class="ssd-panel-title">{{ conversationTicket.subject }}</h2>
                <div class="ssd-panel-badges">
                  <span class="ssd-badge-cat">{{ conversationTicket.category || 'General' }}</span>
                  <span class="ssd-badge-priority" :class="conversationTicket.priority?.toLowerCase() || 'low'">{{ conversationTicket.priority || 'Low' }}</span>
                  <span class="ssd-badge-status" :class="conversationTicket.status?.toLowerCase() || 'open'">{{ conversationTicket.status || 'Open' }}</span>
                </div>
              </div>
            </div>

            <div class="ssd-panel-section">
              <h4 class="ssd-panel-section-title">Status Timeline</h4>
              <div class="ssd-timeline">
                <div class="ssd-tl-item" :class="{ active: true, done: true }">
                  <div class="ssd-tl-dot done"></div>
                  <div class="ssd-tl-content">
                    <span class="ssd-tl-label">Ticket Created</span>
                    <span class="ssd-tl-time">{{ conversationTicket.createdAt }}</span>
                  </div>
                </div>
                <div class="ssd-tl-item" :class="{ active: timelineStage >= 1, done: timelineStage > 1 }">
                  <div class="ssd-tl-dot" :class="timelineStage >= 1 ? (timelineStage > 1 ? 'done' : 'active') : ''"></div>
                  <div class="ssd-tl-content">
                    <span class="ssd-tl-label">Under Review</span>
                    <span class="ssd-tl-time" v-if="timelineStage >= 1">Reviewed</span>
                  </div>
                </div>
                <div class="ssd-tl-item" :class="{ active: timelineStage >= 2, done: timelineStage > 2 }">
                  <div class="ssd-tl-dot" :class="timelineStage >= 2 ? (timelineStage > 2 ? 'done' : 'active') : ''"></div>
                  <div class="ssd-tl-content">
                    <span class="ssd-tl-label">Admin Replied</span>
                    <span class="ssd-tl-time" v-if="timelineStage >= 2">Replied</span>
                  </div>
                </div>
                <div class="ssd-tl-item" :class="{ active: timelineStage >= 3, done: timelineStage > 3 }">
                  <div class="ssd-tl-dot" :class="timelineStage >= 3 ? (timelineStage > 3 ? 'done' : 'active') : ''"></div>
                  <div class="ssd-tl-content">
                    <span class="ssd-tl-label">Waiting for Student</span>
                    <span class="ssd-tl-time" v-if="timelineStage >= 3">Waiting</span>
                  </div>
                </div>
                <div class="ssd-tl-item" :class="{ active: conversationTicket.status === 'Resolved', done: conversationTicket.status === 'Resolved' }">
                  <div class="ssd-tl-dot" :class="conversationTicket.status === 'Resolved' ? 'done' : ''"></div>
                  <div class="ssd-tl-content">
                    <span class="ssd-tl-label">Resolved</span>
                    <span class="ssd-tl-time" v-if="conversationTicket.status === 'Resolved'">{{ conversationTicket.lastUpdated }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="ssd-panel-section">
              <h4 class="ssd-panel-section-title">Conversation</h4>
              <div class="ssd-chat">
                <div
                  v-for="msg in conversationTicket.messages"
                  :key="msg.id"
                  class="ssd-msg"
                  :class="msg.from === 'admin' ? 'admin' : 'student'"
                >
                  <div class="ssd-msg-avatar">
                    <div class="ssd-msg-avatar-inner" :style="{ background: msg.from === 'admin' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'linear-gradient(135deg, #34d399, #10b981)' }">
                      {{ msg.from === 'admin' ? 'AD' : 'You' }}
                    </div>
                  </div>
                  <div class="ssd-msg-body">
                    <div class="ssd-msg-header">
                      <span class="ssd-msg-author">{{ msg.from === 'admin' ? 'Admin' : 'You' }}</span>
                      <span class="ssd-msg-time">{{ msg.timestamp }}</span>
                    </div>
                    <div class="ssd-msg-bubble">
                      <p>{{ msg.text }}</p>
                      <div v-if="msg.attachments && msg.attachments.length" class="ssd-msg-attachments">
                        <button
                          v-for="att in msg.attachments"
                          :key="attachmentKey(att)"
                          type="button"
                          class="ssd-msg-attach"
                          @click="openAttachmentPreview(att)"
                        >
                          <i class="bi bi-paperclip"></i>{{ attachmentName(att) }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="conversationTicket.status === 'Resolved'" class="ssd-resolved-banner">
              <i class="bi bi-check-circle-fill"></i>
              <div>
                <strong>This ticket has been resolved</strong>
                <span>If you need further assistance, you can reopen this ticket.</span>
              </div>
              <button class="ssd-btn-reopen" @click="reopenTicket(conversationTicket)">
                <i class="bi bi-arrow-counterclockwise me-1"></i>Reopen Ticket
              </button>
            </div>

            <div v-else class="ssd-reply-area">
              <textarea v-model="replyText" class="ssd-reply-input" rows="2" placeholder="Type your reply..." @keydown.meta.enter="sendReply" @keydown.ctrl.enter="sendReply"></textarea>
              <div class="ssd-reply-toolbar">
                <button class="ssd-reply-tool" title="Attach file"><i class="bi bi-paperclip"></i></button>
                <button class="ssd-reply-send" :disabled="!replyText.trim()" @click="sendReply">
                  <i class="bi bi-send-fill"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="ssd-toast">
      <div v-if="showToast" class="ssd-toast" :class="toastType">
        <i :class="'bi bi-' + (toastType === 'success' ? 'check-circle-fill' : 'info-circle-fill')"></i>
        <div class="ssd-toast-content">
          <strong>{{ toastTitle }}</strong>
          <span>{{ toastMessage }}</span>
        </div>
      </div>
    </Transition>

    <Transition name="ssd-modal">
      <div v-if="previewAttachment" class="ssd-attach-overlay" @click.self="closeAttachmentPreview">
        <div class="ssd-attach-modal">
          <div class="ssd-attach-header">
            <div>
              <h3>{{ attachmentName(previewAttachment) }}</h3>
              <span>{{ attachmentMeta(previewAttachment) }}</span>
            </div>
            <button class="ssd-attach-close" @click="closeAttachmentPreview"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="ssd-attach-body">
            <img
              v-if="isImageAttachment(previewAttachment) && attachmentUrl(previewAttachment)"
              :src="attachmentUrl(previewAttachment)"
              :alt="attachmentName(previewAttachment)"
              class="ssd-attach-image"
            />
            <iframe
              v-else-if="isPdfAttachment(previewAttachment) && attachmentUrl(previewAttachment)"
              :src="attachmentUrl(previewAttachment)"
              class="ssd-attach-frame"
              :title="attachmentName(previewAttachment)"
            ></iframe>
            <div v-else class="ssd-attach-fallback">
              <i class="bi bi-file-earmark-text"></i>
              <strong>{{ attachmentName(previewAttachment) }}</strong>
              <span>Preview is not available for this file type.</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { store } from '../../store/mockData';

const ongoingEvents = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return store.events.filter(e => e.status === 'Approved' && new Date(e.date) >= today);
});

const props = defineProps({
  tickets: { type: Array, required: true }
});

const emit = defineEmits(['ticket-submitted']);

const searchQuery = ref('');
const statusFilter = ref('');
const categoryFilter = ref('');
const priorityFilter = ref('');
const sortBy = ref('newest');
const showNewTicketModal = ref(false);
const conversationTicket = ref(null);
const replyText = ref('');
const showToast = ref(false);
const toastType = ref('success');
const toastTitle = ref('');
const toastMessage = ref('');
const focusSubject = ref(false);
const attachInput = ref(null);

const newForm = reactive({
  subject: '',
  category: '',
  priority: '',
  description: '',
  relatedEvent: '',
  attachment: null,
  attachmentName: ''
});

const categories = computed(() => {
  const cats = new Set(props.tickets.map(t => t.category).filter(Boolean));
  return [...cats];
});

const studentTickets = computed(() => {
  return props.tickets.filter(t => t.student === 'Current Student');
});

const filteredTickets = computed(() => {
  let result = [...studentTickets.value];

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(t =>
      t.subject.toLowerCase().includes(q) ||
      (t.description || '').toLowerCase().includes(q) ||
      (t.category || '').toLowerCase().includes(q)
    );
  }

  if (statusFilter.value) result = result.filter(t => t.status === statusFilter.value);
  if (categoryFilter.value) result = result.filter(t => t.category === categoryFilter.value);
  if (priorityFilter.value) result = result.filter(t => t.priority === priorityFilter.value);

  if (sortBy.value === 'newest') result.sort((a, b) => b.id - a.id);
  else result.sort((a, b) => a.id - b.id);

  return result;
});

const stats = computed(() => [
  {
    icon: 'chat-dots-fill',
    value: studentTickets.value.filter(t => t.status === 'Open').length,
    label: 'Open Tickets',
    iconBg: 'linear-gradient(135deg, rgba(244,114,182,0.2), rgba(236,72,153,0.1))',
    iconColor: '#f472b6'
  },
  {
    icon: 'check-circle-fill',
    value: studentTickets.value.filter(t => t.status === 'Resolved').length,
    label: 'Resolved',
    iconBg: 'linear-gradient(135deg, rgba(52,211,153,0.2), rgba(16,185,129,0.1))',
    iconColor: '#34d399'
  },
  {
    icon: 'clock-fill',
    value: '~2h',
    label: 'Avg Response',
    iconBg: 'linear-gradient(135deg, rgba(129,140,248,0.2), rgba(99,102,241,0.1))',
    iconColor: '#818cf8'
  },
  {
    icon: 'send-fill',
    value: studentTickets.value.length,
    label: 'Total Requests',
    iconBg: 'linear-gradient(135deg, rgba(251,191,36,0.2), rgba(245,158,11,0.1))',
    iconColor: '#fbbf24'
  }
]);

const formValid = computed(() => {
  return newForm.subject.trim() && newForm.category && newForm.priority && newForm.relatedEvent && newForm.description.trim();
});

const hasUnread = (ticket) => {
  if (ticket.status === 'Resolved') return false;
  const msgs = ticket.messages || [];
  const lastMsg = msgs[msgs.length - 1];
  return lastMsg && lastMsg.from === 'admin';
};

const timelineStage = computed(() => {
  const t = conversationTicket.value;
  if (!t) return 0;
  const msgs = t.messages || [];
  let stage = 0;
  for (const m of msgs) {
    if (m.from === 'admin') stage = 2;
    else if (stage === 2) stage = 3;
  }
  if (stage === 0) stage = 1;
  return stage;
});

const submitTicket = () => {
  if (!formValid.value) return;
  const attachments = newForm.attachmentName
    ? [{
        name: newForm.attachmentName,
        size: newForm.attachment?.size || 0,
        type: newForm.attachment?.type || 'application/octet-stream',
        url: newForm.attachment ? URL.createObjectURL(newForm.attachment) : '',
      }]
    : [];
  const ticketData = {
    subject: newForm.subject,
    category: newForm.category,
    priority: newForm.priority,
    description: newForm.description,
    relatedEvent: newForm.relatedEvent || '',
    attachments
  };
  store.addTicket(ticketData);
  newForm.subject = '';
  newForm.category = '';
  newForm.priority = '';
  newForm.description = '';
  newForm.relatedEvent = '';
  newForm.attachment = null;
  newForm.attachmentName = '';
  showNewTicketModal.value = false;
  emit('ticket-submitted');
  showToastMsg('success', 'Ticket Created', 'Your support request has been submitted successfully.');
};

const handleAttach = (e) => {
  const file = e.target.files?.[0];
  if (file) {
    newForm.attachment = file;
    newForm.attachmentName = file.name;
  }
};

const handleDrop = (e) => {
  const file = e.dataTransfer?.files?.[0];
  if (file) {
    newForm.attachment = file;
    newForm.attachmentName = file.name;
  }
};

const attachmentName = (attachment) => typeof attachment === 'string' ? attachment : attachment.name;
const attachmentUrl = (attachment) => typeof attachment === 'string' ? '' : attachment.url;
const attachmentKey = (attachment) => typeof attachment === 'string' ? attachment : `${attachment.name}-${attachment.size}`;

const previewAttachment = ref(null);
const openAttachmentPreview = (att) => { previewAttachment.value = att; };
const closeAttachmentPreview = () => { previewAttachment.value = null; };
const isImageAttachment = (att) => {
  const name = attachmentName(att).toLowerCase();
  return name.endsWith('.png') || name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.gif') || name.endsWith('.webp') || name.endsWith('.svg');
};
const isPdfAttachment = (att) => attachmentName(att).toLowerCase().endsWith('.pdf');
const attachmentMeta = (att) => {
  const name = attachmentName(att);
  if (typeof att === 'string') return 'Unknown file';
  const size = att.size || 0;
  const kb = (size / 1024).toFixed(1);
  const ext = name.includes('.') ? name.split('.').pop().toUpperCase() : 'Unknown';
  return `${ext} · ${kb} KB`;
};

const openConversation = (ticket) => {
  conversationTicket.value = ticket;
  replyText.value = '';
};

const closeConversation = () => {
  conversationTicket.value = null;
  replyText.value = '';
};

const sendReply = () => {
  if (!replyText.value.trim() || !conversationTicket.value) return;
  store.studentReply(conversationTicket.value.id, replyText.value);
  replyText.value = '';
  showToastMsg('info', 'Reply Sent', 'Your message has been sent.');
};

const reopenTicket = (ticket) => {
  store.reopenTicket(ticket.id);
  showToastMsg('info', 'Ticket Reopened', 'The ticket has been reopened.');
};

const closeTicket = (ticket) => {
  store.resolveTicket(ticket.id, '');
  showToastMsg('success', 'Ticket Closed', 'The ticket has been closed.');
};

const showToastMsg = (type, title, message) => {
  toastType.value = type;
  toastTitle.value = title;
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => { showToast.value = false; }, 3000);
};
</script>

<style scoped>
.ssd-page { position: relative; }

/* ── Hero ── */
.ssd-hero { position: relative; padding: 2rem 0 2.5rem; margin-bottom: 2.5rem; overflow: hidden; }
.ssd-hero-bg {
  position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 600px 400px at 70% 40%, rgba(129,140,248,0.07) 0%, transparent 65%),
    radial-gradient(ellipse 300px 300px at 30% 80%, rgba(52,211,153,0.04) 0%, transparent 70%);
}
.ssd-hero-inner { display: flex; align-items: flex-start; justify-content: space-between; gap: 2.5rem; position: relative; z-index: 1; }
.ssd-hero-left { flex: 1; min-width: 0; }
.ssd-hero-tag {
  display: inline-flex; align-items: center; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px;
  text-transform: uppercase; padding: 0.25rem 0.75rem; border-radius: 999px;
  background: rgba(52,211,153,0.1); color: #34d399; border: 1px solid rgba(52,211,153,0.12); margin-bottom: 1rem;
}
.ssd-hero-title { font-size: 1.75rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.8px; margin: 0 0 0.6rem; line-height: 1.15; }
.ssd-hero-sub { font-size: 0.92rem; color: #64748b; margin: 0 0 1.25rem; max-width: 520px; line-height: 1.6; }
.ssd-hero-cta {
  display: inline-flex; align-items: center; padding: 0.7rem 1.5rem; border: none; border-radius: 12px;
  font-size: 0.9rem; font-weight: 700; font-family: inherit; cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff;
  box-shadow: 0 4px 20px rgba(99,102,241,0.35); transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
}
.ssd-hero-cta:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(99,102,241,0.45); }
.ssd-hero-right { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; flex-shrink: 0; }
.ssd-stat-card {
  background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px;
  padding: 1rem 1.1rem; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  display: flex; align-items: center; gap: 0.85rem; min-width: 125px;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.ssd-stat-card:hover { border-color: rgba(129,140,248,0.15); box-shadow: 0 8px 30px rgba(0,0,0,0.2); transform: translateY(-2px); }
.ssd-stat-icon { width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.ssd-stat-body { display: flex; flex-direction: column; }
.ssd-stat-value { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.5px; line-height: 1.2; }
.ssd-stat-label { font-size: 0.68rem; color: #64748b; font-weight: 500; white-space: nowrap; }

/* ── Toolbar ── */
.ssd-toolbar {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  margin-bottom: 1.75rem; padding: 0.75rem 1rem;
  background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px;
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); flex-wrap: wrap;
}
.ssd-toolbar-left { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; flex-wrap: wrap; }
.ssd-search-wrap { position: relative; min-width: 180px; flex: 1; max-width: 260px; }
.ssd-search-icon { position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%); color: #475569; font-size: 0.85rem; pointer-events: none; }
.ssd-search-input {
  width: 100%; padding: 0.55rem 0.85rem 0.55rem 2.3rem; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; color: #e2e8f0;
  font-size: 0.85rem; font-family: inherit; outline: none; transition: all 0.25s ease;
}
.ssd-search-input:focus { border-color: rgba(129,140,248,0.3); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); background: rgba(255,255,255,0.06); }
.ssd-search-input::placeholder { color: rgba(255,255,255,0.5); }
.ssd-search-clear { position: absolute; right: 0.65rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: #475569; font-size: 0.6rem; cursor: pointer; padding: 0.2rem; border-radius: 4px; transition: color 0.2s; }
.ssd-search-clear:hover { color: #94a3b8; }
.ssd-filter-group { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.ssd-select-wrap { position: relative; }
.ssd-select-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: #475569; font-size: 0.75rem; pointer-events: none; }
.ssd-select {
  padding: 0.5rem 2rem 0.5rem 2rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px; color: #94a3b8; font-size: 0.8rem; font-family: inherit; outline: none;
  cursor: pointer; appearance: none; -webkit-appearance: none; transition: all 0.25s ease; min-width: 115px;
}
.ssd-select:focus { border-color: rgba(129,140,248,0.3); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); color: #e2e8f0; }
.ssd-select option { background: #0f172a; color: #e2e8f0; }
.ssd-toolbar-right { display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }
.ssd-result-count { font-size: 0.78rem; color: #64748b; font-weight: 500; white-space: nowrap; }
.ssd-btn-new {
  display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; border: none; border-radius: 10px;
  font-size: 0.82rem; font-weight: 700; font-family: inherit; cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff;
  box-shadow: 0 4px 16px rgba(99,102,241,0.25); transition: all 0.25s cubic-bezier(0.4,0,0.2,1); white-space: nowrap;
}
.ssd-btn-new:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(99,102,241,0.35); }
.ssd-btn-new:active { transform: translateY(0); }

/* ── Grid ── */
.ssd-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; animation: ssdFadeIn 0.3s ease; }

/* ── Card ── */
.ssd-card {
  background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px;
  padding: 1rem 1.1rem 0.85rem; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
  opacity: 0; transform: translateY(20px); animation: ssdCardUp 0.45s ease forwards;
  position: relative;
}
.ssd-card:hover { transform: translateY(-4px); border-color: rgba(129,140,248,0.2); box-shadow: 0 12px 36px rgba(129,140,248,0.08), 0 4px 16px rgba(0,0,0,0.15); }
.ssd-card-resolved { opacity: 0.7; }
.ssd-card-resolved:hover { opacity: 1; }
.ssd-card-unread { border-color: rgba(129,140,248,0.2); }
.ssd-card-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem; }
.ssd-card-badges-top { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.ssd-badge-cat {
  font-size: 0.58rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 999px;
  background: rgba(255,255,255,0.04); color: #64748b; border: 1px solid rgba(255,255,255,0.06);
}
.ssd-badge-priority { font-size: 0.55rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.2px; }
.ssd-badge-priority.high { background: rgba(244,63,94,0.12); color: #fb7185; border: 1px solid rgba(244,63,94,0.12); }
.ssd-badge-priority.medium { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.12); }
.ssd-badge-priority.low { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.12); }
.ssd-badge-status { font-size: 0.55rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.2px; }
.ssd-badge-status.open { background: rgba(129,140,248,0.12); color: #a5b4fc; border: 1px solid rgba(129,140,248,0.12); }
.ssd-badge-status.resolved { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.12); }
.ssd-unread-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #818cf8;
  box-shadow: 0 0 8px rgba(129,140,248,0.4); flex-shrink: 0; margin-top: 0.15rem;
}
.ssd-card-title { font-size: 0.9rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.3rem; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
.ssd-card-preview { font-size: 0.78rem; color: #64748b; margin: 0 0 0.6rem; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.ssd-card-meta { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 0.65rem; }
.ssd-card-meta span { font-size: 0.65rem; color: #475569; display: flex; align-items: center; gap: 0.25rem; }
.ssd-card-meta span i { font-size: 0.6rem; }
.ssd-card-actions { display: flex; gap: 0.3rem; padding-top: 0.6rem; border-top: 1px solid rgba(255,255,255,0.04); }
.ssd-action-btn {
  display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.3rem 0.6rem; border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px; font-size: 0.68rem; font-weight: 600; font-family: inherit; cursor: pointer;
  background: rgba(255,255,255,0.04); color: #64748b; transition: all 0.2s ease;
}
.ssd-action-btn:hover { background: rgba(255,255,255,0.08); color: #cbd5e1; }
.ssd-action-btn.subtle:hover { background: rgba(99,102,241,0.1); color: #a5b4fc; border-color: rgba(99,102,241,0.15); }
.ssd-action-btn.danger:hover { background: rgba(244,63,94,0.1); color: #fb7185; border-color: rgba(244,63,94,0.15); }

/* ── Empty ── */
.ssd-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; text-align: center; }
.ssd-empty-illustration { width: 160px; height: 160px; margin-bottom: 1.5rem; opacity: 0.45; }
.ssd-empty-illustration svg { width: 100%; height: 100%; }
.ssd-empty-title { font-size: 1.15rem; font-weight: 700; color: #94a3b8; margin: 0 0 0.5rem; }
.ssd-empty-text { font-size: 0.85rem; color: #64748b; margin: 0 0 1.5rem; max-width: 360px; line-height: 1.5; }
.ssd-empty-btn {
  display: inline-flex; align-items: center; padding: 0.7rem 1.6rem; border: none; border-radius: 12px;
  font-size: 0.9rem; font-weight: 700; font-family: inherit; cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff;
  box-shadow: 0 4px 20px rgba(99,102,241,0.3); transition: all 0.25s ease;
}
.ssd-empty-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(99,102,241,0.4); }

/* ── Modal ── */
.ssd-modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.65); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  z-index: 3000; display: flex; align-items: center; justify-content: center; padding: 1.5rem;
}
.ssd-modal {
  width: 600px; max-width: 100vw; max-height: 90vh;
  background: rgba(10,15,28,0.97); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.06); border-radius: 24px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden;
}
.ssd-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; padding: 1.5rem 2rem; border-bottom: 1px solid rgba(255,255,255,0.05); flex-shrink: 0; }
.ssd-modal-title { font-size: 1.25rem; font-weight: 800; color: #f1f5f9; margin: 0 0 0.25rem; letter-spacing: -0.4px; }
.ssd-modal-sub { font-size: 0.82rem; color: #64748b; margin: 0; }
.ssd-modal-close { width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #64748b; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.7rem; flex-shrink: 0; transition: all 0.2s ease; }
.ssd-modal-close:hover { background: rgba(244,63,94,0.12); color: #fb7185; border-color: rgba(244,63,94,0.2); }
.ssd-modal-body { padding: 1.5rem 2rem; overflow-y: auto; flex: 1; }
.ssd-modal-footer { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1rem 2rem; border-top: 1px solid rgba(255,255,255,0.05); flex-shrink: 0; background: rgba(10,15,28,0.5); }
.ssd-footer-hint { font-size: 0.72rem; color: rgba(255,255,255,0.4); }
.ssd-footer-actions { display: flex; align-items: center; gap: 0.5rem; }
.ssd-btn-ghost { padding: 0.5rem 1rem; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; font-size: 0.8rem; font-weight: 600; font-family: inherit; cursor: pointer; background: transparent; color: #64748b; transition: all 0.2s ease; }
.ssd-btn-ghost:hover { background: rgba(255,255,255,0.06); color: #94a3b8; }
.ssd-btn-primary { display: inline-flex; align-items: center; padding: 0.5rem 1.2rem; border: none; border-radius: 10px; font-size: 0.8rem; font-weight: 700; font-family: inherit; cursor: pointer; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; transition: all 0.25s cubic-bezier(0.4,0,0.2,1); }
.ssd-btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(99,102,241,0.35); }
.ssd-btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

/* ── Form ── */
.ssd-form-section { margin-bottom: 1rem; }
.ssd-form-section-title { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 1rem; }
.ssd-form-group { margin-bottom: 1rem; }
.ssd-form-label { display: block; font-size: 0.78rem; font-weight: 600; color: rgba(255,255,255,0.92); margin-bottom: 0.35rem; }
.required { color: #fb7185; }
.ssd-optional { color: rgba(255,255,255,0.4); font-weight: 400; }
.ssd-input-wrap { position: relative; }
.ssd-input-wrap.focus .ssd-form-input { border-color: rgba(129,140,248,0.35); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); background: rgba(255,255,255,0.06); }
.ssd-form-input {
  width: 100%; padding: 0.6rem 0.85rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px; color: rgba(255,255,255,0.95); font-size: 0.85rem; font-family: inherit; outline: none;
  transition: all 0.25s ease; box-sizing: border-box;
}
.ssd-form-input:focus { border-color: rgba(129,140,248,0.35); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); background: rgba(255,255,255,0.06); }
.ssd-form-input::placeholder { color: rgba(255,255,255,0.5); }
select.ssd-form-input { appearance: none; -webkit-appearance: none; padding-right: 2rem; cursor: pointer; }
select.ssd-form-input option { background: #0f172a; color: #e2e8f0; }
.ssd-form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.ssd-select-styled { position: relative; }
.ssd-select-arrow { position: absolute; right: 0.85rem; top: 50%; transform: translateY(-50%); color: #475569; font-size: 0.65rem; pointer-events: none; }
.ssd-form-textarea { width: 100%; padding: 0.6rem 0.85rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07); border-radius: 10px; color: rgba(255,255,255,0.95); font-size: 0.85rem; font-family: inherit; outline: none; transition: all 0.25s ease; resize: vertical; min-height: 80px; box-sizing: border-box; line-height: 1.6; }
.ssd-form-textarea:focus { border-color: rgba(129,140,248,0.35); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); background: rgba(255,255,255,0.06); }
.ssd-form-textarea::placeholder { color: rgba(255,255,255,0.5); }
.ssd-upload-zone {
  border: 1.5px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 1.25rem;
  text-align: center; cursor: pointer; transition: all 0.25s ease;
}
.ssd-upload-zone:hover { border-color: rgba(129,140,248,0.25); background: rgba(129,140,248,0.03); }
.ssd-upload-icon { font-size: 1.3rem; color: #475569; margin-bottom: 0.35rem; }
.ssd-upload-text { font-size: 0.8rem; color: #64748b; margin: 0; }
.ssd-upload-text span { color: #818cf8; font-weight: 600; }
.ssd-attach-preview { display: inline-flex; align-items: center; gap: 0.3rem; margin-top: 0.5rem; padding: 0.25rem 0.6rem; background: rgba(129,140,248,0.06); border-radius: 8px; font-size: 0.75rem; color: #a5b4fc; }
.ssd-attach-remove { background: none; border: none; color: #64748b; cursor: pointer; padding: 0; font-size: 0.7rem; }
.ssd-attach-remove:hover { color: #fb7185; }

/* ── Panel ── */
.ssd-panel-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); z-index: 2000; display: flex; justify-content: flex-end; }
.ssd-panel { width: 520px; max-width: 100vw; height: 100vh; background: rgba(10,15,28,0.97); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-left: 1px solid rgba(255,255,255,0.06); box-shadow: -8px 0 40px rgba(0,0,0,0.4); display: flex; flex-direction: column; overflow: hidden; }
.ssd-panel-close { position: absolute; top: 1rem; right: 1rem; z-index: 10; width: 34px; height: 34px; border-radius: 50%; background: rgba(15,23,42,0.7); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.75rem; transition: all 0.2s ease; }
.ssd-panel-close:hover { background: rgba(244,63,94,0.15); color: #fb7185; border-color: rgba(244,63,94,0.2); }
.ssd-panel-scroll { flex: 1; overflow-y: auto; padding: 1.5rem 1.5rem 6rem; }
.ssd-panel-scroll::-webkit-scrollbar { width: 4px; }
.ssd-panel-scroll::-webkit-scrollbar-track { background: transparent; }
.ssd-panel-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
.ssd-panel-section { padding-bottom: 1.25rem; margin-bottom: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); }
.ssd-panel-section-title { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 0.85rem; }
.ssd-panel-head { }
.ssd-panel-title { font-size: 1.15rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.6rem; letter-spacing: -0.3px; line-height: 1.35; }
.ssd-panel-badges { display: flex; gap: 0.35rem; flex-wrap: wrap; }

/* ── Timeline ── */
.ssd-timeline { display: flex; flex-direction: column; gap: 0.5rem; position: relative; padding-left: 1rem; }
.ssd-tl-item { display: flex; align-items: flex-start; gap: 0.75rem; position: relative; }
.ssd-tl-item::before { content: ''; position: absolute; left: 0.35rem; top: 1rem; bottom: -0.5rem; width: 1.5px; background: rgba(255,255,255,0.06); }
.ssd-tl-item:last-child::before { display: none; }
.ssd-tl-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 0.2rem; border: 2px solid rgba(255,255,255,0.06); background: transparent; transition: all 0.3s ease; }
.ssd-tl-dot.active { border-color: #818cf8; background: #818cf8; box-shadow: 0 0 8px rgba(129,140,248,0.3); }
.ssd-tl-dot.done { border-color: #34d399; background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,0.3); }
.ssd-tl-content { display: flex; flex-direction: column; }
.ssd-tl-label { font-size: 0.82rem; color: #cbd5e1; font-weight: 600; }
.ssd-tl-time { font-size: 0.68rem; color: #475569; }

/* ── Chat ── */
.ssd-chat { display: flex; flex-direction: column; gap: 1rem; }
.ssd-msg { display: flex; gap: 0.65rem; animation: ssdMsgIn 0.35s ease both; }
.ssd-msg.admin { flex-direction: row-reverse; }
.ssd-msg-avatar { flex-shrink: 0; }
.ssd-msg-avatar-inner { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.6rem; color: #fff; }
.ssd-msg-body { max-width: 78%; }
.ssd-msg.admin .ssd-msg-body { display: flex; flex-direction: column; align-items: flex-end; }
.ssd-msg-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.ssd-msg.admin .ssd-msg-header { flex-direction: row-reverse; }
.ssd-msg-author { font-size: 0.72rem; font-weight: 600; color: #94a3b8; }
.ssd-msg-time { font-size: 0.62rem; color: #475569; }
.ssd-msg-bubble { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 0.6rem 0.8rem; }
.ssd-msg.admin .ssd-msg-bubble { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.1); }
.ssd-msg-bubble p { font-size: 0.82rem; color: #cbd5e1; margin: 0; line-height: 1.6; }
.ssd-msg-attachments { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.35rem; }
.ssd-msg-attach {
  font-size: 0.7rem;
  color: #818cf8;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  background: rgba(129,140,248,0.06);
  border-radius: 6px;
  text-decoration: none;
}
@keyframes ssdMsgIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

/* ── Resolved Banner ── */
.ssd-resolved-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.85rem 1rem; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.15); border-radius: 12px; margin-top: 0.5rem; flex-wrap: wrap; }
.ssd-resolved-banner i { font-size: 1.2rem; color: #34d399; }
.ssd-resolved-banner div { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.ssd-resolved-banner strong { font-size: 0.85rem; color: #f1f5f9; }
.ssd-resolved-banner span { font-size: 0.75rem; color: #64748b; }
.ssd-btn-reopen { padding: 0.5rem 1rem; border: 1px solid rgba(129,140,248,0.2); border-radius: 10px; font-size: 0.78rem; font-weight: 600; font-family: inherit; cursor: pointer; background: rgba(129,140,248,0.08); color: #a5b4fc; transition: all 0.2s ease; white-space: nowrap; }
.ssd-btn-reopen:hover { background: rgba(129,140,248,0.15); border-color: rgba(129,140,248,0.3); }

/* ── Reply ── */
.ssd-reply-area { padding-top: 0.5rem; }
.ssd-reply-input { width: 100%; padding: 0.65rem 0.85rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07); border-radius: 12px; color: #e2e8f0; font-size: 0.85rem; font-family: inherit; outline: none; resize: none; min-height: 56px; line-height: 1.6; transition: all 0.25s ease; box-sizing: border-box; }
.ssd-reply-input:focus { border-color: rgba(129,140,248,0.35); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); background: rgba(255,255,255,0.06); }
.ssd-reply-input::placeholder { color: #475569; }
.ssd-reply-toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; }
.ssd-reply-tool { width: 32px; height: 32px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.04); color: #64748b; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.75rem; transition: all 0.2s ease; }
.ssd-reply-tool:hover { background: rgba(255,255,255,0.08); color: #94a3b8; }
.ssd-reply-send { width: 36px; height: 36px; border-radius: 10px; border: none; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.85rem; transition: all 0.2s ease; }
.ssd-reply-send:hover:not(:disabled) { transform: scale(1.05); box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
.ssd-reply-send:disabled { opacity: 0.3; cursor: not-allowed; }

/* ── Toast ── */
.ssd-toast { position: fixed; bottom: 2rem; right: 2rem; z-index: 5000; display: flex; align-items: center; gap: 0.75rem; padding: 0.85rem 1.25rem; background: rgba(15,23,42,0.95); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
.ssd-toast.success { border-color: rgba(52,211,153,0.2); }
.ssd-toast.info { border-color: rgba(129,140,248,0.2); }
.ssd-toast i { font-size: 1.2rem; }
.ssd-toast.success i { color: #34d399; }
.ssd-toast.info i { color: #818cf8; }
.ssd-toast-content { display: flex; flex-direction: column; }
.ssd-toast-content strong { font-size: 0.85rem; color: #f1f5f9; font-weight: 700; }
.ssd-toast-content span { font-size: 0.75rem; color: #64748b; }

/* ── Animations ── */
@keyframes ssdFadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes ssdCardUp { to { opacity: 1; transform: translateY(0); } }

/* ── Transitions ── */
.ssd-modal-enter-active, .ssd-modal-leave-active { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.ssd-modal-enter-from, .ssd-modal-leave-to { opacity: 0; }
.ssd-modal-enter-from .ssd-modal, .ssd-modal-leave-to .ssd-modal { transform: scale(0.95) translateY(10px); }
.ssd-modal-enter-active .ssd-modal, .ssd-modal-leave-active .ssd-modal { transition: transform 0.3s cubic-bezier(0.4,0,0.2,1); }

.ssd-panel-enter-active, .ssd-panel-leave-active { transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.ssd-panel-enter-from, .ssd-panel-leave-to { opacity: 0; }
.ssd-panel-enter-from .ssd-panel, .ssd-panel-leave-to .ssd-panel { transform: translateX(100%); }
.ssd-panel-enter-active .ssd-panel, .ssd-panel-leave-active .ssd-panel { transition: transform 0.35s cubic-bezier(0.4,0,0.2,1); }

.ssd-toast-enter-active, .ssd-toast-leave-active { transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.ssd-toast-enter-from, .ssd-toast-leave-to { opacity: 0; transform: translateY(16px); }

/* ── Responsive ── */
@media (max-width: 1200px) { .ssd-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 992px) {
  .ssd-hero-inner { flex-direction: column; }
  .ssd-hero-right { width: 100%; }
  .ssd-grid { grid-template-columns: repeat(2, 1fr); }
  .ssd-panel { width: 100%; }
}
@media (max-width: 768px) {
  .ssd-grid { grid-template-columns: 1fr; }
  .ssd-toolbar-left { flex-direction: column; align-items: stretch; }
  .ssd-search-wrap { max-width: none; }
  .ssd-filter-group { flex-direction: column; }
  .ssd-select { width: 100%; }
}

.ssd-attach-overlay {
  position: fixed; inset: 0; z-index: 10000; display: flex; align-items: center;
  justify-content: center; background: rgba(3, 6, 20, 0.85);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  padding: 2rem; animation: ssdFadeIn 0.2s ease;
}
.ssd-attach-modal {
  background: #111827; border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px; width: 100%; max-width: 720px; max-height: 90vh;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 25px 60px rgba(0,0,0,0.6);
}
.ssd-attach-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.06);
}
.ssd-attach-header h3 { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.ssd-attach-header span { font-size: 0.75rem; color: #64748b; }
.ssd-attach-close {
  background: rgba(255,255,255,0.04); border: none; color: #64748b; width: 32px; height: 32px;
  border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.2s; flex-shrink: 0;
}
.ssd-attach-close:hover { background: rgba(255,255,255,0.1); color: #f1f5f9; }
.ssd-attach-body {
  flex: 1; overflow: auto; display: flex; align-items: center; justify-content: center;
  padding: 1.5rem; min-height: 300px;
}
.ssd-attach-image { max-width: 100%; max-height: 70vh; border-radius: 8px; object-fit: contain; }
.ssd-attach-frame { width: 100%; height: 70vh; border: none; border-radius: 8px; }
.ssd-attach-fallback {
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem; color: #64748b; text-align: center;
}
.ssd-attach-fallback i { font-size: 2.5rem; }
.ssd-attach-fallback strong { font-size: 0.9rem; color: #f1f5f9; }
.ssd-attach-fallback span { font-size: 0.8rem; }
.ssd-attach-body::-webkit-scrollbar { width: 4px; }
.ssd-attach-body::-webkit-scrollbar-track { background: transparent; }
.ssd-attach-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }
.ssd-msg-attach {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.2rem 0.55rem; border-radius: 6px; font-size: 0.7rem; font-weight: 600;
  background: rgba(129,140,248,0.08); color: #818cf8; border: 1px solid rgba(129,140,248,0.12);
  cursor: pointer; font-family: inherit; transition: background 0.2s;
}
.ssd-msg-attach:hover { background: rgba(129,140,248,0.15); }
</style>
