<template>
  <div class="event-details-page">
      <div v-if="data" class="ed-hero">
      <button class="ed-hero-back" @click="goBack"><i class="bi bi-arrow-left"></i></button>
      <img :src="data.image" alt="" class="ed-hero-img" />
      <div class="ed-hero-overlay"></div>
      <div class="ed-hero-content">
        <div class="ed-hero-badges">
          <span class="ed-badge-category">{{ data.category }}</span>
          <span class="ed-badge-status" :class="data.status.toLowerCase()">{{ data.status }}</span>
          <span class="ed-badge-date"><i class="bi bi-calendar3 me-1"></i>{{ data.date }}</span>
          <span class="ed-badge-club"><i class="bi bi-building me-1"></i>{{ data.organizedBy }}</span>
        </div>
        <div class="ed-hero-bottom">
          <div class="ed-hero-text">
            <h1 class="ed-hero-title">{{ data.name }}</h1>
            <p class="ed-hero-tagline">{{ data.tagline }}</p>
          </div>
          <div class="ed-hero-actions">
            <button class="ed-btn-register" :class="{ 'ed-btn-disabled': data.hasDeadlinePassed && !isRegistered }" :disabled="data.hasDeadlinePassed && !isRegistered" @click="handleRegister">
              <i v-if="data.hasDeadlinePassed && !isRegistered" class="bi bi-x-circle me-2"></i>
              <i v-else class="bi bi-check-circle me-2"></i>{{ isRegistered ? 'Registered ✓' : (data.hasDeadlinePassed ? 'Registration Closed' : 'Register Now') }}
            </button>
            <button class="ed-btn-icon" title="Share" @click="shareEvent"><i class="bi bi-share"></i></button>
            <button v-if="canAddToCalendar" class="ed-btn-icon ed-btn-calendar" title="Add to Calendar" @click="showCalendarModal = true"><i class="bi bi-calendar-plus"></i></button>
            <button class="ed-btn-volunteer-text" @click="showVolModal = true">Volunteering</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="data" class="ed-content">
      <div class="ed-content-inner">
        <div class="ed-left">
          <section class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">About Event</h2>
            <p class="ed-description">{{ data.fullDescription }}</p>
          </section>

          <section class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">Agenda / Schedule</h2>
            <div class="ed-agenda">
              <div v-for="(item, i) in data.agenda" :key="i" class="ed-agenda-item" :style="{ '--idx': i }">
                <div class="ed-agenda-time">{{ item.time }}</div>
                <div class="ed-agenda-dot"><div class="ed-agenda-pulse"></div></div>
                <div class="ed-agenda-info">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </section>

          <section class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">What You'll Learn</h2>
            <div class="ed-list-grid">
              <div v-for="(item, i) in data.whatYouLearn" :key="i" class="ed-list-item">
                <i class="bi bi-check-lg"></i><span>{{ item }}</span>
              </div>
            </div>
          </section>

          <section class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">Requirements</h2>
            <div class="ed-list-grid">
              <div v-for="(item, i) in data.requirements" :key="i" class="ed-list-item">
                <i class="bi bi-shield-check"></i><span>{{ item }}</span>
              </div>
            </div>
          </section>

          <section class="ed-section" data-reveal="up">
            <h2 class="ed-section-title">Who Can Attend</h2>
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
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-calendar-event"></i>Date</span><span class="ed-info-value">{{ data.date }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-clock"></i>Time</span><span class="ed-info-value">09:00 AM - 05:00 PM</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-geo-alt"></i>Venue</span><span class="ed-info-value">{{ data.venue }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-hourglass-split"></i>Deadline</span><span class="ed-info-value" :class="{ 'text-danger': data.hasDeadlinePassed }">{{ data.deadline || data.date }}<span v-if="data.hasDeadlinePassed" class="d-block small text-danger"><i class="bi bi-exclamation-circle me-1"></i>Registration deadline has been passed</span></span></div>
            <div class="ed-info-divider"></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-people"></i>Available Seats</span><span class="ed-info-value ed-highlight">{{ data.availableSeats }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-person-check"></i>Registered</span><span class="ed-info-value">{{ data.registeredStudents }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-clock-history"></i>Duration</span><span class="ed-info-value">{{ data.duration }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-building"></i>Organized By</span><span class="ed-info-value">{{ data.organizedBy }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-cash"></i>Fee</span><span class="ed-info-value ed-highlight" style="color: #4ade80 !important;">{{ data.registrationFee }}</span></div>
            <div class="ed-info-row"><span class="ed-info-label"><i class="bi bi-person-badge"></i>Contact</span><span class="ed-info-value">{{ data.contactPerson }}</span></div>
            <div class="ed-info-divider"></div>
            <button class="ed-btn-register ed-btn-full" :class="{ 'ed-btn-disabled': data.hasDeadlinePassed && !isRegistered }" :disabled="data.hasDeadlinePassed && !isRegistered" @click="handleRegister">
              <i v-if="data.hasDeadlinePassed && !isRegistered" class="bi bi-x-circle me-2"></i>
              <i v-else class="bi bi-check-circle me-2"></i>{{ isRegistered ? 'Registered ✓' : (data.hasDeadlinePassed ? 'Registration Closed' : 'Register Now') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="data" class="ed-section-wrap" data-reveal="up">
      <div class="ed-container">
        <div class="ed-section-header">
          <span class="ed-section-badge">Speakers</span>
          <h2 class="ed-heading">Meet Your Mentors</h2>
          <p class="ed-section-sub">Industry experts and faculty guiding this event.</p>
        </div>
        <div class="ed-speakers-grid">
          <div v-for="(speaker, i) in data.speakers" :key="i" class="ed-speaker-card" :style="{ transitionDelay: `${i * 0.1}s` }" data-reveal="up">
            <div class="ed-speaker-avatar">{{ speaker.avatar }}</div>
            <div class="ed-speaker-info">
              <h4 class="ed-speaker-name">{{ speaker.name }}</h4>
              <span class="ed-speaker-role">{{ speaker.role }}</span>
              <span class="ed-speaker-dept">{{ speaker.dept }}</span>
              <div class="ed-speaker-links">
                <a :href="speaker.linkedin" class="ed-speaker-link" target="_blank"><i class="bi bi-linkedin"></i></a>
                <a :href="'mailto:' + speaker.email" class="ed-speaker-link"><i class="bi bi-envelope-fill"></i></a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="data" class="ed-section-wrap ed-timeline-wrap" data-reveal="up">
      <div class="ed-container">
        <div class="ed-section-header">
          <span class="ed-section-badge">Timeline</span>
          <h2 class="ed-heading">Event Journey</h2>
          <p class="ed-section-sub">Key milestones from registration to closing ceremony.</p>
        </div>
        <div class="ed-timeline">
          <div v-for="(item, i) in data.timeline" :key="i" class="ed-timeline-item" :style="{ transitionDelay: `${i * 0.15}s` }" data-reveal="up">
            <div class="ed-timeline-dot"><div class="ed-timeline-glow"></div></div>
            <div class="ed-timeline-line" v-if="i < data.timeline.length - 1"></div>
            <div class="ed-timeline-content">
              <h4>{{ item.label }}</h4>
              <span>{{ item.date }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="data" class="ed-section-wrap" data-reveal="up">
      <div class="ed-container">
        <div class="ed-section-header">
          <span class="ed-section-badge">Gallery</span>
          <h2 class="ed-heading">Event Highlights</h2>
          <p class="ed-section-sub">Moments captured from our previous editions.</p>
        </div>
        <div class="ed-gallery-grid">
          <div v-for="(img, i) in data.galleryImages" :key="i" class="ed-gallery-item" :class="{ 'ed-gallery-span-2': i === 0 }">
            <div class="ed-gallery-img-wrap">
              <img :src="img" :alt="'Gallery ' + (i+1)" loading="lazy" />
              <div class="ed-gallery-overlay"><i class="bi bi-eye"></i></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="data" class="ed-cta-wrap" data-reveal="up">
      <div class="ed-container">
        <div class="ed-cta-box">
          <h2 class="ed-cta-title">Ready to Join?</h2>
          <p class="ed-cta-text">Secure your spot and be part of this amazing learning experience.</p>
          <div class="ed-cta-benefits">
            <div class="ed-benefit"><i class="bi bi-check-circle-fill"></i><span>{{ data.availableSeats }} Seats Remaining</span></div>
            <div class="ed-benefit" :class="{ 'text-danger': data.hasDeadlinePassed }"><i class="bi bi-check-circle-fill"></i><span>Registration {{ data.hasDeadlinePassed ? 'deadline has been passed' : 'Ends ' + data.registrationEndsIn }}</span></div>
            <div class="ed-benefit"><i class="bi bi-check-circle-fill"></i><span>Free Certificate</span></div>
            <div class="ed-benefit"><i class="bi bi-check-circle-fill"></i><span>Snacks Included</span></div>
          </div>
          <button class="ed-btn-register ed-btn-cta" @click="handleRegister">
            <i class="bi bi-check-circle me-2"></i>{{ isRegistered ? 'Registered ✓' : 'Register Now' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="similarEvents.length" class="ed-section-wrap ed-similar-wrap" data-reveal="up">
      <div class="ed-container">
        <div class="ed-section-header">
          <span class="ed-section-badge">More Events</span>
          <h2 class="ed-heading">Similar Events</h2>
          <p class="ed-section-sub">Check out other exciting events from the club.</p>
        </div>
        <div class="row g-4">
          <div v-for="sim in similarEvents" :key="sim.id" class="col-md-4">
            <div class="event-card glass" @click="openEvent(sim)">
              <div class="event-card-image" :style="{ backgroundImage: `url(${sim.image})` }">
                <div class="event-image-overlay">
                  <span class="event-date-badge">{{ sim.date }}</span>
                </div>
              </div>
              <div class="event-card-body">
                <h5 class="event-card-title">{{ sim.name }}</h5>
                <p class="event-card-desc">{{ sim.description }}</p>
              </div>
              <div class="event-card-footer">
                <span class="event-participants"><i class="bi bi-people-fill me-1"></i>{{ sim.participants }} seats</span>
                <div class="d-flex align-items-center gap-2">
                  <span class="event-status approved">{{ sim.status }}</span>
                  <button class="btn-register-sm" @click.stop="openEvent(sim)">Details</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <RegistrationModal v-if="showRegModal" :event="event" @close="showRegModal = false" @registered="onRegistered" />
    <CalendarPickerModal v-if="showCalendarModal" @close="showCalendarModal = false" @selected="triggerCalendarToast" />
    <VolunteerApplicationModal v-if="showVolModal" :event="event" @close="showVolModal = false" @submitted="onVolunteerApplied" />
    <div v-if="toast" class="ed-toast glass-toast"><i class="bi bi-check-circle-fill me-2" style="color: #4ade80;"></i>{{ toast }}</div>
    <div v-if="showCalendarToast" class="ed-toast glass-toast"><i class="bi bi-info-circle-fill me-2" style="color: #818cf8;"></i>{{ calendarToastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { store } from '../store/mockData';
import RegistrationModal from './RegistrationModal.vue';
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import VolunteerApplicationModal from './shared/VolunteerApplicationModal.vue';
import { useCalendarToast } from '../composables/useCalendarToast';

const route = useRoute();
const router = useRouter();
const toast = ref('');
const showRegModal = ref(false);
const showCalendarModal = ref(false);
const showVolModal = ref(false);

const { show: showCalendarToast, message: calendarToastMsg, showCalendarToast: triggerCalendarToast } = useCalendarToast();

const event = computed(() => store.events.find(e => e.name === decodeURIComponent(route.params.eventName)));

const data = computed(() => {
  const e = event.value;
  if (!e) return null;

  const category = e.category
    ? (e.category.charAt(0).toUpperCase() + e.category.slice(1))
    : (e.name.toLowerCase().includes('hackathon') ? 'Hackathon' : (e.name.toLowerCase().includes('seminar') ? 'Seminar' : 'Workshop'));

  // Live Agendas from Backend
  const liveAgendas = Array.isArray(e.agendas) && e.agendas.length > 0
    ? e.agendas.map(a => ({
        time: [a.start_time ? String(a.start_time).slice(0, 5) : '', a.end_time ? String(a.end_time).slice(0, 5) : ''].filter(Boolean).join(' - ') || 'TBD',
        title: a.title || 'Session',
        desc: a.description || ''
      }))
    : [
        { time: '09:00 AM', title: 'Registration & Check-in', desc: 'Participants arrive and verify registration.' },
        { time: '10:00 AM', title: 'Main Session', desc: e.description || 'Hands-on practical session.' },
        { time: '04:00 PM', title: 'Q&A and Closing', desc: 'Open floor for questions and closing remarks.' }
      ];

  // Live Additional Info from Backend
  const learningInfo = (e.additional_info || []).filter(i => i.section_type === 'learning').map(i => i.content);
  const requirementInfo = (e.additional_info || []).filter(i => i.section_type === 'requirement').map(i => i.content);
  const eligibilityInfo = (e.additional_info || []).filter(i => i.section_type === 'eligibility').map(i => i.content);

  const whatYouLearn = learningInfo.length > 0 ? learningInfo : [
    'Core concepts and industry best practices',
    'Hands-on experience with modern tools and technologies',
    'Real-world project deployment workflows',
  ];

  const requirements = requirementInfo.length > 0 ? requirementInfo : [
    'Basic programming fundamentals',
    'Laptop with development environment installed',
    'Enthusiasm to learn and build',
  ];

  const whoCanAttend = eligibilityInfo.length > 0 ? eligibilityInfo : [
    'All undergraduate and postgraduate students',
    'Open to all branches and departments',
  ];

  // Live Mentors from Backend
  const liveMentors = Array.isArray(e.mentors) && e.mentors.length > 0
    ? e.mentors.map(m => {
        const initials = m.name ? m.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'ME';
        return {
          name: m.name || 'Mentor',
          role: m.designation || 'Industry Expert',
          dept: m.company || 'Tech Partner',
          avatar: initials,
          linkedin: m.linkedin_url || '#',
          email: m.email || ''
        };
      })
    : [
        { name: 'Faculty Lead', role: 'Event Coordinator', dept: 'Engineering Department', avatar: 'FL', linkedin: '#', email: '' }
      ];

  return {
    ...e,
    category,
    image: e.cover_image_url || e.image || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop',
    tagline: e.short_description || e.tagline || `An immersive ${category.toLowerCase()} experience designed for college students to build real-world skills.`,
    fullDescription: e.description || `${e.name} is designed to provide participants with hands-on experience and deep industry insights.`,
    agenda: liveAgendas,
    whatYouLearn,
    requirements,
    whoCanAttend,
    speakers: liveMentors,
    timeline: [
      { label: 'Registration Opens', date: 'Upcoming' },
      { label: 'Registration Closes', date: e.deadline || e.date },
      { label: 'Event Date', date: e.date },
      { label: 'Main Sessions', date: e.date },
      { label: 'Closing Ceremony', date: e.date },
    ],
    galleryImages: [
      'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800&h=600&fit=crop',
    ],
    registrationEndsIn: (() => {
      if (!e.registration_deadline && !e.deadline) return 'N/A';
      const target = new Date(e.registration_deadline || e.deadline);
      const diff = Math.ceil((target - new Date()) / (1000 * 60 * 60 * 24));
      if (diff < 0) return 'Closed';
      if (diff === 0) return 'Today';
      return `${diff} days`;
    })(),
    availableSeats: Math.max(1, (e.max_participants || e.participants || 50) - Math.floor((e.max_participants || e.participants || 50) * 0.35)),
    registeredStudents: Math.min((e.max_participants || e.participants || 50) - 1, Math.floor((e.max_participants || e.participants || 50) * 0.35)),
    duration: '1 Day',
    organizedBy: 'Student Club Management',
    registrationFee: 'Free',
    contactPerson: liveMentors[0]?.name || 'Event Coordinator',
    hasDeadlinePassed: (e.registration_deadline || e.deadline) ? new Date(e.registration_deadline || e.deadline) < new Date() : false,
  };
});

const isRegistered = computed(() => data.value && store.registeredEvents.includes(data.value.id));
const canAddToCalendar = computed(() => {
  if (!data.value) return false;
  if (store.currentUserRole === 'club_admin') return data.value.status === 'Approved';
  return isRegistered.value || !data.value.hasDeadlinePassed;
});

const similarEvents = computed(() => {
  if (!event.value) return [];
  return store.events.filter(e => e.id !== event.value.id).slice(0, 3);
});

const goBack = () => { router.back(); };
const goHome = () => { router.push({ name: 'home' }); };
const openEvent = (ev) => { router.push({ name: 'event-details', params: { eventName: encodeURIComponent(ev.name) } }); window.scrollTo({ top: 0, behavior: 'smooth' }); };

const handleRegister = () => {
  if (!data.value) return;
  if (isRegistered.value) {
    toast.value = 'You are already registered for this event!';
    setTimeout(() => { toast.value = ''; }, 3000);
    return;
  }
  showRegModal.value = true;
};

const onRegistered = () => {
  showRegModal.value = false;
  toast.value = `Successfully registered for ${data.value?.name}!`;
  setTimeout(() => { toast.value = ''; }, 3000);
};

const onVolunteerApplied = () => {
  showVolModal.value = false;
  toast.value = 'Volunteer application submitted successfully. You\'ll be notified once the club reviews your request.';
  setTimeout(() => { toast.value = ''; }, 4000);
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
onMounted(() => {
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

.ed-agenda { position: relative; }
.ed-agenda-item {
  display: flex;
  gap: 1.25rem;
  padding-bottom: 1.75rem;
  position: relative;
}
.ed-agenda-item:last-child { padding-bottom: 0; }
.ed-agenda-time {
  min-width: 90px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #818cf8;
  padding-top: 0.15rem;
}
.ed-agenda-dot {
  position: relative;
  flex-shrink: 0;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: rgba(79, 70, 229, 0.3);
  border: 2px solid #818cf8;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ed-agenda-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #818cf8;
  box-shadow: 0 0 8px rgba(129, 140, 248, 0.6);
}
.ed-agenda-item:not(:last-child) .ed-agenda-dot::after {
  content: '';
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: 1.5px;
  height: calc(100% + 6px);
  background: linear-gradient(180deg, rgba(129, 140, 248, 0.3), transparent);
}
.ed-agenda-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.3rem;
}
.ed-agenda-info p {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
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
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.ed-speaker-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem;
  background: rgba(18, 27, 48, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 18px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
}
.ed-speaker-card:hover {
  transform: translateY(-6px);
  border-color: rgba(129, 140, 248, 0.2);
  background: rgba(22, 33, 55, 0.7);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(129, 140, 248, 0.05);
}
.ed-speaker-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.1rem;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
}
.ed-speaker-info { display: flex; flex-direction: column; min-width: 0; }
.ed-speaker-name {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.ed-speaker-role {
  font-size: 0.82rem;
  color: #818cf8;
  font-weight: 600;
  margin-bottom: 0.1rem;
}
.ed-speaker-dept {
  font-size: 0.78rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}
.ed-speaker-links {
  display: flex;
  gap: 0.5rem;
}
.ed-speaker-link {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.ed-speaker-link:hover {
  background: rgba(79, 70, 229, 0.15);
  border-color: rgba(79, 70, 229, 0.2);
  color: #818cf8;
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
}
</style>
