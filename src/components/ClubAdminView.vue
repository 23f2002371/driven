<template>
  <div class="club-admin">
    <div class="admin-bg">
      <div class="bg-glow glow-1"></div>
      <div class="bg-glow glow-2"></div>
    </div>

    <Sidebar :nav-items="navItems" :active-tab="currentTab" @update:active-tab="currentTab = $event" />

    <div class="main-wrapper">
      <nav class="top-navbar">
        <div class="navbar-left">
          <h5 class="navbar-title">{{ currentTabTitle }}</h5>
        </div>
        <div class="navbar-right">
          <button class="navbar-icon-btn" @click="currentTab = 'notifications'">
            <i class="bi bi-bell"></i>
            <span v-if="clubNotifCount > 0" class="navbar-badge">{{ clubNotifCount > 99 ? '99+' : clubNotifCount }}</span>
          </button>
          <span class="navbar-role">Club Lead</span>
          <div class="navbar-avatar">CA</div>
        </div>
      </nav>

      <main class="main-content">
        <div v-if="currentTab === 'dashboard'" class="pt-3">
          <div class="row g-4 mb-4">
            <div class="col-md-4">
              <div class="metric-card">
                <div class="metric-icon-wrap purple"><i class="bi bi-calendar-event-fill"></i></div>
                <div class="metric-body">
                  <span class="metric-label">Upcoming Events</span>
                  <div class="metric-value-row">
                    <span class="metric-value">{{ store.events.filter(e => e.status === 'Approved').length }}</span>
                    <span class="metric-trend up"><i class="bi bi-arrow-up-short"></i>+2</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="metric-card">
                <div class="metric-icon-wrap green"><i class="bi bi-box-seam-fill"></i></div>
                <div class="metric-body">
                  <span class="metric-label">Inventory Items</span>
                  <div class="metric-value-row">
                    <span class="metric-value">{{ totalInventory }}</span>
                    <span class="metric-trend up"><i class="bi bi-arrow-up-short"></i>+3</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="metric-card">
                <div class="metric-icon-wrap amber"><i class="bi bi-chat-dots-fill"></i></div>
                <div class="metric-body">
                  <span class="metric-label">Pending Tickets</span>
                  <div class="metric-value-row">
                    <span class="metric-value">{{ openTicketsCount }}</span>
                    <span class="metric-trend down"><i class="bi bi-arrow-down-short"></i>-1</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="action-buttons-container mb-4">
            <button class="btn-create-event" @click="currentTab = 'create_event'">
              <i class="bi bi-plus-lg me-2"></i>Create Event
            </button>
            <button class="btn-manage-inventory" @click="currentTab = 'inventory'">
              <i class="bi bi-box-seam me-2"></i>Manage Inventory
            </button>
          </div>

          <div class="events-section-card">
            <div class="events-header">
              <h5 class="events-title"><i class="bi bi-calendar-event me-2"></i>Recent Events</h5>
              <button class="events-view-all" @click="currentTab = 'events'">View all <i class="bi bi-chevron-right ms-1"></i></button>
            </div>
            <div class="events-list">
              <div v-for="event in store.events" :key="event.id" class="event-row" @click="openEventDetails(event)">
                <div class="event-thumb" :style="{ backgroundImage: `url(${event.image})` }">
                  <span class="event-badge">{{ event.name.includes('Workshop') ? 'Workshop' : event.name.includes('Hack') ? 'Hackathon' : event.name.includes('Bootcamp') ? 'Bootcamp' : event.name.includes('Seminar') ? 'Seminar' : 'Event' }}</span>
                </div>
                <div class="event-info">
                  <div class="event-name-row">
                    <h6 class="event-name">{{ event.name }}</h6>
                    <span class="event-status" :class="event.status === 'Approved' ? 'approved' : 'pending'">{{ event.status }}</span>
                  </div>
                  <div class="event-meta">
                    <span><i class="bi bi-geo-alt"></i>{{ event.venue }}</span>
                    <span><i class="bi bi-calendar3"></i>{{ event.date }}</span>
                    <span><i class="bi bi-people"></i>{{ event.participants }} registered</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="currentTab === 'events'" class="pt-3">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="fw-bold m-0 text-light">All Club Events</h5>
            <button class="btn-primary-premium btn-sm" @click="currentTab = 'create_event'"><i class="bi bi-plus-lg me-1"></i>New Event</button>
          </div>
          <CopilotRecommendation
            title="AI Recommendation"
            icon="stars"
            message="Seminar Hall is available this Friday. Perfect for a last-minute workshop."
            action="Switch Venue"
            class="mb-4"
          />
          <div class="row g-4">
            <div v-for="event in store.events" :key="event.id" class="col-md-6">
              <div class="card-glass p-0 h-100 d-flex flex-column event-card-hover overflow-hidden" @click="openEventDetails(event)" style="cursor:pointer;">
                <div class="event-card-img" :style="{ backgroundImage: `url(${event.image})` }">
                  <div class="event-img-overlay d-flex justify-content-between align-items-start p-3">
                    <span class="event-date-tag"><i class="bi bi-calendar3 me-1"></i>{{ event.date }}</span>
                    <span class="event-status" :class="event.status === 'Approved' ? 'approved' : 'pending'">{{ event.status }}</span>
                  </div>
                </div>
                <div class="p-3 d-flex flex-column flex-grow-1">
                  <h6 class="fw-bold text-light mb-1">{{ event.name }}</h6>
                  <p class="text-secondary small mb-2 flex-grow-1">{{ event.description }}</p>
                  <div class="event-meta">
                    <span><i class="bi bi-geo-alt-fill me-1"></i>{{ event.venue }}</span>
                    <span><i class="bi bi-people-fill me-1"></i>{{ event.participants }} Max</span>
                  </div>
                  <div class="d-flex align-items-center gap-2 mt-2">
                    <button class="btn-dashboard-primary btn-sm" @click.stop="openEventDetails(event)">View Details</button>
                    <button v-if="event.status === 'Approved'" class="btn-calendar-admin" title="Add to Calendar" @click.stop="openCalendarForEvent(event)">
                      <i class="bi bi-calendar-plus"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="currentTab === 'create_event'">
          <section class="ce-hero" ref="heroRef" @mousemove="onHeroMove" @mouseleave="onHeroLeave">
            <div class="ce-hero-bg"></div>
            <div class="ce-hero-inner">
              <div class="ce-hero-left">
                <div>
                  <h1 class="ce-page-title">Create Event</h1>
                  <p class="ce-page-sub">Bring your next workshop, hackathon, or seminar to life. Fill in the details below and preview your event in real time.</p>
                </div>
              </div>
              <div class="ce-hero-right" :style="sceneParallax">
                <div class="ce-ill-scene">
                  <div class="ce-ill-glow"></div>
                  <svg class="ce-ill-person" viewBox="0 0 60 100" fill="none">
                    <circle cx="30" cy="20" r="10" fill="rgba(255,255,255,0.06)"/>
                    <path d="M30 30c-10 0-18 6-18 20v6l8 3v28l10 5 10-5V59l8-3v-6c0-14-8-20-18-20z" fill="rgba(255,255,255,0.04)"/>
                    <path d="M14 48c6-6 16-8 16-8s4 0 16 8" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" fill="none"/>
                  </svg>
                  <div class="ce-ill-laptop">
                    <div class="ce-lid">
                      <div class="ce-screen">
                        <div class="ce-screen-top"><div class="ce-screen-dot"></div><div class="ce-screen-line w32"></div><div class="ce-screen-line w20"></div></div>
                        <div class="ce-screen-divider"></div>
                        <div class="ce-screen-body">
                          <div class="ce-sc-line"></div>
                          <div class="ce-sc-bar"><div class="ce-sc-fill"></div></div>
                          <div class="ce-sc-line short"></div>
                          <div class="ce-sc-grid">
                            <div class="ce-sc-col"><div class="ce-sc-cell"></div><div class="ce-sc-cell"></div></div>
                            <div class="ce-sc-col"><div class="ce-sc-cell"></div><div class="ce-sc-cell"></div></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="ce-base"></div>
                    <div class="ce-laptop-glow"></div>
                  </div>
                  <div class="ce-ill-holo">
                    <div class="ce-holo-inner">
                      <div class="ce-holo-icon"><div class="ce-holo-dot"></div><span>Event Dashboard</span></div>
                      <div class="ce-holo-row"><div class="ce-holo-label">Event</div><div class="ce-holo-val">IoT Workshop</div></div>
                      <div class="ce-holo-row"><div class="ce-holo-label">Date</div><div class="ce-holo-val">Jul 30</div></div>
                      <div class="ce-holo-divider"></div>
                      <div class="ce-holo-status"><div class="ce-holo-pulse"></div>Ready</div>
                    </div>
                    <div class="ce-holo-glow"></div>
                  </div>
                  <div class="ce-ill-card ce-ill-card-1">
                    <div class="ce-card-inner"><span class="ce-card-icon bi bi-calendar3"></span><span class="ce-card-text">Jul 30</span></div>
                  </div>
                  <div class="ce-ill-card ce-ill-card-2">
                    <div class="ce-card-inner"><span class="ce-card-icon bi bi-ticket"></span><span class="ce-card-text">50 seats</span></div>
                  </div>
                  <div class="ce-ill-card ce-ill-card-3">
                    <div class="ce-card-inner"><span class="ce-card-icon bi bi-people"></span><span class="ce-card-text">RSVP</span></div>
                  </div>
                  <div class="ce-ill-line ce-ill-line-1"></div>
                  <div class="ce-ill-line ce-ill-line-2"></div>
                  <div class="ce-ill-line ce-ill-line-3"></div>
                  <div class="ce-ill-particles">
                    <div v-for="i in 6" :key="i" class="ce-ill-p" :style="{ animationDelay: `${i * 0.6}s`, left: `${12 + i * 14}%`, top: `${20 + (i % 3) * 25}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <div class="ce-layout">
            <div class="ce-left">
              <section class="ce-section" data-idx="0">
                <div class="ce-section-head">
                  <h3>Event Information</h3>
                  <p>Give your event a name and choose a category.</p>
                </div>
                <div class="ce-field">
                  <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.name }">
                    <input v-model="formEvent.name" type="text" placeholder="e.g. IoT Workshop" />
                    <label>Event Name</label>
                  </div>
                </div>
                <div class="ce-field">
                  <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.tagline }">
                    <input v-model="formEvent.tagline" type="text" placeholder="e.g. Build real-world IoT solutions" />
                    <label>Short Description</label>
                  </div>
                  <span class="ce-helper">A short, catchy description that appears on the event card.</span>
                </div>
                <div class="ce-field">
                  <label class="ce-field-label">Category</label>
                  <div class="ce-chips">
                    <button v-for="cat in categories" :key="cat" class="ce-chip" :class="{ active: formEvent.category === cat }" @click="formEvent.category = cat">{{ cat }}</button>
                  </div>
                  <span class="ce-helper">Select the category that best fits your event.</span>
                </div>
              </section>

              <div class="ce-divider"></div>

              <section class="ce-section" data-idx="1">
                <div class="ce-section-head">
                  <h3>Date & Venue</h3>
                  <p>When and where is your event taking place?</p>
                </div>
                <div class="ce-row">
                  <div class="ce-field">
                    <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.date }">
                      <input v-model="formEvent.date" type="text" placeholder="e.g. Jul 30, 2026" />
                      <label>Date</label>
                    </div>
                  </div>
                  <div class="ce-field">
                    <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.time }">
                      <input v-model="formEvent.time" type="text" placeholder="e.g. 09:00 AM" />
                      <label>Time</label>
                    </div>
                  </div>
                </div>
                <div class="ce-field">
                  <div class="ce-input-wrap ce-select-wrap" :class="{ 'ce-has-value': formEvent.venue }">
                    <select v-model="formEvent.venue">
                      <option v-for="v in venues" :key="v" :value="v">{{ v }}</option>
                    </select>
                    <label>Venue</label>
                    <i class="bi bi-chevron-down ce-select-arrow"></i>
                  </div>
                </div>
              </section>

              <div class="ce-divider"></div>

              <section class="ce-section" data-idx="2">
                <div class="ce-section-head">
                  <h3>Registration Settings</h3>
                  <p>Configure capacity, deadlines, and visibility.</p>
                </div>
                <div class="ce-field">
                  <label class="ce-field-label">Expected Participants</label>
                  <div class="ce-stepper">
                    <button class="ce-step-btn" @click="formEvent.participants > 1 && formEvent.participants--" :disabled="formEvent.participants <= 1"><i class="bi bi-dash"></i></button>
                    <div class="ce-step-value">
                      <span class="ce-step-num">{{ formEvent.participants }}</span>
                      <span class="ce-step-unit">participants</span>
                    </div>
                    <button class="ce-step-btn" @click="formEvent.participants++" :disabled="formEvent.participants >= 500"><i class="bi bi-plus"></i></button>
                  </div>
                  <span class="ce-helper">Maximum capacity for this event.</span>
                </div>
                <div class="ce-field">
                  <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.deadline }">
                    <input v-model="formEvent.deadline" type="text" placeholder="e.g. Jul 28, 2026" />
                    <label>Registration Deadline</label>
                  </div>
                  <span class="ce-helper">Last date for participants to register.</span>
                </div>
              </section>

              <div class="ce-divider"></div>

              <section class="ce-section" data-idx="3">
                <div class="ce-section-head">
                  <h3>Description</h3>
                  <p>Tell attendees what your event is about.</p>
                </div>
                <div class="ce-field">
                  <div class="ce-textarea-wrap">
                    <textarea v-model="formEvent.description" rows="5" placeholder="Write a compelling description of your event. Include key takeaways, agenda highlights, and what participants will gain..." maxlength="500"></textarea>
                    <div class="ce-textarea-bottom">
                      <span class="ce-helper">Make it engaging to attract more participants.</span>
                      <span class="ce-char-count" :class="{ near: formEvent.description.length > 450 }">{{ formEvent.description.length }}/500</span>
                    </div>
                  </div>
                </div>
              </section>

              <div class="ce-divider"></div>

              <section class="ce-section" data-idx="4">
                <div class="ce-section-head">
                  <h3>Banner Image</h3>
                  <p>Upload a cover image for your event card.</p>
                </div>
                <div class="ce-field">
                  <div class="ce-upload-zone" @click="fileInput?.click()" @dragover.prevent @drop.prevent="handleDrop" :class="{ 'ce-has-banner': formEvent.bannerPreview }">
                    <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleFile" />
                    <template v-if="!formEvent.bannerPreview">
                      <div class="ce-upload-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                      <p class="ce-upload-text">Drag & drop banner or <span>Browse files</span></p>
                      <p class="ce-upload-hint">PNG, JPG, WebP &middot; Max 5MB</p>
                    </template>
                    <template v-else>
                      <img :src="formEvent.bannerPreview" alt="Banner preview" class="ce-banner-img" />
                      <button class="ce-banner-remove" @click.stop="removeBanner" title="Remove"><i class="bi bi-x-lg"></i></button>
                    </template>
                  </div>
                </div>
              </section>
            </div>

            <div class="ce-right">
              <div class="ce-sidebar">
                <div class="ce-preview-card glass">
                  <div class="ce-preview-img" :style="{ backgroundImage: `url(${previewImage})` }">
                    <div class="ce-preview-img-overlay">
                      <span class="ce-preview-date-tag"><i class="bi bi-calendar3 me-1"></i>{{ formEvent.date || 'Select Date' }}</span>
                    </div>
                  </div>
                  <div class="ce-preview-body">
                    <span class="ce-preview-cat">{{ formEvent.category }}</span>
                    <h4 class="ce-preview-title">{{ formEvent.name || 'Event Title' }}</h4>
                    <p v-if="formEvent.tagline" class="ce-preview-tagline">{{ formEvent.tagline }}</p>
                    <p class="ce-preview-desc">{{ formEvent.description ? (formEvent.description.length > 80 ? formEvent.description.slice(0, 80) + '...' : formEvent.description) : 'Your event description will appear here.' }}</p>
                  </div>
                  <div class="ce-preview-footer">
                    <span class="ce-preview-meta"><i class="bi bi-people-fill me-1"></i>{{ formEvent.participants }} seats</span>
                    <span class="ce-preview-status">{{ formEvent.name ? 'Draft' : 'Not Saved' }}</span>
                  </div>
                </div>

                <div class="ce-summary glass">
                  <h5 class="ce-summary-title">Event Summary</h5>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-tag me-2"></i>Category</span><span class="ce-summary-val">{{ formEvent.category }}</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-people me-2"></i>Participants</span><span class="ce-summary-val">{{ formEvent.participants }}</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-flag me-2"></i>Status</span><span class="ce-summary-val"><span class="ce-badge-draft">Draft</span></span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-eye me-2"></i>Visibility</span><span class="ce-summary-val">Public</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-person me-2"></i>Organizer</span><span class="ce-summary-val">Club Lead</span></div>
                  <div class="ce-summary-divider"></div>
                  <div class="ce-summary-save"><i class="bi bi-check-circle-fill"></i><span>Auto-save active</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="ce-action-bar glass">
            <div class="ce-action-left"><i class="bi bi-check-circle-fill" style="color: #4ade80;"></i><span>Draft saved</span></div>
            <div class="ce-action-right">
              <button class="ce-btn-secondary" @click="saveDraft"><i class="bi bi-archive me-2"></i>Save Draft</button>
              <button class="ce-btn-primary" @click="submitNewEvent">Submit for Approval <i class="bi bi-arrow-right ms-2"></i></button>
            </div>
          </div>
        </div>

        <div v-else-if="currentTab === 'inventory'" class="pt-3">
          <CopilotRecommendation
            title="AI Alert"
            icon="exclamation-triangle-fill"
            message="Only 3 Arduino Uno boards remaining. Current stock may not last the week."
            action="Generate Procurement"
            class="mb-3"
          />
          <InventoryGrid :items="store.inventory" :is-admin="true" @borrow="borrowItem" @add-item="addNewInventoryItem" @add-stock="addStock" />
        </div>

        <div v-else-if="currentTab === 'support'" class="pt-3">
          <CopilotRecommendation
            title="AI Analysis"
            icon="search-heart-fill"
            message="Found 3 similar resolved issues that match this ticket description."
            action="View Similar"
            class="mb-3"
          />
          <SupportDesk :tickets="store.tickets" @reply="handleReply" @resolve="handleResolve" />
        </div>

        <div v-else-if="currentTab === 'bounties'" class="pt-3">
          <CampusBountyAdmin />
        </div>

        <div v-else-if="currentTab === 'notifications'" class="notifications-page">
          <div class="notifications-header">
            <div>
              <h2 class="notifications-title"><i class="bi bi-bell-fill"></i>Notifications</h2>
              <span class="notifications-count">{{ clubNotifs.length }} notification{{ clubNotifs.length !== 1 ? 's' : '' }}</span>
            </div>
            <button class="notifications-clear" @click="store.clearNotifsForRole('club_admin')" v-if="clubNotifs.length">Clear all</button>
          </div>
          <div v-if="clubNotifs.length === 0" class="notifications-empty">
            <i class="bi bi-bell-slash"></i>
            <span>No notifications yet</span>
          </div>
          <div v-else class="notifications-list">
            <button v-for="n in clubNotifs" :key="n.id" type="button" class="notification-card" :class="{ unread: !n.read }" @click="store.markNotifRead(n.id)">
              <span class="notification-icon" :style="{ background: n.color + '18', color: n.color }">
                <i :class="'bi bi-' + n.icon"></i>
              </span>
              <span class="notification-body">
                <strong>{{ n.message }}</strong>
                <small>{{ n.timestamp }}</small>
              </span>
              <span v-if="!n.read" class="notification-dot"></span>
            </button>
          </div>
        </div>
      </main>
      </div>
    </div>
    <CalendarPickerModal v-if="showCalendarModal" @close="showCalendarModal = false" @selected="triggerCalendarToast" />
    <div v-if="showCalendarToast" class="ca-toast"><i class="bi bi-info-circle-fill me-2" style="color:#818cf8;"></i>{{ calendarToastMsg }}</div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store/mockData';
import Sidebar from './shared/Sidebar.vue';
import InventoryGrid from './shared/InventoryGrid.vue';
import SupportDesk from './shared/SupportDesk.vue';
import CopilotRecommendation from './shared/CopilotRecommendation.vue';
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import CampusBountyAdmin from './CampusBountyAdmin.vue';
import { useCalendarToast } from '../composables/useCalendarToast';

const router = useRouter();
const { show: showCalendarToast, message: calendarToastMsg, showCalendarToast: triggerCalendarToast } = useCalendarToast();
const showCalendarModal = ref(false);
const calendarEventTarget = ref(null);
const openCalendarForEvent = (event) => {
  calendarEventTarget.value = event;
  showCalendarModal.value = true;
};

const currentTab = ref('dashboard');

const currentTabTitle = computed(() => {
  switch (currentTab.value) {
    case 'dashboard': return 'Dashboard';
    case 'events': return 'All Club Events';
    case 'create_event': return 'Create New Event';
    case 'inventory': return 'Inventory Management';
    case 'support': return 'Support Desk';
    case 'bounties': return 'Campus Bounties';
    case 'notifications': return 'Notifications';
    default: return 'Club Admin';
  }
});

const clubNotifs = computed(() => store.notifications.filter(n => n.role === 'club_admin'));
const clubNotifCount = computed(() => clubNotifs.value.filter(n => !n.read).length);

const categories = ['Workshop', 'Hackathon', 'Seminar', 'Competition', 'Bootcamp', 'Webinar'];
const venues = ['Lab A', 'Lab B', 'Auditorium', 'Seminar Hall', 'Innovation Lab', 'Robotics Lab'];
const fileInput = ref(null);

const formEvent = reactive({ name: '', tagline: '', category: 'Workshop', venue: 'Lab A', date: '', time: '09:00 AM', participants: 50, description: '', deadline: '', bannerPreview: null });

const defaultBanner = 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop';
const previewImage = computed(() => formEvent.bannerPreview || defaultBanner);

const handleFile = (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => { formEvent.bannerPreview = ev.target?.result || null; };
  reader.readAsDataURL(file);
};
const handleDrop = (e) => {
  const file = e.dataTransfer?.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => { formEvent.bannerPreview = ev.target?.result || null; };
  reader.readAsDataURL(file);
};
const removeBanner = () => { formEvent.bannerPreview = null; };
const saveDraft = () => { /* auto-save in demo */ };

const navItems = computed(() => [
  { label: 'Dashboard', icon: 'bar-chart-fill', key: 'dashboard' },
  { label: 'Events', icon: 'calendar-event-fill', key: 'events' },
  { label: 'Create Event', icon: 'plus-circle-fill', key: 'create_event' },
  { label: 'Campus Bounties', icon: 'briefcase-fill', key: 'bounties' },
  { label: 'Inventory', icon: 'box-seam-fill', key: 'inventory' },
  { label: 'Support Desk', icon: 'chat-dots-fill', key: 'support' },
]);

const totalInventory = computed(() => store.inventory.reduce((acc, item) => acc + item.available + item.borrowed, 0));
const openTicketsCount = computed(() => store.tickets.filter(t => t.status === 'Open').length);
const borrowedItems = computed(() => store.inventory.filter(i => i.borrowed > 0));
const openEventDetails = (event) => { router.push({ name: 'event-details', params: { eventName: encodeURIComponent(event.name) } }); };

/* ── Hero 3D Parallax ── */
const heroRef = ref(null);
const mouse = reactive({ x: 0, y: 0 });
const onHeroMove = (e) => {
  const r = heroRef.value.getBoundingClientRect();
  mouse.x = ((e.clientX - r.left) / r.width - 0.5) * 2;
  mouse.y = ((e.clientY - r.top) / r.height - 0.5) * 2;
};
const onHeroLeave = () => { mouse.x = 0; mouse.y = 0; };
const sceneParallax = computed(() => ({
  transform: `translateX(${mouse.x * 8}px) translateY(${mouse.y * 6}px)`
}));

const submitNewEvent = () => {
  if (!formEvent.name || !formEvent.date || !formEvent.description) return;
  store.addEvent({ name: formEvent.name, tagline: formEvent.tagline, category: formEvent.category, venue: formEvent.venue, date: formEvent.date, deadline: formEvent.deadline, participants: formEvent.participants, description: formEvent.description });
  Object.assign(formEvent, { name: '', tagline: '', date: '', time: '09:00 AM', description: '', deadline: '', bannerPreview: null, participants: 50, category: 'Workshop', venue: 'Lab A' });
  currentTab.value = 'events';
};
const addNewInventoryItem = (item) => {
  store.inventory.push(item);
};
const borrowItem = (item) => store.borrowItem(item.id);
const addStock = (item, qty = 1) => store.increaseItemQuantity(item.id, qty);
const returnItem = (item) => store.returnItem(item.id);
const handleReply = ({ ticket, text, resolve }) => {
  store.resolveTicket(ticket.id, text);
};
const handleResolve = (ticket) => {
  store.resolveTicket(ticket.id, '');
};
</script>

<style scoped>
.club-admin {
  display: flex;
  min-height: 100vh;
  background: #070b16;
  overflow-x: hidden;
}

/* ── Background ── */
.admin-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: #070b16;
}
.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  animation: glowDrift 25s ease-in-out infinite;
}
.glow-1 {
  width: 500px; height: 500px;
  top: -15%; left: -8%;
  background: radial-gradient(circle, rgba(109,93,246,0.1) 0%, transparent 70%);
}
.glow-2 {
  width: 400px; height: 400px;
  bottom: -10%; right: -5%;
  background: radial-gradient(circle, rgba(139,92,246,0.07) 0%, transparent 70%);
  animation-delay: -12s;
}
@keyframes glowDrift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(40px, -30px) scale(1.05); }
}

/* ── Main Wrapper ── */
.main-wrapper {
  margin-left: 240px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* ── Top Navbar ── */
.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 70px;
  background: rgba(11, 17, 31, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: -0.2px;
}
.navbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.navbar-icon-btn {
  position: relative;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8892a8;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}
.navbar-icon-btn:hover {
  background: rgba(255,255,255,0.08);
  color: #e2e8f0;
  border-color: rgba(255,255,255,0.15);
}
.navbar-dot {
  position: absolute;
  top: 6px; right: 6px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #fb7185;
  border: 1.5px solid #090B16;
}
.navbar-badge {
  position: absolute;
  top: -4px; right: -4px;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #fb7185;
  border: 2px solid #090B16;
  color: #fff;
  font-size: 0.55rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
  line-height: 1;
}
.navbar-role {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  background: rgba(109,93,246,0.1);
  color: #a5b4fc;
  border: 1px solid rgba(109,93,246,0.12);
}
.navbar-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6D5DF6, #8B5CF6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.65rem;
  box-shadow: 0 2px 6px rgba(109,93,246,0.3);
}

/* ── Main Content ── */
.main-content {
  padding: 0 2rem;
  flex: 1;
  margin-left: 0;
}

/* ── Metric Cards ── */
.metric-card {
  background: rgba(18, 27, 48, 0.65);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 1.25rem;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  display: flex;
  align-items: flex-start;
  gap: 2rem;
}
.metric-card:hover {
  transform: translateY(-3px);
  border-color: rgba(129,140,248,0.2);
  box-shadow: 0 8px 30px rgba(0,0,0,0.3);
  background: rgba(22, 33, 55, 0.7);
}
.metric-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}
.metric-icon-wrap.purple {
  background: linear-gradient(135deg, rgba(109,93,246,0.2), rgba(139,92,246,0.1));
  color: #818cf8;
  box-shadow: 0 4px 12px rgba(109,93,246,0.15);
}
.metric-icon-wrap.green {
  background: linear-gradient(135deg, rgba(52,211,153,0.2), rgba(16,185,129,0.1));
  color: #34d399;
  box-shadow: 0 4px 12px rgba(52,211,153,0.15);
}
.metric-icon-wrap.amber {
  background: linear-gradient(135deg, rgba(251,191,36,0.2), rgba(245,158,11,0.1));
  color: #fbbf24;
  box-shadow: 0 4px 12px rgba(251,191,36,0.15);
}
.metric-body { flex: 1; min-width: 0; }
.metric-label {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 0.85rem;
  letter-spacing: 0.2px;
}
.metric-value-row {
  display: flex;
  align-items: baseline;
  gap: 0.85rem;
}
.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -1px;
  line-height: 1;
}
.metric-trend {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  line-height: 1.3;
}
.metric-trend.up { background: rgba(52,211,153,0.1); color: #34d399; }
.metric-trend.down { background: rgba(244,63,94,0.1); color: #fb7185; }

/* ── Dashboard Action Buttons ── */
.action-buttons-container {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  gap: 1.25rem !important;
  margin-top: 4rem !important;
  margin-bottom: 2.5rem !important;
  position: relative !important;
  z-index: 10 !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.btn-create-event {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0.75rem 1.6rem !important;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  color: #ffffff !important;
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  border: 1px solid rgba(165, 180, 252, 0.5) !important;
  border-radius: 12px !important;
  cursor: pointer !important;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.btn-create-event:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
}

.btn-manage-inventory {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0.75rem 1.6rem !important;
  background: rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 12px !important;
  cursor: pointer !important;
  backdrop-filter: blur(10px) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.btn-manage-inventory:hover {
  transform: translateY(-2px) !important;
  background: rgba(255, 255, 255, 0.18) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.2) !important;
}

/* ── Buttons ── */
.btn-primary-premium {
  display: inline-flex !important;
  align-items: center !important;
  padding: 0.55rem 1.25rem !important;
  border: none !important;
  border-radius: 10px !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  color: #fff !important;
  background: linear-gradient(135deg, #6D5DF6, #8B5CF6) !important;
  cursor: pointer !important;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  box-shadow: 0 4px 16px rgba(109,93,246,0.25) !important;
  opacity: 1 !important;
}
.btn-primary-premium:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(109,93,246,0.35) !important;
}
.btn-primary-premium:active { transform: translateY(0); }
.btn-primary-premium.btn-sm { padding: 0.4rem 1rem; font-size: 0.8rem; }
.btn-secondary-premium {
  display: inline-flex !important;
  align-items: center !important;
  padding: 0.55rem 1.25rem !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  border-radius: 10px !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  color: #e2e8f0 !important;
  background: rgba(255,255,255,0.06) !important;
  cursor: pointer !important;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  opacity: 1 !important;
}
.btn-secondary-premium:hover {
  background: rgba(255,255,255,0.12) !important;
  border-color: rgba(255,255,255,0.25) !important;
  color: #f1f5f9 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.btn-secondary-premium.btn-sm { padding: 0.4rem 1rem; font-size: 0.8rem; }
/* ── Events Section ── */
.events-section-card {
  background: rgba(18, 27, 48, 0.55);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px;
  overflow: hidden;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  transition: border-color 0.3s;
}
.events-section-card:hover { border-color: rgba(129,140,248,0.15); }
.events-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.events-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: 0.2px;
}
.events-title i { color: #818cf8; }
.events-view-all {
  background: none;
  border: none;
  color: #8892a8;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
}
.events-view-all:hover { color: #a5b4fc; }
.events-list { padding: 0.5rem; display: flex; flex-direction: column; gap: 1rem; }
.event-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.6rem 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.1s ease;
}
.event-row:hover {
  background: rgba(255,255,255,0.05);
  border-color: rgba(129,140,248,0.15);
}
.event-thumb {
  width: 70px;
  height: 70px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.event-badge {
  position: absolute;
  bottom: 3px; left: 3px;
  font-size: 0.45rem;
  font-weight: 700;
  padding: 0.12rem 0.28rem;
  border-radius: 4px;
  background: rgba(0,0,0,0.7);
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.event-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.25rem; }
.event-name-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.event-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.event-status {
  font-size: 0.5rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.2px;
  white-space: nowrap;
  flex-shrink: 0;
}
.event-status.approved { background: rgba(52,211,153,0.12); color: #34d399; font-size: 0.5rem; font-weight: 600; padding: 0.1rem 0.4rem; }
.event-status.pending { background: rgba(251,191,36,0.12); color: #fbbf24; font-size: 0.5rem; font-weight: 600; padding: 0.1rem 0.4rem; }
.event-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.68rem;
  color: #8892a8;
}
.event-meta span { display: flex; align-items: center; gap: 0.25rem; }
.event-meta span i { font-size: 0.7rem; color: #64748b; }

/* ── Tab Content ── */
.main-content { animation: fadeIn 0.3s ease; }
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ═══════════════════════════════════════════
   CREATE EVENT — Premium Landing Hero
   ═══════════════════════════════════════════ */
.ce-hero {
  position: relative;
  margin-bottom: 1rem;
  padding: 0 0 0.5rem;
  overflow: hidden;
}
.ce-hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 500px 350px at 78% 50%, rgba(129,140,248,0.07) 0%, transparent 65%),
    radial-gradient(ellipse 250px 250px at 65% 90%, rgba(99,102,241,0.04) 0%, transparent 70%);
}
.ce-hero-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
  position: relative;
  z-index: 1;
}
.ce-hero-left {
  flex: 1;
  max-width: 580px;
}
.ce-hero-right {
  position: relative;
  flex-shrink: 0;
  width: 340px;
  height: 220px;
  will-change: transform;
  transition: transform 0.15s ease-out;
}
.ce-page-title {
  font-size: 2rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.8px;
  margin: 0 0 0.5rem;
  line-height: 1.15;
}
.ce-page-sub {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0;
  max-width: 480px;
  line-height: 1.6;
}

/* ── Illustration Scene ── */
.ce-ill-scene {
  position: absolute;
  inset: 0;
  perspective: 600px;
}
.ce-ill-glow {
  position: absolute;
  top: 20%; left: 15%;
  width: 240px; height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(129,140,248,0.12) 0%, transparent 70%);
  filter: blur(40px);
  pointer-events: none;
  animation: illPulse 6s ease-in-out infinite;
}
@keyframes illPulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

/* ── Developer Silhouette ── */
.ce-ill-person {
  position: absolute;
  left: 6%; bottom: -2%;
  width: 48px;
  height: auto;
  opacity: 0.5;
  animation: illFloat 7s ease-in-out infinite;
}

/* ── Laptop ── */
.ce-ill-laptop {
  position: absolute;
  left: 18%; bottom: 6%;
  width: 100px;
  height: 68px;
  animation: illFloat 7s ease-in-out infinite 0.3s;
}
.ce-lid {
  width: 100px; height: 52px;
  background: linear-gradient(145deg, rgba(30,41,59,0.85), rgba(15,23,42,0.95));
  border-radius: 6px 6px 0 0;
  border: 1px solid rgba(255,255,255,0.06);
  border-bottom: none;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  position: relative;
  overflow: hidden;
  transform: rotateX(4deg);
  transform-origin: bottom;
}
.ce-screen {
  position: absolute;
  inset: 4px;
  border-radius: 3px;
  background: rgba(15,23,42,0.9);
  overflow: hidden;
  padding: 6px 5px;
}
.ce-screen-top { display: flex; align-items: center; gap: 4px; margin-bottom: 5px; }
.ce-screen-dot { width: 3px; height: 3px; border-radius: 50%; background: rgba(129,140,248,0.4); flex-shrink: 0; }
.ce-screen-line { height: 2px; border-radius: 1px; background: rgba(255,255,255,0.06); }
.w32 { width: 32px; }
.w20 { width: 20px; }
.ce-screen-divider { height: 1px; background: rgba(255,255,255,0.04); margin-bottom: 5px; }
.ce-screen-body { }
.ce-sc-line { height: 2px; border-radius: 1px; background: rgba(129,140,248,0.12); margin-bottom: 4px; width: 60px; }
.ce-sc-line.short { width: 36px; }
.ce-sc-bar { height: 4px; border-radius: 2px; background: rgba(255,255,255,0.04); margin-bottom: 5px; width: 70px; overflow: hidden; }
.ce-sc-fill { height: 100%; width: 55%; border-radius: 2px; background: linear-gradient(90deg, #818cf8, #6366f1); }
.ce-sc-grid { display: flex; gap: 6px; margin-top: 5px; }
.ce-sc-col { display: flex; flex-direction: column; gap: 3px; }
.ce-sc-cell { width: 12px; height: 8px; border-radius: 1px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.04); }
.ce-base {
  width: 112px; height: 6px;
  background: linear-gradient(145deg, rgba(30,41,59,0.7), rgba(15,23,42,0.8));
  border-radius: 0 0 3px 3px;
  margin: 0 auto;
  margin-left: -5px;
  border: 1px solid rgba(255,255,255,0.05);
  border-top: none;
  transform: rotateX(3deg);
  transform-origin: top;
}
.ce-laptop-glow {
  position: absolute;
  top: 40%; left: 10%;
  width: 80px; height: 40px;
  background: radial-gradient(ellipse, rgba(129,140,248,0.08) 0%, transparent 70%);
  filter: blur(15px);
  pointer-events: none;
}

/* ── Holographic Dashboard ── */
.ce-ill-holo {
  position: absolute;
  top: 10%; right: 6%;
  width: 108px;
  animation: illFloat 8s ease-in-out infinite 0.8s;
  z-index: 2;
}
.ce-holo-inner {
  background: rgba(15,23,42,0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(129,140,248,0.1);
  border-radius: 10px;
  padding: 8px 10px;
  box-shadow:
    0 8px 32px rgba(0,0,0,0.25),
    inset 0 1px 0 rgba(255,255,255,0.06);
}
.ce-holo-icon { display: flex; align-items: center; gap: 5px; margin-bottom: 6px; font-size: 0.55rem; color: #818cf8; font-weight: 600; letter-spacing: 0.3px; }
.ce-holo-dot { width: 5px; height: 5px; border-radius: 50%; background: #818cf8; box-shadow: 0 0 6px rgba(129,140,248,0.5); }
.ce-holo-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; }
.ce-holo-label { font-size: 0.5rem; color: #64748b; }
.ce-holo-val { font-size: 0.55rem; color: #e2e8f0; font-weight: 600; }
.ce-holo-divider { height: 1px; background: rgba(255,255,255,0.04); margin: 4px 0; }
.ce-holo-status { display: flex; align-items: center; gap: 4px; font-size: 0.5rem; color: #34d399; }
.ce-holo-pulse { width: 4px; height: 4px; border-radius: 50%; background: #34d399; animation: illPulse 2s ease-in-out infinite; }
.ce-holo-glow {
  position: absolute;
  top: 10%; left: 20%;
  width: 60px; height: 50px;
  background: radial-gradient(ellipse, rgba(129,140,248,0.08) 0%, transparent 70%);
  filter: blur(20px);
  pointer-events: none;
}

/* ── Small Glass Cards ── */
.ce-ill-card {
  position: absolute;
  background: rgba(15,23,42,0.35);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.ce-card-inner {
  display: flex; align-items: center; gap: 4px; padding: 5px 8px;
}
.ce-card-icon { font-size: 0.6rem; color: #818cf8; }
.ce-card-text { font-size: 0.55rem; color: #cbd5e1; font-weight: 500; white-space: nowrap; }
.ce-ill-card-1 {
  top: 30%; left: 2%;
  animation: illFloat 7.5s ease-in-out infinite 1.2s;
  z-index: 3;
}
.ce-ill-card-2 {
  bottom: 24%; right: 2%;
  animation: illFloat 6.5s ease-in-out infinite 2s;
  z-index: 3;
}
.ce-ill-card-3 {
  top: 48%; left: 14%;
  animation: illFloat 8.5s ease-in-out infinite 0.5s;
  z-index: 1;
}

/* ── Connection Lines ── */
.ce-ill-line {
  position: absolute;
  pointer-events: none;
  opacity: 0.25;
}
.ce-ill-line-1 {
  top: 45%; left: 22%;
  width: 40px; height: 1px;
  background: linear-gradient(90deg, rgba(129,140,248,0.4), transparent);
  transform: rotate(-20deg);
  transform-origin: left;
}
.ce-ill-line-2 {
  top: 55%; right: 30%;
  width: 30px; height: 1px;
  background: linear-gradient(270deg, rgba(129,140,248,0.3), transparent);
  transform: rotate(15deg);
  transform-origin: right;
}
.ce-ill-line-3 {
  top: 32%; left: 32%;
  width: 25px; height: 1px;
  background: linear-gradient(90deg, rgba(129,140,248,0.2), transparent);
  transform: rotate(45deg);
  transform-origin: left;
}

/* ── Particles ── */
.ce-ill-particles { position: absolute; inset: 0; pointer-events: none; }
.ce-ill-p {
  position: absolute;
  width: 3px; height: 3px;
  border-radius: 50%;
  background: rgba(129,140,248,0.25);
  animation: illDrift 8s ease-in-out infinite;
}
@keyframes illDrift {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.15; }
  50% { transform: translateY(-16px) scale(1.3); opacity: 0.4; }
}
@keyframes illFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

/* ── 2-Column Layout ── */
.ce-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 2.5rem;
  align-items: start;
}
.ce-left { min-width: 0; }
.ce-right { position: sticky; top: 5rem; }

/* ── Form Sections ── */
.ce-section {
  animation: ceFadeUp 0.5s ease both;
}
.ce-section:nth-child(1) { animation-delay: 0s; }
.ce-section:nth-child(2) { animation-delay: 0.08s; }
.ce-section:nth-child(3) { animation-delay: 0.16s; }
.ce-section:nth-child(4) { animation-delay: 0.24s; }
.ce-section:nth-child(5) { animation-delay: 0.32s; }

@keyframes ceFadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.ce-section-head { margin-bottom: 1.25rem; }
.ce-section-head h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.3rem;
  letter-spacing: -0.3px;
}
.ce-section-head p {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.ce-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0.06), transparent);
  margin: 2rem 0;
}

/* ── Floating Label Inputs ── */
.ce-field { margin-bottom: 1.25rem; }
.ce-field:last-child { margin-bottom: 0; }
.ce-field-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin-bottom: 0.6rem;
}
.ce-helper {
  display: block;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.4);
  margin-top: 0.4rem;
}
.ce-input-wrap {
  position: relative;
  min-height: 56px;
}
.ce-input-wrap input,
.ce-input-wrap select {
  width: 100%;
  min-height: 56px;
  padding: 1.5rem 1rem 0.85rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1.5px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  color: rgba(255,255,255,0.95);
  font-size: 0.92rem;
  font-family: inherit;
  line-height: 1.4;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  outline: none;
  box-sizing: border-box;
}
.ce-input-wrap select {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  padding-right: 2.5rem;
  line-height: 1.3;
}
.ce-input-wrap input:focus,
.ce-input-wrap select:focus {
  border-color: rgba(129, 140, 248, 0.4);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.08), 0 4px 20px rgba(0,0,0,0.1);
}
.ce-input-wrap input::placeholder,
.ce-input-wrap select::placeholder {
  color: transparent;
}
.ce-input-wrap label {
  position: absolute;
  top: 50%;
  left: 1rem;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: #64748b;
  transition: all 0.2s cubic-bezier(0.4,0,0.2,1);
  pointer-events: none;
  transform-origin: left top;
}
.ce-input-wrap.ce-has-value label,
.ce-input-wrap input:focus + label,
.ce-input-wrap select:focus + label {
  top: 0.35rem;
  transform: translateY(0) scale(0.72);
  color: #818cf8;
}
.ce-select-arrow {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
  font-size: 0.8rem;
}

.ce-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* ── Category Chips ── */
.ce-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.ce-chip {
  padding: 0.45rem 1.1rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1.5px solid rgba(255, 255, 255, 0.07);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.ce-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  transform: translateY(-1px);
}
.ce-chip.active {
  background: rgba(129, 140, 248, 0.15);
  border-color: rgba(129, 140, 248, 0.35);
  color: #a5b4fc;
  box-shadow: 0 0 20px rgba(129, 140, 248, 0.08);
}

/* ── Number Stepper ── */
.ce-stepper {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 1.25rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1.5px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  max-width: 280px;
}
.ce-step-btn {
  width: 42px; height: 42px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.ce-step-btn:hover:not(:disabled) {
  background: rgba(129, 140, 248, 0.12);
  border-color: rgba(129, 140, 248, 0.2);
  color: #a5b4fc;
}
.ce-step-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.ce-step-value {
  flex: 1;
  text-align: center;
}
.ce-step-num {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.1;
}
.ce-step-unit {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 500;
}

/* ── Textarea ── */
.ce-textarea-wrap textarea {
  width: 100%;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1.5px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  color: rgba(255,255,255,0.95);
  font-size: 0.9rem;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  outline: none;
  min-height: 120px;
}
.ce-textarea-wrap textarea:focus {
  border-color: rgba(129, 140, 248, 0.4);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.08);
}
.ce-textarea-wrap textarea::placeholder {
  color: rgba(255,255,255,0.5);
}
.ce-textarea-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.4rem;
}
.ce-char-count {
  font-size: 0.75rem;
  color: #475569;
  font-weight: 500;
  transition: color 0.2s;
}
.ce-char-count.near { color: #fbbf24; }

/* ── Banner Upload Zone ── */
.ce-upload-zone {
  position: relative;
  border: 2px dashed rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 2.5rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  background: rgba(15, 23, 42, 0.3);
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ce-upload-zone:hover {
  border-color: rgba(129, 140, 248, 0.25);
  background: rgba(15, 23, 42, 0.5);
  transform: scale(1.01);
}
.ce-upload-zone.ce-has-banner {
  padding: 0.5rem;
  border-style: solid;
  border-color: rgba(129, 140, 248, 0.2);
  background: rgba(15, 23, 42, 0.5);
}
.ce-upload-icon {
  font-size: 2.5rem;
  color: #818cf8;
  margin-bottom: 0.75rem;
}
.ce-upload-text {
  font-size: 0.95rem;
  color: #94a3b8;
  margin: 0 0 0.3rem;
  font-weight: 500;
}
.ce-upload-text span {
  color: #818cf8;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.ce-upload-hint {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.4);
  margin: 0;
}
.ce-banner-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 10px;
  display: block;
}
.ce-banner-remove {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 32px; height: 32px;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}
.ce-banner-remove:hover {
  background: rgba(239, 68, 68, 0.6);
  transform: scale(1.1);
}

/* ── Sticky Sidebar ── */
.ce-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Preview Card */
.ce-preview-card {
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  border: 1.5px solid rgba(255, 255, 255, 0.06);
  border-radius: 18px;
  overflow: hidden;
  transition: all 0.3s;
}
.ce-preview-card:hover {
  border-color: rgba(129, 140, 248, 0.15);
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.ce-preview-img {
  height: 140px;
  background-size: cover;
  background-position: center;
  position: relative;
}
.ce-preview-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7,11,20,0.2), rgba(7,11,20,0.7));
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 0.75rem;
}
.ce-preview-date-tag {
  background: rgba(79, 70, 229, 0.2);
  color: #a5b4fc;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  backdrop-filter: blur(4px);
}
.ce-preview-body {
  padding: 1rem 1.25rem;
}
.ce-preview-cat {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.15);
  color: #a5b4fc;
  margin-bottom: 0.5rem;
}
.ce-preview-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.ce-preview-tagline {
  font-size: 0.78rem;
  color: #818cf8;
  margin: 0 0 0.35rem;
  line-height: 1.3;
  font-weight: 500;
}
.ce-preview-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}
.ce-preview-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border-top: 1px solid rgba(255,255,255,0.04);
}
.ce-preview-meta {
  font-size: 0.75rem;
  color: #64748b;
}
.ce-preview-status {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
}

/* Summary Card */
.ce-summary {
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  border: 1.5px solid rgba(255, 255, 255, 0.06);
  border-radius: 18px;
  padding: 1.25rem;
}
.ce-summary-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 1rem;
  letter-spacing: 0.2px;
}
.ce-summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
}
.ce-summary-label {
  font-size: 0.8rem;
  color: #64748b;
  display: flex;
  align-items: center;
}
.ce-summary-label i { font-size: 0.75rem; color: #475569; }
.ce-summary-val {
  font-size: 0.82rem;
  font-weight: 600;
  color: #e2e8f0;
}
.ce-badge-draft {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
}
.ce-summary-divider {
  height: 1px;
  background: rgba(255,255,255,0.05);
  margin: 0.75rem 0;
}
.ce-summary-save {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: #4ade80;
  font-weight: 500;
}
.ce-summary-save i { font-size: 0.85rem; }

/* ── Bottom Action Bar ── */
.ce-action-bar {
  position: sticky;
  bottom: 0;
  margin-top: 1.5rem;
  margin-left: -2rem;
  margin-right: -2rem;
  padding: 1rem 2rem;
  background: rgba(9, 11, 22, 0.9);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 50;
}
.ce-action-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 500;
}
.ce-action-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.ce-btn-secondary {
  padding: 0.65rem 1.5rem;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  color: #cbd5e1;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  display: inline-flex;
  align-items: center;
}
.ce-btn-secondary:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.2);
  color: #f1f5f9;
  transform: translateY(-1px);
}
.ce-btn-primary {
  padding: 0.65rem 1.75rem;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  display: inline-flex;
  align-items: center;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
}
.ce-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.45);
}

/* ── Responsive ── */
@media (max-width: 1200px) {
  .ce-hero-right { width: 260px; height: 180px; }
  .ce-ill-laptop { left: 12%; }
  .ce-ill-person { left: 2%; }
  .ce-ill-holo { right: 2%; }
}
@media (max-width: 992px) {
  .ce-layout { grid-template-columns: 1fr; }
  .ce-right { position: static; }
  .ce-sidebar { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .ce-action-bar { margin-left: -1.5rem; margin-right: -1.5rem; padding: 1rem 1.5rem; }
  .ce-hero { padding: 0 0 0; }
  .ce-hero-right { width: 200px; height: 150px; }
  .ce-page-title { font-size: 1.6rem; }
  .ce-ill-laptop { width: 80px; height: auto; left: 14%; }
  .ce-lid { width: 80px; height: 42px; }
  .ce-base { width: 90px; margin-left: -4px; }
  .ce-ill-holo { width: 90px; }
  .ce-ill-person { width: 38px; left: 4%; }
  .ce-ill-card-1 { top: 25%; left: 0; }
  .ce-ill-card-2 { bottom: 18%; }
}
@media (max-width: 768px) {
  .ce-row { grid-template-columns: 1fr; }
  .ce-sidebar { grid-template-columns: 1fr; }
  .ce-action-bar { flex-direction: column; gap: 0.75rem; }
  .ce-page-title { font-size: 1.35rem; }
  .ce-stepper { max-width: 100%; }
  .ce-hero { padding: 0 0 0; }
  .ce-hero-inner { flex-direction: column; align-items: flex-start; gap: 1.5rem; }
  .ce-hero-right { width: 100%; height: 120px; }
  .ce-ill-laptop { width: 60px; left: 20%; }
  .ce-lid { width: 60px; height: 32px; }
  .ce-base { width: 68px; height: 4px; margin-left: -3px; }
  .ce-screen { padding: 3px; }
  .ce-screen-top { margin-bottom: 2px; }
  .ce-ill-holo { width: 70px; top: 5%; right: 5%; }
  .ce-holo-inner { padding: 5px 7px; }
  .ce-ill-person { display: none; }
  .ce-ill-card-1 { top: 20%; left: 2%; }
  .ce-ill-card-2 { display: none; }
  .ce-ill-card-3 { display: none; }
  .ce-ill-line { display: none; }
}
.notifications-page {
  position: relative;
  z-index: 2;
  padding: 1.25rem 0 2rem;
  max-width: 860px;
}
.notifications-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}
.notifications-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0 0 0.25rem;
  color: #f1f5f9;
  font-size: 1.15rem;
  font-weight: 800;
}
.notifications-title i { color: #818cf8; }
.notifications-count {
  color: #94a3b8;
  font-size: 0.82rem;
  font-weight: 500;
}
.notifications-clear {
  border: 1px solid rgba(129,140,248,0.25);
  border-radius: 10px;
  background: rgba(129,140,248,0.12);
  color: #c7d2fe;
  padding: 0.5rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
}
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.notification-card {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  width: 100%;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  background: rgba(15,23,42,0.68);
  padding: 1rem;
  text-align: left;
  cursor: pointer;
}
.notification-card.unread {
  border-left: 3px solid rgba(129,140,248,0.7);
  background: rgba(129,140,248,0.08);
}
.notification-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notification-body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
  flex: 1;
}
.notification-body strong {
  color: #f8fafc;
  font-size: 0.9rem;
  line-height: 1.45;
}
.notification-body small {
  color: #94a3b8;
  font-size: 0.74rem;
}
.notification-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #818cf8;
  margin-top: 0.35rem;
  flex-shrink: 0;
}
.notifications-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  min-height: 180px;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  background: rgba(15,23,42,0.55);
  color: #94a3b8;
  font-size: 0.85rem;
}
.notifications-empty i {
  color: #475569;
  font-size: 2rem;
}
.btn-calendar-admin {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1.5px solid rgba(129,140,248,0.15);
  background: rgba(129,140,248,0.08);
  color: #818cf8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.7rem;
  flex-shrink: 0;
}
.btn-calendar-admin:hover {
  background: rgba(129,140,248,0.15);
  border-color: rgba(129,140,248,0.3);
  transform: translateY(-2px);
}
.ca-toast {
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
  animation: caSlideUp 0.35s cubic-bezier(0.16,1,0.3,1);
}
@keyframes caSlideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
