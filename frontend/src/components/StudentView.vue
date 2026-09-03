<template>
  <div class="student-view">
    <div class="std-bg">
      <div class="std-glow glow-1"></div>
      <div class="std-glow glow-2"></div>
    </div>
 
    <Sidebar :nav-items="navItems" :active-tab="currentTab" @update:active-tab="currentTab = $event" />
 
    <div class="std-wrapper">
      <nav class="std-topbar">
        <div class="std-topbar-left">
          <h5 class="std-topbar-title">{{ currentTabLabel }}</h5>
        </div>
        <div class="std-topbar-right">
          <button class="std-icon-btn" title="Search"><i class="bi bi-search"></i></button>
          <button class="std-icon-btn" title="Notifications" @click="goToNotifications"><i class="bi bi-bell"></i><span v-if="studentNotifCount > 0" class="std-badge">{{ studentNotifCount > 99 ? '99+' : studentNotifCount }}</span></button>
          <button class="std-profile-btn" @click="showProfileModal = true"><i class="bi bi-person-gear me-1"></i>Profile</button>
          <span class="std-role-badge">Student Member</span>
          <div class="std-avatar" style="cursor: pointer;" title="Edit Profile" @click="showProfileModal = true">{{ userInitials }}</div>
        </div>
      </nav>

      <main class="std-main">
        <div v-if="currentTab === 'dashboard'">
        <div class="row g-4 mb-4">
          <div class="col-md-3 col-sm-6">
            <div class="std-metric-card">
              <div class="std-metric-icon purple"><i class="bi bi-calendar-event-fill"></i></div>
              <div class="std-metric-body">
                <span class="std-metric-label">Ongoing Events</span>
                <div class="std-metric-row">
                  <span class="std-metric-value">{{ ongoingEvents.length }}</span>
                  <span class="std-metric-trend up"><i class="bi bi-arrow-up-short"></i>+{{ ongoingEvents.length }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="std-metric-card">
              <div class="std-metric-icon blue"><i class="bi bi-check-circle-fill"></i></div>
              <div class="std-metric-body">
                <span class="std-metric-label">Applied Events</span>
                <div class="std-metric-row">
                  <span class="std-metric-value">{{ (store.registeredEvents || []).length }}</span>
                  <span class="std-metric-trend up"><i class="bi bi-arrow-up-short"></i>+{{ (store.registeredEvents || []).length }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="std-metric-card">
              <div class="std-metric-icon amber"><i class="bi bi-archive-fill"></i></div>
              <div class="std-metric-body">
                <span class="std-metric-label">Closed Events</span>
                <div class="std-metric-row">
                  <span class="std-metric-value">1</span>
                  <span class="std-metric-trend down"><i class="bi bi-arrow-down-short"></i>-0</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="std-metric-card">
              <div class="std-metric-icon green"><i class="bi bi-box-seam-fill"></i></div>
              <div class="std-metric-body">
                <span class="std-metric-label">Borrowed Items</span>
                <div class="std-metric-row">
                  <span class="std-metric-value">{{ myBorrowedCount }}</span>
                  <span class="std-metric-trend up"><i class="bi bi-arrow-up-short"></i>+{{ myBorrowedCount }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="std-actions mb-4">
          <button class="std-btn-primary" @click="currentTab = 'events'">
            <i class="bi bi-calendar-event me-2"></i>Browse Events
          </button>
          <button class="std-btn-secondary" @click="currentTab = 'inventory'">
            <i class="bi bi-box-seam me-2"></i>Request Inventory
          </button>
        </div>

        <h6 class="fw-bold mb-3 text-light">Ongoing Club Events</h6>
        <div class="row g-3 mb-5">
          <div v-for="event in ongoingEvents" :key="event.id" class="col-md-4 col-sm-6">
            <div class="card-glass p-0 h-100 d-flex flex-column event-card-hover overflow-hidden" @click="openEventDetails(event)" style="min-height: 280px;">
              <div class="event-card-img-sm" :style="{ backgroundImage: `url(${event.image})` }">
                <div class="event-img-overlay d-flex justify-content-between align-items-start p-2">
                  <span class="status-badge status-ongoing">Ongoing</span>
                  <span class="event-date-tag-sm"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(event.date || event.event_date) }}</span>
                </div>
              </div>
              <div class="p-3 d-flex flex-column flex-grow-1 justify-content-between">
                <div>
                  <h6 class="fw-bold text-light mb-1" style="color: #f1f5f9 !important;">{{ event.name }}</h6>
                  <p class="text-secondary small m-0" style="color: #94a3b8 !important;"><i class="bi bi-geo-alt-fill me-1"></i>{{ formatVenue(event.venue) }}</p>
                </div>
                <div v-if="(store.registeredEvents || []).includes(event.id)" class="d-flex align-items-center gap-2 mt-3">
                  <button class="btn-dashboard-primary btn-sm" disabled style="opacity: 0.85;">
                    <i class="bi bi-check-circle-fill me-1"></i>Registered
                  </button>
                  <button class="btn-calendar-sm" title="Add to Calendar" @click.stop="openCalendarForEvent(event)">
                    <i class="bi bi-calendar-plus"></i>
                  </button>
                </div>
                <div v-else class="mt-3">
                  <button class="btn-dashboard-primary btn-sm" @click.stop="openEventDetails(event)">
                    View Details & Register
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <h6 class="fw-bold mb-3 text-muted">Closed Events</h6>
        <div class="card-glass p-3">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <span class="fw-bold text-light">AI/ML Seminar</span>
              <small class="text-muted d-block">Seminar Hall &bull; Jun 20, 2026</small>
             </div>
            <span class="badge-status badge-approved">Closed</span>
           </div>
         </div>
      </div>

      <div v-else-if="currentTab === 'events'">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
          <div>
            <h5 class="fw-bold m-0 text-light">Available Events</h5>
            <span class="text-secondary" style="font-size:0.82rem;">Explore and register for upcoming club workshops, seminars, and hackathons.</span>
          </div>

          <!-- Interactive Filters -->
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <button
              type="button"
              class="std-event-filter-pill"
              :class="{ active: studentEventFilter === 'all' }"
              @click="studentEventFilter = 'all'"
            >
              <i class="bi bi-grid-fill me-1"></i>All Events
              <span class="std-filter-count">{{ approvedEvents.length }}</span>
            </button>

            <button
              type="button"
              class="std-event-filter-pill registered"
              :class="{ active: studentEventFilter === 'registered' }"
              @click="studentEventFilter = 'registered'"
              title="Show only events you have registered for"
            >
              <i class="bi bi-check-circle-fill me-1 text-success"></i>My Registered Events
              <span class="std-filter-count">{{ myRegisteredCount }}</span>
            </button>
          </div>
        </div>

        <CopilotRecommendation
          title="AI Recommendation"
          icon="stars"
          message="Seminar Hall is available this Friday. Perfect for a last-minute workshop."
          action="Switch Venue"
          class="mb-4"
        />

        <div v-if="displayedBrowseEvents.length > 0" class="row g-3">
          <div v-for="event in displayedBrowseEvents" :key="event.id" class="col-xl-4 col-md-6">
            <div class="card-glass p-0 h-100 d-flex flex-column event-card-hover overflow-hidden" @click="openEventDetails(event)" style="cursor: pointer;">
              <div class="event-card-img-sm position-relative" :style="{ backgroundImage: `url(${event.image || event.cover_image_url || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop'})` }">
                <div class="event-card-top-bar">
                  <span class="event-date-pill"><i class="bi bi-calendar3"></i>{{ formatDate(event.date || event.event_date) }}</span>
                  <span v-if="store.registeredEvents.includes(event.id)" class="event-status-pill registered">
                    <i class="bi bi-check-circle-fill me-1"></i>Registered
                  </span>
                  <span v-else-if="isEventOver(event)" class="event-status-pill closed">Closed</span>
                  <span v-else class="event-status-pill open">Open</span>
                </div>
              </div>

              <div class="p-3 d-flex flex-column flex-grow-1">
                <h6 class="fw-bold text-light mb-1" style="font-size: 0.95rem;">{{ event.name }}</h6>
                <p class="text-secondary small mb-2 flex-grow-1" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-size: 0.8rem; line-height: 1.45; min-height: 2.3em;">
                  {{ event.short_description || event.description }}
                </p>
                <div class="event-meta mb-2">
                  <span><i class="bi bi-geo-alt-fill me-1"></i>{{ formatVenue(event.venue) }}</span>
                  <span><i class="bi bi-people-fill me-1"></i>{{ event.participants || event.max_participants || 50 }} Max</span>
                </div>
                <div class="event-card-actions">
                  <button
                    v-if="store.registeredEvents.includes(event.id)"
                    class="btn-dashboard-primary btn-sm flex-grow-1"
                    style="background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(52, 211, 153, 0.4); color: #34d399;"
                    @click.stop="openEventDetails(event)"
                  >
                    <i class="bi bi-ticket-perforated-fill me-1"></i>Registered &bull; Details
                  </button>
                  <button
                    v-else-if="isEventOver(event)"
                    class="btn-dashboard-primary btn-sm flex-grow-1"
                    style="opacity: 0.6; cursor: default;"
                    @click.stop="openEventDetails(event)"
                  >
                    Registration Closed
                  </button>
                  <button
                    v-else
                    class="btn-dashboard-primary btn-sm flex-grow-1"
                    @click.stop="openEventDetails(event)"
                  >
                    <i class="bi bi-eye me-1"></i>View Details & Register
                  </button>

                  <button
                    v-if="store.registeredEvents.includes(event.id) || !isEventOver(event)"
                    class="btn-calendar-admin"
                    title="Add to Calendar"
                    @click.stop="openCalendarForEvent(event)"
                  >
                    <i class="bi bi-calendar-plus"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="card-glass p-5 text-center d-flex flex-column align-items-center justify-content-center">
          <i class="bi bi-ticket-perforated text-secondary mb-2" style="font-size: 2.2rem;"></i>
          <h5 class="text-light fw-bold mb-1">
            {{ studentEventFilter === 'registered' ? 'No Registered Events Yet' : 'No Events Available' }}
          </h5>
          <p class="text-secondary small mb-3">
            {{ studentEventFilter === 'registered' ? 'You have not registered for any events yet. Switch to "All Events" to explore and register!' : 'No upcoming events found.' }}
          </p>
          <button v-if="studentEventFilter === 'registered'" class="btn-primary-premium btn-sm" @click="studentEventFilter = 'all'">
            <i class="bi bi-compass me-1"></i>Explore All Events
          </button>
        </div>
      </div>

      <div v-else-if="currentTab === 'passes'">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h5 class="fw-bold m-0 text-light">My Event Passes</h5>
            <span class="text-secondary" style="font-size:0.82rem;">Access your registered event tickets and QR passes.</span>
           </div>
         </div>
        <div v-if="registeredEventsList.length > 0" class="d-flex flex-column gap-3">
          <EventPassCard
            v-for="event in registeredEventsList"
            :key="event.id"
            :event="event"
            @open="selectedPassEvent = event; showPassModal = true"
            @calendar="openCalendarForEvent(event)"
          />
        </div>
        <div v-else class="ep-empty">
          <div class="ep-empty-ill">
            <svg viewBox="0 0 200 160" fill="none">
              <rect x="50" y="25" width="100" height="70" rx="14" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
              <rect x="55" y="30" width="28" height="28" rx="4" stroke="rgba(255,255,255,0.06)" stroke-width="1" fill="rgba(255,255,255,0.02)"/>
              <rect x="88" y="32" width="56" height="6" rx="3" fill="rgba(255,255,255,0.05)"/>
              <rect x="88" y="43" width="36" height="4" rx="2" fill="rgba(255,255,255,0.03)"/>
              <rect x="88" y="51" width="42" height="4" rx="2" fill="rgba(255,255,255,0.03)"/>
              <rect x="55" y="64" width="90" height="5" rx="2.5" fill="rgba(129,140,248,0.1)"/>
              <rect x="55" y="73" width="60" height="3" rx="1.5" fill="rgba(255,255,255,0.03)"/>
              <circle cx="72" cy="120" r="6" fill="rgba(129,140,248,0.08)"/>
              <path d="M58 140h90" stroke="rgba(255,255,255,0.04)" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M68 132c0-5 4-9 9-9s9 4 9 9" stroke="rgba(129,140,248,0.15)" stroke-width="1.5" fill="none"/>
              <path d="M82 132c0-4 3-7 7-7s7 3 7 7" stroke="rgba(129,140,248,0.1)" stroke-width="1.5" fill="none"/>
            </svg>
           </div>
          <h3 class="ep-empty-title">No Event Passes Yet</h3>
          <p class="ep-empty-text">Register for an event to receive your digital pass.</p>
          <button class="ep-empty-btn" @click="currentTab = 'events'"><i class="bi bi-calendar-event me-2"></i>Browse Events</button>
         </div>
      </div>
 
      <div v-else-if="currentTab === 'volunteering'">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h5 class="fw-bold m-0 text-light">My Volunteering</h5>
            <span class="text-secondary" style="font-size:0.82rem;">Track your volunteer applications and assigned tasks.</span>
          </div>
        </div>
        <VolunteerView :applications="assignedVolunteerWork" @browse-events="currentTab = 'events'" />
      </div>

      <div v-else-if="currentTab === 'certificates'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h5 class="fw-bold m-0 text-light">My Certificates</h5>
            <span class="text-secondary" style="font-size:0.82rem;">View and download certificates earned from completed events.</span>
          </div>
        </div>
        <div class="d-flex flex-wrap align-items-center gap-2 mb-4">
          <div class="cc-search-wrap">
            <i class="bi bi-search"></i>
            <input v-model="certSearchQuery" type="text" placeholder="Search certificates..." />
          </div>
          <div class="d-flex gap-1 flex-wrap">
            <button v-for="t in ['All', 'Participation', 'Volunteer', 'Organizer', 'Winner']" :key="t" class="cc-filter-btn" :class="{ active: certTypeFilter === t }" @click="certTypeFilter = t">{{ t }}</button>
          </div>
          <select v-model="certSortBy" class="cc-sort">
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
          </select>
        </div>
        <div v-if="filteredCerts.length > 0" class="cert-row">
          <div v-for="cert in filteredCerts" :key="cert.id" class="cert-col">
            <CertificateCard
              :cert="cert"
              @view="selectedCert = cert; showCertModal = true"
              @download="selectedCert = cert; showCertModal = true"
              @share="shareCert"
            />
          </div>
        </div>
        <div v-else class="cc-empty">
          <div class="cc-empty-ill">
            <svg viewBox="0 0 200 160" fill="none">
              <rect x="45" y="25" width="110" height="80" rx="12" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
              <circle cx="100" cy="48" r="10" stroke="rgba(255,255,255,0.06)" stroke-width="1" fill="rgba(255,255,255,0.02)"/>
              <rect x="80" y="65" width="40" height="5" rx="2.5" fill="rgba(255,255,255,0.05)"/>
              <rect x="72" y="76" width="56" height="3" rx="1.5" fill="rgba(255,255,255,0.03)"/>
              <rect x="72" y="84" width="40" height="3" rx="1.5" fill="rgba(255,255,255,0.03)"/>
              <rect x="60" y="94" width="80" height="1" rx="0.5" fill="rgba(255,255,255,0.04)"/>
              <path d="M62 116c0-6 5-11 11-11h54c6 0 11 5 11 11" stroke="rgba(129,140,248,0.1)" stroke-width="1.5" fill="none"/>
              <circle cx="100" cy="126" r="4" fill="rgba(129,140,248,0.08)"/>
            </svg>
          </div>
          <h3 class="cc-empty-title">No Certificates Yet</h3>
          <p class="cc-empty-text">Complete events to earn digital certificates.</p>
          <button class="cc-empty-btn" @click="currentTab = 'events'"><i class="bi bi-calendar-event me-2"></i>Browse Events</button>
        </div>
      </div>

      <div v-else-if="currentTab === 'inventory'">
        <CopilotRecommendation
          title="AI Alert"
          icon="exclamation-triangle-fill"
          message="Only 3 Arduino Uno boards remaining. Current stock may not last the week."
          action="Generate Procurement"
          class="mb-3"
        />
        <InventoryGrid
          :items="liveInventory"
          :loading="isInventoryLoading"
          @borrow="studentBorrow"
          @return="studentReturn"
        />
      </div>

      <div v-else-if="currentTab === 'support'">
        <SupportDeskDiscussionHub :is-admin="false" />
      </div>

      <div v-else-if="currentTab === 'bounties'">
        <CampusBountyStudent @navigate="currentTab = $event" />
      </div>

      <div v-else-if="currentTab === 'notifications'" class="notifications-page">
        <div class="notifications-header">
          <div>
            <h2 class="notifications-title"><i class="bi bi-bell-fill"></i>Notifications</h2>
            <span class="notifications-count">{{ studentNotifs.length }} notification{{ studentNotifs.length !== 1 ? 's' : '' }}</span>
          </div>
          <button class="notifications-clear" @click="store.clearNotifsForRole('student')" v-if="studentNotifs.length">Clear all</button>
        </div>
        <div v-if="studentNotifs.length === 0" class="notifications-empty">
          <i class="bi bi-bell-slash"></i>
          <span>No notifications yet</span>
        </div>
        <div v-else class="notifications-list">
          <button v-for="n in studentNotifs" :key="n.id" type="button" class="notification-card" :class="{ unread: !n.read }" @click="store.markNotifRead(n.id)">
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

      <!-- Event Detail Modal -->
      <div v-if="selectedEvent" class="modal-overlay" @click.self="closeEventDetails">
        <div class="modal-card glass-modal" style="max-width: 520px;">
          <div class="modal-card-header">
            <h5 class="modal-card-title">Event Information</h5>
            <button class="modal-close" @click="closeEventDetails"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-card-body">
            <h4 class="fw-bold text-light mb-3">{{ selectedEvent.name }}</h4>
            <div class="d-flex flex-wrap gap-2 mb-4">
              <span class="badge-tag"><i class="bi bi-geo-alt-fill me-1"></i>{{ selectedEvent.venue }}</span>
              <span class="badge-tag"><i class="bi bi-calendar-check-fill me-1"></i>{{ selectedEvent.date }}</span>
              <span v-if="selectedEvent.deadline" class="badge-tag"><i class="bi bi-hourglass-split me-1"></i>Deadline: {{ selectedEvent.deadline }}</span>
            </div>
            <p class="text-muted mb-4" style="line-height: 1.6;">{{ selectedEvent.description }}</p>
            <div v-if="isDeadlinePassed(selectedEvent) && !store.registeredEvents.includes(selectedEvent.id)" class="alert alert-danger py-2 px-3 mb-3 rounded-3 d-flex align-items-center gap-2" style="background: rgba(220,38,38,0.12); border: 1px solid rgba(220,38,38,0.2); font-size: 0.85rem;">
              <i class="bi bi-exclamation-circle-fill" style="color: #ef4444;"></i>
              <span class="text-danger">Registration deadline has been passed</span>
            </div>
            <div class="glass p-3 rounded-4 mb-4">
              <div class="row text-center">
                <div class="col-6 border-end" style="border-color: rgba(255,255,255,0.1) !important;">
                  <span class="d-block text-muted small fw-bold text-uppercase mb-1">Capacity</span>
                  <span class="fw-bold text-light">{{ selectedEvent.participants }} Max</span>
                 </div>
                <div class="col-6">
                  <span class="d-block text-muted small fw-bold text-uppercase mb-1">Status</span>
                  <span class="fw-bold text-success">{{ selectedEvent.status }}</span>
                 </div>
               </div>
             </div>
            <button
              class="btn-dashboard-primary w-100 py-3"
              :class="{ 'btn-disabled': store.registeredEvents.includes(selectedEvent.id) || isDeadlinePassed(selectedEvent) }"
              @click="confirmRegistration(selectedEvent.id)"
              :disabled="store.registeredEvents.includes(selectedEvent.id) || isDeadlinePassed(selectedEvent)"
            >
              {{ store.registeredEvents.includes(selectedEvent.id) ? '✓ Successfully Registered' : (isDeadlinePassed(selectedEvent) ? 'Registration Closed' : 'Confirm Registration') }}
            </button>
            <button v-if="store.registeredEvents.includes(selectedEvent.id)" class="btn-calendar-secondary w-100 mt-2" @click="openCalendarForEvent(selectedEvent)">
              <i class="bi bi-calendar-plus me-2"></i>Add to Calendar
            </button>
           </div>
         </div>
\ No newline at end of file
      </div>
    </main>
  </div>
</div>
<CalendarPickerModal v-if="showCalendarModal" @close="showCalendarModal = false" @selected="triggerCalendarToast" />
<EventPassModal v-if="showPassModal && selectedPassEvent" :event="selectedPassEvent" @close="showPassModal = false" />
<CertificateModal v-if="showCertModal && selectedCert" :cert="selectedCert" @close="showCertModal = false" />
<StudentProfileModal v-if="showProfileModal" @close="showProfileModal = false" />
<div v-if="showCalendarToast" class="std-toast"><i class="bi bi-info-circle-fill me-2" style="color:#818cf8;"></i>{{ calendarToastMsg }}</div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store/mockData';
import { fetchEquipmentApi } from '../api/inventory';

import Sidebar from './shared/Sidebar.vue';
import InventoryGrid from './shared/InventoryGrid.vue';
import SupportDeskDiscussionHub from './shared/SupportDeskDiscussionHub.vue';
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import EventPassCard from './shared/EventPassCard.vue';
import EventPassModal from './shared/EventPassModal.vue';
import CertificateCard from './shared/CertificateCard.vue';
import CertificateModal from './shared/CertificateModal.vue';
import CampusBountyStudent from './CampusBountyStudent.vue';
import VolunteerView from './shared/VolunteerView.vue';
import StudentProfileModal from './StudentProfileModal.vue';
import { getMyEventRegistrationsApi } from '../api/qr';
import { useCalendarToast } from '../composables/useCalendarToast';

const router = useRouter();
const { show: showCalendarToast, message: calendarToastMsg, showCalendarToast: triggerCalendarToast } = useCalendarToast();
const calendarEventTarget = ref(null);
const showCalendarModal = ref(false);
const showProfileModal = ref(false);
const showPassModal = ref(false);
const selectedPassEvent = ref(null);
const showCertModal = ref(false);
const selectedCert = ref(null);
const certTypeFilter = ref('All');
const certSortBy = ref('newest');
const certSearchQuery = ref('');

const liveInventory = ref([]);
const isInventoryLoading = ref(false);

const loadInventory = async () => {
  isInventoryLoading.value = true;
  try {
    const token = store.token || localStorage.getItem('driven_token');
    const data = await fetchEquipmentApi(token);
    if (Array.isArray(data)) {
      liveInventory.value = data.map((eq) => ({
        id: eq.id,
        name: eq.name,
        category: eq.category,
        description: eq.description || '',
        available: eq.available_quantity,
        borrowed: Math.max(0, eq.total_quantity - eq.available_quantity),
        total_quantity: eq.total_quantity,
        available_quantity: eq.available_quantity,
        storage_location: eq.storage_location,
        location: eq.storage_location || 'Campus Lab',
        image: eq.equipment_image_url || 'https://images.unsplash.com/photo-1581092335397-9583eb92d232?w=400&h=300&fit=crop',
        equipment_image_url: eq.equipment_image_url,
      }));
    }
  } catch (err) {
    console.error('Failed to load inventory for student:', err);
    liveInventory.value = [];
  } finally {
    isInventoryLoading.value = false;
  }
};

const shareCert = (cert) => {
  const toast = document.createElement('div');
  toast.className = 'std-toast';
  toast.innerHTML = '<i class="bi bi-check-circle-fill me-2" style="color:#4ade80;"></i>Certificate link copied!';
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
};

const openCalendarForEvent = (event) => {
  calendarEventTarget.value = event;
  showCalendarModal.value = true;
};

const liveRegistrations = ref([]);

const loadMyRegistrations = async () => {
  const token = store.token || localStorage.getItem('driven_token');
  if (token) {
    try {
      const list = await getMyEventRegistrationsApi(token);
      if (Array.isArray(list)) {
        liveRegistrations.value = list;
        store.registeredEvents = list.map(r => r.event_id);
      } else {
        liveRegistrations.value = [];
        store.registeredEvents = [];
      }
    } catch {
      liveRegistrations.value = [];
      store.registeredEvents = [];
    }
  } else {
    liveRegistrations.value = [];
    store.registeredEvents = [];
  }
};

onMounted(() => {
  store.fetchEvents();
  loadMyRegistrations();
  loadInventory();
});

const registeredEventsList = computed(() => {
  if (liveRegistrations.value.length > 0) {
    return liveRegistrations.value.map(reg => {
      const ev = reg.event || {};
      const foundStoreEvent = store.events.find(e => e.id === reg.event_id) || {};
      const img = ev.cover_image_url || ev.image || foundStoreEvent.cover_image_url || foundStoreEvent.image || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop';
      return {
        ...foundStoreEvent,
        ...ev,
        id: reg.event_id,
        registration_id: reg.id,
        team_name: reg.team_name,
        qr_code_url: reg.qr_code_url,
        attendance_status: reg.attendance_status,
        student: reg.student,
        image: img,
        cover_image_url: img,
        name: ev.name || foundStoreEvent.name || 'Event Pass',
        date: ev.date || ev.event_date || foundStoreEvent.date || 'TBD',
        venue: ev.venue || foundStoreEvent.venue || 'Campus Facility',
      };
    });
  }
  return [];
});
const filteredCerts = computed(() => {
  let result = [...store.certificates];
  if (certTypeFilter.value !== 'All') {
    result = result.filter(c => c.type === certTypeFilter.value);
  }
  if (certSearchQuery.value) {
    const q = certSearchQuery.value.toLowerCase();
    result = result.filter(c => c.eventName.toLowerCase().includes(q) || c.type.toLowerCase().includes(q));
  }
  result.sort((a, b) => {
    const da = new Date(a.issueDate), db = new Date(b.issueDate);
    return certSortBy.value === 'newest' ? db - da : da - db;
  });
  return result;
});
const studentNotifs = computed(() => store.notifications.filter(n => n.role === 'student'));
const studentNotifCount = computed(() => studentNotifs.value.filter(n => !n.read).length);

const userInitials = computed(() => {
  const name = store.currentUser?.full_name || store.studentProfile?.fullName || 'Student';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
});

const navItems = computed(() => [
  { label: 'Dashboard', icon: 'bar-chart-fill', key: 'dashboard' },
  { label: 'Browse Events', icon: 'calendar-event-fill', key: 'events' },
  { label: 'My Event Passes', icon: 'ticket-perforated-fill', key: 'passes' },
  { label: 'My Volunteering', icon: 'hand-thumbs-up-fill', key: 'volunteering' },
  { label: 'My Certificates', icon: 'award-fill', key: 'certificates' },
  { label: 'Campus Bounties', icon: 'briefcase-fill', key: 'bounties' },
  { label: 'Inventory', icon: 'box-seam-fill', key: 'inventory' },
  { label: 'Support Desk', icon: 'chat-dots-fill', key: 'support' },
]);

const currentTab = ref('dashboard');
const currentTabLabel = computed(() => {
  const item = navItems.value.find(i => i.key === currentTab.value);
  if (item) return item.label;
  if (currentTab.value === 'notifications') return 'Notifications';
  return 'Dashboard';
});
const goToNotifications = () => {
  currentTab.value = 'notifications';
};
const myBorrowedCount = ref(0);
const myBorrowedItems = reactive({});
const selectedEvent = ref(null);

const approvedEvents = computed(() => store.events.filter(e => e.status === 'Approved'));
const ongoingEvents = computed(() => approvedEvents.value);

const studentEventFilter = ref('all'); // 'all' | 'registered'
const myRegisteredCount = computed(() => {
  return approvedEvents.value.filter(e => (store.registeredEvents || []).includes(e.id)).length;
});
const displayedBrowseEvents = computed(() => {
  let list = approvedEvents.value;
  if (studentEventFilter.value === 'registered') {
    return list.filter(e => (store.registeredEvents || []).includes(e.id));
  }
  return list;
});

const assignedVolunteerWork = computed(() =>
  store.volunteerApplications.filter(a => a.assignedTask && (a.status === 'accepted' || a.status === 'completed'))
);

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

const formatVenue = (v) => {
  if (!v) return 'TBD';
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const isDeadlinePassed = (event) => {
  if (!event.deadline) return false;
  return new Date(event.deadline) < new Date();
};
const isEventOver = (event) => {
  return new Date(event.date) < new Date();
};

const openEventDetails = (event) => { router.push({ name: 'event-details', params: { eventName: encodeURIComponent(event.name) } }); };

const confirmRegistration = (id) => {
  if (!store.registeredEvents.includes(id)) {
    store.registeredEvents.push(id);
    setTimeout(() => { selectedEvent.value = null; }, 1500);
  }
};

const studentBorrow = ({ item, quantity }) => {
  if (store.borrowItem(item.id, quantity)) {
    myBorrowedCount.value += quantity;
    myBorrowedItems[item.id] = (myBorrowedItems[item.id] || 0) + quantity;
  }
};

const studentReturn = ({ item, quantity }) => {
  if (store.returnItem(item.id, quantity)) {
    myBorrowedCount.value -= quantity;
    myBorrowedItems[item.id] = (myBorrowedItems[item.id] || 0) - quantity;
  }
};

const refreshTickets = () => {};
</script>

<style scoped>
.student-view {
  min-height: 100vh;
  background: #0c1220;
}

.std-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background-color: #0c1220;
  background-image:
    radial-gradient(ellipse 900px 700px at 85% 12%, rgba(124, 58, 237, 0.08) 0%, rgba(99, 102, 241, 0.03) 45%, transparent 70%),
    radial-gradient(ellipse 750px 600px at 15% 88%, rgba(99, 102, 241, 0.07) 0%, rgba(139, 92, 246, 0.02) 50%, transparent 70%),
    radial-gradient(ellipse 600px 450px at 20% 8%, rgba(139, 92, 246, 0.05) 0%, transparent 60%);
}
.std-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(140px);
  animation: stdGlowDrift 28s ease-in-out infinite;
  pointer-events: none;
}
.glow-1 {
  width: 600px; height: 600px;
  top: -10%; left: -5%;
  background: radial-gradient(circle, rgba(109, 93, 246, 0.09) 0%, rgba(99, 102, 241, 0.03) 50%, transparent 70%);
}
.glow-2 {
  width: 550px; height: 550px;
  top: 10%; right: -8%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, rgba(124, 58, 237, 0.02) 50%, transparent 70%);
  animation-delay: -14s;
}
@keyframes stdGlowDrift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -20px) scale(1.04); }
}

.std-wrapper {
  position: relative;
  z-index: 1;
  margin-left: 240px;
  min-height: 100vh;
  overflow: visible;
}

.std-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 56px;
  background: #0b111f;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  position: sticky;
  top: 0;
  z-index: 100;
}
.std-topbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: -0.2px;
}
.std-topbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.std-icon-btn {
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
.std-icon-btn:hover {
  background: rgba(255,255,255,0.08);
  color: #e2e8f0;
  border-color: rgba(255,255,255,0.15);
}
.std-dot {
  position: absolute;
  top: 6px; right: 6px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #fb7185;
  border: 1.5px solid #090B16;
}
.std-badge {
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
.std-role-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  background: rgba(52,211,153,0.1);
  color: #34d399;
  border: 1px solid rgba(52,211,153,0.12);
}
.std-profile-btn {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.28);
  color: #c7d2fe;
  padding: 0.28rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}
.std-profile-btn:hover {
  background: rgba(99, 102, 241, 0.3);
  border-color: rgba(165, 180, 252, 0.5);
  color: #ffffff;
}
.std-avatar {
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

.std-main {
  position: relative;
  z-index: 2;
  padding: 1.5rem 2rem 3rem;
  margin-left: 0;
}

/* ── Metric Cards ── */
.std-metric-card {
  background: rgba(18, 27, 48, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  padding: 1.25rem;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.std-metric-card:hover {
  transform: translateY(-3px);
  border-color: rgba(129, 140, 248, 0.35);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35), 0 0 20px rgba(99, 102, 241, 0.12);
  background: rgba(22, 33, 55, 0.98);
}
.std-metric-icon {
  width: 44px; height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}
.std-metric-icon.purple {
  background: linear-gradient(135deg, rgba(109,93,246,0.2), rgba(139,92,246,0.1));
  color: #818cf8;
  box-shadow: 0 4px 12px rgba(109,93,246,0.15);
}
.std-metric-icon.green {
  background: linear-gradient(135deg, rgba(52,211,153,0.2), rgba(16,185,129,0.1));
  color: #34d399;
  box-shadow: 0 4px 12px rgba(52,211,153,0.15);
}
.std-metric-icon.blue {
  background: linear-gradient(135deg, rgba(96,165,250,0.2), rgba(59,130,246,0.1));
  color: #60a5fa;
  box-shadow: 0 4px 12px rgba(96,165,250,0.15);
}
.std-metric-icon.amber {
  background: linear-gradient(135deg, rgba(251,191,36,0.2), rgba(245,158,11,0.1));
  color: #fbbf24;
  box-shadow: 0 4px 12px rgba(251,191,36,0.15);
}
.std-metric-body { flex: 1; min-width: 0; }
.std-metric-label {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 0.85rem;
  letter-spacing: 0.2px;
}
.std-metric-row {
  display: flex;
  align-items: baseline;
  gap: 0.85rem;
}
.std-metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -1px;
  line-height: 1;
}
.std-metric-trend {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  line-height: 1.3;
}
.std-metric-trend.up { background: rgba(52,211,153,0.1); color: #34d399; }
.std-metric-trend.down { background: rgba(244,63,94,0.1); color: #fb7185; }

/* ── Action Buttons ── */
.std-actions {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-top: 2rem;
  margin-bottom: 2.5rem;
  position: relative;
  z-index: 10;
}
.std-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.6rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 700;
  border: 1px solid rgba(165, 180, 252, 0.5);
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.std-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6);
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}
.std-btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.6rem;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.std-btn-secondary:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.2);
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
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  background: rgba(18, 27, 48, 0.7);
  padding: 1rem;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}
.notification-card:hover {
  background: rgba(22, 33, 55, 0.75);
  border-color: rgba(255,255,255,0.12);
}
.notification-card.unread {
  border-left: 3px solid rgba(129,140,248,0.6);
  background: rgba(129,140,248,0.06);
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
.std-closed-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: rgba(239,68,68,0.15);
  color: #ef4444;
  display: inline-flex;
  align-items: center;
}
.btn-calendar-sm {
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
.btn-calendar-sm:hover {
  background: rgba(129,140,248,0.15);
  border-color: rgba(129,140,248,0.3);
  transform: translateY(-2px);
}
.btn-calendar-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  border: 1.5px solid rgba(129,140,248,0.15);
  background: rgba(129,140,248,0.06);
  color: #818cf8;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-calendar-secondary:hover {
  background: rgba(129,140,248,0.12);
  border-color: rgba(129,140,248,0.3);
  color: #a5b4fc;
}
.ep-empty {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(18, 27, 48, 0.5);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.06);
}
.ep-empty-ill { margin-bottom: 1.5rem; }
.ep-empty-ill svg { width: 140px; height: auto; }
.ep-empty-title {
  font-size: 1.1rem; font-weight: 700; color: #f1f5f9;
  margin: 0 0 0.4rem;
}
.ep-empty-text {
  font-size: 0.82rem; color: #64748b; margin: 0 0 1.25rem;
}
.ep-empty-btn {
  display: inline-flex; align-items: center; padding: 0.5rem 1.25rem;
  border-radius: 10px; font-size: 0.78rem; font-weight: 600; font-family: inherit;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none; color: #fff; cursor: pointer; transition: all 0.2s;
}
.ep-empty-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(79,70,229,0.4); }
.std-toast {
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
  animation: stdSlideUp 0.35s cubic-bezier(0.16,1,0.3,1);
}
@keyframes stdSlideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.cc-search-wrap {
  position: relative; display: flex; align-items: center;
  background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px; padding: 0 0.75rem; min-width: 200px;
}
.cc-search-wrap:focus-within { border-color: rgba(129,140,248,0.35); }
.cc-search-wrap i { font-size: 0.7rem; color: #475569; pointer-events: none; }
.cc-search-wrap input {
  background: transparent; border: none; outline: none; color: rgba(255,255,255,0.95);
  font-size: 0.78rem; font-family: inherit; padding: 0.45rem 0.5rem; width: 100%;
}
.cc-search-wrap input::placeholder { color: rgba(255,255,255,0.5); }
.cc-filter-btn {
  padding: 0.3rem 0.75rem; border-radius: 8px;
  font-size: 0.68rem; font-weight: 600; font-family: inherit;
  background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07);
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
}
.cc-filter-btn:hover { border-color: rgba(129,140,248,0.2); color: #cbd5e1; }
.cc-filter-btn.active { background: rgba(129,140,248,0.12); border-color: rgba(129,140,248,0.3); color: #a5b4fc; }
.cc-sort {
  appearance: none; background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.07); border-radius: 8px;
  color: #e2e8f0; font-size: 0.68rem; font-family: inherit;
  padding: 0.3rem 1.5rem 0.3rem 0.6rem; cursor: pointer; outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='%23475569'%3E%3Cpath d='M1 1l4 4 4-4'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 0.4rem center;
}
.cc-sort option { background: #111827; color: #e2e8f0; }
.cc-empty {
  text-align: center; padding: 4rem 2rem;
  background: rgba(15,23,42,0.4); border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.04);
}
.cc-empty-ill { margin-bottom: 1.5rem; }
.cc-empty-ill svg { width: 140px; height: auto; }
.cc-empty-title { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.4rem; }
.cc-empty-text { font-size: 0.82rem; color: #64748b; margin: 0 0 1.25rem; }
.cc-empty-btn {
  display: inline-flex; align-items: center; padding: 0.5rem 1.25rem;
  border-radius: 10px; font-size: 0.78rem; font-weight: 600; font-family: inherit;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none; color: #fff; cursor: pointer; transition: all 0.2s;
}
.cc-empty-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(79,70,229,0.4); }
.cert-row {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}
.cert-col {
  position: relative;
  z-index: 1;
  flex: 1 1 300px;
  max-width: 100%;
}

/* ── Browse Events Filter & Card Styles (Same as ClubAdminView) ── */
.std-event-filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.09);
  color: #94a3b8;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.std-event-filter-pill:hover {
  background: rgba(15, 23, 42, 0.85);
  border-color: rgba(129, 140, 248, 0.35);
  color: #e2e8f0;
  transform: translateY(-1px);
}
.std-event-filter-pill.active {
  background: rgba(99, 102, 241, 0.22);
  border-color: #818cf8;
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.25);
}
.std-event-filter-pill.registered.active {
  background: rgba(16, 185, 129, 0.2);
  border-color: #34d399;
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.25);
}
.std-filter-count {
  font-size: 0.68rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
}
.std-event-filter-pill.active .std-filter-count {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}

.event-card-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  background: linear-gradient(180deg, rgba(7, 11, 20, 0.7) 0%, rgba(7, 11, 20, 0.1) 85%, transparent 100%);
  z-index: 2;
}
.event-date-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(15, 23, 42, 0.75);
  color: #c7d2fe;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid rgba(129, 140, 248, 0.25);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}
.event-status-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}
.event-status-pill.approved,
.event-status-pill.registered,
.event-status-pill.open {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.35);
}
.event-status-pill.pending {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.35);
}
.event-status-pill.rejected,
.event-status-pill.closed {
  background: rgba(244, 63, 94, 0.2);
  color: #fb7185;
  border: 1px solid rgba(244, 63, 94, 0.35);
}
.event-card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.25rem;
}
.btn-calendar-admin {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 8px;
  border: 1.5px solid rgba(129,140,248,0.25);
  background: rgba(129,140,248,0.1);
  color: #a5b4fc;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.btn-calendar-admin:hover {
  background: rgba(129,140,248,0.25);
  border-color: #818cf8;
  color: #ffffff;
  transform: scale(1.05);
}
</style>
