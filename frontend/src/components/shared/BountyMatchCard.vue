<template>
  <div class="bounty-match-card">
    <div v-if="!result && !loading" class="match-prompt-row">
      <button type="button" class="btn-match-analyze" @click="analyze">
        <i class="bi bi-stars me-1 text-purple"></i>AI Fit Analysis
      </button>
      <span class="match-subtext">Screen candidate with Gemini</span>
    </div>

    <div v-else-if="loading" class="match-loading-row">
      <span class="spinner-border spinner-border-sm me-2 text-purple"></span>
      <span class="text-secondary small">Evaluating candidate profile & experience...</span>
    </div>

    <div v-else class="match-result-content">
      <div class="match-result-header">
        <div class="match-badge-wrap" :class="scoreClass">
          <i class="bi bi-shield-check me-1"></i>
          <span>{{ result.match_score }}% Match</span>
        </div>
        <button type="button" class="btn-match-reanalyze" title="Re-evaluate" @click="analyze">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
      <p class="match-summary-text">{{ result.summary }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { analyzeApplicationApi } from '../../api/ai';
import { store } from '../../store/mockData';

const props = defineProps({
  applicationId: { type: String, required: true }
});

const result = ref(null);
const loading = ref(false);

const scoreClass = computed(() => {
  if (!result.value) return '';
  const score = result.value.match_score;
  if (score >= 80) return 'score-high';
  if (score >= 60) return 'score-med';
  return 'score-low';
});

const analyze = async () => {
  if (!props.applicationId) return;
  loading.value = true;
  try {
    const token = store.token || localStorage.getItem('driven_token');
    result.value = await analyzeApplicationApi(props.applicationId, token);
  } catch (err) {
    alert('Analysis failed: ' + (err.message || 'Please check Gemini API key.'));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.bounty-match-card {
  margin-top: 0.75rem;
  padding: 0.75rem 0.9rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.2s ease;
}

.match-prompt-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-match-analyze {
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(129, 140, 248, 0.3);
  color: #c7d2fe;
  font-size: 0.76rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.15s ease;
}

.btn-match-analyze:hover {
  background: rgba(99, 102, 241, 0.25);
  border-color: #818cf8;
  color: #fff;
}

.match-subtext {
  font-size: 0.72rem;
  color: #64748b;
}

.match-loading-row {
  display: flex;
  align-items: center;
  font-size: 0.78rem;
}

.text-purple {
  color: #a78bfa;
}

.match-result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.match-badge-wrap {
  display: inline-flex;
  align-items: center;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: 6px;
}

.match-badge-wrap.score-high {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #34d399;
}

.match-badge-wrap.score-med {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #fbbf24;
}

.match-badge-wrap.score-low {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #f87171;
}

.btn-match-reanalyze {
  background: none;
  border: none;
  color: #64748b;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.1rem;
  transition: color 0.15s;
}

.btn-match-reanalyze:hover {
  color: #cbd5e1;
}

.match-summary-text {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.4;
  color: #cbd5e1;
}
</style>
