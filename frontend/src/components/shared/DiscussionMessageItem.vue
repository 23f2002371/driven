<template>
  <div class="chat-msg-row" :class="{ 'chat-msg-nested': depth > 0, 'chat-msg-deleted': isDeleted, 'chat-msg-mine': isMyMessage }">
    <div class="chat-msg-inner">
      <!-- Avatar -->
      <div class="chat-avatar" :class="avatarClass">
        {{ getInitials(message.author_name) }}
      </div>

      <!-- Content Area -->
      <!-- Content Area -->
      <div class="chat-msg-content">
        <!-- Author + Meta Line -->
        <div class="chat-meta-line">
          <i v-if="parentMessage || depth > 0" class="bi bi-arrow-return-right text-primary me-1" title="Reply"></i>
          <span class="chat-author-name">{{ message.author_name || 'Participant' }}</span>

          <span v-if="isClubAdmin" class="chat-badge badge-admin">
            <i class="bi bi-shield-check me-1"></i>Club Admin
          </span>

          <span class="chat-time" :title="formatFullDate(message.created_at)">
            {{ formatRelativeTime(message.created_at) }}
            <span v-if="isEdited && !isDeleted" class="chat-edited-tag">(edited)</span>
          </span>

          <!-- Quick Action Buttons (Show on hover) -->
          <div v-if="!isDeleted" class="chat-hover-actions">
            <button class="chat-action-btn" title="Reply" @click="$emit('start-reply', message)">
              <i class="bi bi-reply-fill"></i>
            </button>
            <button v-if="canEdit" class="chat-action-btn" title="Edit" @click="$emit('start-edit', message)">
              <i class="bi bi-pencil-fill"></i>
            </button>
            <button v-if="canDelete" class="chat-action-btn chat-action-delete" title="Delete" @click="$emit('confirm-delete', message)">
              <i class="bi bi-trash3-fill"></i>
            </button>
          </div>
        </div>

        <!-- Edit Form -->
        <div v-if="editingMessageId === message.id" class="chat-edit-wrap">
          <textarea
            :value="editText"
            class="chat-edit-input"
            rows="2"
            placeholder="Edit your message..."
            @input="$emit('update:editText', $event.target.value)"
            @keydown.enter.prevent="onEditEnterPress"
          ></textarea>
          <div class="chat-edit-btns">
            <button class="chat-btn-xs chat-btn-cancel" :disabled="isEditing" @click="$emit('cancel-edit')">Cancel</button>
            <button
              class="chat-btn-xs chat-btn-save"
              :disabled="isEditing || !editText.trim() || editText.trim() === message.message"
              @click="$emit('submit-edit', { messageId: message.id, text: editText })"
            >
              Save
            </button>
          </div>
        </div>

        <!-- Message Bubble / Text -->
        <div v-else class="chat-bubble" :class="{ 'bubble-deleted': isDeleted, 'bubble-mine': isMyMessage }">
          <template v-if="isDeleted">
            <i class="bi bi-slash-circle me-1"></i>
            <em>This message has been deleted.</em>
          </template>
          <template v-else>
            {{ message.message }}
          </template>
        </div>
      </div>
    </div>

    <!-- Recursive Nested Replies Tree -->
    <div v-if="message.replies && message.replies.length > 0" class="chat-nested-replies">
      <DiscussionMessageItem
        v-for="reply in message.replies"
        :key="reply.id"
        :message="reply"
        :parent-message="message"
        :depth="depth + 1"
        :current-user-id="currentUserId"
        :current-user-name="currentUserName"
        :is-admin="isAdmin"
        :replying-to-id="replyingToId"
        :reply-text="replyText"
        :is-posting-reply="isPostingReply"
        :editing-message-id="editingMessageId"
        :edit-text="editText"
        :is-editing="isEditing"
        @start-reply="$emit('start-reply', $event)"
        @cancel-reply="$emit('cancel-reply')"
        @submit-reply="$emit('submit-reply', $event)"
        @start-edit="$emit('start-edit', $event)"
        @cancel-edit="$emit('cancel-edit')"
        @submit-edit="$emit('submit-edit', $event)"
        @confirm-delete="$emit('confirm-delete', $event)"
        @update:reply-text="$emit('update:replyText', $event)"
        @update:edit-text="$emit('update:editText', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  message: { type: Object, required: true },
  parentMessage: { type: Object, default: null },
  depth: { type: Number, default: 0 },
  currentUserId: { type: [String, Number], default: null },
  currentUserName: { type: String, default: '' },
  isAdmin: { type: Boolean, default: false },
  replyingToId: { type: [String, Number], default: null },
  replyText: { type: String, default: '' },
  isPostingReply: { type: Boolean, default: false },
  editingMessageId: { type: [String, Number], default: null },
  editText: { type: String, default: '' },
  isEditing: { type: Boolean, default: false },
});

const emit = defineEmits([
  'start-reply',
  'cancel-reply',
  'submit-reply',
  'start-edit',
  'cancel-edit',
  'submit-edit',
  'confirm-delete',
  'update:replyText',
  'update:editText',
]);

const isDeleted = computed(() => {
  return props.message.message === '[deleted]' || props.message.is_deleted === true;
});

const isClubAdmin = computed(() => {
  const role = (props.message.author_role || '').toLowerCase();
  return role === 'club_admin' || role === 'admin' || role === 'club admin';
});

const isMyMessage = computed(() => {
  if (props.message.user_id && props.currentUserId) {
    return String(props.currentUserId) === String(props.message.user_id);
  }
  if (props.isAdmin !== isClubAdmin.value) {
    return false;
  }
  if (props.currentUserName && props.message.author_name) {
    return props.currentUserName.trim().toLowerCase() === props.message.author_name.trim().toLowerCase();
  }
  return false;
});

const isEdited = computed(() => {
  if (!props.message.created_at || !props.message.updated_at) return false;
  return new Date(props.message.updated_at).getTime() - new Date(props.message.created_at).getTime() > 2000;
});

const canEdit = computed(() => {
  return isMyMessage.value && !isDeleted.value;
});

const canDelete = computed(() => {
  return (isMyMessage.value || props.isAdmin) && !isDeleted.value;
});

const avatarClass = computed(() => {
  if (isClubAdmin.value) return 'avatar-admin';
  return 'avatar-default';
});

const getInitials = (name) => {
  if (!name) return 'U';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
};

const onEditEnterPress = (e) => {
  if (e.shiftKey) return;
  if (props.editText.trim() && props.editText.trim() !== props.message.message) {
    emit('submit-edit', { messageId: props.message.id, text: props.editText });
  }
};

const formatRelativeTime = (d) => {
  if (!d) return 'Just now';
  const date = new Date(d);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);
  if (diffSec < 45) return 'just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHrs = Math.floor(diffMin / 60);
  if (diffHrs < 24) return `${diffHrs}h ago`;
  const diffDays = Math.floor(diffHrs / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const formatFullDate = (d) => {
  if (!d) return '';
  return new Date(d).toLocaleString();
};
</script>

<style scoped>
.chat-msg-row {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.chat-msg-inner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  position: relative;
  padding: 0.4rem 0.6rem;
  border-radius: 12px;
  transition: background 0.15s ease;
}
.chat-msg-inner:hover {
  background: rgba(255, 255, 255, 0.03);
}

.chat-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
  color: #ffffff;
  flex-shrink: 0;
  margin-top: 2px;
}
.avatar-admin {
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  box-shadow: 0 0 10px rgba(168, 85, 247, 0.4);
}
.avatar-default {
  background: linear-gradient(135deg, #475569 0%, #334155 100%);
}

.chat-msg-content {
  flex: 1;
  min-width: 0;
}


.chat-meta-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
  flex-wrap: wrap;
}

.chat-author-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #f1f5f9;
}

.chat-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.badge-admin {
  background: rgba(168, 85, 247, 0.2);
  color: #d8b4fe;
  border: 1px solid rgba(168, 85, 247, 0.35);
}

.chat-time {
  font-size: 0.72rem;
  color: #64748b;
  margin-left: auto;
}

.chat-edited-tag {
  font-size: 0.68rem;
  color: #64748b;
  font-style: italic;
  margin-left: 2px;
}

/* Hover Action Bar */
.chat-hover-actions {
  display: none;
  align-items: center;
  gap: 0.25rem;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 2px 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.chat-msg-inner:hover .chat-hover-actions {
  display: flex;
}

.chat-action-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
}
.chat-action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}
.chat-action-delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Message Bubble */
.chat-bubble {
  color: #e2e8f0;
  font-size: 0.9rem;
  line-height: 1.45;
  word-break: break-word;
  white-space: pre-wrap;
}
.bubble-deleted {
  color: #64748b;
  font-style: italic;
}

/* Edit Mode */
.chat-edit-wrap {
  margin-top: 0.25rem;
}
.chat-edit-input {
  width: 100%;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid #818cf8;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
  resize: vertical;
}
.chat-edit-btns {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.35rem;
}
.chat-btn-xs {
  border-radius: 6px;
  padding: 0.25rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
}
.chat-btn-cancel {
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
}
.chat-btn-save {
  background: #6366f1;
  color: #ffffff;
}

/* Threaded Replies Tree */
.chat-nested-replies {
  margin-left: 1.75rem;
  padding-left: 0.85rem;
  border-left: 2px solid rgba(129, 140, 248, 0.3);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.25rem;
}
</style>
