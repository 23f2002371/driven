<template>
  <Teleport to="body">
    <div class="rm-backdrop" @click.self="handleBackdrop" @keydown.escape="close">
      <div class="rm-container" :class="{ 'rm-success-active': success }">
        <button class="rm-close-btn" @click="close"><i class="bi bi-x-lg"></i></button>

        <div v-if="!success" class="rm-layout">
          <div class="rm-form-panel">
            <div class="rm-event-header">
              <img :src="eventImage" alt="" class="rm-event-thumb" />
              <div class="rm-event-meta">
                <h3>{{ event.name }}</h3>
                <div class="rm-event-tags">
                  <span><i class="bi bi-calendar3"></i>{{ eventDate }}</span>
                  <span><i class="bi bi-geo-alt"></i>{{ eventVenue }}</span>
                  <span class="rm-badge-cat">{{ category }}</span>
                </div>
                <div class="rm-event-stats">
                  <span class="rm-seat-count"><i class="bi bi-people"></i>{{ event.max_participants || event.participants || 50 }} Seats Max</span>
                  <span v-if="!deadlinePassed && eventDeadline" class="rm-deadline"><i class="bi bi-hourglass-split"></i>Closes {{ regEndsIn }}</span>
                  <span v-else-if="deadlinePassed" class="rm-deadline-passed"><i class="bi bi-exclamation-circle"></i>Registration closed</span>
                </div>
              </div>
            </div>

            <!-- Server Error Banner -->
            <div v-if="submitError" class="rm-alert-error">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ submitError }}
            </div>

            <!-- Student Profile Section -->
            <div class="rm-section">
              <div class="rm-section-title"><i class="bi bi-person-badge"></i>Student Information</div>
              <div class="rm-grid-2">
                <div class="rm-field">
                  <label>Full Name <span class="rm-req">*</span></label>
                  <input v-model="form.name" placeholder="Enter your full name" :class="{ 'rm-error': errors.name }" @blur="validate('name')" />
                  <span v-if="errors.name" class="rm-err-text">{{ errors.name }}</span>
                </div>
                <div class="rm-field">
                  <label>Student ID / Roll No <span class="rm-req">*</span></label>
                  <input v-model="form.student_id" placeholder="e.g. CS2024001" :class="{ 'rm-error': errors.student_id }" @blur="validate('student_id')" />
                  <span v-if="errors.student_id" class="rm-err-text">{{ errors.student_id }}</span>
                </div>
              </div>
              <div class="rm-grid-2">
                <div class="rm-field">
                  <label>Email Address <span class="rm-req">*</span></label>
                  <input v-model="form.email" type="email" placeholder="you@university.edu" :class="{ 'rm-error': errors.email }" @blur="validate('email')" />
                  <span v-if="errors.email" class="rm-err-text">{{ errors.email }}</span>
                </div>
                <div class="rm-field">
                  <label>Phone Number <span class="rm-req">*</span></label>
                  <input v-model="form.phone" placeholder="+91 9876543210" :class="{ 'rm-error': errors.phone }" @blur="validate('phone')" />
                  <span v-if="errors.phone" class="rm-err-text">{{ errors.phone }}</span>
                </div>
              </div>
              <div class="rm-grid-2">
                <div class="rm-field">
                  <label>Department <span class="rm-req">*</span></label>
                  <select v-model="form.department" :class="{ 'rm-error': errors.department }" @change="validate('department')">
                    <option value="" disabled>Select Department</option>
                    <option value="computer_science">Computer Science</option>
                    <option value="information_technology">Information Technology</option>
                    <option value="electronics">Electronics Engineering</option>
                    <option value="electrical">Electrical Engineering</option>
                    <option value="mechanical">Mechanical Engineering</option>
                    <option value="civil">Civil Engineering</option>
                    <option value="chemical">Chemical Engineering</option>
                    <option value="biotechnology">Biotechnology</option>
                    <option value="mathematics">Mathematics</option>
                    <option value="physics">Physics</option>
                    <option value="other">Other</option>
                  </select>
                  <span v-if="errors.department" class="rm-err-text">{{ errors.department }}</span>
                </div>
                <div class="rm-field">
                  <label>Team Name / Registration Name <span class="rm-req">*</span></label>
                  <input v-model="form.team_name" placeholder="e.g. Solo / Team Spark" :class="{ 'rm-error': errors.team_name }" @blur="validate('team_name')" />
                  <span v-if="errors.team_name" class="rm-err-text">{{ errors.team_name }}</span>
                </div>
              </div>
            </div>

            <!-- Domains & Skills Section -->
            <div class="rm-section">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <div class="rm-section-title m-0"><i class="bi bi-compass"></i>Domain & Skills for this Event</div>
                <span class="rm-count-badge">{{ form.selectedDomains.length }} domains</span>
              </div>
              <p class="rm-hint">Select relevant skill domains and technologies you will use in this event. New selections will be appended to your student profile.</p>
              <div class="rm-chips-grid mb-3">
                <button
                  v-for="domain in DOMAINS"
                  :key="domain.value"
                  type="button"
                  class="rm-domain-chip"
                  :class="{ active: form.selectedDomains.includes(domain.value) }"
                  @click="toggleDomain(domain.value)"
                >
                  <i :class="['bi', domain.icon, 'me-1']"></i>{{ domain.label }}
                </button>
              </div>

              <!-- Specific Skills under Selected Domains -->
              <div v-if="form.selectedDomains.length > 0" class="rm-tech-container">
                <div v-for="dVal in form.selectedDomains" :key="dVal" class="rm-tech-group">
                  <div class="rm-tech-group-title">
                    <i class="bi bi-check2-circle me-1" style="color: #818cf8;"></i>{{ getDomainLabel(dVal) }}
                  </div>
                  <div class="rm-tech-chips">
                    <button
                      v-for="tech in (DOMAIN_TECHNOLOGIES[dVal] || [])"
                      :key="tech.value"
                      type="button"
                      class="rm-tech-chip"
                      :class="{ active: isTechSelected(dVal, tech.value) }"
                      @click="toggleTech(dVal, tech.value)"
                    >
                      {{ tech.label }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Optional Profile Links Section -->
            <div class="rm-section">
              <div class="rm-section-title"><i class="bi bi-link-45deg"></i>Professional Profiles (Optional)</div>
              <div class="rm-grid-3">
                <div class="rm-field">
                  <label>GitHub Profile</label>
                  <input v-model="form.github" placeholder="username or link" />
                </div>
                <div class="rm-field">
                  <label>LinkedIn Profile</label>
                  <input v-model="form.linkedin" placeholder="username or link" />
                </div>
                <div class="rm-field">
                  <label>Portfolio Website</label>
                  <input v-model="form.portfolio" placeholder="https://" />
                </div>
              </div>
            </div>

            <!-- Terms & Consent Section -->
            <div class="rm-section">
              <div class="rm-section-title"><i class="bi bi-check2-square"></i>Terms & Guidelines</div>
              <label class="rm-checkbox">
                <input type="checkbox" v-model="form.agreeGuidelines" />
                <span class="rm-checkmark"></span>
                I confirm that the submitted details are accurate and agree to follow the event guidelines. <span class="rm-req">*</span>
              </label>
            </div>
          </div>

          <!-- Preview Summary Panel -->
          <div class="rm-preview-panel">
            <div class="rm-preview-sticky">
              <div class="rm-preview-header">Registration Summary</div>
              <div class="rm-preview-card">
                <img :src="eventImage" alt="" class="rm-preview-img" />
                <div class="rm-preview-body">
                  <h5>{{ event.name }}</h5>
                  <span><i class="bi bi-calendar3"></i>{{ eventDate }}</span>
                  <span><i class="bi bi-geo-alt"></i>{{ eventVenue }}</span>
                  <span><i class="bi bi-tag"></i>{{ category }}</span>
                </div>
              </div>
              <div class="rm-preview-divider"></div>
              <div class="rm-preview-section">
                <div class="rm-preview-label">Participant</div>
                <div class="rm-preview-value">{{ form.name || '—' }}</div>
                <div class="rm-preview-label">Student ID</div>
                <div class="rm-preview-value">{{ form.student_id || '—' }}</div>
                <div class="rm-preview-label">Email</div>
                <div class="rm-preview-value rm-truncate">{{ form.email || '—' }}</div>
                <div class="rm-preview-label">Department</div>
                <div class="rm-preview-value">{{ formatDepartment(form.department) }}</div>
                <div class="rm-preview-label">Team / Participation</div>
                <div class="rm-preview-value">{{ form.team_name || '—' }}</div>
                <div v-if="form.selectedDomains.length > 0" class="rm-preview-label">Domains & Skills</div>
                <div v-if="form.selectedDomains.length > 0" class="rm-preview-value">
                  {{ form.selectedDomains.length }} domain(s), {{ totalSelectedTechs }} skill(s)
                </div>
                <div v-if="eventDeadline" class="rm-preview-divider"></div>
                <div v-if="eventDeadline" class="rm-preview-section rm-preview-deadline">
                  <div class="rm-preview-label">Registration Deadline</div>
                  <div class="rm-preview-value" :class="{ 'rm-text-danger': deadlinePassed }">
                    <span>{{ formattedDeadline }}</span>
                    <small class="rm-deadline-pill" :class="{ 'rm-pill-passed': deadlinePassed }">
                      <i class="bi bi-hourglass-split me-1"></i>{{ deadlinePassed ? 'Passed' : regEndsIn + ' left' }}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!success" class="rm-footer">
          <button class="rm-btn rm-btn-ghost" :disabled="isSubmitting" @click="close">Cancel</button>
          <div class="rm-footer-right">
            <button class="rm-btn rm-btn-primary" :disabled="!formValid || deadlinePassed || isSubmitting" @click="submitRegistration">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="bi bi-check-circle me-2"></i>{{ isSubmitting ? 'Registering...' : 'Confirm Registration' }}
            </button>
          </div>
        </div>

        <!-- Registration Success Screen -->
        <div v-else class="rm-success-wrap">
          <div class="rm-success-check">
            <svg viewBox="0 0 80 80" class="rm-check-svg">
              <circle cx="40" cy="40" r="36" class="rm-check-circle-bg" />
              <circle cx="40" cy="40" r="36" class="rm-check-circle" style="stroke-dasharray: 226; stroke-dashoffset: 0;" />
              <polyline points="22,42 35,55 58,27" class="rm-check-path" style="stroke-dasharray: 80; stroke-dashoffset: 0;" />
            </svg>
            <div class="rm-confetti">
              <span v-for="i in 30" :key="i" class="rm-confetti-piece" :style="confettiStyle(i)"></span>
            </div>
          </div>
          <h2 class="rm-success-title">Registration Successful!</h2>
          <p class="rm-success-sub">You're officially registered for {{ event.name }}</p>
          <div class="rm-success-pass">
            <div class="rm-pass-header">
              <span class="rm-pass-badge">Digital Pass</span>
              <span class="rm-pass-id">{{ registrationId }}</span>
            </div>
            <div class="rm-pass-body">
              <div class="rm-pass-qr">
                <img v-if="successQrCodeUrl" :src="successQrCodeUrl" alt="QR Pass" class="rm-qr-img" />
                <div v-else class="rm-qr-placeholder">
                  <div v-for="i in 7" :key="i" class="rm-qr-row">
                    <span v-for="j in 7" :key="j" class="rm-qr-dot" :class="{ 'rm-qr-filled': (i * 7 + j + i * j) % 3 !== 0 }"></span>
                  </div>
                </div>
              </div>
              <div class="rm-pass-info">
                <strong>{{ form.name }}</strong>
                <span>{{ eventDate }} &middot; {{ eventVenue }}</span>
                <span class="rm-pass-category">{{ category }}</span>
              </div>
            </div>
          </div>
          <div class="rm-success-actions">
            <button class="rm-btn rm-btn-primary" @click="showCalendarModal = true"><i class="bi bi-calendar-plus me-2"></i>Add to Calendar</button>
            <button class="rm-btn rm-btn-outline" @click="close"><i class="bi bi-x-circle me-2"></i>Close</button>
          </div>
        </div>
      </div>
    </div>
    <CalendarPickerModal v-if="showCalendarModal" @close="showCalendarModal = false" @selected="triggerCalendarToast" />
    <div v-if="showCalendarToast" class="rm-toast"><i class="bi bi-info-circle-fill me-2" style="color:#818cf8;"></i>{{ calendarToastMsg }}</div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { store } from '../store/mockData';
import { registerForEventApi } from '../api/events';
import { getMyStudentProfileApi } from '../api/student';
import { DOMAINS, DOMAIN_TECHNOLOGIES } from '../utils/domains';
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import { useCalendarToast } from '../composables/useCalendarToast';

const { show: showCalendarToast, message: calendarToastMsg, showCalendarToast: triggerCalendarToast } = useCalendarToast();
const showCalendarModal = ref(false);

const props = defineProps({
  event: { type: Object, required: true },
});
const emit = defineEmits(['close', 'registered']);

const success = ref(false);
const isSubmitting = ref(false);
const submitError = ref('');
const registrationId = ref('');
const successQrCodeUrl = ref('');

const eventImage = computed(() => props.event?.cover_image_url || props.event?.image || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop');

const eventDate = computed(() => {
  const d = props.event?.event_date || props.event?.date;
  if (!d) return 'TBD';
  try {
    const dateObj = new Date(d);
    if (!isNaN(dateObj.getTime())) {
      return `${dateObj.getDate()} ${dateObj.toLocaleDateString('en-US', { month: 'short' })} ${dateObj.getFullYear()}`;
    }
  } catch {}
  return d;
});

const eventVenue = computed(() => {
  const v = props.event?.venue;
  if (!v) return 'TBD';
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
});

const category = computed(() => {
  const c = props.event?.category;
  if (c) return c.charAt(0).toUpperCase() + c.slice(1);
  return 'Event';
});

const eventDeadline = computed(() => props.event?.registration_deadline || props.event?.deadline);

const deadlinePassed = computed(() => {
  if (!eventDeadline.value) return false;
  return new Date(eventDeadline.value) < new Date();
});

const regEndsIn = computed(() => {
  if (!eventDeadline.value) return 'N/A';
  const diff = Math.ceil((new Date(eventDeadline.value) - new Date()) / (1000 * 60 * 60 * 24));
  if (diff <= 0) return 'Today';
  return `${diff} days`;
});

const formattedDeadline = computed(() => {
  if (!eventDeadline.value) return '';
  try {
    const d = new Date(eventDeadline.value);
    if (!isNaN(d.getTime())) {
      return `${d.getDate()} ${d.toLocaleDateString('en-US', { month: 'short' })} ${d.getFullYear()}`;
    }
  } catch {}
  return eventDeadline.value;
});

const formatDepartment = (dept) => {
  if (!dept) return '—';
  return String(dept).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const user = store.currentUser || {};

const form = reactive({
  name: user.full_name || user.name || '',
  student_id: user.student_id || '',
  email: user.email || '',
  phone: user.phone || '',
  department: user.department || 'computer_science',
  team_name: user.full_name || user.name ? `${user.full_name || user.name}` : '',
  github: '',
  linkedin: '',
  portfolio: '',
  selectedDomains: [],
  selectedTechs: {}, // { DOMAIN_KEY: [TECH_KEYS] }
  agreeGuidelines: false,
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

const totalSelectedTechs = computed(() => {
  let count = 0;
  Object.values(form.selectedTechs).forEach(arr => {
    count += (arr || []).length;
  });
  return count;
});

const errors = reactive({});

const validate = (field) => {
  const v = (name) => form[name]?.toString().trim() || '';
  delete errors[field];
  if (field === 'name' && !v('name')) errors.name = 'Full name is required';
  else if (field === 'student_id' && !v('student_id')) errors.student_id = 'Student ID is required';
  else if (field === 'email') {
    if (!v('email')) errors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email'))) errors.email = 'Invalid email format';
  }
  else if (field === 'phone') {
    if (!v('phone')) errors.phone = 'Phone is required';
    else if (!/^[\+\d\s\-\(\)]{7,20}$/.test(v('phone'))) errors.phone = 'Invalid phone number';
  }
  else if (field === 'department' && !v('department')) errors.department = 'Department is required';
  else if (field === 'team_name' && !v('team_name')) errors.team_name = 'Team or registration name is required';
};

const validateAll = () => {
  const required = ['name', 'student_id', 'email', 'phone', 'department', 'team_name'];
  required.forEach(f => validate(f));
  return Object.keys(errors).length === 0 && form.agreeGuidelines;
};

const formValid = computed(() => {
  const filled = form.name?.trim() && form.student_id?.trim() && form.email?.trim() && form.phone?.trim() && form.department && form.team_name?.trim();
  return Boolean(filled && form.agreeGuidelines);
});

const close = () => emit('close');

const submitRegistration = async () => {
  if (!validateAll() || deadlinePassed.value || isSubmitting.value) return;

  isSubmitting.value = true;
  submitError.value = '';

  const domainsPayload = form.selectedDomains.map(d => ({
    domain: d,
    technologies: (form.selectedTechs[d] || []).map(t => ({ technology: t })),
  }));

  const payload = {
    event_id: props.event.id,
    name: form.name.trim(),
    student_id: form.student_id.trim(),
    email: form.email.trim(),
    phone: form.phone.trim(),
    department: form.department,
    team_name: form.team_name.trim(),
    github: form.github?.trim() || null,
    linkedin: form.linkedin?.trim() || null,
    portfolio: form.portfolio?.trim() || null,
    domains: domainsPayload,
  };

  const token = store.token || localStorage.getItem('driven_token');

  try {
    const res = await registerForEventApi(payload, token);
    registrationId.value = res.id ? `REG-${String(res.id).slice(0, 8).toUpperCase()}` : `REG-${String(props.event.id).slice(0, 8).toUpperCase()}`;
    successQrCodeUrl.value = res.qr_code_url || '';
    if (!store.registeredEvents.includes(props.event.id)) {
      store.registeredEvents.push(props.event.id);
    }
    success.value = true;
    emit('registered', res);
    setTimeout(() => {
      document.querySelector('.rm-container')?.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  } catch (err) {
    submitError.value = err.message || 'Failed to complete registration. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
};

const confettiStyle = (i) => {
  const colors = ['#818cf8', '#34d399', '#fbbf24', '#fb7185', '#60a5fa', '#4ade80', '#a78bfa'];
  return {
    left: `${(i * 3.3) % 100}%`,
    animationDelay: `${i * 0.05}s`,
    backgroundColor: colors[i % colors.length],
    width: `${6 + (i % 4) * 2}px`,
    height: `${6 + (i % 3) * 2}px`,
  };
};

const handleBackdrop = () => {
  if (!success.value && !isSubmitting.value) close();
};

onMounted(async () => {
  const token = store.token || localStorage.getItem('driven_token');
  if (token) {
    try {
      const studentProfile = await getMyStudentProfileApi(token);
      if (studentProfile) {
        if (studentProfile.user_full_name) form.name = studentProfile.user_full_name;
        if (studentProfile.student_id) form.student_id = studentProfile.student_id;
        if (studentProfile.user_email) form.email = studentProfile.user_email;
        if (studentProfile.phone) form.phone = studentProfile.phone;
        if (studentProfile.department) form.department = studentProfile.department;
        if (studentProfile.github_url) form.github = studentProfile.github_url;
        if (studentProfile.linkedin_url) form.linkedin = studentProfile.linkedin_url;
        if (studentProfile.portfolio_url) form.portfolio = studentProfile.portfolio_url;

        if (Array.isArray(studentProfile.domains)) {
          form.selectedDomains = studentProfile.domains.map(d => d.domain);
          const techs = {};
          studentProfile.domains.forEach(d => {
            techs[d.domain] = Array.isArray(d.technologies) ? d.technologies.map(t => t.technology) : [];
          });
          form.selectedTechs = techs;
        }
      }
    } catch (e) {
      console.warn('Could not load student profile for pre-filling:', e);
    }
  }

  if (form.name && !form.team_name) {
    form.team_name = form.name;
  }
});
</script>

<style scoped>
.rm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(3, 5, 12, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: rmFadeIn 0.2s ease;
}

.rm-container {
  position: relative;
  width: 96%;
  max-width: 1060px;
  height: 94vh;
  max-height: 96vh;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 24px;
  backdrop-filter: blur(24px);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(79, 70, 229, 0.08);
  display: flex;
  flex-direction: column;
  animation: rmScaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.rm-container.rm-success-active {
  max-width: 520px;
  height: auto;
  max-height: 90vh;
}

.rm-close-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  z-index: 10;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.3);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.rm-close-btn:hover { background: rgba(255, 255, 255, 0.1); color: #f1f5f9; }

.rm-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.rm-form-panel {
  flex: 1;
  padding: 1.75rem 2rem 1.5rem 2rem;
  overflow-y: auto;
}

.rm-preview-panel {
  width: 320px;
  flex-shrink: 0;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(9, 13, 24, 0.5);
  overflow-y: auto;
  overflow-x: hidden;
  max-height: 100%;
}

.rm-preview-sticky {
  padding: 1.5rem 1.25rem 2.5rem 1.25rem;
  display: flex;
  flex-direction: column;
}

.rm-preview-header {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #64748b;
  margin-bottom: 1rem;
}

.rm-preview-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 1rem;
}
.rm-preview-img {
  width: 100%;
  height: 100px;
  object-fit: cover;
  display: block;
}
.rm-preview-body {
  padding: 0.85rem;
}
.rm-preview-body h5 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.5rem;
}
.rm-preview-body span {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}
.rm-preview-body span i {
  margin-right: 0.4rem;
  width: 14px;
}

.rm-preview-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.06), transparent);
  margin: 0.75rem 0;
}

.rm-preview-section {
  margin-bottom: 0.5rem;
}
.rm-preview-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.15rem;
}
.rm-preview-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
}
.rm-preview-deadline .rm-preview-value {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}
.rm-deadline-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: rgba(129, 140, 248, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(129, 140, 248, 0.25);
  width: fit-content;
}
.rm-deadline-pill.rm-pill-passed {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.25);
}
.rm-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rm-text-danger { color: #ef4444 !important; }

.rm-event-header {
  display: flex;
  gap: 1rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.rm-event-thumb {
  width: 80px;
  height: 80px;
  border-radius: 14px;
  object-fit: cover;
  flex-shrink: 0;
}
.rm-event-meta { flex: 1; min-width: 0; }
.rm-event-meta h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.35rem;
}
.rm-event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.78rem;
  color: #64748b;
  margin-bottom: 0.4rem;
}
.rm-event-tags span i { margin-right: 0.3rem; }
.rm-event-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}
.rm-seat-count { color: #4ade80; }
.rm-seat-count.rm-low { color: #fb7185; }
.rm-deadline { color: #818cf8; }
.rm-deadline-passed { color: #ef4444; }

.rm-section {
  margin-bottom: 1.5rem;
}
.rm-section-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #cbd5e1;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.rm-section-title i { color: #818cf8; font-size: 1rem; }

.rm-hint {
  font-size: 0.78rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

.rm-count-badge {
  font-size: 0.72rem;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-weight: 600;
}

.rm-chips-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.rm-domain-chip {
  padding: 0.4rem 0.85rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  display: inline-flex;
  align-items: center;
}
.rm-domain-chip:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #f1f5f9;
  border-color: rgba(129, 140, 248, 0.3);
}
.rm-domain-chip.active {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.35), rgba(124, 58, 237, 0.35));
  border-color: #818cf8;
  color: #ffffff;
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.2);
}

.rm-tech-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rm-tech-group {
  padding: 0.85rem;
  border-radius: 12px;
  background: rgba(18, 27, 48, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.rm-tech-group-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 0.6rem;
  display: flex;
  align-items: center;
}

.rm-tech-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.rm-tech-chip {
  padding: 0.3rem 0.7rem;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.rm-tech-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}
.rm-tech-chip.active {
  background: rgba(99, 102, 241, 0.3);
  border-color: #818cf8;
  color: #ffffff;
}

.rm-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.15rem;
  margin-bottom: 0.5rem;
}
.rm-grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.15rem;
  margin-bottom: 0.5rem;
}

.rm-field { margin-bottom: 1rem; }
.rm-field label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin-bottom: 0.45rem;
}
.rm-req { color: #ef4444; }
.rm-field input, .rm-field select, .rm-field textarea {
  width: 100%;
  padding: 0.72rem 1rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 12px;
  color: rgba(255,255,255,0.95);
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}
.rm-field input:focus, .rm-field select:focus, .rm-field textarea:focus {
  border-color: rgba(129, 140, 248, 0.4);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.1);
}
.rm-field input.rm-error, .rm-field select.rm-error, .rm-field textarea.rm-error {
  border-color: rgba(239, 68, 68, 0.4);
}
.rm-field textarea { resize: vertical; min-height: 70px; }
.rm-field select { cursor: pointer; }
.rm-field select option { background: #1e293b; color: #f1f5f9; }
.rm-disabled { opacity: 0.5; cursor: not-allowed; }
.rm-err-text {
  display: block;
  font-size: 0.72rem;
  color: #ef4444;
  margin-top: 0.2rem;
}

.rm-radio-group {
  display: flex;
  gap: 1rem;
  padding-top: 0.3rem;
}
.rm-radio {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #cbd5e1;
  cursor: pointer;
}
.rm-radio input { width: auto; }

.rm-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.rm-chip {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.rm-chip:hover { border-color: rgba(129, 140, 248, 0.3); color: #cbd5e1; }
.rm-chip-active {
  background: rgba(129, 140, 248, 0.15);
  border-color: rgba(129, 140, 248, 0.4);
  color: #a5b4fc;
}

.rm-team-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.rm-team-row input { flex: 1; }
.rm-remove-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.rm-remove-btn:hover { background: rgba(239, 68, 68, 0.2); }

.rm-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  border: 1px dashed rgba(129, 140, 248, 0.3);
  background: transparent;
  color: #818cf8;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.rm-add-btn:hover { background: rgba(129, 140, 248, 0.08); border-color: rgba(129, 140, 248, 0.5); }

.rm-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.82rem;
  color: #94a3b8;
  cursor: pointer;
  margin-bottom: 0.6rem;
  line-height: 1.4;
}
.rm-checkbox input { display: none; }
.rm-checkmark {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  transition: all 0.2s;
}
.rm-checkbox input:checked + .rm-checkmark {
  background: #818cf8;
  border-color: #818cf8;
}
.rm-checkbox input:checked + .rm-checkmark::after {
  content: '\F26E';
  font-family: 'bootstrap-icons';
  font-size: 0.65rem;
  color: #fff;
}

.rm-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(9, 13, 24, 0.5);
}
.rm-footer-right {
  display: flex;
  gap: 0.75rem;
}

.rm-btn {
  padding: 0.6rem 1.25rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s;
  display: inline-flex;
  align-items: center;
  border: none;
  font-family: inherit;
}
.rm-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.rm-btn-ghost { background: transparent; color: #64748b; }
.rm-btn-ghost:hover { color: #f1f5f9; }
.rm-btn-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
}
.rm-btn-outline:hover { border-color: rgba(255, 255, 255, 0.2); color: #f1f5f9; }
.rm-btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
}
.rm-btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5); }

.rm-success-wrap {
  padding: 3rem 2rem;
  text-align: center;
  animation: rmFadeIn 0.4s ease;
}

.rm-success-check {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 1.5rem;
}
.rm-check-svg {
  width: 100%;
  height: 100%;
}
.rm-check-circle-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.06);
  stroke-width: 6;
}
.rm-check-circle {
  fill: none;
  stroke: #4ade80;
  stroke-width: 6;
  stroke-linecap: round;
  animation: rmCircleAnim 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.rm-check-path {
  fill: none;
  stroke: #4ade80;
  stroke-width: 6;
  stroke-linecap: round;
  stroke-linejoin: round;
  animation: rmCheckAnim 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
}

@keyframes rmCircleAnim {
  from { stroke-dashoffset: 226; }
  to { stroke-dashoffset: 0; }
}
@keyframes rmCheckAnim {
  from { stroke-dashoffset: 80; }
  to { stroke-dashoffset: 0; }
}

.rm-confetti {
  position: absolute;
  inset: -20px;
  pointer-events: none;
  overflow: hidden;
}
.rm-confetti-piece {
  position: absolute;
  top: -10px;
  border-radius: 2px;
  animation: rmConfettiFall 1.5s ease-in forwards;
}
@keyframes rmConfettiFall {
  0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; }
  100% { transform: translateY(120px) rotate(720deg) scale(0); opacity: 0; }
}

.rm-success-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0 0 0.25rem;
}
.rm-success-sub {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0 0 1.5rem;
}

.rm-success-pass {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  max-width: 380px;
  margin: 0 auto 1.5rem;
}
.rm-pass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.rm-pass-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #818cf8;
}
.rm-pass-id {
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  font-family: monospace;
}
.rm-pass-body {
  padding: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}
.rm-pass-qr { flex-shrink: 0; }
.rm-qr-img {
  width: 90px;
  height: 90px;
  object-fit: contain;
  background: #ffffff;
  padding: 4px;
  border-radius: 8px;
  display: block;
}
.rm-qr-placeholder {
  width: 90px;
  height: 90px;
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 6px;
  background: #fff;
  border-radius: 8px;
}
.rm-qr-row { display: flex; gap: 2px; }
.rm-qr-dot {
  width: 8px;
  height: 8px;
  border-radius: 1px;
  background: #e2e8f0;
}
.rm-qr-filled { background: #1e293b; }
.rm-pass-info {
  text-align: left;
  font-size: 0.8rem;
  color: #94a3b8;
}
.rm-pass-info strong {
  display: block;
  font-size: 0.95rem;
  color: #f1f5f9;
  margin-bottom: 0.2rem;
}
.rm-pass-info span { display: block; margin-bottom: 0.15rem; }
.rm-pass-category {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 600;
  background: rgba(129, 140, 248, 0.1);
  color: #a5b4fc;
  margin-top: 0.3rem !important;
}

.rm-success-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

@keyframes rmFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes rmScaleIn {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.rm-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 100001;
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  color: #f1f5f9;
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  background: rgba(15,23,42,0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 10px 40px rgba(0,0,0,0.4);
  animation: rmSlideUp 0.35s cubic-bezier(0.16,1,0.3,1);
}
@keyframes rmSlideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@media (max-width: 768px) {
  .rm-layout { flex-direction: column; }
  .rm-preview-panel { width: 100%; border-left: none; border-top: 1px solid rgba(255, 255, 255, 0.06); }
  .rm-container { max-height: 95vh; }
  .rm-grid-2, .rm-grid-3 { grid-template-columns: 1fr; }
}
</style>
