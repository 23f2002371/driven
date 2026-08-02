<template>
  <div class="igc-card" :class="{ 'igc-resolved': issue.status === 'Resolved' }" @click="$emit('open', issue)">
    <div class="igc-top">
      <div class="igc-title-row">
        <h3 class="igc-title">{{ issue.title }}</h3>
        <div class="igc-badges">
          <span class="igc-badge igc-status" :class="'igc-status--' + issue.status.toLowerCase()">{{ issue.status }}</span>
          <span class="igc-badge igc-priority" :class="'igc-priority--' + issue.priority.toLowerCase()">{{ issue.priority }}</span>
          <span class="igc-badge igc-category">{{ issue.category }}</span>
        </div>
      </div>
    </div>

    <p class="igc-summary">{{ issue.summary }}</p>

    <div class="igc-stats">
      <span class="igc-stat"><i class="bi bi-people-fill"></i>{{ issue.affectedCount }} Students affected</span>
      <span class="igc-stat"><i class="bi bi-chat-dots-fill"></i>{{ issue.replyCount }} Replies</span>
      <span class="igc-stat"><i class="bi bi-clock-fill"></i>Last: {{ issue.lastReport }}</span>
      <span class="igc-stat"><i class="bi bi-calendar-check-fill"></i>{{ issue.firstReported }}</span>
    </div>

    <div class="igc-avatars">
      <div class="igc-avatar-stack">
        <div
          v-for="(av, ai) in issue.avatars.slice(0, 5)"
          :key="ai"
          class="igc-avatar"
          :style="{ background: av.color, zIndex: 5 - ai }"
          :title="av.name"
        >
          {{ av.initials }}
        </div>
        <div v-if="issue.avatars.length > 5" class="igc-avatar igc-avatar-more">
          +{{ issue.avatars.length - 5 }}
        </div>
      </div>
    </div>

    <div class="igc-footer">
      <div class="igc-actions">
        <button class="igc-btn igc-btn-primary" @click.stop="$emit('open', issue)">
          <i class="bi bi-eye"></i>View Discussion
        </button>
        <button class="igc-btn igc-btn-secondary" @click.stop>
          <i class="bi bi-reply-all-fill"></i>Respond to All
        </button>
        <button class="igc-btn igc-btn-success" @click.stop v-if="issue.status !== 'Resolved'">
          <i class="bi bi-check-lg"></i>Mark Resolved
        </button>
      </div>
      <div class="igc-impact" v-if="issue.impact">
        <span class="igc-impact-badge" :class="'igc-impact--' + issue.impact.toLowerCase().replace(/\s+/g, '-')">
          <i class="bi bi-lightning-fill" v-if="issue.impact === 'High Impact'"></i>
          <i class="bi bi-check-circle-fill" v-else-if="issue.impact === 'Resolved'"></i>
          <i class="bi bi-bar-chart-fill" v-else></i>
          {{ issue.impact }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ issue: Object });
defineEmits(['open']);
</script>

<style scoped>
.igc-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1.5px solid color-mix(in srgb, var(--card-glow, rgba(255,255,255,0.06)) 20%, transparent);
  border-radius: 18px;
  padding: 1.35rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}
.igc-card:hover {
  transform: translateY(-4px);
  border-color: color-mix(in srgb, var(--card-glow, rgba(79,70,229,0.3)) 50%, transparent);
  box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 60px color-mix(in srgb, rgba(79,70,229,0.08) 30%, transparent);
}
.igc-card.igc-resolved {
  opacity: 0.7;
}
.igc-card.igc-resolved:hover {
  opacity: 0.85;
}

.igc-top {
  margin-bottom: 0.75rem;
}
.igc-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.igc-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  line-height: 1.3;
}
.igc-badges {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
  flex-shrink: 0;
}
.igc-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  white-space: nowrap;
}
.igc-status--open { background: rgba(52,211,153,0.12); color: #34d399; }
.igc-status--resolved { background: rgba(129,140,248,0.12); color: #818cf8; }
.igc-priority--high { background: rgba(251,113,133,0.12); color: #fb7185; }
.igc-priority--medium { background: rgba(251,191,36,0.12); color: #fbbf24; }
.igc-priority--low { background: rgba(148,163,184,0.12); color: #94a3b8; }
.igc-category { background: rgba(129,140,248,0.08); color: #a5b4fc; }

.igc-summary {
  font-size: 0.82rem;
  color: #94a3b8;
  line-height: 1.55;
  margin: 0 0 0.85rem;
}

.igc-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}
.igc-stat {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 500;
}
.igc-stat i {
  font-size: 0.6rem;
  color: #475569;
}

.igc-avatars {
  margin-bottom: 0.85rem;
}
.igc-avatar-stack {
  display: flex;
  align-items: center;
}
.igc-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.55rem;
  font-weight: 700;
  color: #fff;
  border: 2px solid rgba(10,15,28,0.9);
  margin-right: -8px;
  flex-shrink: 0;
}
.igc-avatar-more {
  background: rgba(255,255,255,0.08) !important;
  color: #94a3b8 !important;
  font-size: 0.5rem;
  font-weight: 600;
  border-color: rgba(255,255,255,0.04);
}

.igc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(255,255,255,0.04);
}
.igc-actions {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}
.igc-btn {
  padding: 0.35rem 0.85rem;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.igc-btn i { font-size: 0.65rem; }
.igc-btn-primary { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; }
.igc-btn-primary:hover { box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.igc-btn-secondary { background: rgba(255,255,255,0.06); color: #94a3b8; border: 1px solid rgba(255,255,255,0.06); }
.igc-btn-secondary:hover { background: rgba(255,255,255,0.1); color: #e2e8f0; }
.igc-btn-success { background: rgba(52,211,153,0.12); color: #34d399; }
.igc-btn-success:hover { background: rgba(52,211,153,0.2); }

.igc-impact { flex-shrink: 0; }
.igc-impact-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}
.igc-impact--high-impact { background: rgba(251,113,133,0.12); color: #fb7185; }
.igc-impact--medium-impact { background: rgba(251,191,36,0.12); color: #fbbf24; }
.igc-impact--resolved { background: rgba(129,140,248,0.12); color: #818cf8; }
.igc-impact-badge i { font-size: 0.55rem; }
</style>
