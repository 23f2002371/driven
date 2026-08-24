<template>
  <Teleport to="body">
    <div class="spm-backdrop" @click.self="close" @keydown.escape="close">
      <div class="spm-modal">
        <div class="spm-header">
          <div class="d-flex align-items-center gap-3">
            <div class="spm-avatar-badge">{{ avatarInitials }}</div>
            <div>
              <h4 class="spm-title">Student Profile</h4>
              <p class="spm-subtitle">Update your personal details, academic department, and technical skills.</p>
            </div>
          </div>
          <button class="spm-close-btn" @click="close"><i class="bi bi-x-lg"></i></button>
        </div>

        <div v-if="isLoading" class="spm-loading">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-3 text-muted">Loading profile details...</p>
        </div>

        <div v-else class="spm-body">
          <div v-if="serverError" class="spm-alert-error">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ serverError }}
          </div>
          <div v-if="successMsg" class="spm-alert-success">
            <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
          </div>

          <!-- Basic Information -->
          <div class="spm-section">
            <h6 class="spm-section-title"><i class="bi bi-person-badge me-2"></i>Personal & Academic Info</h6>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="spm-label">Full Name <span class="text-danger">*</span></label>
                <input v-model="form.name" type="text" class="spm-input" placeholder="e.g. Navanit Kumar" :class="{ 'is-invalid': errors.name }" />
                <span v-if="errors.name" class="spm-err">{{ errors.name }}</span>
              </div>
              <div class="col-md-6">
                <label class="spm-label">Email Address</label>
                <div class="spm-input-icon-wrap">
                  <input :value="form.email" type="email" class="spm-input spm-readonly" disabled />
                  <i class="bi bi-lock-fill spm-input-icon"></i>
                </div>
              </div>
              <div class="col-md-6">
                <label class="spm-label">Student ID / Roll Number <span class="text-danger">*</span></label>
                <input v-model="form.student_id" type="text" class="spm-input" placeholder="e.g. CS2024001" :class="{ 'is-invalid': errors.student_id }" />
                <span v-if="errors.student_id" class="spm-err">{{ errors.student_id }}</span>
              </div>
              <div class="col-md-6">
                <label class="spm-label">Department <span class="text-danger">*</span></label>
                <select v-model="form.department" class="spm-input" :class="{ 'is-invalid': errors.department }">
                  <option value="" disabled>Select Department</option>
                  <option v-for="d in DEPARTMENTS" :key="d.value" :value="d.value">{{ d.label }}</option>
                </select>
                <span v-if="errors.department" class="spm-err">{{ errors.department }}</span>
              </div>
              <div class="col-md-6">
                <label class="spm-label">Phone Number <span class="text-secondary small">(Optional)</span></label>
                <input v-model="form.phone" type="text" class="spm-input" placeholder="+91 9876543210" />
              </div>
            </div>
          </div>

          <!-- Professional Links -->
          <div class="spm-section">
            <h6 class="spm-section-title"><i class="bi bi-link-45deg me-2"></i>Social & Portfolio Profiles <span class="text-secondary small">(Optional)</span></h6>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="spm-label"><i class="bi bi-github me-1"></i>GitHub Profile</label>
                <input v-model="form.github_url" type="text" class="spm-input" placeholder="username or link" />
              </div>
              <div class="col-md-4">
                <label class="spm-label"><i class="bi bi-linkedin me-1"></i>LinkedIn Profile</label>
                <input v-model="form.linkedin_url" type="text" class="spm-input" placeholder="profile URL" />
              </div>
              <div class="col-md-4">
                <label class="spm-label"><i class="bi bi-globe me-1"></i>Portfolio Website</label>
                <input v-model="form.portfolio_url" type="text" class="spm-input" placeholder="https://yourportfolio.dev" />
              </div>
            </div>
          </div>

          <!-- Domains of Interest -->
          <div class="spm-section">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="spm-section-title m-0"><i class="bi bi-compass me-2"></i>Domains of Interest <span class="text-secondary small">(Select multiple)</span></h6>
              <span class="spm-count-badge">{{ form.selectedDomains.length }} selected</span>
            </div>
            <p class="spm-hint">Choose the areas you are interested in or actively working on:</p>
            <div class="spm-chips-grid">
              <button
                v-for="domain in DOMAINS"
                :key="domain.value"
                type="button"
                class="spm-domain-chip"
                :class="{ active: form.selectedDomains.includes(domain.value) }"
                @click="toggleDomain(domain.value)"
              >
                <i :class="['bi', domain.icon, 'me-2']"></i>{{ domain.label }}
              </button>
            </div>
          </div>

          <!-- Specific Skills under Selected Domains -->
          <div v-if="form.selectedDomains.length > 0" class="spm-section">
            <h6 class="spm-section-title"><i class="bi bi-stars me-2"></i>Technical Skills & Technologies</h6>
            <p class="spm-hint">Select the specific tools, frameworks, and languages you have experience with:</p>
            
            <div v-for="dVal in form.selectedDomains" :key="dVal" class="spm-tech-group">
              <div class="spm-tech-group-title">
                <i class="bi bi-check2-circle me-1 text-primary"></i>{{ getDomainLabel(dVal) }}
              </div>
              <div class="spm-tech-chips">
                <button
                  v-for="tech in (DOMAIN_TECHNOLOGIES[dVal] || [])"
                  :key="tech.value"
                  type="button"
                  class="spm-tech-chip"
                  :class="{ active: isTechSelected(dVal, tech.value) }"
                  @click="toggleTech(dVal, tech.value)"
                >
                  {{ tech.label }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="spm-footer">
          <button class="spm-btn-cancel" :disabled="isSaving" @click="close">Cancel</button>
          <button class="spm-btn-save" :disabled="isSaving" @click="handleSave">
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <i v-else class="bi bi-check2-circle me-2"></i>{{ isSaving ? 'Saving...' : 'Save Profile' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { store } from '../store/mockData';
import { getMyStudentProfileApi, saveMyStudentProfileApi } from '../api/student';
import { DOMAINS, DOMAIN_TECHNOLOGIES, DEPARTMENTS } from '../utils/domains';

const emit = defineEmits(['close', 'saved']);

const isLoading = ref(true);
const isSaving = ref(false);
const serverError = ref('');
const successMsg = ref('');

const user = store.currentUser || {};

const form = reactive({
  name: user.full_name || user.name || '',
  email: user.email || '',
  student_id: user.student_id || '',
  department: user.department || 'computer_science',
  phone: user.phone || '',
  github_url: user.github_url || '',
  linkedin_url: user.linkedin_url || '',
  portfolio_url: user.portfolio_url || '',
  selectedDomains: [],
  selectedTechs: {}, // { DOMAIN_KEY: [TECH_KEYS] }
});

const errors = reactive({});

const avatarInitials = computed(() => {
  const n = form.name || user.email || 'ST';
  return n.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();
});

const getDomainLabel = (dVal) => {
  const found = DOMAINS.find(d => d.value === dVal);
  return found ? found.label : dVal;
};

const isTechSelected = (dVal, techVal) => {
  const list = form.selectedTechs[dVal] || [];
  return list.includes(techVal);
};

const toggleDomain = (dVal) => {
  const idx = form.selectedDomains.indexOf(dVal);
  if (idx >= 0) {
    form.selectedDomains.splice(idx, 1);
    delete form.selectedTechs[dVal];
  } else {
    form.selectedDomains.push(dVal);
    if (!form.selectedTechs[dVal]) {
      form.selectedTechs[dVal] = [];
    }
  }
};

const toggleTech = (dVal, techVal) => {
  if (!form.selectedTechs[dVal]) {
    form.selectedTechs[dVal] = [];
  }
  const list = form.selectedTechs[dVal];
  const idx = list.indexOf(techVal);
  if (idx >= 0) {
    list.splice(idx, 1);
  } else {
    list.push(techVal);
  }
};

const validate = () => {
  Object.keys(errors).forEach(k => delete errors[k]);
  if (!form.name.trim()) errors.name = 'Full name is required';
  if (!form.student_id.trim()) errors.student_id = 'Student ID is required';
  if (!form.department) errors.department = 'Department is required';
  return Object.keys(errors).length === 0;
};

const loadProfile = async () => {
  isLoading.value = true;
  const token = store.token || localStorage.getItem('driven_token');
  try {
    const data = await getMyStudentProfileApi(token);
    if (data) {
      form.name = data.user_full_name || form.name;
      form.email = data.user_email || form.email;
      form.student_id = data.student_id || form.student_id;
      form.department = data.department || form.department;
      form.phone = data.phone || '';
      form.github_url = data.github_url || '';
      form.linkedin_url = data.linkedin_url || '';
      form.portfolio_url = data.portfolio_url || '';

      if (Array.isArray(data.domains)) {
        form.selectedDomains = data.domains.map(d => d.domain);
        const techs = {};
        data.domains.forEach(d => {
          techs[d.domain] = Array.isArray(d.technologies) ? d.technologies.map(t => t.technology) : [];
        });
        form.selectedTechs = techs;
      }
    }
  } catch (err) {
    console.error('Failed to load student profile:', err);
  } finally {
    isLoading.value = false;
  }
};

const handleSave = async () => {
  if (!validate() || isSaving.value) return;

  isSaving.value = true;
  serverError.value = '';
  successMsg.value = '';

  const domainsPayload = form.selectedDomains.map(d => ({
    domain: d,
    technologies: (form.selectedTechs[d] || []).map(t => ({ technology: t })),
  }));

  const payload = {
    name: form.name.trim(),
    student_id: form.student_id.trim(),
    department: form.department,
    phone: form.phone.trim() || null,
    github_url: form.github_url.trim() || null,
    linkedin_url: form.linkedin_url.trim() || null,
    portfolio_url: form.portfolio_url.trim() || null,
    domains: domainsPayload,
  };

  const token = store.token || localStorage.getItem('driven_token');

  try {
    const res = await saveMyStudentProfileApi(payload, token);
    if (store.currentUser) {
      store.currentUser.full_name = form.name.trim();
      store.currentUser.student_id = form.student_id.trim();
      store.currentUser.department = form.department;
      localStorage.setItem('driven_user', JSON.stringify(store.currentUser));
    }
    successMsg.value = 'Profile updated successfully!';
    emit('saved', res);
    setTimeout(() => {
      emit('close');
    }, 900);
  } catch (err) {
    serverError.value = err.message || 'Failed to save student profile. Please try again.';
  } finally {
    isSaving.value = false;
  }
};

const close = () => {
  if (!isSaving.value) emit('close');
};

onMounted(() => {
  loadProfile();
});
</script>

<style scoped>
.spm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(3, 5, 12, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: spmFadeIn 0.25s ease;
}

.spm-modal {
  width: 95%;
  max-width: 900px;
  height: 88vh;
  max-height: 92vh;
  background: rgba(15, 23, 42, 0.97);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 24px;
  backdrop-filter: blur(24px);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(99, 102, 241, 0.1);
  display: flex;
  flex-direction: column;
  animation: spmScaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.spm-header {
  padding: 1.6rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.spm-avatar-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.1rem;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35);
  flex-shrink: 0;
}

.spm-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.spm-subtitle {
  font-size: 0.84rem;
  color: #94a3b8;
  margin: 0.15rem 0 0;
}

.spm-close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.spm-close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.spm-loading {
  padding: 4rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spm-body {
  padding: 2rem 2.25rem;
  overflow-y: auto;
  flex: 1;
}

.spm-alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.88rem;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
}

.spm-alert-success {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.35);
  color: #86efac;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.88rem;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
}

.spm-section {
  margin-bottom: 2.25rem;
}

.spm-section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cbd5e1;
  margin-bottom: 0.95rem;
  display: flex;
  align-items: center;
}

.spm-section-title i {
  color: #818cf8;
}

.spm-hint {
  font-size: 0.82rem;
  color: #94a3b8;
  margin-bottom: 0.95rem;
}

.spm-label {
  font-size: 0.84rem;
  font-weight: 600;
  color: #cbd5e1;
  margin-bottom: 0.45rem;
  display: block;
}

.spm-input {
  width: 100%;
  background: rgba(18, 27, 48, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  font-size: 0.88rem;
  color: #f1f5f9;
  outline: none;
  transition: all 0.2s;
}

.spm-input:focus {
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15);
}

.spm-input.is-invalid {
  border-color: #ef4444;
}

.spm-input option {
  background: #0f172a;
  color: #f1f5f9;
}

.spm-readonly {
  background: rgba(255, 255, 255, 0.03);
  color: #94a3b8;
  cursor: not-allowed;
}

.spm-input-icon-wrap {
  position: relative;
}

.spm-input-icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.9rem;
}

.spm-err {
  font-size: 0.75rem;
  color: #f87171;
  margin-top: 0.25rem;
  display: block;
}

.spm-count-badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-weight: 600;
}

/* Domain Chips */
.spm-chips-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.spm-domain-chip {
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: rgba(18, 27, 48, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  display: inline-flex;
  align-items: center;
}

.spm-domain-chip:hover {
  background: rgba(30, 41, 69, 0.8);
  border-color: rgba(129, 140, 248, 0.3);
  color: #f1f5f9;
}

.spm-domain-chip.active {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.4), rgba(124, 58, 237, 0.4));
  border-color: #818cf8;
  color: #ffffff;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
}

/* Tech Group & Chips */
.spm-tech-group {
  margin-top: 1.25rem;
  padding: 1rem;
  border-radius: 14px;
  background: rgba(18, 27, 48, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.spm-tech-group-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.spm-tech-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.spm-tech-chip {
  padding: 0.35rem 0.8rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
  color: #94a3b8;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.spm-tech-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.spm-tech-chip.active {
  background: rgba(99, 102, 241, 0.3);
  border-color: #818cf8;
  color: #ffffff;
}

.spm-footer {
  padding: 1.25rem 1.75rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(9, 13, 24, 0.5);
}

.spm-btn-cancel {
  padding: 0.6rem 1.4rem;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.spm-btn-cancel:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.spm-btn-save {
  padding: 0.6rem 1.5rem;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
  display: inline-flex;
  align-items: center;
}
.spm-btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
}
.spm-btn-save:disabled,
.spm-btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes spmFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spmScaleIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}
</style>
