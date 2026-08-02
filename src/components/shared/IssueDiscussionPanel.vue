<template>
  <Transition name="idp-overlay">
    <div v-if="issue" class="idp-overlay" @click.self="$emit('close')">
      <Transition name="idp-panel">
        <div v-if="issue" class="idp-panel">
          <button class="idp-close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>

          <div class="idp-scroll">
            <div class="idp-section">
              <div class="idp-header">
                <div>
                  <div class="idp-tag-row">
                    <span class="idp-badge" :class="'idp-status--' + issue.status.toLowerCase()">{{ issue.status }}</span>
                    <span class="idp-badge" :class="'idp-priority--' + issue.priority.toLowerCase()">{{ issue.priority }}</span>
                    <span class="idp-badge idp-category">{{ issue.category }}</span>
                  </div>
                  <h2 class="idp-title">{{ issue.title }}</h2>
                </div>
              </div>
              <p class="idp-desc">{{ issue.summary }}</p>
              <div class="idp-stats-row">
                <span><i class="bi bi-people-fill"></i>{{ issue.affectedCount }} affected</span>
                <span><i class="bi bi-chat-dots-fill"></i>{{ issue.replyCount }} replies</span>
                <span><i class="bi bi-clock-fill"></i>Last: {{ issue.lastReport }}</span>
                <span><i class="bi bi-calendar-check-fill"></i>First: {{ issue.firstReported }}</span>
              </div>
            </div>

            <div class="idp-section">
              <h4 class="idp-section-title"><i class="bi bi-people-fill"></i>Affected Students</h4>
              <div class="idp-avatar-grid">
                <div
                  v-for="(av, ai) in issue.avatars.slice(0, 12)"
                  :key="ai"
                  class="idp-avatar-item"
                  :title="av.name"
                >
                  <div class="idp-avatar" :style="{ background: av.color }">{{ av.initials }}</div>
                  <span class="idp-avatar-name">{{ av.name }}</span>
                </div>
                <div v-if="issue.avatars.length > 12" class="idp-avatar-more-btn">
                  <i class="bi bi-plus-lg"></i>
                  <span>{{ issue.avatars.length - 12 }} more</span>
                </div>
              </div>
            </div>

            <div class="idp-section">
              <h4 class="idp-section-title"><i class="bi bi-clock-history"></i>Timeline</h4>
              <div class="idp-timeline">
                <div v-for="(ev, ei) in issue.timeline" :key="ei" class="idp-timeline-item">
                  <div class="idp-timeline-dot"></div>
                  <div class="idp-timeline-content">
                    <span class="idp-timeline-date">{{ ev.date }}</span>
                    <p>{{ ev.event }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="idp-section">
              <h4 class="idp-section-title"><i class="bi bi-chat-dots-fill"></i>Discussion</h4>
              <div class="idp-discussion">
                <div
                  v-for="msg in issue.discussion"
                  :key="msg.id"
                  class="idp-msg"
                  :class="msg.from"
                >
                  <div class="idp-msg-avatar" :style="{ background: msg.color }">{{ msg.initials }}</div>
                  <div class="idp-msg-body">
                    <div class="idp-msg-header">
                      <span class="idp-msg-author">{{ msg.name }}</span>
                      <span class="idp-msg-time">{{ msg.timestamp }}</span>
                    </div>
                    <p>{{ msg.text }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="idp-section" v-if="issue.acceptedResolution">
              <h4 class="idp-section-title" style="color: #34d399;">
                <i class="bi bi-check-circle-fill"></i>Accepted Resolution
              </h4>
              <div class="idp-resolution-card">
                <p>{{ issue.acceptedResolution }}</p>
              </div>
            </div>

            <div class="idp-section" v-if="issue.relatedIssues.length">
              <h4 class="idp-section-title"><i class="bi bi-diagram-3-fill"></i>Related Issues</h4>
              <div class="idp-related-grid">
                <div
                  v-for="rel in issue.relatedIssues"
                  :key="rel.id"
                  class="idp-related-card"
                >
                  <div class="idp-related-top">
                    <span class="idp-related-title">{{ rel.title }}</span>
                    <span class="idp-related-badge" :class="rel.status === 'Open' ? 'idp-related-open' : 'idp-related-resolved'">
                      {{ rel.status }}
                    </span>
                  </div>
                  <span class="idp-related-meta"><i class="bi bi-people-fill"></i>{{ rel.affected }} affected</span>
                </div>
              </div>
            </div>

            <div class="idp-section" v-if="issue.aiSuggestion">
              <h4 class="idp-section-title" style="color: #818cf8;">
                <i class="bi bi-stars"></i>AI Suggestion
              </h4>
              <div class="idp-ai-card">
                <div v-if="issue.aiSuggestion.duplicate" class="idp-ai-row">
                  <div class="idp-ai-icon" style="background: rgba(251,191,36,0.12); color: #fbbf24;">
                    <i class="bi bi-exclamation-triangle-fill"></i>
                  </div>
                  <div class="idp-ai-text">
                    <strong>Possible Duplicate</strong>
                    <span>{{ issue.aiSuggestion.similarCount }} similar reports detected — Merge into existing discussion?</span>
                  </div>
                  <button class="idp-ai-btn">Merge</button>
                </div>
                <div class="idp-ai-row">
                  <div class="idp-ai-icon" style="background: rgba(129,140,248,0.12); color: #818cf8;">
                    <i class="bi bi-tag-fill"></i>
                  </div>
                  <div class="idp-ai-text">
                    <strong>Suggested Category</strong>
                    <span>{{ issue.aiSuggestion.suggestedCategory }} · {{ issue.aiSuggestion.confidence }}% confidence</span>
                  </div>
                </div>
                <div class="idp-ai-row">
                  <div class="idp-ai-icon" style="background: rgba(52,211,153,0.12); color: #34d399;">
                    <i class="bi bi-chat-quote-fill"></i>
                  </div>
                  <div class="idp-ai-text">
                    <strong>Suggested Response</strong>
                    <span>"{{ issue.aiSuggestion.suggestedResponse }}"</span>
                  </div>
                  <button class="idp-ai-btn">Use Response</button>
                </div>
              </div>
            </div>

            <div class="idp-section">
              <h4 class="idp-section-title"><i class="bi bi-send-fill"></i>Admin Response</h4>
              <div class="idp-reply-card">
                <p class="idp-reply-note"><i class="bi bi-info-circle-fill"></i>This response will be sent to all  <strong>{{ issue.affectedCount }} affected students</strong>.</p>
                <textarea v-model="replyText" class="idp-textarea" rows="4" placeholder="Type your response to all affected students..."></textarea>
                <div class="idp-reply-actions">
                  <button class="idp-btn idp-btn-secondary" @click="replyText = ''">Discard</button>
                  <button class="idp-btn idp-btn-primary" :disabled="!replyText.trim()">
                    <i class="bi bi-send-fill"></i>Send to All
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue';
defineProps({ issue: Object });
defineEmits(['close']);
const replyText = ref('');
</script>

<style scoped>
.idp-overlay {
  position: fixed; inset: 0; z-index: 10000; background: rgba(0,0,0,0.5);
  backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  display: flex; justify-content: flex-end;
}
.idp-overlay-enter-active { transition: opacity 0.3s ease; }
.idp-overlay-leave-active { transition: opacity 0.2s ease; }
.idp-overlay-enter-from, .idp-overlay-leave-to { opacity: 0; }

.idp-panel {
  width: 640px; max-width: 100vw; height: 100vh;
  background: rgba(10,15,28,0.97); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border-left: 1px solid rgba(255,255,255,0.06);
  box-shadow: -8px 0 48px rgba(0,0,0,0.5);
  display: flex; flex-direction: column;
  position: relative;
}
.idp-panel-enter-active { transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.idp-panel-leave-active { transition: all 0.25s cubic-bezier(0.4,0,0.2,1); }
.idp-panel-enter-from { transform: translateX(100%); }
.idp-panel-leave-to { transform: translateX(100%); }

.idp-close {
  position: absolute; top: 1rem; right: 1rem; z-index: 10;
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04); color: #64748b;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.idp-close:hover { background: rgba(244,63,94,0.12); color: #fb7185; }

.idp-scroll {
  flex: 1; overflow-y: auto; padding: 1.5rem;
}
.idp-scroll::-webkit-scrollbar { width: 4px; }
.idp-scroll::-webkit-scrollbar-track { background: transparent; }
.idp-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }

.idp-section { margin-bottom: 1.5rem; }
.idp-section-title {
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.5px; color: #64748b; margin: 0 0 0.75rem;
  display: flex; align-items: center; gap: 0.4rem;
}
.idp-section-title i { font-size: 0.65rem; }

.idp-header { margin-bottom: 0.75rem; }
.idp-tag-row { display: flex; gap: 0.35rem; margin-bottom: 0.5rem; }
.idp-badge {
  font-size: 0.6rem; font-weight: 700; padding: 0.2rem 0.55rem;
  border-radius: 999px; letter-spacing: 0.3px; text-transform: uppercase;
}
.idp-status--open { background: rgba(52,211,153,0.12); color: #34d399; }
.idp-status--resolved { background: rgba(129,140,248,0.12); color: #818cf8; }
.idp-priority--high { background: rgba(251,113,133,0.12); color: #fb7185; }
.idp-priority--medium { background: rgba(251,191,36,0.12); color: #fbbf24; }
.idp-priority--low { background: rgba(148,163,184,0.12); color: #94a3b8; }
.idp-category { background: rgba(129,140,248,0.08); color: #a5b4fc; }

.idp-title {
  font-size: 1.3rem; font-weight: 800; color: #f1f5f9;
  margin: 0; line-height: 1.3; letter-spacing: -0.5px;
}
.idp-desc {
  font-size: 0.85rem; color: #94a3b8; line-height: 1.6; margin: 0 0 0.75rem;
}
.idp-stats-row {
  display: flex; flex-wrap: wrap; gap: 0.75rem;
}
.idp-stats-row span {
  font-size: 0.7rem; color: #64748b; display: inline-flex; align-items: center; gap: 0.3rem;
}
.idp-stats-row i { font-size: 0.6rem; }

.idp-avatar-grid {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
}
.idp-avatar-item {
  display: flex; flex-direction: column; align-items: center; gap: 0.2rem;
  width: 60px; padding: 0.4rem; border-radius: 10px;
  background: rgba(255,255,255,0.02); transition: background 0.2s;
}
.idp-avatar-item:hover { background: rgba(255,255,255,0.04); }
.idp-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.6rem; font-weight: 700; color: #fff;
}
.idp-avatar-name { font-size: 0.6rem; color: #64748b; text-align: center; }
.idp-avatar-more-btn {
  width: 60px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 0.15rem;
  padding: 0.4rem; border-radius: 10px; cursor: pointer;
  background: rgba(255,255,255,0.02); color: #64748b; transition: background 0.2s;
}
.idp-avatar-more-btn:hover { background: rgba(255,255,255,0.04); }
.idp-avatar-more-btn i { font-size: 1rem; }
.idp-avatar-more-btn span { font-size: 0.55rem; }

.idp-timeline { position: relative; padding-left: 1.25rem; }
.idp-timeline::before {
  content: ''; position: absolute; left: 4px; top: 4px; bottom: 4px;
  width: 2px; background: rgba(255,255,255,0.06); border-radius: 2px;
}
.idp-timeline-item { position: relative; padding-bottom: 1rem; }
.idp-timeline-item:last-child { padding-bottom: 0; }
.idp-timeline-dot {
  position: absolute; left: -1.05rem; top: 0.25rem;
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(129,140,248,0.2); border: 2px solid rgba(129,140,248,0.4);
}
.idp-timeline-content span {
  display: block; font-size: 0.65rem; color: #64748b; margin-bottom: 0.15rem;
}
.idp-timeline-content p {
  margin: 0; font-size: 0.82rem; color: #cbd5e1; line-height: 1.4;
}

.idp-discussion { display: flex; flex-direction: column; gap: 0.75rem; }
.idp-msg { display: flex; gap: 0.6rem; align-items: flex-start; }
.idp-msg.admin { flex-direction: row-reverse; }
.idp-msg-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.55rem; font-weight: 700; color: #fff;
  flex-shrink: 0; margin-top: 0.15rem;
}
.idp-msg-body { max-width: 80%; }
.idp-msg.admin .idp-msg-body { text-align: right; }
.idp-msg-header { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.2rem; }
.idp-msg.admin .idp-msg-header { justify-content: flex-end; }
.idp-msg-author { font-size: 0.75rem; font-weight: 700; color: #e2e8f0; }
.idp-msg-time { font-size: 0.6rem; color: #475569; }
.idp-msg-body p {
  margin: 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.5;
  background: rgba(255,255,255,0.03); border-radius: 10px;
  padding: 0.55rem 0.75rem; border: 1px solid rgba(255,255,255,0.04);
}
.idp-msg.admin .idp-msg-body p {
  background: rgba(79,70,229,0.1); border-color: rgba(79,70,229,0.1);
  color: #c7d2fe;
}

.idp-resolution-card {
  background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.1);
  border-radius: 12px; padding: 0.85rem 1rem;
}
.idp-resolution-card p {
  margin: 0; font-size: 0.82rem; color: #cbd5e1; line-height: 1.6;
}

.idp-related-grid { display: flex; flex-direction: column; gap: 0.5rem; }
.idp-related-card {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.65rem 0.85rem; border-radius: 10px;
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
  cursor: pointer; transition: all 0.2s;
}
.idp-related-card:hover { background: rgba(255,255,255,0.04); }
.idp-related-top { display: flex; align-items: center; gap: 0.5rem; }
.idp-related-title { font-size: 0.78rem; font-weight: 600; color: #e2e8f0; }
.idp-related-badge {
  font-size: 0.55rem; font-weight: 700; padding: 0.15rem 0.45rem;
  border-radius: 999px; text-transform: uppercase;
}
.idp-related-open { background: rgba(52,211,153,0.12); color: #34d399; }
.idp-related-resolved { background: rgba(129,140,248,0.12); color: #818cf8; }
.idp-related-meta {
  font-size: 0.6rem; color: #64748b; display: flex; align-items: center; gap: 0.2rem;
}

.idp-ai-card {
  background: linear-gradient(135deg, rgba(79,70,229,0.06), rgba(124,58,237,0.03));
  border: 1px solid rgba(129,140,248,0.1);
  border-radius: 12px; padding: 0.75rem 1rem;
  display: flex; flex-direction: column; gap: 0.65rem;
}
.idp-ai-row {
  display: flex; align-items: center; gap: 0.65rem;
}
.idp-ai-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; flex-shrink: 0;
}
.idp-ai-text { flex: 1; }
.idp-ai-text strong { display: block; font-size: 0.75rem; color: #e2e8f0; font-weight: 700; }
.idp-ai-text span { font-size: 0.7rem; color: #64748b; }
.idp-ai-btn {
  padding: 0.3rem 0.7rem; border-radius: 8px; font-size: 0.68rem;
  font-weight: 600; font-family: inherit; cursor: pointer; border: none;
  background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff;
  white-space: nowrap;
}

.idp-reply-card {
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px; padding: 1rem;
}
.idp-reply-note {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.72rem; color: #818cf8; margin: 0 0 0.75rem;
}
.idp-reply-note i { font-size: 0.7rem; }
.idp-textarea {
  width: 100%; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px; padding: 0.65rem 0.85rem; color: #e2e8f0;
  font-size: 0.82rem; font-family: inherit; resize: vertical;
  outline: none; transition: border-color 0.2s; box-sizing: border-box;
}
.idp-textarea:focus { border-color: rgba(129,140,248,0.35); }
.idp-textarea::placeholder { color: #475569; }
.idp-reply-actions {
  display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.65rem;
}
.idp-btn {
  padding: 0.45rem 1rem; border-radius: 8px; font-size: 0.78rem;
  font-weight: 600; font-family: inherit; cursor: pointer;
  transition: all 0.2s; border: none; display: inline-flex;
  align-items: center; gap: 0.35rem;
}
.idp-btn-primary { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; }
.idp-btn-primary:hover { box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.idp-btn-primary:disabled { opacity: 0.3; cursor: not-allowed; }
.idp-btn-secondary { background: rgba(255,255,255,0.06); color: #94a3b8; border: 1px solid rgba(255,255,255,0.06); }
.idp-btn-secondary:hover { background: rgba(255,255,255,0.1); }
</style>
