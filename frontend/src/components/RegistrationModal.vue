<template>
  <Teleport to="body">
    <div class="rm-backdrop" @click.self="handleBackdrop" @keydown.escape="close">
      <div class="rm-container" :class="{ 'rm-success-active': success }">
        <button class="rm-close-btn" @click="close"><i class="bi bi-x-lg"></i></button>

        <div v-if="!success" class="rm-layout">
          <div class="rm-form-panel">
            <div class="rm-event-header">
              <img :src="event.image" alt="" class="rm-event-thumb" />
              <div class="rm-event-meta">
                <h3>{{ event.name }}</h3>
                <div class="rm-event-tags">
                  <span><i class="bi bi-calendar3"></i>{{ event.date }} &middot; 09:00 AM - 05:00 PM</span>
                  <span><i class="bi bi-geo-alt"></i>{{ event.venue }}</span>
                </div>
                <div class="rm-event-stats">
                  <span class="rm-seat-count" :class="{ 'rm-low': seatsRemaining <= 5 }"><i class="bi bi-people"></i>{{ seatsRemaining }} / {{ event.participants }} seats</span>
                  <span v-if="!deadlinePassed" class="rm-deadline"><i class="bi bi-hourglass-split"></i>Closes {{ regEndsIn }}</span>
                  <span v-else class="rm-deadline-passed"><i class="bi bi-exclamation-circle"></i>Deadline passed</span>
                </div>
              </div>
            </div>

            <div class="rm-section">
              <div class="rm-section-title"><i class="bi bi-person-badge"></i>Student Information</div>
              <div class="rm-grid-2">
                <div class="rm-field">
                  <label>Full Name <span class="rm-req">*</span></label>
                  <input v-model="form.fullName" placeholder="Enter your full name" :class="{ 'rm-error': errors.fullName }" @blur="validate('fullName')" />
                  <span v-if="errors.fullName" class="rm-err-text">{{ errors.fullName }}</span>
                </div>
                <div class="rm-field">
                  <label>Student ID <span class="rm-req">*</span></label>
                  <input v-model="form.studentId" placeholder="e.g. CS2024001" :class="{ 'rm-error': errors.studentId }" @blur="validate('studentId')" />
                  <span v-if="errors.studentId" class="rm-err-text">{{ errors.studentId }}</span>
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
                  <input v-model="form.phone" placeholder="+91 98765 43210" :class="{ 'rm-error': errors.phone }" @blur="validate('phone')" />
                  <span v-if="errors.phone" class="rm-err-text">{{ errors.phone }}</span>
                </div>
              </div>
              <div class="rm-grid-2">
                <div class="rm-field">
                  <label>Department <span class="rm-req">*</span></label>
                  <select v-model="form.department" :class="{ 'rm-error': errors.department }" @change="validate('department')">
                    <option value="" disabled>Select department</option>
                    <option value="Computer Science">Computer Science</option>
                    <option value="Electronics Engineering">Electronics Engineering</option>
                    <option value="Mechanical Engineering">Mechanical Engineering</option>
                    <option value="Electrical Engineering">Electrical Engineering</option>
                    <option value="Civil Engineering">Civil Engineering</option>
                    <option value="AI & ML">AI & ML</option>
                    <option value="Information Technology">Information Technology</option>
                  </select>
                  <span v-if="errors.department" class="rm-err-text">{{ errors.department }}</span>
                </div>
                <div class="rm-field">
                  <label>Year / Semester <span class="rm-req">*</span></label>
                  <select v-model="form.yearSemester" :class="{ 'rm-error': errors.yearSemester }" @change="validate('yearSemester')">
                    <option value="" disabled>Select year</option>
                    <option value="1st Year / 2nd Sem">1st Year / 2nd Sem</option>
                    <option value="2nd Year / 4th Sem">2nd Year / 4th Sem</option>
                    <option value="3rd Year / 6th Sem">3rd Year / 6th Sem</option>
                    <option value="4th Year / 8th Sem">4th Year / 8th Sem</option>
                  </select>
                  <span v-if="errors.yearSemester" class="rm-err-text">{{ errors.yearSemester }}</span>
                </div>
              </div>
            </div>

            <div class="rm-section" v-if="showEventFields">
              <div class="rm-section-title"><i class="bi bi-question-circle"></i>Event Questions</div>

              <div class="rm-field" v-if="showField('reason')">
                <label>Why do you want to participate? <span class="rm-req">*</span></label>
                <textarea v-model="form.reason" rows="3" placeholder="Tell us what motivates you to join..." :class="{ 'rm-error': errors.reason }" @blur="validate('reason')"></textarea>
                <span v-if="errors.reason" class="rm-err-text">{{ errors.reason }}</span>
              </div>

              <div class="rm-grid-2" v-if="showField('experienceLevel') || showField('laptopRequired')">
                <div class="rm-field" v-if="showField('experienceLevel')">
                  <label>Experience Level <span class="rm-req">*</span></label>
                  <select v-model="form.experienceLevel" :class="{ 'rm-error': errors.experienceLevel }" @change="validate('experienceLevel')">
                    <option value="" disabled>Select level</option>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                  <span v-if="errors.experienceLevel" class="rm-err-text">{{ errors.experienceLevel }}</span>
                </div>
                <div class="rm-field" v-if="showField('laptopRequired')">
                  <label>Laptop Required? <span class="rm-req">*</span></label>
                  <div class="rm-radio-group">
                    <label class="rm-radio"><input type="radio" v-model="form.laptopRequired" :value="true" /> Yes</label>
                    <label class="rm-radio"><input type="radio" v-model="form.laptopRequired" :value="false" /> No</label>
                  </div>
                </div>
              </div>

              <div class="rm-field" v-if="showField('skills')">
                <label>Technical Skills</label>
                <div class="rm-chips">
                  <span v-for="skill in allSkills" :key="skill" class="rm-chip" :class="{ 'rm-chip-active': form.skills.includes(skill) }" @click="toggleSkill(skill)">{{ skill }}</span>
                </div>
              </div>

              <div class="rm-grid-3" v-if="showField('github') || showField('linkedin') || showField('portfolio')">
                <div class="rm-field" v-if="showField('github')">
                  <label>GitHub Profile</label>
                  <input v-model="form.github" placeholder="username" />
                </div>
                <div class="rm-field" v-if="showField('linkedin')">
                  <label>LinkedIn Profile</label>
                  <input v-model="form.linkedin" placeholder="username" />
                </div>
                <div class="rm-field" v-if="showField('portfolio')">
                  <label>Portfolio Website</label>
                  <input v-model="form.portfolio" placeholder="https://" />
                </div>
              </div>

              <div class="rm-grid-2" v-if="showField('teamName')">
                <div class="rm-field">
                  <label>Team Name <span class="rm-req">*</span></label>
                  <input v-model="form.teamName" placeholder="Enter team name" :class="{ 'rm-error': errors.teamName }" @blur="validate('teamName')" />
                  <span v-if="errors.teamName" class="rm-err-text">{{ errors.teamName }}</span>
                </div>
                <div class="rm-field">
                  <label>Team Size</label>
                  <input :value="form.teamMembers.length + 1" disabled class="rm-disabled" />
                </div>
              </div>

              <div v-if="showField('teamMembers') && form.teamMembers.length > 0" class="rm-field">
                <label>Team Members</label>
                <div v-for="(m, i) in form.teamMembers" :key="i" class="rm-team-row">
                  <input v-model="form.teamMembers[i]" :placeholder="'Member ' + (i + 2) + ' name'" />
                  <button class="rm-remove-btn" @click="form.teamMembers.splice(i, 1)"><i class="bi bi-x"></i></button>
                </div>
              </div>
              <button v-if="showField('teamMembers')" class="rm-add-btn" @click="form.teamMembers.push('')"><i class="bi bi-plus-lg"></i> Add Team Member</button>

              <div class="rm-grid-2" v-if="showField('dietaryPreference') || showField('tshirtSize')">
                <div class="rm-field" v-if="showField('dietaryPreference')">
                  <label>Dietary Preference</label>
                  <select v-model="form.dietaryPreference">
                    <option value="">None</option>
                    <option value="Vegetarian">Vegetarian</option>
                    <option value="Vegan">Vegan</option>
                    <option value="Non-Vegetarian">Non-Vegetarian</option>
                    <option value="Jain">Jain</option>
                  </select>
                </div>
                <div class="rm-field" v-if="showField('tshirtSize')">
                  <label>T-Shirt Size <span class="rm-req">*</span></label>
                  <select v-model="form.tshirtSize" :class="{ 'rm-error': errors.tshirtSize }" @change="validate('tshirtSize')">
                    <option value="" disabled>Select size</option>
                    <option value="S">S</option>
                    <option value="M">M</option>
                    <option value="L">L</option>
                    <option value="XL">XL</option>
                    <option value="XXL">XXL</option>
                  </select>
                  <span v-if="errors.tshirtSize" class="rm-err-text">{{ errors.tshirtSize }}</span>
                </div>
              </div>

              <div class="rm-grid-2">
                <div class="rm-field" v-if="showField('emergencyName')">
                  <label>Emergency Contact Name <span class="rm-req">*</span></label>
                  <input v-model="form.emergencyName" placeholder="Full name" :class="{ 'rm-error': errors.emergencyName }" @blur="validate('emergencyName')" />
                  <span v-if="errors.emergencyName" class="rm-err-text">{{ errors.emergencyName }}</span>
                </div>
                <div class="rm-field" v-if="showField('emergencyPhone')">
                  <label>Emergency Contact Number <span class="rm-req">*</span></label>
                  <input v-model="form.emergencyPhone" placeholder="+91 ..." :class="{ 'rm-error': errors.emergencyPhone }" @blur="validate('emergencyPhone')" />
                  <span v-if="errors.emergencyPhone" class="rm-err-text">{{ errors.emergencyPhone }}</span>
                </div>
              </div>
            </div>

            <div class="rm-section">
              <div class="rm-section-title"><i class="bi bi-check2-square"></i>Terms & Consent</div>
              <label class="rm-checkbox"><input type="checkbox" v-model="form.agreeGuidelines" /><span class="rm-checkmark"></span>I agree to follow the event guidelines and code of conduct. <span class="rm-req">*</span></label>
              <label class="rm-checkbox"><input type="checkbox" v-model="form.agreeAttendance" /><span class="rm-checkmark"></span>I understand the attendance policy and will inform in advance if unable to attend. <span class="rm-req">*</span></label>
              <label class="rm-checkbox"><input type="checkbox" v-model="form.consentNotifications" /><span class="rm-checkmark"></span>I consent to receive event-related notifications via email and SMS.</label>
            </div>
          </div>

          <div class="rm-preview-panel">
            <div class="rm-preview-sticky">
              <div class="rm-preview-header">Registration Summary</div>
              <div class="rm-preview-card">
                <img :src="event.image" alt="" class="rm-preview-img" />
                <div class="rm-preview-body">
                  <h5>{{ event.name }}</h5>
                  <span><i class="bi bi-calendar3"></i>{{ event.date }}</span>
                  <span><i class="bi bi-clock"></i>09:00 AM - 05:00 PM</span>
                  <span><i class="bi bi-geo-alt"></i>{{ event.venue }}</span>
                  <span><i class="bi bi-tag"></i>{{ category }}</span>
                  <span><i class="bi bi-cash"></i>{{ event.registrationFee || 'Free' }}</span>
                </div>
              </div>
              <div class="rm-preview-divider"></div>
              <div class="rm-preview-section">
                <div class="rm-preview-label">Participant</div>
                <div class="rm-preview-value">{{ form.fullName || '—' }}</div>
                <div class="rm-preview-label">Student ID</div>
                <div class="rm-preview-value">{{ form.studentId || '—' }}</div>
                <div class="rm-preview-label">Email</div>
                <div class="rm-preview-value rm-truncate">{{ form.email || '—' }}</div>
                <div class="rm-preview-label">Department</div>
                <div class="rm-preview-value">{{ form.department || '—' }}</div>
              </div>
              <div v-if="showField('teamName') && form.teamName" class="rm-preview-divider"></div>
              <div v-if="showField('teamName') && form.teamName" class="rm-preview-section">
                <div class="rm-preview-label">Team</div>
                <div class="rm-preview-value">{{ form.teamName }} ({{ form.teamMembers.length + 1 }} members)</div>
              </div>
              <div class="rm-preview-divider"></div>
              <div class="rm-preview-section">
                <div class="rm-preview-label">Seats</div>
                <div class="rm-preview-value" :class="{ 'rm-text-danger': seatsRemaining <= 5 }">{{ seatsRemaining }} remaining</div>
                <div class="rm-preview-label">Deadline</div>
                <div class="rm-preview-value" :class="{ 'rm-text-danger': deadlinePassed }">{{ deadlinePassed ? 'Passed' : regEndsIn }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!success" class="rm-footer">
          <button class="rm-btn rm-btn-ghost" @click="close">Cancel</button>
          <div class="rm-footer-right">
            <button class="rm-btn rm-btn-outline" @click="saveDraft">Save Draft</button>
            <button class="rm-btn rm-btn-primary" :disabled="!formValid || deadlinePassed" @click="submitRegistration">
              <i class="bi bi-check-circle me-2"></i>Confirm Registration
            </button>
          </div>
        </div>

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
          <p class="rm-success-sub">You're all set for {{ event.name }}</p>
          <div class="rm-success-pass">
            <div class="rm-pass-header">
              <span class="rm-pass-badge">Digital Pass</span>
              <span class="rm-pass-id">{{ registrationId }}</span>
            </div>
            <div class="rm-pass-body">
              <div class="rm-pass-qr">
                <div class="rm-qr-placeholder">
                  <div v-for="i in 7" :key="i" class="rm-qr-row">
                    <span v-for="j in 7" :key="j" class="rm-qr-dot" :class="{ 'rm-qr-filled': (i * 7 + j + i * j) % 3 !== 0 }"></span>
                  </div>
                </div>
              </div>
              <div class="rm-pass-info">
                <strong>{{ form.fullName }}</strong>
                <span>{{ event.date }} &middot; {{ event.venue }}</span>
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
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import { useCalendarToast } from '../composables/useCalendarToast';

const { show: showCalendarToast, message: calendarToastMsg, showCalendarToast: triggerCalendarToast } = useCalendarToast();
const showCalendarModal = ref(false);

const props = defineProps({
  event: { type: Object, required: true },
});
const emit = defineEmits(['close', 'registered']);

const success = ref(false);
const registrationId = ref('');
const existingRegistration = computed(() => store.registeredEvents.includes(props.event.id));
const profile = computed(() => store.studentProfile);

const category = computed(() => {
  const n = props.event.name.toLowerCase();
  if (n.includes('hackathon')) return 'Hackathon';
  if (n.includes('seminar')) return 'Seminar';
  if (n.includes('bootcamp')) return 'Bootcamp';
  return 'Workshop';
});

const seatsRemaining = computed(() => Math.max(0, props.event.participants - Math.floor(props.event.participants * 0.55)));
const deadlinePassed = computed(() => props.event.deadline ? new Date(props.event.deadline) < new Date() : false);
const regEndsIn = computed(() => {
  if (!props.event.deadline) return 'N/A';
  const diff = Math.ceil((new Date(props.event.deadline) - new Date()) / (1000 * 60 * 60 * 24));
  if (diff <= 0) return 'Today';
  return `${diff} days`;
});

const allSkills = ['Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'AI/ML', 'IoT', 'Blockchain', 'UI/UX', 'Django', 'Flutter'];

const showEventFields = computed(() => category.value !== 'Seminar');

const eventFields = computed(() => {
  const c = category.value;
  const fields = ['reason', 'experienceLevel', 'skills', 'github', 'linkedin', 'portfolio', 'laptopRequired', 'dietaryPreference', 'tshirtSize', 'emergencyName', 'emergencyPhone'];
  if (c === 'Hackathon' || c === 'Competition') fields.push('teamName', 'teamMembers');
  if (c === 'Seminar') return ['reason', 'linkedin', 'emergencyName', 'emergencyPhone'];
  if (c === 'Workshop' || c === 'Bootcamp') return fields;
  return fields;
});

const showField = (name) => eventFields.value.includes(name);

const form = reactive({
  fullName: profile.value.fullName || '',
  studentId: profile.value.studentId || '',
  email: profile.value.email || '',
  phone: profile.value.phone || '',
  department: profile.value.department || '',
  yearSemester: profile.value.yearSemester || '',
  reason: '',
  experienceLevel: '',
  skills: [],
  github: profile.value.github || '',
  linkedin: profile.value.linkedin || '',
  portfolio: profile.value.portfolio || '',
  teamName: '',
  teamMembers: [],
  laptopRequired: null,
  dietaryPreference: profile.value.dietaryPreference || '',
  emergencyName: profile.value.emergencyName || '',
  emergencyPhone: profile.value.emergencyPhone || '',
  tshirtSize: profile.value.tshirtSize || '',
  agreeGuidelines: false,
  agreeAttendance: false,
  consentNotifications: false,
});

const errors = reactive({});

const validate = (field) => {
  const v = (name) => form[name]?.toString().trim() || '';
  delete errors[field];
  if (field === 'fullName' && !v('fullName')) errors.fullName = 'Full name is required';
  else if (field === 'studentId' && !v('studentId')) errors.studentId = 'Student ID is required';
  else if (field === 'email') {
    if (!v('email')) errors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email'))) errors.email = 'Invalid email format';
  }
  else if (field === 'phone') {
    if (!v('phone')) errors.phone = 'Phone is required';
    else if (!/^[\+\d\s\-\(\)]{7,20}$/.test(v('phone'))) errors.phone = 'Invalid phone number';
  }
  else if (field === 'department' && !v('department')) errors.department = 'Department is required';
  else if (field === 'yearSemester' && !v('yearSemester')) errors.yearSemester = 'Year/Semester is required';
  else if (field === 'reason' && showField('reason') && !v('reason')) errors.reason = 'This field is required';
  else if (field === 'experienceLevel' && showField('experienceLevel') && !form.experienceLevel) errors.experienceLevel = 'Select your experience level';
  else if (field === 'teamName' && showField('teamName') && !v('teamName')) errors.teamName = 'Team name is required';
  else if (field === 'tshirtSize' && showField('tshirtSize') && !v('tshirtSize')) errors.tshirtSize = 'T-shirt size is required';
  else if (field === 'emergencyName' && showField('emergencyName') && !v('emergencyName')) errors.emergencyName = 'Emergency contact is required';
  else if (field === 'emergencyPhone' && showField('emergencyPhone') && !v('emergencyPhone')) errors.emergencyPhone = 'Emergency phone is required';
};

const validateAll = () => {
  const required = ['fullName', 'studentId', 'email', 'phone', 'department', 'yearSemester'];
  if (showField('reason')) required.push('reason');
  if (showField('experienceLevel')) required.push('experienceLevel');
  if (showField('teamName')) required.push('teamName');
  if (showField('tshirtSize')) required.push('tshirtSize');
  if (showField('emergencyName')) required.push('emergencyName');
  if (showField('emergencyPhone')) required.push('emergencyPhone');
  required.forEach(f => validate(f));
  return Object.keys(errors).length === 0;
};

const formValid = computed(() => {
  const filled = form.fullName?.trim() && form.studentId?.trim() && form.email?.trim() && form.phone?.trim() && form.department && form.yearSemester;
  const terms = form.agreeGuidelines && form.agreeAttendance;
  if (!filled || !terms) return false;
  if (showField('reason') && !form.reason?.trim()) return false;
  if (showField('experienceLevel') && !form.experienceLevel) return false;
  if (showField('teamName') && !form.teamName?.trim()) return false;
  if (showField('tshirtSize') && !form.tshirtSize) return false;
  if (showField('emergencyName') && !form.emergencyName?.trim()) return false;
  if (showField('emergencyPhone') && !form.emergencyPhone?.trim()) return false;
  return true;
});

const toggleSkill = (skill) => {
  const idx = form.skills.indexOf(skill);
  if (idx >= 0) form.skills.splice(idx, 1);
  else form.skills.push(skill);
};

const close = () => emit('close');

const saveDraft = () => {
  store.saveRegistrationDraft({ eventId: props.event.id, form: { ...form }, category: category.value });
  const toast = document.createElement('div');
  toast.className = 'ed-toast glass-toast';
  toast.innerHTML = '<i class="bi bi-check-circle-fill me-2" style="color:#4ade80;"></i>Draft saved!';
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2000);
};

const submitRegistration = () => {
  if (!validateAll() || deadlinePassed.value) return;
  if (existingRegistration.value) return;
  store.registeredEvents.push(props.event.id);
  registrationId.value = store.generateRegistrationId();
  success.value = true;
  store.addNotification({
    type: 'event_registered', message: `Registered for ${props.event.name}`,
    role: 'student', icon: 'check-circle-fill', color: '#34d399',
  });
  emit('registered');
  setTimeout(() => {
    document.querySelector('.rm-container')?.scrollTo({ top: 0, behavior: 'smooth' });
  }, 100);
};

const addToCalendar = () => {
  showCalendarModal.value = true;
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

const handleBackdrop = (e) => {
  if (!success.value) close();
};

onMounted(() => {
  const draft = store.getRegistrationDraft(props.event.id);
  if (draft) Object.assign(form, draft.form);
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
  max-width: 960px;
  max-height: 90vh;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  padding: 1.5rem 1.5rem 0 1.5rem;
  overflow-y: auto;
}

.rm-preview-panel {
  width: 300px;
  flex-shrink: 0;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(9, 13, 24, 0.5);
}

.rm-preview-sticky {
  position: sticky;
  top: 0;
  padding: 1.5rem;
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

.rm-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.rm-grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.75rem;
}

.rm-field { margin-bottom: 0.6rem; }
.rm-field label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin-bottom: 0.3rem;
}
.rm-req { color: #ef4444; }
.rm-field input, .rm-field select, .rm-field textarea {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255,255,255,0.95);
  font-size: 0.85rem;
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
