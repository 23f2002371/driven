<template>
  <div class="chat-window">
    <!-- Toast Notification -->
    <Transition name="chat-toast">
      <div v-if="toastMessage" class="chat-toast" :class="{ 'chat-toast-error': isToastError }">
        <i class="bi me-2" :class="isToastError ? 'bi-exclamation-octagon-fill' : 'bi-check-circle-fill'"></i>
        {{ toastMessage }}
      </div>
    </Transition>

    <!-- Loading State -->
    <div v-if="isLoading" class="chat-center-state">
      <div class="spinner-border text-primary mb-3" role="status"></div>
      <span class="text-secondary small">Loading conversation...</span>
    </div>

    <!-- No Thread State -->
    <div v-else-if="noThread" class="chat-center-state">
      <div class="chat-state-icon">
        <i class="bi bi-chat-square-dots"></i>
      </div>
      <h5 class="text-light fw-bold mb-1">
        {{ isAdmin ? 'Discussion Not Created Yet' : 'Discussion Not Opened' }}
      </h5>
      <p class="text-secondary small mb-3" style="max-width: 320px;">
        {{
          isAdmin
            ? 'Create the discussion thread so attendees and members can collaborate and ask questions.'
            : 'The club admin has not opened a discussion thread for this event yet.'
        }}
      </p>
      <button
        v-if="isAdmin"
        class="chat-btn-primary"
        :disabled="isCreatingThread"
        @click="handleCreateThread"
      >
        <span v-if="isCreatingThread" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-plus-circle-fill me-2"></i>
        {{ isCreatingThread ? 'Creating...' : 'Create Discussion' }}
      </button>
    </div>

    <!-- Active Chat Window -->
    <template v-else>
      <!-- Chat Sub-Header Info Bar -->
      <div class="chat-sub-header">
        <div class="d-flex align-items-center gap-2">
          <span class="chat-host-tag">
            <i class="bi bi-person-badge-fill me-1"></i>Host: {{ thread?.creator_name || 'Club Lead' }}
          </span>
          <span class="chat-count-tag">
            <i class="bi bi-chat-dots-fill me-1"></i>{{ totalMessagesCount }} {{ totalMessagesCount === 1 ? 'message' : 'messages' }}
          </span>
        </div>
        <button class="chat-btn-refresh-sm" :disabled="isLoading" @click="refreshMessages" title="Refresh messages">
          <i class="bi bi-arrow-clockwise" :class="{ 'spin-anim': isLoading }"></i>
        </button>
      </div>

      <!-- Scrollable Chat Messages Feed -->
      <div ref="chatFeedRef" class="chat-feed">
        <!-- Empty Messages Placeholder -->
        <div v-if="messages.length === 0" class="chat-feed-empty">
          <div class="chat-feed-empty-icon">
            <i class="bi bi-chat-dots"></i>
          </div>
          <h6 class="text-light fw-bold mb-1">No messages yet</h6>
          <p class="text-secondary small m-0">Start the conversation! Be the first to ask a question or share a thought.</p>
        </div>

        <!-- Messages List -->
        <div v-else class="chat-messages-wrap">
          <DiscussionMessageItem
            v-for="msg in messages"
            :key="msg.id"
            :message="msg"
            :depth="0"
            :current-user-id="currentUserId"
            :current-user-name="currentUserName"
            :is-admin="isAdmin"
            :replying-to-id="replyingToId"
            :reply-text="replyText"
            :is-posting-reply="isPostingReply"
            :editing-message-id="editingMessageId"
            :edit-text="editText"
            :is-editing="isEditing"
            @start-reply="startReply"
            @cancel-reply="cancelReply"
            @submit-reply="handlePostReply"
            @start-edit="startEdit"
            @cancel-edit="cancelEdit"
            @submit-edit="handleSaveEdit"
            @confirm-delete="openDeleteModal"
            @update:reply-text="replyText = $event"
            @update:edit-text="editText = $event"
          />
        </div>
      </div>

      <!-- Bottom Chat Composer Bar -->
      <div class="chat-composer-area">
        <!-- Replying-To Banner -->
        <div v-if="replyingToMessage" class="chat-reply-banner">
          <div class="d-flex align-items-center gap-2 text-truncate">
            <i class="bi bi-reply-fill text-primary"></i>
            <span class="small text-secondary">
              Replying to <strong class="text-light">@{{ replyingToMessage.author_name }}</strong>:
              <span class="chat-reply-preview">"{{ replyingToMessage.message }}"</span>
            </span>
          </div>
          <button class="chat-reply-cancel-btn" @click="cancelReply" title="Cancel reply">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Input Box Row -->
        <div class="chat-input-row">
          <textarea
            ref="chatInputRef"
            v-model="composerText"
            class="chat-input-field"
            :placeholder="replyingToMessage ? `Reply to @${replyingToMessage.author_name}...` : 'Type a message... (Press Enter to send)'"
            rows="1"
            @keydown.enter="onComposerEnter"
            @input="adjustTextareaHeight"
          ></textarea>

          <button
            class="chat-send-btn"
            :disabled="isSending || !composerText.trim()"
            @click="submitComposer"
            title="Send Message"
          >
            <span v-if="isSending" class="spinner-border spinner-border-sm"></span>
            <i v-else class="bi bi-send-fill"></i>
          </button>
        </div>
      </div>
    </template>

    <!-- Delete Message Confirmation Modal -->
    <Teleport to="body">
      <div v-if="showDeleteModal && messageToDelete" class="chat-modal-backdrop" @click.self="closeDeleteModal">
        <div class="chat-modal-box">
          <div class="chat-modal-icon-wrap">
            <i class="bi bi-trash3-fill"></i>
          </div>
          <h5 class="text-light fw-bold mb-2">Delete Message?</h5>
          <p class="text-secondary small mb-4">
            Are you sure you want to delete this message? Any replies to this message will remain in the thread.
          </p>
          <div class="d-flex gap-2">
            <button class="chat-btn-modal-cancel flex-fill" :disabled="isDeleting" @click="closeDeleteModal">
              Cancel
            </button>
            <button class="chat-btn-modal-delete flex-fill" :disabled="isDeleting" @click="executeDeleteMessage">
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-1"></span>
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted } from 'vue';
import { store } from '../../store/mockData';
import {
  getDiscussionThreadApi,
  createDiscussionThreadApi,
  getDiscussionMessagesApi,
  createDiscussionMessageApi,
  updateDiscussionMessageApi,
  deleteDiscussionMessageApi,
} from '../../api/discussion';
import DiscussionMessageItem from './DiscussionMessageItem.vue';

const props = defineProps({
  eventId: { type: String, required: true },
  eventName: { type: String, default: 'Event' },
  isAdmin: { type: Boolean, default: false },
});

const thread = ref(null);
const messages = ref([]);
const noThread = ref(false);
const isLoading = ref(true);
const isCreatingThread = ref(false);
const isSending = ref(false);

const composerText = ref('');
const replyingToId = ref(null);
const replyingToMessage = ref(null);
const replyText = ref('');
const isPostingReply = ref(false);

const editingMessageId = ref(null);
const editText = ref('');
const isEditing = ref(false);

const showDeleteModal = ref(false);
const messageToDelete = ref(null);
const isDeleting = ref(false);

const toastMessage = ref('');
const isToastError = ref(false);

const chatFeedRef = ref(null);
const chatInputRef = ref(null);

const currentUserName = computed(() => {
  return store.currentUser?.full_name || store.studentProfile?.fullName || 'Participant';
});

const currentUserId = computed(() => {
  return store.currentUser?.id || null;
});

const countAllMessages = (msgList) => {
  let count = 0;
  for (const m of msgList) {
    count += 1;
    if (m.replies && m.replies.length > 0) {
      count += countAllMessages(m.replies);
    }
  }
  return count;
};

const totalMessagesCount = computed(() => countAllMessages(messages.value));

const showToast = (msg, isError = false) => {
  toastMessage.value = msg;
  isToastError.value = isError;
  setTimeout(() => { toastMessage.value = ''; }, 3500);
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatFeedRef.value) {
      chatFeedRef.value.scrollTop = chatFeedRef.value.scrollHeight;
    }
  });
};

const adjustTextareaHeight = (e) => {
  const el = e?.target || chatInputRef.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
};

/* ── Lifecycle & Data Loading ── */
const loadDiscussion = async () => {
  if (!props.eventId) return;
  isLoading.value = true;
  const token = store.token || localStorage.getItem('driven_token');

  try {
    const threadData = await getDiscussionThreadApi(props.eventId, token);
    if (!threadData) {
      noThread.value = true;
      thread.value = null;
      messages.value = [];
    } else {
      thread.value = threadData;
      noThread.value = false;
      await fetchMessages(threadData.id, token);
      scrollToBottom();
    }
  } catch (err) {
    if (err.message && err.message.includes('404')) {
      noThread.value = true;
      thread.value = null;
    } else {
      showToast(err.message || 'Failed to load discussion.', true);
    }
  } finally {
    isLoading.value = false;
  }
};

const fetchMessages = async (threadId, token = null) => {
  const authToken = token || store.token || localStorage.getItem('driven_token');
  try {
    const msgs = await getDiscussionMessagesApi(threadId, authToken);
    messages.value = Array.isArray(msgs) ? msgs : [];
  } catch (err) {
    console.error('Failed to fetch messages:', err);
  }
};

const refreshMessages = async () => {
  if (!thread.value) return;
  await fetchMessages(thread.value.id);
  showToast('Messages refreshed');
};

const handleCreateThread = async () => {
  const token = store.token || localStorage.getItem('driven_token');
  isCreatingThread.value = true;
  try {
    const defaultTitle = `${props.eventName} Discussion`;
    const res = await createDiscussionThreadApi(props.eventId, defaultTitle, token);
    thread.value = res;
    noThread.value = false;
    messages.value = [];
    showToast('Discussion thread created successfully!');
  } catch (err) {
    showToast(err.message || 'Failed to create discussion thread.', true);
  } finally {
    isCreatingThread.value = false;
  }
};

/* ── Composer Submit (Top Level or Inline Reply) ── */
const onComposerEnter = (e) => {
  if (e.shiftKey) return;
  e.preventDefault();
  submitComposer();
};

const submitComposer = async () => {
  const text = composerText.value.trim();
  if (!text || isSending.value || !thread.value) return;

  const token = store.token || localStorage.getItem('driven_token');
  isSending.value = true;

  try {
    const parentId = replyingToId.value || null;
    await createDiscussionMessageApi(thread.value.id, { message: text, parent_message_id: parentId }, token);
    composerText.value = '';
    cancelReply();
    if (chatInputRef.value) {
      chatInputRef.value.style.height = 'auto';
    }
    await fetchMessages(thread.value.id, token);
    scrollToBottom();
  } catch (err) {
    showToast(err.message || 'Failed to post message.', true);
  } finally {
    isSending.value = false;
  }
};

/* ── Reply Handlers ── */
const startReply = (msg) => {
  replyingToId.value = msg.id;
  replyingToMessage.value = msg;
  nextTick(() => {
    if (chatInputRef.value) {
      chatInputRef.value.focus();
    }
  });
};

const cancelReply = () => {
  replyingToId.value = null;
  replyingToMessage.value = null;
  replyText.value = '';
};

const handlePostReply = async ({ parentId, text }) => {
  if (!thread.value || !text.trim()) return;
  const token = store.token || localStorage.getItem('driven_token');
  isPostingReply.value = true;

  try {
    await createDiscussionMessageApi(thread.value.id, { message: text.trim(), parent_message_id: parentId }, token);
    cancelReply();
    await fetchMessages(thread.value.id, token);
    scrollToBottom();
  } catch (err) {
    showToast(err.message || 'Failed to post reply.', true);
  } finally {
    isPostingReply.value = false;
  }
};

/* ── Edit Handlers ── */
const startEdit = (msg) => {
  editingMessageId.value = msg.id;
  editText.value = msg.message;
};

const cancelEdit = () => {
  editingMessageId.value = null;
  editText.value = '';
};

const handleSaveEdit = async ({ messageId, text }) => {
  if (!text.trim()) return;
  const token = store.token || localStorage.getItem('driven_token');
  isEditing.value = true;

  try {
    await updateDiscussionMessageApi(messageId, { message: text.trim() }, token);
    cancelEdit();
    await fetchMessages(thread.value.id, token);
    showToast('Message updated');
  } catch (err) {
    showToast(err.message || 'Failed to update message.', true);
  } finally {
    isEditing.value = false;
  }
};

/* ── Delete Handlers ── */
const openDeleteModal = (msg) => {
  messageToDelete.value = msg;
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
  messageToDelete.value = null;
};

const executeDeleteMessage = async () => {
  if (!messageToDelete.value || !thread.value) return;
  const token = store.token || localStorage.getItem('driven_token');
  isDeleting.value = true;

  try {
    await deleteDiscussionMessageApi(messageToDelete.value.id, token);
    closeDeleteModal();
    await fetchMessages(thread.value.id, token);
    showToast('Message deleted');
  } catch (err) {
    showToast(err.message || 'Failed to delete message.', true);
  } finally {
    isDeleting.value = false;
  }
};

watch(() => props.eventId, () => {
  loadDiscussion();
});

onMounted(() => {
  loadDiscussion();
});
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #090f1d;
  position: relative;
  overflow: hidden;
}

/* Toast */
.chat-toast {
  position: absolute;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  background: rgba(34, 197, 94, 0.9);
  backdrop-filter: blur(8px);
  color: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}
.chat-toast-error {
  background: rgba(239, 68, 68, 0.9);
}

/* Center States */
.chat-center-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
}

.chat-state-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: #818cf8;
  margin-bottom: 1rem;
}

.chat-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 10px;
  padding: 0.65rem 1.4rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
  transition: all 0.2s;
}
.chat-btn-primary:hover {
  filter: brightness(1.1);
}

/* Sub-Header */
.chat-sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem 1.25rem;
  background: rgba(15, 23, 42, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.chat-host-tag {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
}

.chat-count-tag {
  font-size: 0.75rem;
  color: #64748b;
}

.chat-btn-refresh-sm {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: color 0.2s;
}
.chat-btn-refresh-sm:hover {
  color: #ffffff;
}

/* Messages Feed */
.chat-feed {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 1.25rem 0.5rem;
  display: flex;
  flex-direction: column;
}

.chat-feed-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #64748b;
  padding: 3rem 1rem;
}

.chat-feed-empty-icon {
  font-size: 2.2rem;
  color: #475569;
  margin-bottom: 0.75rem;
}

.chat-messages-wrap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Composer Area */
.chat-composer-area {
  padding: 0.85rem 1.25rem 1.25rem;
  background: rgba(15, 23, 42, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.chat-reply-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  margin-bottom: 0.6rem;
}

.chat-reply-preview {
  font-style: italic;
  opacity: 0.8;
  max-width: 250px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

.chat-reply-cancel-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  padding: 2px;
}
.chat-reply-cancel-btn:hover {
  color: #ffffff;
}

.chat-input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.65rem;
  background: rgba(2, 6, 23, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.4rem 0.6rem 0.4rem 0.85rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.chat-input-row:focus-within {
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.chat-input-field {
  flex: 1;
  background: transparent;
  border: none;
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
  resize: none;
  max-height: 120px;
  line-height: 1.4;
  padding: 0.35rem 0;
}
.chat-input-field::placeholder {
  color: #64748b;
}

.chat-send-btn {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 8px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.chat-send-btn:hover {
  filter: brightness(1.15);
  transform: scale(1.05);
}
.chat-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* Modals */
.chat-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.chat-modal-box {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  max-width: 380px;
  width: 100%;
  padding: 1.75rem;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
}

.chat-modal-icon-wrap {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  color: #ef4444;
  margin: 0 auto 1rem;
}

.chat-btn-modal-cancel {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.55rem;
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}
.chat-btn-modal-delete {
  background: #dc2626;
  border: none;
  border-radius: 8px;
  padding: 0.55rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
}

.spin-anim {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  100% { transform: rotate(360deg); }
}

.chat-toast-enter-active,
.chat-toast-leave-active {
  transition: all 0.25s ease;
}
.chat-toast-enter-from,
.chat-toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
