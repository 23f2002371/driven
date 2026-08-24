<template>
  <div class="la-page">
    <Sidebar :nav-items="navItems" :active-tab="currentTab" @update:active-tab="currentTab = $event" />

    <div class="la-wrapper">
      <TopHeader
        title="Lab Administrator Portal"
        badge-text="Facility Controller"
        badge-class="badge bg-warning bg-opacity-10 text-warning px-3 py-2 rounded-pill"
        :avatar-initials="adminInitials"
        :notif-count="labNotifCount"
        @notif-click="currentTab = 'notifications'"
      />

      <!-- ─── DASHBOARD TAB ─── -->
      <div v-if="currentTab === 'dashboard'" class="la-content">
        <!-- 2 Metrics: Pending & Today's Bookings -->
        <div class="la-stats-row">
          <div class="la-stat" v-for="s in stats" :key="s.label">
            <div class="la-stat-icon" :style="{ background: s.bg, color: s.color }">
              <i :class="'bi bi-' + s.icon"></i>
            </div>
            <div class="la-stat-body">
              <span class="la-stat-value">{{ s.value }}</span>
              <span class="la-stat-label">{{ s.label }}</span>
            </div>
          </div>
        </div>

        <div class="la-dash-section">
          <div class="la-dash-header">
            <div>
              <h4 class="la-dash-title">Pending Event Requests</h4>
              <span class="la-dash-subtitle">{{ pendingEvents.length }} pending request{{ pendingEvents.length !== 1 ? 's' : '' }}</span>
            </div>
            <button class="la-today-btn" @click="currentTab = 'approvals'">
              <i class="bi bi-calendar-check me-1"></i>Go to Approvals
            </button>
          </div>

          <div v-if="pendingEvents.length === 0" class="p-5 text-center text-muted">
            <i class="bi bi-inbox-fill" style="font-size: 2.2rem; color: #475569; display: block; margin-bottom: 0.75rem;"></i>
            <span>No pending event requests at the moment.</span>
          </div>

          <div v-else class="la-dash-list">
            <div
              v-for="ev in pendingEvents"
              :key="ev.id"
              class="la-dash-item la-dash-pending"
            >
              <div class="la-dash-item-left">
                <div class="la-dash-item-img" :style="{ backgroundImage: `url(${ev.image || ev.cover_image_url})` }"></div>
                <div class="la-dash-item-body">
                  <div class="la-dash-item-title-row">
                    <strong class="la-dash-item-title">{{ ev.name }}</strong>
                    <span class="la-status-badge la-status-pending">{{ ev.status }}</span>
                  </div>
                  <div class="la-dash-item-meta">
                    <span><i class="bi bi-geo-alt"></i>{{ formatVenue(ev.venue) }}</span>
                    <span><i class="bi bi-calendar"></i>{{ ev.date }}</span>
                    <span><i class="bi bi-people"></i>{{ ev.participants }} participants</span>
                  </div>
                </div>
              </div>
              <div class="la-dash-item-actions">
                <button class="la-qi-btn la-qi-btn-review" @click="openReview(ev)">Review</button>
                <button class="la-qi-btn la-qi-btn-approve" @click="openApprove(ev)">Approve</button>
                <button class="la-qi-btn la-qi-btn-reject" @click="openReject(ev)">Reject</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── EVENT APPROVALS TAB ─── -->
      <div v-else-if="currentTab === 'approvals'" class="la-content">
        <!-- 2 Metrics: Pending & Today's Bookings -->
        <div class="la-stats-row">
          <div class="la-stat" v-for="s in stats" :key="s.label">
            <div class="la-stat-icon" :style="{ background: s.bg, color: s.color }">
              <i :class="'bi bi-' + s.icon"></i>
            </div>
            <div class="la-stat-body">
              <span class="la-stat-value">{{ s.value }}</span>
              <span class="la-stat-label">{{ s.label }}</span>
            </div>
          </div>
        </div>

        <div class="la-main-layout">
          <!-- ─── CALENDAR (left 65%) ─── -->
          <div class="la-cal-section">
            <div class="la-cal-topbar">
              <div class="la-venue-picker">
                <i class="bi bi-geo-alt-fill" style="color:#818cf8;font-size:0.85rem;"></i>
                <select v-model="calVenue" class="la-venue-select">
                  <option v-for="v in venueOptions" :key="v.value" :value="v.value">{{ v.label }}</option>
                </select>
              </div>
              <div class="la-cal-nav">
                <button class="la-cal-nav-btn" @click="calOffset--"><i class="bi bi-chevron-left"></i></button>
                <span class="la-cal-label">{{ calLabel }}</span>
                <button class="la-cal-nav-btn" @click="calOffset++"><i class="bi bi-chevron-right"></i></button>
              </div>
              <button class="la-today-btn" @click="goToday">Today</button>
            </div>

            <!-- Month View (Only month view is kept) -->
            <div class="la-cal-month">
              <div class="la-cal-row la-cal-header">
                <span v-for="d in dayNames" :key="d" class="la-cal-hd">{{ d }}</span>
              </div>
              <div v-for="(week, wi) in monthWeeks" :key="wi" class="la-cal-row">
                <div
                  v-for="(day, di) in week"
                  :key="di"
                  class="la-cal-cell"
                  :class="{
                    'la-cell-other': day.month !== 0,
                    'la-cell-today': day.isToday,
                    'la-cell-selected': day.date === selectedDate && day.month === 0,
                    'la-cell-clickable': day.month === 0,
                  }"
                  @click="day.month === 0 && selectDate(day.date)"
                >
                  <span class="la-cell-num">{{ day.date }}</span>
                  <div v-if="day.bookings.length" class="la-cell-bookings">
                    <div
                      v-for="(bk, bi) in day.bookings.slice(0, 2)"
                      :key="bi"
                      class="la-cell-bk"
                      :class="'la-bk-' + bk.status"
                      :title="bk.name + ' (' + bk.venue + ')'"
                      @click.stop="goToEventDetails(bk.id)"
                    >{{ bk.name }}</div>
                    <div v-if="day.bookings.length > 2" class="la-cell-more">+{{ day.bookings.length - 2 }} more</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="la-legend">
              <span class="la-legend-item"><span class="la-legend-dot la-legend-approved"></span> Approved</span>
              <span class="la-legend-item"><span class="la-legend-dot la-legend-pending"></span> Pending</span>
            </div>
          </div>

          <!-- ─── APPROVAL QUEUE (right 35%) ─── -->
          <div class="la-queue-section">
            <div class="la-queue-header">
              <div>
                <h5 class="la-queue-title">Venue Approval Queue</h5>
                <span class="la-queue-subtitle">
                  {{ filteredQueue.length }} request{{ filteredQueue.length !== 1 ? 's' : '' }}
                  <span v-if="selectedDate"> for {{ formatDateLabel(selectedDate) }}</span>
                </span>
              </div>
              <button v-if="selectedDate !== null" class="la-today-btn btn-sm" @click="selectedDate = null">Clear Day</button>
            </div>

            <div class="la-queue-search">
              <input v-model="queueSearch" placeholder="Search requests..." class="la-qs-input" />
            </div>

            <div class="la-queue-list">
              <div v-if="filteredQueue.length === 0" class="la-queue-empty">
                <i class="bi bi-inbox"></i>
                <span>No requests match selected venue & date</span>
              </div>

              <div
                v-for="ev in filteredQueue"
                :key="ev.id"
                class="la-queue-item"
                :class="{
                  'la-qi-highlight': highlightedId === ev.id,
                  'la-qi-pending': ev.status === 'Pending',
                  'la-qi-approved': ev.status === 'Approved',
                  'la-qi-rejected': ev.status === 'Rejected',
                }"
                @click="highlightedId = ev.id"
              >
                <div class="la-qi-top">
                  <strong class="la-qi-title">{{ ev.name }}</strong>
                  <div class="la-qi-meta">
                    <span><i class="bi bi-geo-alt"></i>{{ formatVenue(ev.venue) }}</span>
                    <span><i class="bi bi-calendar"></i>{{ ev.date }}</span>
                  </div>
                  <div class="la-qi-meta">
                    <span><i class="bi bi-people"></i>{{ ev.participants }} participants</span>
                    <span class="la-status-badge" :class="'la-status-' + ev.status.toLowerCase()">{{ ev.status }}</span>
                  </div>
                  <div v-if="hasConflict(ev)" class="la-qi-conflict">
                    <i class="bi bi-exclamation-triangle-fill"></i> Scheduling conflict detected
                  </div>
                </div>
                <div class="la-qi-actions">
                  <button class="la-qi-btn la-qi-btn-review" @click.stop="openReview(ev)">Review</button>
                  <button
                    v-if="ev.status === 'Pending'"
                    class="la-qi-btn la-qi-btn-approve"
                    @click.stop="openApprove(ev)"
                  >Approve</button>
                  <button
                    v-if="ev.status === 'Pending'"
                    class="la-qi-btn la-qi-btn-reject"
                    @click.stop="openReject(ev)"
                  >Reject</button>
                  <span v-else class="la-qi-done">{{ ev.status }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── EVENTS TAB (Approved & Rejected Cards) ─── -->
      <div v-else-if="currentTab === 'events'" class="la-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="la-dash-title text-light">Approved & Rejected Events</h4>
            <span class="text-secondary small">{{ approvedAndRejectedEvents.length }} upcoming/ongoing event{{ approvedAndRejectedEvents.length !== 1 ? 's' : '' }}</span>
          </div>
        </div>

        <div v-if="approvedAndRejectedEvents.length === 0" class="la-dash-section p-5 text-center">
          <i class="bi bi-calendar-x" style="font-size:2.5rem;color:#475569;display:block;margin-bottom:0.75rem;"></i>
          <span class="text-secondary">No upcoming or ongoing approved/rejected events</span>
        </div>

        <div v-else class="row g-4">
          <div v-for="event in approvedAndRejectedEvents" :key="event.id" class="col-md-6 col-lg-4">
            <div class="la-event-card h-100 d-flex flex-column" @click="goToEventDetails(event)">
              <div class="la-event-card-img" :style="{ backgroundImage: `url(${event.image || event.cover_image_url})` }">
                <div class="la-event-img-overlay d-flex justify-content-between align-items-start p-3">
                  <span class="la-event-date-tag"><i class="bi bi-calendar3 me-1"></i>{{ event.date }}</span>
                  <span class="la-status-badge" :class="'la-status-' + event.status.toLowerCase()">{{ event.status }}</span>
                </div>
              </div>
              <div class="p-3 d-flex flex-column flex-grow-1">
                <h6 class="fw-bold text-light mb-1">{{ event.name }}</h6>
                <p class="text-secondary small mb-2 flex-grow-1 line-clamp-2">{{ event.short_description || event.description }}</p>
                <div class="la-event-card-meta mb-3">
                  <span><i class="bi bi-geo-alt-fill me-1"></i>{{ formatVenue(event.venue) }}</span>
                  <span><i class="bi bi-people-fill me-1"></i>{{ event.participants }} Max</span>
                </div>
                <div v-if="event.rejection_reason" class="la-rejection-info mb-2 p-2 rounded">
                  <span class="text-danger small fw-semibold"><i class="bi bi-exclamation-octagon me-1"></i>Reason: {{ humanizeRejectionReason(event.rejection_reason.reason) }}</span>
                  <small v-if="event.rejection_reason.admin_comment" class="d-block text-secondary mt-1">{{ event.rejection_reason.admin_comment }}</small>
                </div>
                <div class="mt-auto">
                  <button class="la-btn-view-details w-100" @click.stop="goToEventDetails(event)">
                    <i class="bi bi-eye me-1"></i>View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── NOTIFICATIONS TAB ─── -->
      <div v-else-if="currentTab === 'notifications'" class="la-content">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h5 class="fw-bold m-0 text-light"><i class="bi bi-bell-fill me-2" style="color:#818cf8;"></i>Notifications</h5>
            <span class="text-muted small">{{ labNotifs.length }} notification{{ labNotifs.length !== 1 ? 's' : '' }}</span>
          </div>
          <button class="la-today-btn" @click="store.clearNotifsForRole('lab_admin')" v-if="labNotifs.length">Clear all</button>
        </div>
        <div v-if="labNotifs.length === 0" class="la-dash-section p-5 text-center">
          <i class="bi bi-bell-slash" style="font-size:2rem;color:#475569;display:block;margin-bottom:0.75rem;"></i>
          <span class="text-muted small">No notifications yet</span>
        </div>
        <div v-for="n in labNotifs" :key="n.id" class="la-dash-item d-flex align-items-start gap-3 notif-item" :class="{ 'notif-unread': !n.read }" @click="store.markNotifRead(n.id)">
          <div class="notif-icon-lab" :style="{ background: n.color + '18', color: n.color }">
            <i :class="'bi bi-' + n.icon"></i>
          </div>
          <div class="flex-grow-1 min-w-0">
            <p class="m-0 text-light small fw-semibold">{{ n.message }}</p>
            <small class="text-muted">{{ n.timestamp }}</small>
          </div>
          <span v-if="!n.read" class="notif-dot-lab"></span>
        </div>
      </div>

      <!-- ─── QR SCANNER / ATTENDANCE TAB ─── -->
      <div v-else-if="currentTab === 'scanner'" class="la-content">
        <LabAdminScanner />
      </div>

      <!-- ─── CONFIRM APPROVAL MODAL (Note field removed, uses real data) ─── -->
      <transition name="la-modal-fade">
        <div v-if="approveTarget" class="la-overlay" @click.self="approveTarget = null">
          <div class="la-modal" style="max-width:420px;">
            <div class="la-modal-icon-box la-modal-icon-success"><i class="bi bi-check-circle-fill"></i></div>
            <h4 class="la-modal-title">Confirm Approval</h4>
            <p class="la-modal-sub">This will approve the venue booking and make the event active.</p>
            <div class="la-modal-summary">
              <div class="la-ms-row"><span class="la-ms-lbl">Event</span><span class="la-ms-val">{{ approveTarget.name }}</span></div>
              <div class="la-ms-row"><span class="la-ms-lbl">Venue</span><span class="la-ms-val">{{ formatVenue(approveTarget.venue) }}</span></div>
              <div class="la-ms-row"><span class="la-ms-lbl">Date</span><span class="la-ms-val">{{ approveTarget.date }}</span></div>
              <div class="la-ms-row"><span class="la-ms-lbl">Participants</span><span class="la-ms-val">{{ approveTarget.participants }}</span></div>
            </div>
            <div class="la-modal-actions">
              <button class="la-btn la-btn-ghost" :disabled="isActionLoading" @click="approveTarget = null">Cancel</button>
              <button class="la-btn la-btn-primary" :disabled="isActionLoading" @click="confirmApprove">
                <span v-if="isActionLoading" class="spinner-border spinner-border-sm me-1"></span>
                Confirm Approval
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- ─── REJECT REQUEST MODAL (Enum dropdowns + date picker) ─── -->
      <transition name="la-modal-fade">
        <div v-if="rejectTarget" class="la-overlay" @click.self="rejectTarget = null">
          <div class="la-modal" style="max-width:460px;">
            <div class="la-modal-icon-box la-modal-icon-danger"><i class="bi bi-x-circle-fill"></i></div>
            <h4 class="la-modal-title">Reject Request</h4>
            <p class="la-modal-sub">Provide a reason so the organizer can adjust and resubmit.</p>
            <div class="la-modal-form">
              <div class="la-mf-group">
                <label class="la-mf-lbl">Reason <span class="required">*</span></label>
                <select v-model="rejectReason" class="la-mf-select">
                  <option value="" disabled>Select reason</option>
                  <option value="venue_not_available">Venue not available</option>
                  <option value="time_slot_conflict">Time slot conflict</option>
                  <option value="equipment_not_available">Equipment not available</option>
                  <option value="capacity_exceeded">Capacity exceeded</option>
                  <option value="incomplete_information">Incomplete information</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="la-mf-group">
                <label class="la-mf-lbl">Alternative venue</label>
                <select v-model="rejectAltVenue" class="la-mf-select">
                  <option value="">— None suggested —</option>
                  <option v-for="v in venueOptions.filter(opt => opt.value !== 'all')" :key="v.value" :value="v.value">
                    {{ v.label }}
                  </option>
                </select>
              </div>
              <div class="la-mf-group">
                <label class="la-mf-lbl">Alternative date</label>
                <input type="date" v-model="rejectAltDate" class="la-mf-input" />
              </div>
              <div class="la-mf-group">
                <label class="la-mf-lbl">Admin comments</label>
                <textarea v-model="rejectComments" class="la-mf-textarea" rows="3" placeholder="Additional feedback for the organizer..."></textarea>
              </div>
            </div>
            <div class="la-modal-actions">
              <button class="la-btn la-btn-ghost" :disabled="isActionLoading" @click="rejectTarget = null">Cancel</button>
              <button class="la-btn la-btn-danger" :disabled="!rejectReason || isActionLoading" @click="confirmReject">
                <span v-if="isActionLoading" class="spinner-border spinner-border-sm me-1"></span>
                Reject Request
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- ─── TOAST ─── -->
      <transition name="la-toast-fade">
        <div v-if="toast" class="la-toast" :class="'la-toast-' + toast.type">
          <i :class="'bi bi-' + toast.icon" style="font-size:1.1rem;"></i>
          <span>{{ toast.message }}</span>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store/mockData';
import { updateEventApi } from '../api/events';
import Sidebar from './shared/Sidebar.vue';
import TopHeader from './shared/TopHeader.vue';
import LabAdminScanner from './shared/LabAdminScanner.vue';

const router = useRouter();

onMounted(() => {
  store.fetchEvents();
});

const currentTab = ref('dashboard');
const calVenue = ref('all');
const calOffset = ref(0);
const selectedDate = ref(null);
const highlightedId = ref(null);
const queueSearch = ref('');
const isActionLoading = ref(false);

const labNotifs = computed(() => store.notifications.filter(n => n.role === 'lab_admin'));
const labNotifCount = computed(() => labNotifs.value.filter(n => !n.read).length);

const adminInitials = computed(() => {
  const name = store.currentUser?.full_name || 'Lab Admin';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
});

const navItems = computed(() => [
  { label: 'Dashboard', icon: 'bar-chart-fill', key: 'dashboard' },
  { label: 'Event Approvals', icon: 'check-circle-fill', key: 'approvals' },
  { label: 'Events', icon: 'calendar-event-fill', key: 'events' },
  { label: 'QR Scanner', icon: 'qr-code-scan', key: 'scanner' },
]);

const venueOptions = [
  { value: 'all', label: 'All Venues' },
  { value: 'seminar_hall', label: 'Seminar Hall' },
  { value: 'auditorium', label: 'Auditorium' },
  { value: 'innovation_lab', label: 'Innovation Lab' },
  { value: 'robotics_lab', label: 'Robotics Lab' },
  { value: 'computer_lab_1', label: 'Computer Lab 1' },
  { value: 'computer_lab_2', label: 'Computer Lab 2' },
  { value: 'conference_room', label: 'Conference Room' },
  { value: 'classroom', label: 'Classroom' },
  { value: 'main_ground', label: 'Main Ground' },
  { value: 'online', label: 'Online' },
  { value: 'other', label: 'Other' },
];

const formatVenue = (v) => {
  if (!v) return 'TBD';
  const found = venueOptions.find(opt => opt.value === String(v).toLowerCase());
  if (found && found.value !== 'all') return found.label;
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const venueMatches = (eventVenue, selectedVenue) => {
  if (!selectedVenue || selectedVenue === 'all') return true;
  const evNorm = (eventVenue || '').toLowerCase().replace(/[\s_-]+/g, '');
  const selNorm = selectedVenue.toLowerCase().replace(/[\s_-]+/g, '');
  return evNorm === selNorm || evNorm.includes(selNorm) || selNorm.includes(evNorm);
};

const humanizeRejectionReason = (reason) => {
  const map = {
    venue_not_available: 'Venue Not Available',
    time_slot_conflict: 'Time Slot Conflict',
    equipment_not_available: 'Equipment Not Available',
    capacity_exceeded: 'Capacity Exceeded',
    incomplete_information: 'Incomplete Information',
    other: 'Other',
  };
  return map[reason] || reason;
};

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/* ── Date helpers ── */
const now = new Date();
const today = { date: now.getDate(), month: now.getMonth(), year: now.getFullYear() };

const isUpcomingOrOngoing = (event) => {
  if (!event) return false;
  const dateStr = event.event_date || event.date;
  if (!dateStr) return true;
  const eventDate = new Date(dateStr);
  if (isNaN(eventDate.getTime())) return true;
  const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
  return eventDate >= todayMidnight;
};

const isTodayBooking = (event) => {
  if (!event) return false;
  const dateStr = event.event_date || event.date;
  if (!dateStr) return false;
  const eventDate = new Date(dateStr);
  if (isNaN(eventDate.getTime())) return false;
  return (
    eventDate.getFullYear() === now.getFullYear() &&
    eventDate.getMonth() === now.getMonth() &&
    eventDate.getDate() === now.getDate()
  );
};

const goToday = () => {
  calOffset.value = 0;
  selectedDate.value = today.date;
};

/* ── Filtered event lists ── */
const pendingEvents = computed(() => {
  return store.events.filter(e => e.status === 'Pending' || e.rawStatus === 'pending');
});

const todayBookingsCount = computed(() => {
  return store.events.filter(e => (e.status === 'Approved' || e.rawStatus === 'approved') && isTodayBooking(e)).length;
});

const approvedAndRejectedEvents = computed(() => {
  return store.events
    .filter(e => (e.status === 'Approved' || e.status === 'Rejected' || e.rawStatus === 'approved' || e.rawStatus === 'rejected') && isUpcomingOrOngoing(e))
    .sort((a, b) => new Date(a.event_date || a.date) - new Date(b.event_date || b.date));
});

/* ── Metrics: Only 2 metrics ── */
const stats = computed(() => [
  { label: 'Pending', value: pendingEvents.value.length, icon: 'clock-fill', bg: 'rgba(251,191,36,0.12)', color: '#fbbf24' },
  { label: "Today's Bookings", value: todayBookingsCount.value, icon: 'calendar-check-fill', bg: 'rgba(52,211,153,0.12)', color: '#34d399' },
]);

/* ── Calendar helpers ── */
const calLabel = computed(() => {
  const d = new Date(today.year, today.month + calOffset.value, 1);
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
});

const monthWeeks = computed(() => {
  const d = new Date(today.year, today.month + calOffset.value, 1);
  const month = d.getMonth();
  const year = d.getFullYear();
  const firstDow = d.getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevMonthDays = new Date(year, month, 0).getDate();
  const cells = [];
  for (let i = firstDow - 1; i >= 0; i--) cells.push({ date: prevMonthDays - i, month: -1, isToday: false, bookings: [] });
  for (let i = 1; i <= daysInMonth; i++) cells.push({ date: i, month: 0, isToday: i === today.date && calOffset.value === 0, bookings: getDayBookings(i) });
  while (cells.length % 7 !== 0) { const idx = cells.length - firstDow - daysInMonth + 1; cells.push({ date: idx, month: 1, isToday: false, bookings: [] }); }
  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
  return weeks;
});

const formatDateLabel = (day) => {
  const d = new Date(today.year, today.month + calOffset.value, day);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

/* ── Bookings data: filtered by venue, upcoming/ongoing only, no rejected ── */
const getDayBookings = (day) => {
  const targetDate = new Date(today.year, today.month + calOffset.value, day);
  const curMonth = targetDate.getMonth();
  const curYear = targetDate.getFullYear();

  return store.events
    .filter(e => {
      if (e.status === 'Rejected' || e.rawStatus === 'rejected') return false;
      if (!isUpcomingOrOngoing(e)) return false;
      if (!venueMatches(e.venue, calVenue.value)) return false;

      const dateStr = e.event_date || e.date;
      if (!dateStr) return false;
      const evDate = new Date(dateStr);
      if (isNaN(evDate.getTime())) return false;
      return (
        evDate.getDate() === day &&
        evDate.getMonth() === curMonth &&
        evDate.getFullYear() === curYear
      );
    })
    .map(e => ({
      id: e.id,
      name: e.name,
      status: (e.status || 'Pending').toLowerCase(),
      venue: formatVenue(e.venue),
    }));
};

const selectDate = (day) => {
  selectedDate.value = selectedDate.value === day ? null : day;
};

/* ── Approval Queue: Filtered by venue & upcoming ── */
const filteredQueue = computed(() => {
  let list = store.events.filter(e => {
    if (!isUpcomingOrOngoing(e)) return false;
    if (!venueMatches(e.venue, calVenue.value)) return false;
    return true;
  });

  if (selectedDate.value !== null) {
    const targetDate = new Date(today.year, today.month + calOffset.value, selectedDate.value);
    const curMonth = targetDate.getMonth();
    const curYear = targetDate.getFullYear();

    list = list.filter(e => {
      const dateStr = e.event_date || e.date;
      if (!dateStr) return false;
      const evDate = new Date(dateStr);
      if (isNaN(evDate.getTime())) return false;
      return (
        evDate.getDate() === selectedDate.value &&
        evDate.getMonth() === curMonth &&
        evDate.getFullYear() === curYear
      );
    });
  }

  if (queueSearch.value) {
    const q = queueSearch.value.toLowerCase();
    list = list.filter(e =>
      e.name.toLowerCase().includes(q) ||
      (e.venue || '').toLowerCase().includes(q) ||
      (e.short_description || '').toLowerCase().includes(q)
    );
  }

  list.sort((a, b) => {
    if (a.status === 'Pending' && b.status !== 'Pending') return -1;
    if (a.status !== 'Pending' && b.status === 'Pending') return 1;
    return new Date(a.event_date || a.date) - new Date(b.event_date || b.date);
  });
  return list;
});

const hasConflict = (ev) => {
  const sameVenue = store.events.filter(e => e.venue === ev.venue && e.id !== ev.id && e.status === 'Approved');
  return sameVenue.some(e => {
    return (e.event_date || e.date) === (ev.event_date || ev.date);
  });
};

/* ── Navigation ── */
const goToEventDetails = (ev) => {
  if (!ev) return;
  if (typeof ev === 'object' && ev.name) {
    router.push({ name: 'event-details', params: { eventName: encodeURIComponent(ev.name) } });
  } else if (typeof ev === 'object' && ev.id) {
    router.push({ name: 'event-details-by-id', params: { id: ev.id } });
  } else {
    const found = store.events.find(e => e.id === ev);
    if (found?.name) {
      router.push({ name: 'event-details', params: { eventName: encodeURIComponent(found.name) } });
    } else {
      router.push(`/events/${ev}`);
    }
  }
};

const openReview = (ev) => {
  goToEventDetails(ev);
};

/* ── Approve ── */
const approveTarget = ref(null);

const openApprove = (ev) => {
  approveTarget.value = ev;
};

const confirmApprove = async () => {
  if (!approveTarget.value) return;
  isActionLoading.value = true;
  try {
    const token = store.token || localStorage.getItem('driven_token');
    await updateEventApi(approveTarget.value.id, { status: 'approved' }, token);
    await store.fetchEvents();
    showToast('check-circle-fill', 'success', `"${approveTarget.value.name}" approved successfully`);
    approveTarget.value = null;
  } catch (err) {
    showToast('exclamation-triangle-fill', 'danger', err.message || 'Failed to approve event');
  } finally {
    isActionLoading.value = false;
  }
};

/* ── Reject ── */
const rejectTarget = ref(null);
const rejectReason = ref('');
const rejectAltVenue = ref('');
const rejectAltDate = ref('');
const rejectComments = ref('');

const openReject = (ev) => {
  rejectTarget.value = ev;
  rejectReason.value = '';
  rejectAltVenue.value = '';
  rejectAltDate.value = '';
  rejectComments.value = '';
};

const confirmReject = async () => {
  if (!rejectTarget.value || !rejectReason.value) return;
  isActionLoading.value = true;
  try {
    const token = store.token || localStorage.getItem('driven_token');
    const payload = {
      status: 'rejected',
      rejection_reason: {
        reason: rejectReason.value,
        alternative_venue: rejectAltVenue.value || null,
        alternative_date: rejectAltDate.value || null,
        admin_comment: rejectComments.value ? rejectComments.value.trim() : null,
      },
    };
    await updateEventApi(rejectTarget.value.id, payload, token);
    await store.fetchEvents();
    showToast('x-circle-fill', 'danger', `"${rejectTarget.value.name}" rejected`);
    rejectTarget.value = null;
  } catch (err) {
    showToast('exclamation-triangle-fill', 'danger', err.message || 'Failed to reject event');
  } finally {
    isActionLoading.value = false;
  }
};

/* ── Toast ── */
const toast = ref(null);

const showToast = (icon, type, message) => {
  toast.value = { icon, message, type };
  setTimeout(() => { toast.value = null; }, 3200);
};
</script>

<style scoped>
.la-page { display: flex; min-height: 100vh; background: #0c1220; overflow-x: hidden; }
.la-wrapper { margin-left: 240px; flex: 1; display: flex; flex-direction: column; }
.la-content { padding: 1.25rem 2rem 3rem; flex: 1; }

/* ── Stats ── */
.la-stats-row { display: flex; gap: 0.85rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.la-stat { flex: 1; min-width: 180px; max-width: 320px; display: flex; align-items: center; gap: 0.85rem; padding: 1rem 1.25rem; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); transition: all 0.2s; }
.la-stat:hover { border-color: rgba(129,140,248,0.2); }
.la-stat-icon { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.la-stat-body { display: flex; flex-direction: column; }
.la-stat-value { font-size: 1.35rem; font-weight: 800; color: #f1f5f9; line-height: 1.2; letter-spacing: -0.3px; }
.la-stat-label { font-size: 0.72rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }

/* ── Main Layout ── */
.la-main-layout { display: flex; gap: 1.25rem; align-items: flex-start; }

/* ── Calendar Section ── */
.la-cal-section { flex: 1; min-width: 0; background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); padding: 1.25rem; }

.la-cal-topbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }
.la-venue-picker { display: flex; align-items: center; gap: 0.4rem; }
.la-venue-select { padding: 0.4rem 1.5rem 0.4rem 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #e2e8f0; font-size: 0.8rem; font-family: inherit; outline: none; cursor: pointer; transition: all 0.2s; min-width: 140px; }
.la-venue-select:focus { border-color: rgba(129,140,248,0.4); }
.la-venue-select option { background: #0f172a; color: #e2e8f0; }
.la-cal-nav { display: flex; align-items: center; gap: 0.4rem; }
.la-cal-nav-btn { width: 28px; height: 28px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.03); color: #64748b; font-size: 0.65rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.la-cal-nav-btn:hover { background: rgba(255,255,255,0.07); color: #94a3b8; }
.la-cal-label { font-size: 0.85rem; font-weight: 700; color: #e2e8f0; min-width: 120px; text-align: center; }
.la-today-btn { padding: 0.35rem 0.8rem; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; background: rgba(255,255,255,0.03); color: #94a3b8; font-size: 0.72rem; font-weight: 600; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-today-btn:hover { background: rgba(129,140,248,0.1); border-color: rgba(129,140,248,0.2); color: #818cf8; }

/* ── Month ── */
.la-cal-month { }
.la-cal-row { display: grid; grid-template-columns: repeat(7, 1fr); }
.la-cal-header { margin-bottom: 2px; }
.la-cal-hd { text-align: center; font-size: 0.65rem; font-weight: 700; color: #64748b; padding: 0.35rem 0; text-transform: uppercase; letter-spacing: 0.04em; }
.la-cal-cell { min-height: 84px; padding: 0.35rem 0.45rem; border-radius: 10px; cursor: default; transition: all 0.15s; border: 1px solid transparent; margin: 1px; position: relative; }
.la-cell-clickable { cursor: pointer; }
.la-cell-clickable:hover { background: rgba(255,255,255,0.04); }
.la-cell-today { background: rgba(129,140,248,0.06); border-color: rgba(129,140,248,0.15); }
.la-cell-selected { background: rgba(129,140,248,0.12); border-color: rgba(129,140,248,0.3) !important; }
.la-cell-other .la-cell-num { color: #2a3040; }
.la-cell-num { font-size: 0.75rem; font-weight: 700; color: #94a3b8; display: block; margin-bottom: 3px; }
.la-cell-today .la-cell-num { color: #818cf8; }
.la-cell-bookings { display: flex; flex-direction: column; gap: 2px; }
.la-cell-bk { font-size: 0.6rem; font-weight: 700; padding: 0.15rem 0.35rem; border-radius: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff; cursor: pointer; transition: opacity 0.15s; }
.la-cell-bk:hover { opacity: 0.85; }
.la-bk-approved { background: rgba(52,211,153,0.45); border-left: 2px solid #34d399; }
.la-bk-pending { background: rgba(129,140,248,0.4); border-left: 2px solid #818cf8; }
.la-cell-more { font-size: 0.58rem; color: #64748b; padding-left: 0.3rem; }

/* ── Legend ── */
.la-legend { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem; padding-top: 0.65rem; border-top: 1px solid rgba(255,255,255,0.05); }
.la-legend-item { display: flex; align-items: center; gap: 0.35rem; font-size: 0.68rem; color: #94a3b8; }
.la-legend-dot { width: 8px; height: 8px; border-radius: 50%; }
.la-legend-approved { background: #34d399; }
.la-legend-pending { background: #818cf8; }

/* ── Queue Section ── */
.la-queue-section { width: 340px; flex-shrink: 0; background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); display: flex; flex-direction: column; max-height: calc(100vh - 200px); }
.la-queue-header { display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem 1.1rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); flex-shrink: 0; }
.la-queue-title { font-size: 0.9rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.la-queue-subtitle { font-size: 0.68rem; color: #64748b; display: block; margin-top: 2px; }
.la-queue-search { padding: 0.5rem 1.1rem; flex-shrink: 0; }
.la-qs-input { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; box-sizing: border-box; transition: all 0.2s; }
.la-qs-input:focus { border-color: rgba(129,140,248,0.3); }
.la-queue-list { flex: 1; overflow-y: auto; padding: 0.5rem 1.1rem 1rem; }
.la-queue-list::-webkit-scrollbar { width: 3px; }
.la-queue-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 99px; }
.la-queue-empty { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 2rem 0; color: #64748b; font-size: 0.8rem; text-align: center; }
.la-queue-empty i { font-size: 1.5rem; }

.la-queue-item { padding: 0.75rem 0.85rem; border-radius: 12px; margin-bottom: 0.45rem; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; background: rgba(255,255,255,0.02); }
.la-queue-item:hover { background: rgba(255,255,255,0.04); }
.la-qi-highlight { border-color: rgba(129,140,248,0.2) !important; background: rgba(129,140,248,0.06) !important; }
.la-qi-pending { border-left: 3px solid rgba(129,140,248,0.4); }
.la-qi-approved { border-left: 3px solid rgba(52,211,153,0.4); }
.la-qi-rejected { border-left: 3px solid rgba(244,63,94,0.3); opacity: 0.65; }
.la-qi-top { }
.la-qi-title { font-size: 0.82rem; color: #e2e8f0; display: block; margin-bottom: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.la-qi-meta { display: flex; justify-content: space-between; font-size: 0.68rem; color: #64748b; margin-bottom: 2px; flex-wrap: wrap; }
.la-qi-meta i { margin-right: 0.25rem; font-size: 0.65rem; }
.la-qi-conflict { display: flex; align-items: center; gap: 0.3rem; font-size: 0.62rem; color: #fb7185; margin-top: 0.3rem; }
.la-qi-actions { display: flex; gap: 0.35rem; margin-top: 0.5rem; }
.la-qi-btn { padding: 0.28rem 0.6rem; border: none; border-radius: 6px; font-size: 0.65rem; font-weight: 700; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-qi-btn-review { background: rgba(255,255,255,0.06); color: #94a3b8; }
.la-qi-btn-review:hover { background: rgba(255,255,255,0.12); color: #cbd5e1; }
.la-qi-btn-approve { background: rgba(52,211,153,0.15); color: #34d399; }
.la-qi-btn-approve:hover { background: rgba(52,211,153,0.25); }
.la-qi-btn-reject { background: rgba(244,63,94,0.15); color: #fb7185; }
.la-qi-btn-reject:hover { background: rgba(244,63,94,0.25); }
.la-qi-done { font-size: 0.65rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; padding: 0.25rem 0.5rem; }

/* ── Dashboard List ── */
.la-dash-section { background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); padding: 1.25rem; }
.la-dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.la-dash-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.la-dash-subtitle { font-size: 0.75rem; color: #64748b; }
.la-dash-list { display: flex; flex-direction: column; gap: 0.5rem; }
.la-dash-item { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0.85rem; border-radius: 12px; background: rgba(255,255,255,0.02); border: 1px solid transparent; transition: all 0.2s; }
.la-dash-item:hover { background: rgba(255,255,255,0.04); }
.la-dash-pending { border-left: 3px solid rgba(129,140,248,0.4); }
.la-dash-item-left { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; }
.la-dash-item-img { width: 48px; height: 48px; border-radius: 10px; background-size: cover; background-position: center; flex-shrink: 0; }
.la-dash-item-body { min-width: 0; }
.la-dash-item-title-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.2rem; }
.la-dash-item-title { font-size: 0.85rem; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.la-dash-item-meta { display: flex; gap: 0.75rem; font-size: 0.68rem; color: #64748b; flex-wrap: wrap; }
.la-dash-item-meta i { margin-right: 0.2rem; font-size: 0.65rem; }
.la-dash-item-actions { display: flex; gap: 0.4rem; flex-shrink: 0; margin-left: 0.75rem; }

/* ── Status Badges ── */
.la-status-badge { font-size: 0.62rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.03em; }
.la-status-pending { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.2); }
.la-status-approved { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.2); }
.la-status-rejected { background: rgba(244,63,94,0.12); color: #fb7185; border: 1px solid rgba(244,63,94,0.2); }

/* ── Events Tab Cards ── */
.la-event-card { background: rgba(15,23,42,0.45); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; overflow: hidden; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); cursor: pointer; transition: all 0.25s ease; }
.la-event-card:hover { transform: translateY(-3px); border-color: rgba(129,140,248,0.3); box-shadow: 0 12px 30px rgba(0,0,0,0.35); }
.la-event-card-img { height: 140px; background-size: cover; background-position: center; position: relative; }
.la-event-img-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(7,11,20,0.3) 0%, rgba(7,11,20,0.85) 100%); }
.la-event-date-tag { font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.55rem; border-radius: 6px; background: rgba(15,23,42,0.75); color: #e2e8f0; backdrop-filter: blur(4px); border: 1px solid rgba(255,255,255,0.08); }
.la-event-card-meta { display: flex; gap: 0.85rem; font-size: 0.72rem; color: #94a3b8; }
.la-rejection-info { background: rgba(244,63,94,0.08); border: 1px solid rgba(244,63,94,0.15); }
.la-btn-view-details { padding: 0.45rem 0.85rem; border-radius: 8px; border: 1px solid rgba(129,140,248,0.2); background: rgba(129,140,248,0.08); color: #818cf8; font-size: 0.75rem; font-weight: 700; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-btn-view-details:hover { background: rgba(129,140,248,0.18); border-color: rgba(129,140,248,0.4); color: #a5b4fc; }
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* ── Notifications ── */
.notif-item { border: 1px solid transparent; transition: all 0.2s; cursor: pointer; }
.notif-item:hover { background: rgba(255,255,255,0.04); }
.notif-icon-lab { width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; }
.notif-dot-lab { width: 8px; height: 8px; border-radius: 50%; background: #818cf8; flex-shrink: 0; margin-top: 0.35rem; }
.notif-unread { background: rgba(129,140,248,0.04) !important; border-left: 3px solid rgba(129,140,248,0.2) !important; }

/* ── Modal ── */
.la-overlay { position: fixed; inset: 0; background: rgba(7,11,20,0.65); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); z-index: 500; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.la-modal { width: 100%; background: rgba(15,23,42,0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); box-shadow: 0 24px 64px rgba(0,0,0,0.4); padding: 1.5rem; }
.la-modal-icon-box { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; font-size: 1.3rem; }
.la-modal-icon-success { background: rgba(52,211,153,0.1); color: #34d399; }
.la-modal-icon-danger { background: rgba(244,63,94,0.1); color: #fb7185; }
.la-modal-title { text-align: center; font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.2rem; }
.la-modal-sub { text-align: center; font-size: 0.78rem; color: #64748b; margin: 0 0 1rem; line-height: 1.5; }
.la-modal-summary { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 0.6rem 0.85rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.04); }
.la-ms-row { display: flex; justify-content: space-between; padding: 0.35rem 0; font-size: 0.78rem; }
.la-ms-row:not(:last-child) { border-bottom: 1px solid rgba(255,255,255,0.04); }
.la-ms-lbl { color: #64748b; }
.la-ms-val { color: #e2e8f0; font-weight: 600; }
.la-modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 1rem; }
.la-btn { padding: 0.45rem 1rem; border-radius: 10px; font-size: 0.78rem; font-weight: 700; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-btn-ghost { border: 1px solid rgba(255,255,255,0.1); background: transparent; color: #94a3b8; }
.la-btn-ghost:hover { background: rgba(255,255,255,0.04); color: #e2e8f0; }
.la-btn-primary { border: none; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; box-shadow: 0 4px 16px rgba(99,102,241,0.2); }
.la-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(99,102,241,0.3); }
.la-btn-danger { border: none; background: rgba(244,63,94,0.15); color: #fb7185; }
.la-btn-danger:hover { background: rgba(244,63,94,0.25); }
.la-btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Modal Form ── */
.la-modal-form { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 0.75rem; }
.la-mf-group { }
.la-mf-lbl { display: block; font-size: 0.72rem; font-weight: 600; color: rgba(255,255,255,0.92); margin-bottom: 0.25rem; }
.la-mf-select { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.08); border-radius: 10px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; cursor: pointer; }
.la-mf-select:focus { border-color: rgba(129,140,248,0.4); }
.la-mf-select option { background: #0f172a; color: #e2e8f0; }
.la-mf-input { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.08); border-radius: 10px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; }
.la-mf-input:focus { border-color: rgba(129,140,248,0.4); }
.la-mf-textarea { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.08); border-radius: 10px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; resize: vertical; line-height: 1.5; }
.la-mf-textarea:focus { border-color: rgba(129,140,248,0.4); }
.la-mf-textarea::placeholder { color: rgba(255,255,255,0.4); }
.required { color: #fb7185; }

/* ── Toast ── */
.la-toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: center; gap: 0.6rem; padding: 0.65rem 1.1rem; border-radius: 14px; font-size: 0.8rem; font-weight: 600; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); z-index: 999; }
.la-toast-success { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.25); color: #34d399; }
.la-toast-danger { background: rgba(244,63,94,0.12); border: 1px solid rgba(244,63,94,0.25); color: #fb7185; }
.la-toast-info { background: rgba(129,140,248,0.12); border: 1px solid rgba(129,140,248,0.25); color: #818cf8; }

/* ── Transitions ── */
.la-modal-fade-enter-active, .la-modal-fade-leave-active { transition: all 0.2s ease; }
.la-modal-fade-enter-from, .la-modal-fade-leave-to { opacity: 0; transform: scale(0.95); }
.la-toast-fade-enter-active, .la-toast-fade-leave-active { transition: all 0.3s ease; }
.la-toast-fade-enter-from, .la-toast-fade-leave-to { opacity: 0; transform: translateY(16px); }
</style>
