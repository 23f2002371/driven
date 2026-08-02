<template>
  <Teleport to="body">
    <Transition name="copilot-fade">
      <div v-if="open" class="copilot-backdrop" @click="$emit('close')"></div>
    </Transition>
    <Transition name="copilot-slide">
      <div v-if="open" class="copilot-panel-wrapper" @click.stop>
        <div class="copilot-panel">
          <div class="copilot-header">
            <div class="copilot-header-left">
              <div class="copilot-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
              <div>
                <h3 class="copilot-title">DRIVEN Copilot</h3>
                <div class="copilot-status">
                  <span class="copilot-status-dot"></span>
                  <span>AI Online</span>
                </div>
              </div>
            </div>
            <button class="copilot-close-btn" @click="$emit('close')">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="copilot-body">
            <div class="copilot-chat" ref="chatRef">
              <div v-for="msg in messages" :key="msg.id" class="copilot-msg" :class="msg.role">
                <div class="copilot-msg-avatar" v-if="msg.role === 'assistant'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <div class="copilot-msg-bubble">
                  <p>{{ msg.text }}</p>
                  <div v-if="msg.actions" class="copilot-msg-actions">
                    <button
                      v-for="(action, ai) in msg.actions"
                      :key="ai"
                      class="copilot-action-btn"
                      :class="action.variant"
                    >
                      {{ action.label }}
                    </button>
                  </div>
                  <span class="copilot-msg-time">{{ msg.timestamp }}</span>
                </div>
              </div>
            </div>

            <div class="copilot-suggestions">
              <span class="copilot-suggestions-label">Suggestions</span>
              <div class="copilot-suggestions-grid">
                <button
                  v-for="(prompt, pi) in suggestedPrompts"
                  :key="pi"
                  class="copilot-suggestion-chip"
                  @click="sendPrompt(prompt)"
                >
                  <i class="bi bi-plus-lg"></i>
                  {{ prompt }}
                </button>
              </div>
            </div>

            <div class="copilot-action-cards">
              <span class="copilot-action-label">Quick Actions</span>
              <div class="copilot-action-grid">
                <button class="copilot-action-card">
                  <div class="copilot-action-card-icon" style="background: rgba(52,211,153,0.12); color: #34d399;">
                    <i class="bi bi-box-seam"></i>
                  </div>
                  <div class="copilot-action-card-text">
                    <strong>Analyze Inventory</strong>
                    <span>Check stock levels</span>
                  </div>
                </button>
                <button class="copilot-action-card">
                  <div class="copilot-action-card-icon" style="background: rgba(129,140,248,0.12); color: #818cf8;">
                    <i class="bi bi-calendar-event"></i>
                  </div>
                  <div class="copilot-action-card-text">
                    <strong>Optimize Schedule</strong>
                    <span>Suggest event slots</span>
                  </div>
                </button>
                <button class="copilot-action-card">
                  <div class="copilot-action-card-icon" style="background: rgba(251,191,36,0.12); color: #fbbf24;">
                    <i class="bi bi-graph-up-arrow"></i>
                  </div>
                  <div class="copilot-action-card-text">
                    <strong>Generate Report</strong>
                    <span>Monthly summary</span>
                  </div>
                </button>
                <button class="copilot-action-card">
                  <div class="copilot-action-card-icon" style="background: rgba(251,113,133,0.12); color: #fb7185;">
                    <i class="bi bi-ticket-perforated"></i>
                  </div>
                  <div class="copilot-action-card-text">
                    <strong>Auto-Reply</strong>
                    <span>Draft ticket response</span>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <div class="copilot-footer">
            <div class="copilot-input-wrap">
              <input
                v-model="inputText"
                type="text"
                class="copilot-input"
                placeholder="Ask Copilot anything..."
                @keydown.enter="sendPrompt(inputText)"
              />
              <button class="copilot-send-btn" :disabled="!inputText.trim()" @click="sendPrompt(inputText)">
                <i class="bi bi-arrow-up-short"></i>
              </button>
            </div>
            <span class="copilot-footer-note">Responses are simulated for preview</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { suggestedPrompts, demoMessages } from '../../store/copilotData';

const props = defineProps({ open: Boolean });
const emit = defineEmits(['close']);

const inputText = ref('');
const messages = ref([...demoMessages]);
const chatRef = ref(null);

const sendPrompt = (text) => {
  const prompt = (text || inputText.value).trim();
  if (!prompt) return;
  messages.value.push({
    id: Date.now(),
    role: 'user',
    text: prompt,
    timestamp: 'Just now',
  });
  inputText.value = '';
  setTimeout(() => {
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      text: 'Thanks for your question! I\'m currently in demo mode. In production, I\'ll connect to AI to provide intelligent responses.',
      timestamp: 'Just now',
    });
    scrollToBottom();
  }, 800);
  scrollToBottom();
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight;
  }
};

watch(() => props.open, (val) => {
  if (val) setTimeout(scrollToBottom, 100);
});
</script>

<style scoped>
.copilot-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9998;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.copilot-slide-enter-active { transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
.copilot-slide-leave-active { transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
.copilot-slide-enter-from { opacity: 0; }
.copilot-slide-leave-to { opacity: 0; }
.copilot-slide-enter-from .copilot-panel { transform: translateX(100%); }
.copilot-slide-leave-to .copilot-panel { transform: translateX(100%); }
.copilot-slide-enter-active .copilot-panel,
.copilot-slide-leave-active .copilot-panel { transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1); }

.copilot-fade-enter-active { transition: opacity 0.25s ease; }
.copilot-fade-leave-active { transition: opacity 0.2s ease; }
.copilot-fade-enter-from,
.copilot-fade-leave-to { opacity: 0; }

.copilot-panel-wrapper {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  pointer-events: none;
}
.copilot-panel {
  width: 420px;
  height: 100vh;
  background: rgba(10, 15, 28, 0.97);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: -8px 0 48px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  pointer-events: auto;
}

.copilot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  flex-shrink: 0;
}
.copilot-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.copilot-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.copilot-avatar svg {
  width: 20px;
  height: 20px;
}
.copilot-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: -0.3px;
}
.copilot-status {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  color: #34d399;
  font-weight: 600;
  margin-top: 0.1rem;
}
.copilot-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px rgba(52,211,153,0.5);
  animation: statusPulse 2s ease-in-out infinite;
}
@keyframes statusPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.copilot-close-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.copilot-close-btn:hover {
  background: rgba(244,63,94,0.12);
  color: #fb7185;
  border-color: rgba(244,63,94,0.15);
}

.copilot-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.copilot-body::-webkit-scrollbar { width: 4px; }
.copilot-body::-webkit-scrollbar-track { background: transparent; }
.copilot-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }

.copilot-chat {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  overflow-y: auto;
  max-height: 380px;
  flex-shrink: 0;
}
.copilot-chat::-webkit-scrollbar { width: 4px; }
.copilot-chat::-webkit-scrollbar-track { background: transparent; }
.copilot-chat::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }

.copilot-msg {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
}
.copilot-msg.user {
  flex-direction: row-reverse;
}
.copilot-msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.copilot-msg-avatar svg {
  width: 14px;
  height: 14px;
}
.copilot-msg-bubble {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 0.65rem 0.9rem;
  max-width: 85%;
  border: 1px solid rgba(255, 255, 255, 0.04);
}
.copilot-msg.user .copilot-msg-bubble {
  background: rgba(79, 70, 229, 0.15);
  border-color: rgba(79, 70, 229, 0.15);
}
.copilot-msg-bubble p {
  margin: 0;
  font-size: 0.82rem;
  color: #e2e8f0;
  line-height: 1.5;
}
.copilot-msg.user .copilot-msg-bubble p {
  color: #c7d2fe;
}
.copilot-msg-time {
  display: block;
  font-size: 0.62rem;
  color: #475569;
  margin-top: 0.35rem;
}
.copilot-msg-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.6rem;
}
.copilot-action-btn {
  padding: 0.3rem 0.7rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.copilot-action-btn.primary {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
}
.copilot-action-btn.primary:hover {
  box-shadow: 0 4px 12px rgba(79,70,229,0.3);
}
.copilot-action-btn.ghost {
  background: rgba(255,255,255,0.06);
  color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.06);
}
.copilot-action-btn.ghost:hover {
  background: rgba(255,255,255,0.1);
  color: #e2e8f0;
}

.copilot-suggestions {
  padding: 0.5rem 1.25rem 0;
}
.copilot-suggestions-label {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  margin-bottom: 0.5rem;
}
.copilot-suggestions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.copilot-suggestion-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 500;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  color: #94a3b8;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
  white-space: nowrap;
}
.copilot-suggestion-chip:hover {
  background: rgba(79,70,229,0.1);
  border-color: rgba(79,70,229,0.15);
  color: #a5b4fc;
}
.copilot-suggestion-chip i {
  font-size: 0.55rem;
}

.copilot-action-cards {
  padding: 0.75rem 1.25rem;
}
.copilot-action-label {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  margin-bottom: 0.5rem;
}
.copilot-action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}
.copilot-action-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.04);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-family: inherit;
  color: inherit;
  width: 100%;
}
.copilot-action-card:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.08);
}
.copilot-action-card-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.copilot-action-card-text strong {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 0.05rem;
}
.copilot-action-card-text span {
  font-size: 0.65rem;
  color: #64748b;
}

.copilot-footer {
  border-top: 1px solid rgba(255,255,255,0.04);
  padding: 0.85rem 1.25rem;
  flex-shrink: 0;
}
.copilot-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 0.3rem 0.3rem 0.3rem 1rem;
  transition: border-color 0.2s;
}
.copilot-input-wrap:focus-within {
  border-color: rgba(129,140,248,0.35);
  box-shadow: 0 0 0 3px rgba(129,140,248,0.06);
}
.copilot-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e2e8f0;
  font-size: 0.82rem;
  font-family: inherit;
  padding: 0.4rem 0;
}
.copilot-input::placeholder {
  color: #475569;
}
.copilot-send-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.copilot-send-btn:hover {
  box-shadow: 0 4px 12px rgba(79,70,229,0.3);
}
.copilot-send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.copilot-send-btn i {
  font-size: 1.1rem;
  font-weight: 700;
}
.copilot-footer-note {
  display: block;
  font-size: 0.6rem;
  color: #475569;
  text-align: center;
  margin-top: 0.5rem;
}
</style>
