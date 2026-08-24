<template>
  <div class="ai-event-gen">
    <div class="ai-gen-header">
      <div class="ai-gen-icon-wrap">
        <i class="bi bi-magic"></i>
      </div>
      <div>
        <h6 class="ai-gen-title">AI Quick Event Generator</h6>
        <p class="ai-gen-subtitle">Describe your event naturally and AI will auto-fill the entire form.</p>
      </div>
      <span class="ai-gen-pill">Powered by Gemini</span>
    </div>

    <div class="ai-gen-body">
      <textarea
        v-model="prompt"
        class="ai-gen-textarea"
        rows="2"
        placeholder="e.g., Set up a 24-hour Web3 Hackathon next Saturday in the main auditorium for 50 people with prizes..."
        @keydown.enter.ctrl.prevent="generate"
      ></textarea>
      
      <div class="ai-gen-actions">
        <div class="ai-gen-hints">
          <span>Try:</span>
          <button type="button" class="ai-hint-chip" @click="prompt = '2-day Flutter Bootcamp starting next Monday at Computer Lab 1 with 40 seats'">Flutter Bootcamp</button>
          <button type="button" class="ai-hint-chip" @click="prompt = 'AI Ethics Seminar this Friday in Seminar Hall for 100 participants'">AI Seminar</button>
        </div>

        <button
          type="button"
          class="btn-ai-generate"
          :disabled="loading || !prompt.trim()"
          @click="generate"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-stars me-1"></i>
          {{ loading ? 'Extracting Fields...' : 'Auto-Fill Form' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { generateEventApi } from '../../api/ai';
import { store } from '../../store/mockData';

const emit = defineEmits(['generated']);
const prompt = ref('');
const loading = ref(false);

const generate = async () => {
  if (!prompt.value.trim()) return;
  loading.value = true;
  try {
    const data = await generateEventApi(prompt.value.trim(), store.token || localStorage.getItem('driven_token'));
    emit('generated', data);
    prompt.value = '';
  } catch (err) {
    alert('AI Generation failed: ' + (err.message || 'Please check Gemini API key.'));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.ai-event-gen {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.08) 0%, rgba(147, 51, 234, 0.08) 100%);
  border: 1px solid rgba(129, 140, 248, 0.25);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.ai-gen-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.ai-gen-icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1rem;
  flex-shrink: 0;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.4);
}

.ai-gen-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
}

.ai-gen-subtitle {
  margin: 0;
  font-size: 0.76rem;
  color: #94a3b8;
}

.ai-gen-pill {
  margin-left: auto;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.35);
  color: #d8b4fe;
}

.ai-gen-textarea {
  width: 100%;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.75rem 0.9rem;
  font-size: 0.86rem;
  color: #f8fafc;
  resize: vertical;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.ai-gen-textarea:focus {
  border-color: #818cf8;
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.ai-gen-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.65rem;
  flex-wrap: wrap;
}

.ai-gen-hints {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #64748b;
  flex-wrap: wrap;
}

.ai-hint-chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.ai-hint-chip:hover {
  background: rgba(99, 102, 241, 0.15);
  color: #c7d2fe;
  border-color: rgba(99, 102, 241, 0.3);
}

.btn-ai-generate {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 1rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.35);
  transition: all 0.2s ease;
}

.btn-ai-generate:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.45);
}

.btn-ai-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
