<template>
  <div class="is-page">
    <section class="is-hero">
      <div class="is-hero-bg"></div>
      <div class="is-hero-inner">
        <div class="is-hero-left">
          <div class="is-hero-tag">Community Issue Management</div>
          <h1 class="is-hero-title">Issue Tracker</h1>
          <p class="is-hero-sub">Grouped by topic — one discussion per issue affecting many students.</p>
        </div>
        <div class="is-hero-right">
          <div class="is-stat" v-for="stat in stats" :key="stat.label">
            <div class="is-stat-icon" :style="{ background: stat.iconBg, color: stat.iconColor }">
              <i :class="'bi bi-' + stat.icon"></i>
            </div>
            <div class="is-stat-body">
              <span class="is-stat-value">{{ stat.value }}</span>
              <span class="is-stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="is-toolbar">
      <div class="is-toolbar-left">
        <div class="is-search-wrap">
          <i class="bi bi-search is-search-icon"></i>
          <input v-model="searchQuery" type="text" class="is-search-input" placeholder="Search issues..." />
          <button v-if="searchQuery" class="is-search-clear" @click="searchQuery = ''"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="is-filter-group">
          <div class="is-select-wrap">
            <i class="bi bi-tag is-select-icon"></i>
            <select v-model="categoryFilter" class="is-select">
              <option value="">All Categories</option>
              <option v-for="cat in filterOptions.categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div class="is-select-wrap">
            <i class="bi bi-flag is-select-icon"></i>
            <select v-model="priorityFilter" class="is-select">
              <option value="">All Priorities</option>
              <option v-for="p in filterOptions.priorities" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div class="is-select-wrap">
            <i class="bi bi-circle-fill is-select-icon"></i>
            <select v-model="statusFilter" class="is-select">
              <option value="">All Status</option>
              <option v-for="s in filterOptions.statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="is-select-wrap">
            <i class="bi bi-arrow-down-up is-select-icon"></i>
            <select v-model="sortBy" class="is-select">
              <option v-for="opt in filterOptions.sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>
      </div>
      <div class="is-toolbar-right">
        <span class="is-result-count">{{ filteredIssues.length }} issue groups</span>
      </div>
    </div>

    <div class="is-layout">
      <div class="is-main">
        <div v-if="filteredIssues.length > 0" class="is-grid">
          <IssueGroupCard
            v-for="issue in filteredIssues"
            :key="issue.id"
            :issue="issue"
            @open="openDiscussion"
          />
        </div>

        <div v-else class="is-empty">
          <div class="is-empty-illustration">
            <svg viewBox="0 0 200 160" fill="none">
              <rect x="40" y="30" width="120" height="90" rx="14" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
              <circle cx="100" cy="55" r="12" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
              <rect x="72" y="75" width="56" height="6" rx="3" fill="rgba(255,255,255,0.05)"/>
              <rect x="72" y="87" width="40" height="6" rx="3" fill="rgba(255,255,255,0.03)"/>
              <rect x="72" y="99" width="48" height="6" rx="3" fill="rgba(255,255,255,0.03)"/>
              <path d="M60 140h80" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="68" cy="140" r="4" fill="rgba(52,211,153,0.3)"/>
              <circle cx="100" cy="140" r="4" fill="rgba(251,191,36,0.3)"/>
              <circle cx="132" cy="140" r="4" fill="rgba(129,140,248,0.3)"/>
            </svg>
          </div>
          <h3 class="is-empty-title">No issue groups found</h3>
          <p class="is-empty-text">All issues are resolved or none match your filters.</p>
          <button class="is-empty-btn" @click="resetFilters"><i class="bi bi-arrow-counterclockwise me-2"></i>Reset Filters</button>
        </div>
      </div>

      <aside class="is-sidebar" v-if="!selectedIssue">
        <div class="is-sidebar-section">
          <h4 class="is-sidebar-title"><i class="bi bi-stars"></i>AI Insights</h4>
          <div class="is-ai-card">
            <div class="is-ai-row">
              <div class="is-ai-icon" style="background: rgba(251,191,36,0.12); color: #fbbf24;">
                <i class="bi bi-exclamation-triangle-fill"></i>
              </div>
              <div class="is-ai-text">
                <strong>Possible Duplicates Detected</strong>
                <span>87 similar reports — Merge into existing discussion?</span>
              </div>
              <button class="is-ai-btn">Merge</button>
            </div>
            <div class="is-ai-row">
              <div class="is-ai-icon" style="background: rgba(52,211,153,0.12); color: #34d399;">
                <i class="bi bi-chat-quote-fill"></i>
              </div>
              <div class="is-ai-text">
                <strong>Suggested Response</strong>
                <span>"Install CH340 Driver and verify port selection."</span>
              </div>
              <button class="is-ai-btn">Use</button>
            </div>
          </div>
        </div>

        <div class="is-sidebar-section">
          <h4 class="is-sidebar-title"><i class="bi bi-bar-chart-fill"></i>Trending Issues</h4>
          <div class="is-trend-list">
            <div v-for="issue in trendingIssues" :key="issue.id" class="is-trend-item" @click="openDiscussion(issue)">
              <div class="is-trend-dot" :class="'is-trend--' + issue.trending"></div>
              <div class="is-trend-body">
                <span class="is-trend-title">{{ issue.title }}</span>
                <span class="is-trend-meta">{{ issue.affectedCount }} affected · {{ issue.category }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <Transition name="is-toast">
      <div v-if="showToast" class="is-toast" :class="toastType">
        <i :class="'bi bi-' + (toastType === 'success' ? 'check-circle-fill' : 'info-circle-fill')"></i>
        <div class="is-toast-content">
          <strong>{{ toastTitle }}</strong>
          <span>{{ toastMessage }}</span>
        </div>
      </div>
    </Transition>

    <IssueDiscussionPanel :issue="selectedIssue" @close="closeDiscussion" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { issueGroups, issueFilters, supportStats } from '../../store/issueGroupData';
import IssueGroupCard from './IssueGroupCard.vue';
import IssueDiscussionPanel from './IssueDiscussionPanel.vue';

const searchQuery = ref('');
const categoryFilter = ref('');
const priorityFilter = ref('');
const statusFilter = ref('');
const sortBy = ref('newest');
const selectedIssue = ref(null);
const showToast = ref(false);
const toastType = ref('success');
const toastTitle = ref('');
const toastMessage = ref('');

const filterOptions = issueFilters;

const stats = computed(() => [
  { value: supportStats.openIssueGroups, label: 'Open Issue Groups', icon: 'chat-dots-fill', iconBg: 'rgba(129,140,248,0.12)', iconColor: '#818cf8' },
  { value: supportStats.affectedStudents, label: 'Affected Students', icon: 'people-fill', iconBg: 'rgba(251,191,36,0.12)', iconColor: '#fbbf24' },
  { value: supportStats.resolvedIssues, label: 'Resolved Issues', icon: 'check-circle-fill', iconBg: 'rgba(52,211,153,0.12)', iconColor: '#34d399' },
  { value: supportStats.avgResolutionTime, label: 'Avg Resolution Time', icon: 'clock-fill', iconBg: 'rgba(251,113,133,0.12)', iconColor: '#fb7185' },
]);

const filteredIssues = computed(() => {
  let result = [...issueGroups];

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(i =>
      i.title.toLowerCase().includes(q) ||
      i.summary.toLowerCase().includes(q) ||
      i.category.toLowerCase().includes(q)
    );
  }
  if (categoryFilter.value) {
    result = result.filter(i => i.category === categoryFilter.value);
  }
  if (priorityFilter.value) {
    result = result.filter(i => i.priority === priorityFilter.value);
  }
  if (statusFilter.value) {
    result = result.filter(i => i.status === statusFilter.value);
  }

  switch (sortBy.value) {
    case 'newest':
      result.sort((a, b) => new Date(b.firstReported) - new Date(a.firstReported));
      break;
    case 'most_reported':
      result.sort((a, b) => b.affectedCount - a.affectedCount);
      break;
    case 'trending': {
      const order = { rising: 0, stable: 1, declining: 2, resolved: 3 };
      result.sort((a, b) => (order[a.trending] || 0) - (order[b.trending] || 0));
      break;
    }
    case 'resolved':
      result.sort((a, b) => (a.status === 'Resolved' ? 1 : 0) - (b.status === 'Resolved' ? 1 : 0));
      break;
  }

  return result;
});

const trendingIssues = computed(() =>
  issueGroups.filter(i => i.trending === 'rising' || i.trending === 'stable').slice(0, 3)
);

const openDiscussion = (issue) => { selectedIssue.value = issue; };
const closeDiscussion = () => { selectedIssue.value = null; };

const resetFilters = () => {
  searchQuery.value = '';
  categoryFilter.value = '';
  priorityFilter.value = '';
  statusFilter.value = '';
  sortBy.value = 'newest';
};
</script>

<style scoped>
.is-page { position: relative; }

.is-hero { position: relative; padding: 2rem 0 2.5rem; margin-bottom: 2rem; overflow: hidden; }
.is-hero-bg {
  position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 600px 400px at 70% 40%, rgba(129,140,248,0.07) 0%, transparent 65%),
    radial-gradient(ellipse 300px 300px at 30% 80%, rgba(52,211,153,0.04) 0%, transparent 70%);
}
.is-hero-inner { display: flex; align-items: flex-start; justify-content: space-between; gap: 2.5rem; position: relative; z-index: 1; }
.is-hero-left { flex: 1; min-width: 0; }
.is-hero-tag {
  display: inline-flex; align-items: center; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px;
  text-transform: uppercase; padding: 0.25rem 0.75rem; border-radius: 999px;
  background: rgba(129,140,248,0.1); color: #818cf8; border: 1px solid rgba(129,140,248,0.12); margin-bottom: 1rem;
}
.is-hero-title { font-size: 1.75rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.8px; margin: 0 0 0.6rem; line-height: 1.15; }
.is-hero-sub { font-size: 0.92rem; color: #64748b; margin: 0; max-width: 520px; line-height: 1.6; }
.is-hero-right { display: flex; gap: 1rem; flex-shrink: 0; }

.is-stat {
  display: flex; align-items: center; gap: 0.65rem;
  background: rgba(15,23,42,0.5); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.04); border-radius: 12px; padding: 0.65rem 0.9rem;
  min-width: 120px;
}
.is-stat-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0;
}
.is-stat-body { display: flex; flex-direction: column; }
.is-stat-value { font-size: 1rem; font-weight: 800; color: #f1f5f9; line-height: 1.2; }
.is-stat-label { font-size: 0.6rem; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 0.3px; }

.is-toolbar { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.is-toolbar-left { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; flex: 1; }
.is-search-wrap {
  position: relative; display: flex; align-items: center;
  background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px; padding: 0 0.75rem; transition: border-color 0.2s;
  min-width: 200px;
}
.is-search-wrap:focus-within { border-color: rgba(129,140,248,0.35); }
.is-search-icon { font-size: 0.75rem; color: #475569; pointer-events: none; flex-shrink: 0; }
.is-search-input {
  background: transparent; border: none; outline: none; color: rgba(255,255,255,0.95);
  font-size: 0.82rem; font-family: inherit; padding: 0.55rem 0.5rem; width: 100%;
}
.is-search-input::placeholder { color: rgba(255,255,255,0.5); }
.is-search-clear { background: none; border: none; color: #475569; cursor: pointer; padding: 0; font-size: 0.6rem; }
.is-filter-group { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.is-select-wrap { position: relative; display: flex; align-items: center; }
.is-select-icon { position: absolute; left: 0.6rem; font-size: 0.6rem; color: #475569; pointer-events: none; }
.is-select {
  appearance: none; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 8px; color: #e2e8f0; font-size: 0.72rem; font-family: inherit;
  padding: 0.45rem 1.75rem 0.45rem 1.5rem; cursor: pointer; outline: none;
  transition: border-color 0.2s; min-width: 90px;
}
.is-select:focus { border-color: rgba(129,140,248,0.35); }
.is-select option { background: #111827; color: #e2e8f0; }
.is-toolbar-right { flex-shrink: 0; }
.is-result-count { font-size: 0.72rem; color: #64748b; font-weight: 500; }

.is-layout { display: flex; gap: 1.5rem; align-items: flex-start; }
.is-main { flex: 1; min-width: 0; }

.is-grid { display: flex; flex-direction: column; gap: 1rem; }

.is-empty {
  text-align: center; padding: 4rem 2rem;
  background: rgba(15,23,42,0.4); border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.04);
}
.is-empty-illustration { margin-bottom: 1.5rem; }
.is-empty-illustration svg { width: 140px; height: auto; }
.is-empty-title { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.4rem; }
.is-empty-text { font-size: 0.82rem; color: #64748b; margin: 0 0 1.25rem; }
.is-empty-btn {
  display: inline-flex; align-items: center; padding: 0.5rem 1.25rem;
  border-radius: 10px; font-size: 0.78rem; font-weight: 600; font-family: inherit;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.06);
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
}
.is-empty-btn:hover { background: rgba(255,255,255,0.1); color: #e2e8f0; }

.is-sidebar { width: 280px; flex-shrink: 0; position: sticky; top: 1rem; }
.is-sidebar-section { margin-bottom: 1.25rem; }
.is-sidebar-title {
  font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.5px; color: #64748b; margin: 0 0 0.65rem;
  display: flex; align-items: center; gap: 0.35rem;
}
.is-sidebar-title i { font-size: 0.6rem; }

.is-ai-card {
  background: linear-gradient(135deg, rgba(79,70,229,0.06), rgba(124,58,237,0.03));
  border: 1px solid rgba(129,140,248,0.1); border-radius: 12px;
  padding: 0.65rem 0.75rem; display: flex; flex-direction: column; gap: 0.6rem;
}
.is-ai-row { display: flex; align-items: center; gap: 0.5rem; }
.is-ai-icon {
  width: 28px; height: 28px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.65rem; flex-shrink: 0;
}
.is-ai-text { flex: 1; min-width: 0; }
.is-ai-text strong { display: block; font-size: 0.68rem; color: #e2e8f0; font-weight: 700; }
.is-ai-text span { font-size: 0.63rem; color: #64748b; display: block; }
.is-ai-btn {
  padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.6rem;
  font-weight: 600; font-family: inherit; cursor: pointer; border: none;
  background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff;
  white-space: nowrap; flex-shrink: 0;
}

.is-trend-list { display: flex; flex-direction: column; gap: 0.35rem; }
.is-trend-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 0.6rem; border-radius: 8px;
  cursor: pointer; transition: background 0.2s;
}
.is-trend-item:hover { background: rgba(255,255,255,0.03); }
.is-trend-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.is-trend--rising { background: #fb7185; box-shadow: 0 0 6px rgba(251,113,133,0.4); }
.is-trend--stable { background: #fbbf24; box-shadow: 0 0 6px rgba(251,191,36,0.3); }
.is-trend--declining { background: #64748b; }
.is-trend--resolved { background: #34d399; }
.is-trend-body { display: flex; flex-direction: column; min-width: 0; }
.is-trend-title { font-size: 0.72rem; font-weight: 600; color: #e2e8f0; }
.is-trend-meta { font-size: 0.6rem; color: #475569; }

.is-toast {
  position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9999;
  display: flex; align-items: center; gap: 0.65rem;
  padding: 0.7rem 1rem; border-radius: 10px;
  background: rgba(15,23,42,0.95); backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  min-width: 240px;
}
.is-toast.success { border-color: rgba(52,211,153,0.15); }
.is-toast.info { border-color: rgba(129,140,248,0.15); }
.is-toast i { font-size: 1rem; }
.is-toast.success i { color: #34d399; }
.is-toast.info i { color: #818cf8; }
.is-toast-content { display: flex; flex-direction: column; }
.is-toast-content strong { font-size: 0.82rem; color: #f1f5f9; font-weight: 700; }
.is-toast-content span { font-size: 0.72rem; color: #64748b; }

.is-toast-enter-active { transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.is-toast-leave-active { transition: all 0.25s cubic-bezier(0.4,0,0.2,1); }
.is-toast-enter-from, .is-toast-leave-to { opacity: 0; transform: translateY(16px); }

@media (max-width: 1100px) {
  .is-layout { flex-direction: column; }
  .is-sidebar { width: 100%; position: static; }
  .is-hero-inner { flex-direction: column; }
  .is-hero-right { width: 100%; }
}
</style>
