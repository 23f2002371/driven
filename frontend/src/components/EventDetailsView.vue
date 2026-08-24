<template>
  <div class="event-details-page">
    <div v-if="isLoading" class="ed-loading-state">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3 text-muted">Loading event details...</p>
    </div>

    <div v-else-if="data" class="ed-hero">
      <button class="ed-hero-back" @click="goBack"><i class="bi bi-arrow-left"></i></button>
      <img :src="data.image" alt="" class="ed-hero-img" />
      <div class="ed-hero-overlay"></div>
      <div class="ed-hero-content">
        <div class="ed-hero-badges">
          <span class="ed-badge-category">{{ data.category }}</span>
          <span class="ed-badge-status" :class="data.status.toLowerCase()">{{ data.status }}</span>
          <span class="ed-badge-date"><i class="bi bi-calendar3 me-1"></i>{{ data.formattedDate }}</span>
        </div>
        <div class="ed-hero-bottom">
          <div class="ed-hero-text">
            <h1 class="ed-hero-title">{{ data.name }}</h1>
            <p v-if="data.tagline" class="ed-hero-tagline">{{ data.tagline }}</p>
          </div>
          <div class="ed-hero-actions">
            <button class="ed-btn-register" :class="{ 'ed-btn-disabled': data.hasDeadlinePassed && !isRegistered }" :disabled="data.hasDeadlinePassed && !isRegistered" @click="handleRegister">
              <i v-if="data.hasDeadlinePassed && !isRegistered" class="bi bi-x-circle me-2"></i>
              <i v-else class="bi bi-check-circle me-2"></i>{{ isRegistered ? 'Registered ✓' : (data.hasDeadlinePassed ? 'Registration Closed' : 'Register Now') }}
            </button>
            <button class="ed-btn-icon" title="Share" @click="shareEvent"><i class="bi bi-share"></i></button>
            <button v-if="canAddToCalendar" class="ed-btn-icon ed-btn-calendar" title="Add to Calendar" @click="showCalendarModal = true"><i class="bi bi-calendar-plus"></i></button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isLoading && data" class="ed-content">
      <div class="ed-content-inner">
        <div class="ed-left">
          <section v-if="data.fullDescription" class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">About Event</h2>
            <p class="ed-description">{{ data.fullDescription }}</p>
          </section>

          <section v-if="data.agenda && data.agenda.length > 0" class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">Agenda / Schedule</h2>
            <div class="ed-agenda">
              <div v-for="(item, i) in data.agenda" :key="i" class="ed-agenda-item" :style="{ '--idx': i }">
                <div class="ed-agenda-time">{{ item.time }}</div>
                <div class="ed-agenda-tracker">
                  <div class="ed-agenda-dot"><div class="ed-agenda-pulse"></div></div>
                  <div v-if="i < data.agenda.length - 1" class="ed-agenda-line"></div>
                </div>
                <div class="ed-agenda-info">
                  <h4>{{ item.title }}</h4>
                  <p v-if="item.desc">{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </section>

          <section v-if="data.whatYouLearn && data.whatYouLearn.length > 0" class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">What You'll Learn</h2>
            <div class="ed-list-grid">
              <div v-for="(item, i) in data.whatYouLearn" :key="i" class="ed-list-item">
                <i class="bi bi-check-lg"></i><span>{{ item }}</span>
              </div>
            </div>
          </section>

          <section v-if="data.requirements && data.requirements.length > 0" class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">Prerequisites & Requirements</h2>
            <div class="ed-list-grid">
              <div v-for="(item, i) in data.requirements" :key="i" class="ed-list-item">
                <i class="bi bi-shield-check"></i><span>{{ item }}</span>
              </div>
            </div>
          </section>

          <section v-if="data.whoCanAttend && data.whoCanAttend.length > 0" class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">Eligibility Details</h2>
            <div class="ed-list-grid">
              <div v-for="(item, i) in data.whoCanAttend" :key="i" class="ed-list-item">
                <i class="bi bi-person-check"></i><span>{{ item }}</span>
              </div>
            </div>
          </section>
        </div>

        <div class="ed-right">
          <div class="ed-info-card glass">
            <div class="ed-info-header"><i class="bi bi-info-circle-fill me-2"></i>Event Details</div>
            <div class="ed-info-divider"></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-calendar-event"></i>Date</span><span class="ed-info-value">{{ data.formattedDate }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-geo-alt"></i>Venue</span><span class="ed-info-value">{{ data.formattedVenue }}</span></div>
            <div v-if="data.formattedDeadline" class="ed-info-row"><span class="ed-info-label"><i class="bi bi-hourglass-split"></i>Registration Deadline</span><span class="ed-info-value" :class="{ 'text-danger': data.hasDeadlinePassed }">{{ data.formattedDeadline }}<span v-if="data.hasDeadlinePassed" class="d-block small text-danger"><i class="bi bi-exclamation-circle me-1"></i>Registration deadline has passed</span></span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-people"></i>Max Capacity</span><span class="ed-info-value ed-highlight">{{ data.max_participants }} Seats</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-flag"></i>Status</span><span class="ed-info-value" :class="data.status.toLowerCase()">{{ data.status }}</span></div>
            <div class="ed-info-divider"></div>
            <button class="ed-btn-register ed-btn-full" :class="{ 'ed-btn-disabled': data.hasDeadlinePassed && !isRegistered }" :disabled="data.hasDeadlinePassed && !isRegistered" @click="handleRegister">
              <i v-if="data.hasDeadlinePassed && !isRegistered" class="bi bi-x-circle me-2"></i>
              <i v-else class="bi bi-check-circle me-2"></i>{{ isRegistered ? 'Registered ✓' : (data.hasDeadlinePassed ? 'Registration Closed' : 'Register Now') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mentors Section - rendered only when mentors exist -->
    <div v-if="!isLoading && data && data.speakers && data.speakers.length > 0" class="ed-section-wrap" data-reveal="up">
      <div class="ed-container">
        <div class="ed-section-header">
          <span class="ed-section-badge">Speakers</span>
          <h2 class="ed-heading">Meet Your Mentors & Speakers</h2>
          <p class="ed-section-sub">Industry experts and speakers guiding this event.</p>
        </div>
        <div class="ed-speakers-grid">
          <div v-for="(speaker, i) in data.speakers" :key="i" class="ed-speaker-card" :style="{ transitionDelay: `${i * 0.1}s` }" data-reveal="up">
            <div class="ed-speaker-avatar">{{ speaker.avatar }}</div>
            <div class="ed-speaker-info">
              <h4 class="ed-speaker-name">{{ speaker.name }}</h4>
              <span class="ed-speaker-role">{{ speaker.role }}</span>
              <span v-if="speaker.dept" class="ed-speaker-dept">{{ speaker.dept }}</span>
              <div class="ed-speaker-links" v-if="(speaker.linkedin && speaker.linkedin !== '#') || speaker.email">
                <a v-if="speaker.linkedin && speaker.linkedin !== '#'" :href="speaker.linkedin" class="ed-speaker-link" target="_blank"><i class="bi bi-linkedin"></i></a>
                <a v-if="speaker.email" :href="'mailto:' + speaker.email" class="ed-speaker-link"><i class="bi bi-envelope-fill"></i></a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <RegistrationModal v-if="showRegModal" :event="rawEvent" @close="showRegModal = false" @registered="onRegistered" />
    <CalendarPickerModal v-if="showCalendarModal" @close="showCalendarModal = false" @selected="triggerCalendarToast" />
    <StudentProfileModal v-if="showProfileModal" @close="showProfileModal = false" @saved="onProfileSaved" />

    <!-- Incomplete Profile Notice Modal -->
    <Teleport to="body">
      <div v-if="showIncompleteProfileModal" class="ed-modal-backdrop" @click.self="showIncompleteProfileModal = false">
        <div class="ed-notice-modal">
          <div class="ed-notice-icon-wrap">
            <i class="bi bi-person-exclamation"></i>
          </div>
          <h3 class="ed-notice-title">Complete Your Profile First</h3>
          <p class="ed-notice-desc">
            To register for events, please complete your student profile (department, student ID, and technical interests).
          </p>
          <div class="ed-notice-actions">
            <button class="ed-notice-btn-secondary" @click="goToDashboard">
              <i class="bi bi-speedometer2 me-2"></i>Go to Dashboard
            </button>
            <button class="ed-notice-btn-primary" @click="openProfileModalFromNotice">
              <i class="bi bi-person-gear me-2"></i>Complete Profile
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <div v-if="toast" class="ed-toast glass-toast"><i class="bi bi-check-circle-fill me-2" style="color: #4ade80;"></i>{{ toast }}</div>
    <div v-if="showCalendarToast" class="ed-toast glass-toast"><i class="bi bi-info-circle-fill me-2" style="color: #818cf8;"></i>{{ calendarToastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { store } from '../store/mockData';
import { fetchEventsApi, getPrivateEventApi, getEventApi } from '../api/events';
import { getMyStudentProfileApi } from '../api/student';
import RegistrationModal from './RegistrationModal.vue';
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import StudentProfileModal from './StudentProfileModal.vue';
import { useCalendarToast } from '../composables/useCalendarToast';

const route = useRoute();
const router = useRouter();
const toast = ref('');
const showRegModal = ref(false);
const showCalendarModal = ref(false);
const showProfileModal = ref(false);
const showIncompleteProfileModal = ref(false);
const rawEvent = ref(null);
const isLoading = ref(true);

const { show: showCalendarToast, message: calendarToastMsg, showCalendarToast: triggerCalendarToast } = useCalendarToast();

const formatVenue = (v) => {
  if (!v) return 'TBD';
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'TBD';
  try {
    const d = new Date(dateStr);
    if (!isNaN(d.getTime())) {
      const day = d.getDate();
      const month = d.toLocaleDateString('en-US', { month: 'short' });
      const year = d.getFullYear();
      return `${day} ${month} ${year}`;
    }
  } catch {}
  return dateStr;
};

const loadEventData = async () => {
  isLoading.value = true;
  const param = route.params.eventName || route.params.id;
  if (!param) {
    isLoading.value = false;
    return;
  }
  const decoded = decodeURIComponent(param);
  const token = store.token || localStorage.getItem('driven_token');

  // If param is a UUID, attempt to fetch directly from backend API
  const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(param);
  if (isUUID) {
    try {
      rawEvent.value = await getPrivateEventApi(param, token);
      isLoading.value = false;
      return;
    } catch {
      try {
        rawEvent.value = await getEventApi(param);
        isLoading.value = false;
        return;
      } catch {}
    }
  }

  // Fetch list of events from backend API (independent of store)
  try {
    const list = await fetchEventsApi(token);
    const found = list.find(e =>
      String(e.id) === param ||
      String(e.id) === decoded ||
      e.name === decoded ||
      encodeURIComponent(e.name) === param ||
      e.name?.toLowerCase() === decoded?.toLowerCase()
    );
    if (found) {
      try {
        rawEvent.value = await getPrivateEventApi(found.id, token);
      } catch {
        rawEvent.value = found;
      }
    } else {
      const storeFound = store.events.find(e =>
        String(e.id) === param ||
        String(e.id) === decoded ||
        e.name === decoded ||
        encodeURIComponent(e.name) === param ||
        e.name?.toLowerCase() === decoded?.toLowerCase()
      );
      if (storeFound) rawEvent.value = storeFound;
    }
  } catch (err) {
    console.error('Failed to load event:', err);
    const storeFound = store.events.find(e =>
      String(e.id) === param ||
      String(e.id) === decoded ||
      e.name === decoded ||
      encodeURIComponent(e.name) === param ||
      e.name?.toLowerCase() === decoded?.toLowerCase()
    );
    if (storeFound) rawEvent.value = storeFound;
  } finally {
    isLoading.value = false;
  }
};

const data = computed(() => {
  const e = rawEvent.value;
  if (!e) return null;

  const category = e.category
    ? (e.category.charAt(0).toUpperCase() + e.category.slice(1))
    : 'Event';

  const rawStatus = (e.status || 'Pending').toLowerCase();
  const status = rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1);

  // Live Agendas from Backend - only what exists
  const agendas = Array.isArray(e.agendas) && e.agendas.length > 0
    ? e.agendas.map(a => ({
        time: [a.start_time ? String(a.start_time).slice(0, 5) : '', a.end_time ? String(a.end_time).slice(0, 5) : ''].filter(Boolean).join(' - ') || 'TBD',
        title: a.title || 'Session',
        desc: a.description || ''
      }))
    : [];

  // Live Additional Info from Backend - only what exists
  const additionalInfo = Array.isArray(e.additional_info) ? e.additional_info : [];
  const whatYouLearn = additionalInfo.filter(i => i.section_type === 'learning' && i.content).map(i => i.content);
  const requirements = additionalInfo.filter(i => i.section_type === 'requirement' && i.content).map(i => i.content);
  const whoCanAttend = additionalInfo.filter(i => i.section_type === 'eligibility' && i.content).map(i => i.content);

  // Live Mentors from Backend - only what exists
  const speakers = Array.isArray(e.mentors) && e.mentors.length > 0
    ? e.mentors.map(m => {
        const initials = m.name ? m.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'ME';
        return {
          name: m.name || 'Mentor',
          role: m.designation || 'Speaker',
          dept: m.company || '',
          avatar: initials,
          linkedin: m.linkedin_url || '#',
          email: m.email || ''
        };
      })
    : [];

  const deadlineDate = e.registration_deadline || e.deadline;
  const hasDeadlinePassed = deadlineDate ? new Date(deadlineDate) < new Date() : false;

  return {
    ...e,
    name: e.name,
    category,
    status,
    image: e.cover_image_url || e.image || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=800&h=500&fit=crop',
    tagline: e.short_description || e.tagline || '',
    fullDescription: e.description || '',
    agenda: agendas,
    whatYouLearn,
    requirements,
    whoCanAttend,
    speakers,
    formattedDate: formatDate(e.event_date || e.date),
    formattedVenue: formatVenue(e.venue),
    formattedDeadline: deadlineDate ? formatDate(deadlineDate) : '',
    max_participants: e.max_participants || e.participants || 50,
    hasDeadlinePassed,
  };
});

const isRegistered = computed(() => data.value && store.registeredEvents.includes(data.value.id));
const canAddToCalendar = computed(() => {
  if (!data.value) return false;
  if (store.currentUserRole === 'club_admin') return data.value.status === 'Approved';
  return isRegistered.value || !data.value.hasDeadlinePassed;
});

const goBack = () => { router.back(); };

const goToDashboard = () => {
  showIncompleteProfileModal.value = false;
  router.push({ name: 'student' });
};

const openProfileModalFromNotice = () => {
  showIncompleteProfileModal.value = false;
  showProfileModal.value = true;
};

const onProfileSaved = () => {
  toast.value = 'Profile updated! You can now register for the event.';
  setTimeout(() => { toast.value = ''; }, 3500);
  showRegModal.value = true;
};

const handleRegister = async () => {
  if (!data.value) return;
  if (isRegistered.value) {
    toast.value = 'You are already registered for this event!';
    setTimeout(() => { toast.value = ''; }, 3000);
    return;
  }

  const token = store.token || localStorage.getItem('driven_token');
  if (token) {
    try {
      const studentProfile = await getMyStudentProfileApi(token);
      if (!studentProfile || !studentProfile.department || !studentProfile.student_id) {
        showIncompleteProfileModal.value = true;
        return;
      }
    } catch {
      showIncompleteProfileModal.value = true;
      return;
    }
  }

  showRegModal.value = true;
};

const onRegistered = () => {
  showRegModal.value = false;
  toast.value = `Successfully registered for ${data.value?.name}!`;
  setTimeout(() => { toast.value = ''; }, 3000);
};

const shareEvent = () => {
  if (navigator.share) {
    navigator.share({ title: data.value?.name, url: window.location.href }).catch(() => {});
  } else {
    navigator.clipboard?.writeText(window.location.href);
    toast.value = 'Link copied to clipboard!';
    setTimeout(() => { toast.value = ''; }, 2000);
  }
};

let observer = null;
onMounted(async () => {
  await loadEventData();

  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
  requestAnimationFrame(() => {
    document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
  });
});
onUnmounted(() => { if (observer) observer.disconnect(); });
</script>

<style scoped>
.event-details-page {
  background: #070b14;
  min-height: 100vh;
  color: #e2e8f0;
  overflow-x: hidden;
}

.ed-loading-state {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}


.ed-hero-back {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 1001;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(7, 11, 20, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  cursor: pointer;
  transition: all 0.25s;
}
.ed-hero-back:hover {
  background: rgba(7, 11, 20, 0.85);
  border-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.ed-btn-disabled {
  background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
  box-shadow: 0 4px 25px rgba(220, 38, 38, 0.35) !important;
  cursor: not-allowed !important;
  opacity: 1 !important;
}

.ed-hero {
  position: relative;
  height: 75vh;
  min-height: 500px;
  margin-top: 0;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  animation: heroFade 0.8s ease;
  background: linear-gradient(135deg, #0c1222, #1a1040, #0f172a);
}
@keyframes heroFade {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.ed-hero-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.ed-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7, 11, 20, 0.15) 0%, rgba(7, 11, 20, 0.5) 40%, rgba(7, 11, 20, 0.92) 80%, #070b14 100%);
}
.ed-hero-content {
  position: relative;
  z-index: 2;
  width: 100%;
  padding: 3rem 4rem;
  max-width: 1400px;
  margin: 0 auto;
}
.ed-hero-badges {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.ed-hero-badges span {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.ed-badge-category {
  background: rgba(79, 70, 229, 0.2);
  color: #a5b4fc;
  border: 1px solid rgba(79, 70, 229, 0.3);
}
.ed-badge-status {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.2);
}
.ed-badge-status.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.2);
}
.ed-badge-date, .ed-badge-club {
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.ed-hero-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 2rem;
}
.ed-hero-text { flex: 1; }
.ed-hero-title {
  font-size: 3.25rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -1.5px;
  line-height: 1.1;
  margin: 0 0 0.5rem;
}
.ed-hero-tagline {
  font-size: 1.1rem;
  color: #94a3b8;
  margin: 0;
  max-width: 600px;
  line-height: 1.5;
}
.ed-hero-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.ed-btn-register {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  color: #fff;
  padding: 0.85rem 2rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  box-shadow: 0 4px 25px rgba(79, 70, 229, 0.35);
  white-space: nowrap;
}
.ed-btn-register:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 35px rgba(79, 70, 229, 0.5);
}
.ed-btn-volunteer-text {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.85rem 2rem;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s;
  white-space: nowrap;
}
.ed-btn-volunteer-text:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.35);
  transform: translateY(-1px);
}
.ed-btn-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.25s;
}
.ed-btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  transform: translateY(-2px);
}
.ed-btn-calendar {
  color: #818cf8;
  border-color: rgba(129, 140, 248, 0.15);
}
.ed-btn-calendar:hover {
  background: rgba(129, 140, 248, 0.12) !important;
  border-color: rgba(129, 140, 248, 0.3) !important;
  color: #a5b4fc !important;
}
.ed-btn-volunteer {
  background: linear-gradient(135deg, rgba(129,140,248,0.15), rgba(129,140,248,0.05));
  border-color: rgba(129,140,248,0.2);
  color: #818cf8;
}
.ed-btn-volunteer:hover {
  background: linear-gradient(135deg, rgba(129,140,248,0.25), rgba(129,140,248,0.1)) !important;
  border-color: rgba(129,140,248,0.4) !important;
  color: #a5b4fc !important;
}

.ed-content {
  padding: 3rem 4rem;
  max-width: 1400px;
  margin: 0 auto;
}
.ed-content-inner {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 3rem;
  align-items: start;
}
.ed-left { min-width: 0; }
.ed-section { margin-bottom: 3rem; }
.ed-section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 1.25rem;
  letter-spacing: -0.5px;
}
.ed-description {
  font-size: 1rem;
  line-height: 1.8;
  color: #94a3b8;
  margin: 0;
}

.ed-agenda {
  position: relative;
}
.ed-agenda-item {
  display: flex;
  gap: 1.25rem;
  position: relative;
}
.ed-agenda-time {
  min-width: 120px;
  white-space: nowrap;
  font-size: 0.85rem;
  font-weight: 700;
  color: #818cf8;
  padding-top: 0.15rem;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}
.ed-agenda-tracker {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 16px;
}
.ed-agenda-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(79, 70, 229, 0.25);
  border: 2px solid #818cf8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.ed-agenda-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #818cf8;
  box-shadow: 0 0 8px rgba(129, 140, 248, 0.6);
}
.ed-agenda-line {
  flex: 1;
  width: 2px;
  background: linear-gradient(180deg, #818cf8 0%, rgba(129, 140, 248, 0.3) 100%);
  margin-top: 4px;
  margin-bottom: 4px;
  min-height: 28px;
}
.ed-agenda-info {
  flex: 1;
  padding-bottom: 2rem;
}
.ed-agenda-item:last-child .ed-agenda-info {
  padding-bottom: 0;
}
.ed-agenda-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.35rem;
}
.ed-agenda-info p {
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.55;
}

.ed-list-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.ed-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 1rem;
  background: rgba(18, 27, 48, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  font-size: 0.9rem;
  color: #e2e8f0;
  font-weight: 500;
  transition: all 0.25s;
}
.ed-list-item:hover {
  background: rgba(22, 33, 55, 0.7);
  border-color: rgba(129, 140, 248, 0.2);
  transform: translateX(4px);
}
.ed-list-item i {
  font-size: 1.1rem;
  flex-shrink: 0;
}
.ed-list-item i.bi-check-lg { color: #4ade80; }
.ed-list-item i.bi-shield-check { color: #818cf8; }
.ed-list-item i.bi-person-check { color: #60a5fa; }

.ed-right { position: sticky; top: 5rem; }
.ed-info-card {
  background: rgba(18, 27, 48, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.3s;
}
.ed-info-card:hover {
  border-color: rgba(129, 140, 248, 0.2);
  box-shadow: 0 0 40px rgba(129, 140, 248, 0.05);
}
.ed-info-header {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  display: flex;
  align-items: center;
}
.ed-info-header i { color: #818cf8; font-size: 1.1rem; }
.ed-info-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.08), transparent);
  margin: 1rem 0;
}
.ed-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0;
}
.ed-info-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #64748b;
  font-weight: 500;
}
.ed-info-label i { font-size: 0.9rem; width: 16px; color: #64748b; }
.ed-info-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
  text-align: right;
}
.ed-highlight { color: #818cf8 !important; }
.ed-btn-full {
  width: 100%;
  justify-content: center;
  padding: 0.9rem 1.5rem;
  font-size: 0.95rem;
  margin-top: 0.5rem;
}

.ed-section-wrap {
  padding: 5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}
.ed-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}
.ed-section-header {
  text-align: center;
  margin-bottom: 3rem;
}
.ed-section-badge {
  display: inline-block;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(79, 70, 229, 0.12);
  color: #a5b4fc;
  border: 1px solid rgba(79, 70, 229, 0.2);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.ed-heading {
  font-size: 2.25rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -1px;
  margin: 0 0 0.75rem;
}
.ed-section-sub {
  font-size: 1.05rem;
  color: #64748b;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

.ed-speakers-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
  max-width: 960px;
  margin: 0 auto;
}
.ed-speaker-card {
  flex: 1 1 300px;
  max-width: 420px;
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  padding: 1.5rem;
  background: rgba(18, 27, 48, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: default;
}
.ed-speaker-card:hover {
  transform: translateY(-4px);
  border-color: rgba(129, 140, 248, 0.25);
  background: rgba(22, 33, 55, 0.7);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(129, 140, 248, 0.05);
}
.ed-speaker-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.05rem;
  flex-shrink: 0;
  margin-top: 2px;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
}
.ed-speaker-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}
.ed-speaker-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.25rem;
}
.ed-speaker-role {
  font-size: 0.85rem;
  color: #818cf8;
  font-weight: 600;
  margin-bottom: 0.2rem;
}
.ed-speaker-dept {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 0.65rem;
}
.ed-speaker-links {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}
.ed-speaker-link {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.ed-speaker-link:hover {
  background: rgba(129, 140, 248, 0.2);
  border-color: rgba(129, 140, 248, 0.4);
  color: #ffffff;
  transform: translateY(-2px);
}

.ed-timeline-wrap { background: linear-gradient(180deg, transparent, rgba(79, 70, 229, 0.03), transparent); }
.ed-timeline {
  max-width: 700px;
  margin: 0 auto;
  position: relative;
  padding: 2rem 0;
}
.ed-timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  padding-bottom: 2.5rem;
  position: relative;
}
.ed-timeline-item:last-child { padding-bottom: 0; }
.ed-timeline-dot {
  position: relative;
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(79, 70, 229, 0.2);
  border: 2.5px solid #818cf8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.15rem;
  z-index: 2;
}
.ed-timeline-glow {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #818cf8;
  box-shadow: 0 0 12px rgba(129, 140, 248, 0.8), 0 0 30px rgba(129, 140, 248, 0.3);
  animation: pulseGlow 2s ease-in-out infinite;
}
@keyframes pulseGlow {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}
.ed-timeline-line {
  position: absolute;
  top: 22px;
  left: 9px;
  width: 2px;
  height: calc(100% - 4px);
  background: linear-gradient(180deg, rgba(129, 140, 248, 0.4), rgba(129, 140, 248, 0.05));
  z-index: 0;
}
.ed-timeline-content h4 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.ed-timeline-content span {
  font-size: 0.85rem;
  color: #64748b;
}

.ed-gallery-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.ed-gallery-item { border-radius: 16px; overflow: hidden; }
.ed-gallery-span-2 { grid-column: span 2; grid-row: span 2; }
.ed-gallery-img-wrap {
  position: relative;
  height: 100%;
  min-height: 200px;
  overflow: hidden;
  border-radius: 16px;
}
.ed-gallery-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.ed-gallery-item:hover .ed-gallery-img-wrap img { transform: scale(1.08); }
.ed-gallery-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(7, 11, 20, 0.85));
  opacity: 0;
  transition: opacity 0.4s ease;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 1.5rem;
}
.ed-gallery-item:hover .ed-gallery-overlay { opacity: 1; }
.ed-gallery-overlay i {
  font-size: 1.5rem;
  color: #fff;
  background: rgba(79, 70, 229, 0.3);
  backdrop-filter: blur(8px);
  padding: 0.6rem;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.ed-cta-wrap { background: linear-gradient(180deg, transparent, rgba(79, 70, 229, 0.04), transparent); }
.ed-cta-box {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(124, 58, 237, 0.08), rgba(6, 182, 212, 0.03));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 4rem;
  text-align: center;
}
.ed-cta-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -1px;
  margin-bottom: 0.75rem;
}
.ed-cta-text {
  font-size: 1.1rem;
  color: #64748b;
  margin-bottom: 2rem;
  line-height: 1.6;
}
.ed-cta-benefits {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
  margin-bottom: 2.5rem;
}
.ed-benefit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 500;
}
.ed-benefit i { color: #4ade80; font-size: 1rem; }
.ed-btn-cta { font-size: 1.1rem; padding: 1rem 3rem; }

.ed-similar-wrap { border-bottom: 1px solid rgba(255, 255, 255, 0.04); }

.ed-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  color: #f1f5f9;
  font-weight: 600;
  font-size: 0.9rem;
  z-index: 99999;
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Notice Modal Styles */
.ed-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 999999;
  background: rgba(3, 5, 12, 0.78);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.ed-notice-modal {
  width: 100%;
  max-width: 480px;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2.25rem 2rem;
  text-align: center;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(99, 102, 241, 0.12);
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: edNoticeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ed-notice-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.ed-notice-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0 0 0.5rem;
}

.ed-notice-desc {
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.55;
  margin-bottom: 1.75rem;
}

.ed-notice-actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
}

.ed-notice-btn-secondary {
  flex: 1;
  padding: 0.65rem 1rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 600;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.ed-notice-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
}

.ed-notice-btn-primary {
  flex: 1;
  padding: 0.65rem 1rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 600;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.ed-notice-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
}

@keyframes edNoticeIn {
  from { opacity: 0; transform: scale(0.94); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 992px) {
  .ed-hero-content { padding: 2rem 1.5rem; }
  .ed-hero { min-height: 420px; }
  .ed-hero-title { font-size: 2.25rem; }
  .ed-hero-bottom { flex-direction: column; align-items: flex-start; gap: 1.25rem; }
  .ed-content { padding: 2rem 1.5rem; }
  .ed-content-inner { grid-template-columns: 1fr; }
  .ed-right { position: static; }
  .ed-info-card { max-width: 400px; }
  .ed-speakers-grid { grid-template-columns: 1fr 1fr; }
  .ed-gallery-grid { grid-template-columns: 1fr 1fr; }
  .ed-gallery-span-2 { grid-column: span 1; grid-row: span 1; }
  .ed-list-grid { grid-template-columns: 1fr; }
  .ed-cta-box { padding: 3rem 2rem; }
  .ed-cta-title { font-size: 2rem; }
  .ed-heading { font-size: 1.75rem; }
  .ed-cta-benefits { gap: 1rem; }
}

@media (max-width: 768px) {
  .ed-hero { min-height: 360px; height: 60vh; }
  .ed-hero-title { font-size: 1.75rem; }
  .ed-hero-tagline { font-size: 0.95rem; }
  .ed-hero-badges span { font-size: 0.7rem; padding: 0.25rem 0.75rem; }
  .ed-speakers-grid { grid-template-columns: 1fr; }
  .ed-gallery-grid { grid-template-columns: 1fr; }
  .ed-cta-box { padding: 2rem 1.25rem; }
  .ed-cta-title { font-size: 1.75rem; }
  .ed-section-wrap { padding: 3rem 0; }
  .ed-container { padding: 0 1.25rem; }
  .ed-notice-actions { flex-direction: column; }
}
</style>

