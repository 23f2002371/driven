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

      <div v-if="currentTab === 'dashboard'" class="la-content">
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
              <h4 class="la-dash-title">All Event Requests</h4>
              <span class="la-dash-subtitle">{{ store.events.length }} total requests</span>
            </div>
            <button class="la-today-btn" @click="currentTab = 'approvals'">
              <i class="bi bi-arrow-right me-1"></i>Go to Approvals
            </button>
          </div>
          <div class="la-dash-list">
            <div
              v-for="ev in sortedEvents"
              :key="ev.id"
              class="la-dash-item"
              :class="'la-dash-' + ev.status.toLowerCase()"
            >
              <div class="la-dash-item-left">
                <div class="la-dash-item-img" :style="{ backgroundImage: `url(${ev.image})` }"></div>
                <div class="la-dash-item-body">
                  <div class="la-dash-item-title-row">
                    <strong class="la-dash-item-title">{{ ev.name }}</strong>
                    <span class="la-status-badge" :class="'la-status-' + ev.status.toLowerCase()">{{ ev.status }}</span>
                  </div>
                  <div class="la-dash-item-meta">
                    <span><i class="bi bi-geo-alt"></i>{{ ev.venue }}</span>
                    <span><i class="bi bi-calendar"></i>{{ ev.date }}</span>
                    <span><i class="bi bi-people"></i>{{ ev.participants }} participants</span>
                  </div>
                </div>
              </div>
              <div class="la-dash-item-actions">
                <button class="la-qi-btn la-qi-btn-review" @click="openReview(ev)">Review</button>
                <button v-if="ev.status === 'Pending'" class="la-qi-btn la-qi-btn-approve" @click="openApprove(ev)">Approve</button>
                <button v-if="ev.status === 'Pending'" class="la-qi-btn la-qi-btn-reject" @click="openReject(ev)">Reject</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="currentTab === 'approvals'" class="la-content">

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
                <i class="bi bi-geo-alt-fill" style="color:#818cf8;font-size:0.8rem;"></i>
                <select v-model="calVenue" class="la-venue-select">
                  <option v-for="v in venues" :key="v" :value="v">{{ v }}</option>
                </select>
              </div>
              <div class="la-cal-nav">
                <button class="la-cal-nav-btn" @click="calOffset--"><i class="bi bi-chevron-left"></i></button>
                <span class="la-cal-label">{{ calLabel }}</span>
                <button class="la-cal-nav-btn" @click="calOffset++"><i class="bi bi-chevron-right"></i></button>
              </div>
              <button class="la-today-btn" @click="goToday">Today</button>
              <div class="la-view-toggle">
                <button :class="{ active: calView === 'month' }" @click="calView='month'">Month</button>
                <button :class="{ active: calView === 'week' }" @click="calView='week'">Week</button>
                <button :class="{ active: calView === 'day' }" @click="calView='day'">Day</button>
              </div>
            </div>

            <!-- Month View -->
            <div v-if="calView === 'month'" class="la-cal-month">
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
                      :title="bk.name"
                    >{{ bk.name }}</div>
                    <div v-if="day.bookings.length > 2" class="la-cell-more">+{{ day.bookings.length - 2 }} more</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Week View -->
            <div v-if="calView === 'week'" class="la-cal-week">
              <div class="la-week-header">
                <div class="la-week-gutter"></div>
                <div
                  v-for="d in weekDays"
                  :key="d.iso"
                  class="la-week-hd-cell"
                  :class="{ 'la-week-hd-today': d.isToday }"
                  @click="selectDate(d.day)"
                >
                  <span class="la-week-hd-day">{{ d.name }}</span>
                  <span class="la-week-hd-num">{{ d.day }}</span>
                </div>
              </div>
              <div class="la-week-body">
                <div class="la-week-times">
                  <div v-for="h in hours" :key="h" class="la-week-time">{{ h }}:00</div>
                </div>
                <div class="la-week-grid">
                  <div v-for="d in weekDays" :key="d.iso" class="la-week-col">
                    <div
                      v-for="h in hours"
                      :key="h"
                      class="la-week-slot"
                      :class="getSlotClass(d.day, h)"
                      @click="slotClicked(d.day, h)"
                    >
                      <span v-if="getSlotLabel(d.day, h)" class="la-slot-label">{{ getSlotLabel(d.day, h) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Day View -->
            <div v-if="calView === 'day'" class="la-cal-day">
              <div class="la-day-header">{{ formatDayHeader(selectedDayDate) }}</div>
              <div class="la-day-body">
                <div v-for="h in hours" :key="h" class="la-day-row">
                  <span class="la-day-time">{{ h }}:00</span>
                  <div
                    class="la-day-slot"
                    :class="getSlotClass(selectedDayDate, h)"
                    @click="slotClicked(selectedDayDate, h)"
                  >
                    <span v-if="getSlotLabel(selectedDayDate, h)" class="la-slot-label">{{ getSlotLabel(selectedDayDate, h) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="la-legend">
              <span class="la-legend-item"><span class="la-legend-dot la-legend-approved"></span> Approved</span>
              <span class="la-legend-item"><span class="la-legend-dot la-legend-pending"></span> Pending</span>
              <span class="la-legend-item"><span class="la-legend-dot la-legend-rejected"></span> Rejected</span>
              <span class="la-legend-item"><span class="la-legend-dot la-legend-maintenance"></span> Maintenance</span>
            </div>
          </div>

          <!-- ─── APPROVAL QUEUE (right 35%) ─── -->
          <div class="la-queue-section">
            <div class="la-queue-header">
              <div>
                <h5 class="la-queue-title">Approval Queue</h5>
                <span class="la-queue-subtitle">
                  {{ filteredQueue.length }} request{{ filteredQueue.length !== 1 ? 's' : '' }}
                  <span v-if="selectedDate"> for {{ formatDateLabel(selectedDate) }}</span>
                </span>
              </div>

            </div>

            <div class="la-queue-list">
              <div v-if="filteredQueue.length === 0" class="la-queue-empty">
                <i class="bi bi-inbox"></i>
                <span>No requests match</span>
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
                    <span><i class="bi bi-person"></i>{{ ev.club || 'Student Club' }}</span>
                    <span><i class="bi bi-geo-alt"></i>{{ ev.venue }}</span>
                  </div>
                  <div class="la-qi-meta">
                    <span><i class="bi bi-calendar"></i>{{ ev.date }} {{ ev.time || '09:00' }}</span>
                    <span><i class="bi bi-people"></i>{{ ev.participants }}</span>
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

      <!-- ─── REVIEW SLIDE-OVER ─── -->
      <transition name="la-slide-over">
        <div v-if="reviewTarget" class="la-overlay" @click.self="reviewTarget = null">
          <div class="la-slide">
            <div class="la-slide-top">
              <div class="la-slide-banner" :style="{ backgroundImage: `url(${reviewTarget.image})` }">
                <div class="la-slide-banner-overlay">
                  <button class="la-slide-close" @click="reviewTarget = null"><i class="bi bi-x-lg"></i></button>
                  <span class="la-slide-badge" :class="'la-badge-' + reviewTarget.status.toLowerCase()">{{ reviewTarget.status }}</span>
                </div>
              </div>
              <div class="la-slide-header">
                <h3 class="la-slide-title">{{ reviewTarget.name }}</h3>
                <p class="la-slide-organizer"><i class="bi bi-person-badge me-1"></i>{{ reviewTarget.club || 'Student Tech Club' }}</p>
              </div>
            </div>

            <div class="la-slide-body">
              <section class="la-ss">
                <h6 class="la-ss-title"><i class="bi bi-info-circle me-2"></i>Event Description</h6>
                <p class="la-ss-desc">{{ reviewTarget.description }}</p>
              </section>

              <section class="la-ss">
                <h6 class="la-ss-title"><i class="bi bi-diagram-3 me-2"></i>Resource Requirements</h6>
                <div class="la-ss-grid">
                  <div class="la-ss-item"><span class="la-ss-lbl">Venue</span><span class="la-ss-val">{{ reviewTarget.venue }}</span></div>
                  <div class="la-ss-item"><span class="la-ss-lbl">Date &amp; Time</span><span class="la-ss-val">{{ reviewTarget.date }} {{ reviewTarget.time || '09:00 - 17:00' }}</span></div>
                  <div class="la-ss-item"><span class="la-ss-lbl">Participants</span><span class="la-ss-val">{{ reviewTarget.participants }}</span></div>
                  <div class="la-ss-item"><span class="la-ss-lbl">Equipment</span><span class="la-ss-val">{{ reviewTarget.equipment?.join(', ') || 'Standard AV' }}</span></div>
                  <div class="la-ss-item"><span class="la-ss-lbl">Staff Required</span><span class="la-ss-val">{{ reviewTarget.staff || 2 }}</span></div>
                  <div class="la-ss-item"><span class="la-ss-lbl">Contact</span><span class="la-ss-val">{{ reviewTarget.contact || 'organizer@university.edu' }}</span></div>
                </div>
              </section>

              <section class="la-ss">
                <h6 class="la-ss-title"><i class="bi bi-shield-exclamation me-2"></i>Conflict Analysis</h6>
                <div class="la-ca-list">
                  <div class="la-ca-item" :class="ca.venueClear ? 'la-ca-ok' : 'la-ca-warn'">
                    <i :class="ca.venueClear ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-2"></i>
                    <span>Venue — {{ ca.venueClear ? 'Available' : 'Another event overlaps by ' + ca.overlapHours + ' hours' }}</span>
                  </div>
                  <div class="la-ca-item" :class="ca.equipClear ? 'la-ca-ok' : 'la-ca-warn'">
                    <i :class="ca.equipClear ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-2"></i>
                    <span>Equipment — {{ ca.equipClear ? 'Sufficient stock' : 'Some items low on stock' }}</span>
                  </div>
                  <div class="la-ca-item" :class="ca.capOk ? 'la-ca-ok' : 'la-ca-warn'">
                    <i :class="ca.capOk ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-2"></i>
                    <span>Capacity — {{ ca.capOk ? 'Within venue limit' : 'Exceeds room capacity by ' + (reviewTarget.participants - 80) + ' people' }}</span>
                  </div>
                </div>
              </section>

              <section class="la-ss">
                <h6 class="la-ss-title"><i class="bi bi-card-text me-2"></i>Organizer Notes</h6>
                <p class="la-ss-desc">{{ reviewTarget.notes || 'No additional notes provided by the organizer.' }}</p>
              </section>
            </div>

            <div v-if="reviewTarget.status === 'Pending'" class="la-slide-actions">
              <button class="la-slide-btn la-slide-btn-primary" @click="openApprove(reviewTarget); reviewTarget = null">
                <i class="bi bi-check-lg me-2"></i>Approve
              </button>
              <button class="la-slide-btn la-slide-btn-danger" @click="openReject(reviewTarget); reviewTarget = null">
                <i class="bi bi-x-lg me-2"></i>Reject
              </button>
              <button class="la-slide-btn la-slide-btn-ghost" @click="addNote(reviewTarget)">
                <i class="bi bi-chat-dots me-2"></i>Add Note
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- ─── APPROVE MODAL ─── -->
      <transition name="la-modal-fade">
        <div v-if="approveTarget" class="la-overlay" @click.self="approveTarget = null">
          <div class="la-modal" style="max-width:420px;">
            <div class="la-modal-icon-box la-modal-icon-success"><i class="bi bi-check-circle-fill"></i></div>
            <h4 class="la-modal-title">Confirm Approval</h4>
            <p class="la-modal-sub">This will approve the booking and notify the organizer.</p>
            <div class="la-modal-summary">
              <div class="la-ms-row"><span class="la-ms-lbl">Event</span><span class="la-ms-val">{{ approveTarget.name }}</span></div>
              <div class="la-ms-row"><span class="la-ms-lbl">Venue</span><span class="la-ms-val">{{ approveTarget.venue }}</span></div>
              <div class="la-ms-row"><span class="la-ms-lbl">Date</span><span class="la-ms-val">{{ approveTarget.date }}</span></div>
              <div class="la-ms-row"><span class="la-ms-lbl">Participants</span><span class="la-ms-val">{{ approveTarget.participants }}</span></div>
            </div>
            <div class="la-modal-note">
              <label class="la-note-lbl">Note for organizer</label>
              <input v-model="approveNote" class="la-note-inp" placeholder="Optional note..." />
            </div>
            <div class="la-modal-actions">
              <button class="la-btn la-btn-ghost" @click="approveTarget = null">Cancel</button>
              <button class="la-btn la-btn-primary" @click="confirmApprove">Confirm Approval</button>
            </div>
          </div>
        </div>
      </transition>

      <!-- ─── REJECT MODAL ─── -->
      <transition name="la-modal-fade">
        <div v-if="rejectTarget" class="la-overlay" @click.self="rejectTarget = null">
          <div class="la-modal" style="max-width:440px;">
            <div class="la-modal-icon-box la-modal-icon-danger"><i class="bi bi-x-circle-fill"></i></div>
            <h4 class="la-modal-title">Reject Request</h4>
            <p class="la-modal-sub">Provide a reason so the organizer can adjust and resubmit.</p>
            <div class="la-modal-form">
              <div class="la-mf-group">
                <label class="la-mf-lbl">Reason <span class="required">*</span></label>
                <select v-model="rejectReason" class="la-mf-select">
                  <option value="" disabled>Select reason</option>
                  <option value="venue_unavailable">Venue not available</option>
                  <option value="time_conflict">Time slot conflict</option>
                  <option value="equipment_unavailable">Equipment not available</option>
                  <option value="capacity_exceeded">Capacity exceeded</option>
                  <option value="incomplete">Incomplete information</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="la-mf-group">
                <label class="la-mf-lbl">Alternative venue</label>
                <select v-model="rejectAltVenue" class="la-mf-select">
                  <option value="">— None suggested —</option>
                  <option v-for="v in venues" :key="v" :value="v">{{ v }}</option>
                </select>
              </div>
              <div class="la-mf-group">
                <label class="la-mf-lbl">Alternative date</label>
                <input v-model="rejectAltDate" class="la-mf-input" placeholder="e.g. Aug 15" />
              </div>
              <div class="la-mf-group">
                <label class="la-mf-lbl">Admin comments</label>
                <textarea v-model="rejectComments" class="la-mf-textarea" rows="2" placeholder="Additional feedback..."></textarea>
              </div>
            </div>
            <div class="la-modal-actions">
              <button class="la-btn la-btn-ghost" @click="rejectTarget = null">Cancel</button>
              <button class="la-btn la-btn-danger" :disabled="!rejectReason" @click="confirmReject">Reject Request</button>
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
import { ref, computed, reactive } from 'vue';
import { store } from '../store/mockData';
import Sidebar from './shared/Sidebar.vue';
import TopHeader from './shared/TopHeader.vue';

const currentTab = ref('dashboard');
const calVenue = ref('Lab A');
const calView = ref('month');
const calOffset = ref(0);
const selectedDate = ref(null);
const highlightedId = ref(null);
const queueSearch = ref('');


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
]);

const venues = ['Lab A', 'Lab B', 'Auditorium', 'Seminar Hall', 'Innovation Lab', 'Robotics Lab'];
const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const hours = Array.from({ length: 13 }, (_, i) => i + 7);

/* ── Date helpers ── */
const now = new Date();
const today = { date: now.getDate(), month: now.getMonth(), year: now.getFullYear() };

const goToday = () => {
  calOffset.value = 0;
  calView.value = 'month';
};

/* ── Stats ── */
const pendingCount = computed(() => store.events.filter(e => e.status === 'Pending').length);
const approvedCount = computed(() => store.events.filter(e => e.status === 'Approved').length);
const rejectedCount = computed(() => store.events.filter(e => e.status === 'Rejected').length);

const sortedEvents = computed(() => {
  return [...store.events].sort((a, b) => {
    if (a.status === 'Pending' && b.status !== 'Pending') return -1;
    if (a.status !== 'Pending' && b.status === 'Pending') return 1;
    return b.id - a.id;
  });
});

const stats = computed(() => [
  { label: 'Pending', value: pendingCount.value, icon: 'clock-fill', bg: 'rgba(251,191,36,0.12)', color: '#fbbf24' },
  { label: 'Approved', value: approvedCount.value, icon: 'check-circle-fill', bg: 'rgba(52,211,153,0.12)', color: '#34d399' },
  { label: 'Rejected', value: rejectedCount.value, icon: 'x-circle-fill', bg: 'rgba(244,63,94,0.12)', color: '#fb7185' },
  { label: 'Occupancy', value: Math.round((approvedCount.value / Math.max(store.events.length, 1)) * 100) + '%', icon: 'bar-chart-fill', bg: 'rgba(129,140,248,0.12)', color: '#818cf8' },
  { label: "Today's Bookings", value: '3', icon: 'calendar-check-fill', bg: 'rgba(52,211,153,0.08)', color: '#34d399' },
  { label: 'Upkeep', value: '2 venues', icon: 'tools', bg: 'rgba(251,191,36,0.08)', color: '#fbbf24' },
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

const weekDays = computed(() => {
  const ref = new Date(today.year, today.month + calOffset.value, 1);
  ref.setDate(ref.getDate() - ref.getDay() + (selectedDate.value || today.date) % 7);
  // Actually compute from selectedDate or today
  const base = new Date(today.year, today.month + calOffset.value, selectedDate.value || today.date);
  base.setDate(base.getDate() - base.getDay());
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(base);
    d.setDate(base.getDate() + i);
    return { name: dayNames[d.getDay()], day: d.getDate(), month: d.getMonth(), iso: d.toISOString().slice(0, 10), isToday: d.getDate() === today.date && d.getMonth() === today.month && calOffset.value === 0 };
  });
});

const selectedDayDate = computed(() => selectedDate.value || today.date);

const formatDayHeader = (day) => {
  const d = new Date(today.year, today.month + calOffset.value, day);
  return d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
};

const formatDateLabel = (day) => {
  const d = new Date(today.year, today.month + calOffset.value, day);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

/* ── Bookings data ── */
const getDayBookings = (day) => {
  return store.events.filter(e => {
    const match = e.date.match(/(\d+)/);
    const d = match ? parseInt(match[1]) : null;
    return d === day;
  }).map(e => ({ id: e.id, name: e.name, status: e.status.toLowerCase(), venue: e.venue }));
};

const getSlotClass = (day, hour) => {
  const bookings = store.events.filter(e => {
    const match = e.date.match(/(\d+)/);
    const d = match ? parseInt(match[1]) : null;
    return d === day && e.status !== 'Rejected';
  });
  if (bookings.length === 0) return 'la-slot-free';
  const statuses = bookings.map(b => b.status.toLowerCase());
  if (statuses.some(s => s === 'approved')) return 'la-slot-approved';
  if (statuses.some(s => s === 'pending')) return 'la-slot-pending';
  return 'la-slot-free';
};

const getSlotLabel = (day, hour) => {
  const booking = store.events.find(e => {
    const match = e.date.match(/(\d+)/);
    const d = match ? parseInt(match[1]) : null;
    return d === day && e.status !== 'Rejected';
  });
  return booking ? booking.name : '';
};

const slotClicked = (day, hour) => {
  selectedDate.value = day;
};

const selectDate = (day) => {
  selectedDate.value = day;
};

const isSameDay = (d1, d2) => d1 === d2;

/* ── Approval Queue ── */
const filteredQueue = computed(() => {
  let list = [...store.events];
  if (selectedDate.value !== null) {
    list = list.filter(e => {
      const match = e.date.match(/(\d+)/);
      const d = match ? parseInt(match[1]) : null;
      return d === selectedDate.value;
    });
  }
  if (queueSearch.value) {
    const q = queueSearch.value.toLowerCase();
    list = list.filter(e => e.name.toLowerCase().includes(q) || e.venue.toLowerCase().includes(q) || (e.club || '').toLowerCase().includes(q));
  }
  list.sort((a, b) => {
    if (a.status === 'Pending' && b.status !== 'Pending') return -1;
    if (a.status !== 'Pending' && b.status === 'Pending') return 1;
    return b.id - a.id;
  });
  return list;
});

const hasConflict = (ev) => {
  const sameVenue = store.events.filter(e => e.venue === ev.venue && e.id !== ev.id && e.status === 'Approved');
  return sameVenue.some(e => {
    const m1 = e.date.match(/(\d+)/);
    const m2 = ev.date.match(/(\d+)/);
    return m1 && m2 && m1[1] === m2[1];
  });
};

/* ── Conflict analysis for review ── */
const ca = computed(() => {
  const e = reviewTarget.value;
  if (!e) return { venueClear: true, equipClear: true, capOk: true, overlapHours: 0 };
  const sameVenue = store.events.filter(ev => ev.venue === e.venue && ev.id !== e.id && ev.status === 'Approved');
  const overlap = sameVenue.some(ev => ev.date === e.date);
  const capOk = e.participants <= 80;
  return { venueClear: !overlap, equipClear: true, capOk, overlapHours: overlap ? 2 : 0 };
});

/* ── Review ── */
const reviewTarget = ref(null);

const openReview = (ev) => {
  reviewTarget.value = ev;
};

const addNote = (ev) => {
  showToast('chat-dots-fill', 'info', 'Note added to review for "' + ev.name + '"');
  reviewTarget.value = null;
};

/* ── Approve ── */
const approveTarget = ref(null);
const approveNote = ref('');

const openApprove = (ev) => {
  approveTarget.value = ev;
  approveNote.value = '';
};

const confirmApprove = () => {
  if (!approveTarget.value) return;
  store.approveEvent(approveTarget.value.id);
  showToast('check-circle-fill', 'success', `"${approveTarget.value.name}" approved`);
  approveTarget.value = null;
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

const confirmReject = () => {
  if (!rejectTarget.value || !rejectReason.value) return;
  store.rejectEvent(rejectTarget.value.id);
  showToast('x-circle-fill', 'danger', `"${rejectTarget.value.name}" rejected`);
  rejectTarget.value = null;
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
.la-stats-row { display: flex; gap: 0.65rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.la-stat { flex: 1; min-width: 130px; display: flex; align-items: center; gap: 0.7rem; padding: 0.85rem 1rem; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); transition: all 0.2s; }
.la-stat:hover { border-color: rgba(129,140,248,0.12); }
.la-stat-icon { width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; }
.la-stat-body { display: flex; flex-direction: column; }
.la-stat-value { font-size: 1.15rem; font-weight: 800; color: #f1f5f9; line-height: 1.2; letter-spacing: -0.3px; }
.la-stat-label { font-size: 0.65rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.03em; }

/* ── Main Layout ── */
.la-main-layout { display: flex; gap: 1.25rem; align-items: flex-start; }

/* ── Calendar Section ── */
.la-cal-section { flex: 1; min-width: 0; background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); padding: 1.25rem; }

.la-cal-topbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }
.la-venue-picker { display: flex; align-items: center; gap: 0.4rem; }
.la-venue-select { padding: 0.35rem 1.5rem 0.35rem 0.6rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; cursor: pointer; appearance: none; -webkit-appearance: none; transition: all 0.2s; min-width: 120px; }
.la-venue-select:focus { border-color: rgba(129,140,248,0.3); }
.la-venue-select option { background: #0f172a; color: #e2e8f0; }
.la-cal-nav { display: flex; align-items: center; gap: 0.4rem; }
.la-cal-nav-btn { width: 28px; height: 28px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.03); color: #64748b; font-size: 0.65rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.la-cal-nav-btn:hover { background: rgba(255,255,255,0.07); color: #94a3b8; }
.la-cal-label { font-size: 0.85rem; font-weight: 700; color: #e2e8f0; min-width: 120px; text-align: center; }
.la-today-btn { padding: 0.3rem 0.7rem; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; background: rgba(255,255,255,0.03); color: #94a3b8; font-size: 0.7rem; font-weight: 600; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-today-btn:hover { background: rgba(129,140,248,0.1); border-color: rgba(129,140,248,0.2); color: #818cf8; }
.la-view-toggle { display: flex; background: rgba(255,255,255,0.04); border-radius: 8px; padding: 2px; margin-left: auto; }
.la-view-toggle button { padding: 0.35rem 0.65rem; border: none; background: transparent; color: #64748b; font-size: 0.7rem; font-weight: 700; font-family: inherit; cursor: pointer; border-radius: 6px; transition: all 0.2s; }
.la-view-toggle button.active { background: rgba(129,140,248,0.15); color: #818cf8; }
.la-view-toggle button:hover:not(.active) { color: #94a3b8; }

/* ── Month ── */
.la-cal-month { }
.la-cal-row { display: grid; grid-template-columns: repeat(7, 1fr); }
.la-cal-header { margin-bottom: 2px; }
.la-cal-hd { text-align: center; font-size: 0.6rem; font-weight: 700; color: #475569; padding: 0.3rem 0; text-transform: uppercase; letter-spacing: 0.04em; }
.la-cal-cell { min-height: 72px; padding: 0.25rem 0.35rem; border-radius: 10px; cursor: default; transition: all 0.15s; border: 1px solid transparent; margin: 1px; position: relative; }
.la-cell-clickable { cursor: pointer; }
.la-cell-clickable:hover { background: rgba(255,255,255,0.04); }
.la-cell-today { background: rgba(129,140,248,0.06); }
.la-cell-selected { background: rgba(129,140,248,0.12); border-color: rgba(129,140,248,0.2); }
.la-cell-other .la-cell-num { color: #2a3040; }
.la-cell-num { font-size: 0.72rem; font-weight: 700; color: #94a3b8; display: block; margin-bottom: 2px; }
.la-cell-today .la-cell-num { color: #818cf8; }
.la-cell-bookings { display: flex; flex-direction: column; gap: 1px; }
.la-cell-bk { font-size: 0.55rem; font-weight: 700; padding: 0.1rem 0.3rem; border-radius: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff; }
.la-bk-approved { background: rgba(52,211,153,0.5); }
.la-bk-pending { background: rgba(129,140,248,0.4); }
.la-bk-rejected { background: rgba(244,63,94,0.3); }
.la-bk-maintenance { background: rgba(251,191,36,0.3); }
.la-cell-more { font-size: 0.55rem; color: #475569; padding-left: 0.3rem; }

/* ── Week ── */
.la-cal-week { }
.la-week-header { display: grid; grid-template-columns: 44px repeat(7, 1fr); gap: 2px; margin-bottom: 4px; }
.la-week-gutter { }
.la-week-hd-cell { display: flex; flex-direction: column; align-items: center; padding: 0.3rem 0; border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.la-week-hd-cell:hover { background: rgba(255,255,255,0.04); }
.la-week-hd-today { background: rgba(129,140,248,0.1); }
.la-week-hd-day { font-size: 0.55rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; }
.la-week-hd-num { font-size: 0.75rem; font-weight: 700; color: #94a3b8; }
.la-week-hd-today .la-week-hd-num { color: #818cf8; }

.la-week-body { display: flex; gap: 2px; max-height: 400px; overflow-y: auto; }
.la-week-body::-webkit-scrollbar { width: 3px; }
.la-week-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 99px; }
.la-week-times { display: flex; flex-direction: column; width: 40px; flex-shrink: 0; }
.la-week-time { height: 28px; font-size: 0.55rem; color: #475569; text-align: right; padding-right: 6px; line-height: 28px; }
.la-week-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; flex: 1; }
.la-week-col { display: flex; flex-direction: column; gap: 2px; }
.la-week-slot { height: 28px; border-radius: 4px; cursor: pointer; transition: all 0.12s; display: flex; align-items: center; padding: 0 4px; overflow: hidden; }
.la-slot-free { background: rgba(255,255,255,0.025); }
.la-slot-free:hover { background: rgba(52,211,153,0.08); }
.la-slot-approved { background: rgba(52,211,153,0.12); }
.la-slot-approved:hover { background: rgba(52,211,153,0.2); }
.la-slot-pending { background: rgba(129,140,248,0.12); }
.la-slot-pending:hover { background: rgba(129,140,248,0.2); }
.la-slot-label { font-size: 0.55rem; font-weight: 700; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ── Day ── */
.la-cal-day { }
.la-day-header { font-size: 0.9rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.75rem; text-align: center; }
.la-day-body { max-height: 440px; overflow-y: auto; }
.la-day-body::-webkit-scrollbar { width: 3px; }
.la-day-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 99px; }
.la-day-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 2px; }
.la-day-time { width: 40px; font-size: 0.6rem; color: #475569; text-align: right; flex-shrink: 0; }
.la-day-slot { flex: 1; height: 32px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; padding: 0 0.5rem; transition: all 0.12s; }

/* ── Legend ── */
.la-legend { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem; padding-top: 0.65rem; border-top: 1px solid rgba(255,255,255,0.05); }
.la-legend-item { display: flex; align-items: center; gap: 0.35rem; font-size: 0.62rem; color: #64748b; }
.la-legend-dot { width: 7px; height: 7px; border-radius: 50%; }
.la-legend-approved { background: #34d399; }
.la-legend-pending { background: #818cf8; }
.la-legend-rejected { background: #fb7185; }
.la-legend-maintenance { background: #fbbf24; }

/* ── Queue Section ── */
.la-queue-section { width: 340px; flex-shrink: 0; background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); display: flex; flex-direction: column; max-height: calc(100vh - 200px); }

/* ── Dashboard List ── */
.la-dash-section { background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); padding: 1.25rem; }
.la-dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.la-dash-title { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.la-dash-subtitle { font-size: 0.72rem; color: #64748b; }
.la-dash-list { display: flex; flex-direction: column; gap: 0.4rem; }
.la-dash-item { display: flex; justify-content: space-between; align-items: center; padding: 0.65rem 0.75rem; border-radius: 12px; background: rgba(255,255,255,0.02); border: 1px solid transparent; transition: all 0.2s; }
.la-dash-item:hover { background: rgba(255,255,255,0.04); }
.la-dash-pending { border-left: 3px solid rgba(129,140,248,0.25); }
.la-dash-approved { border-left: 3px solid rgba(52,211,153,0.25); }
.la-dash-rejected { border-left: 3px solid rgba(244,63,94,0.2); opacity: 0.65; }
.la-dash-item-left { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; }
.la-dash-item-img { width: 44px; height: 44px; border-radius: 10px; background-size: cover; background-position: center; flex-shrink: 0; }
.la-dash-item-body { min-width: 0; }
.la-dash-item-title-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.2rem; }
.la-dash-item-title { font-size: 0.82rem; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.la-dash-item-meta { display: flex; gap: 0.65rem; font-size: 0.65rem; color: #64748b; flex-wrap: wrap; }
.la-dash-item-meta i { margin-right: 0.2rem; font-size: 0.6rem; }
.la-dash-item-actions { display: flex; gap: 0.3rem; flex-shrink: 0; margin-left: 0.75rem; }
.notif-item { border: 1px solid transparent; transition: all 0.2s; }
.notif-item:hover { background: rgba(255,255,255,0.04); }
.notif-icon-lab { width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; }
.notif-dot-lab { width: 8px; height: 8px; border-radius: 50%; background: #818cf8; flex-shrink: 0; margin-top: 0.35rem; }
.notif-unread { background: rgba(129,140,248,0.04) !important; border-left: 3px solid rgba(129,140,248,0.15) !important; }
.la-queue-header { display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem 1.1rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); flex-shrink: 0; }
.la-queue-title { font-size: 0.9rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.la-queue-subtitle { font-size: 0.68rem; color: #64748b; display: block; margin-top: 2px; }
.la-queue-filter-btn { width: 30px; height: 30px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.03); color: #64748b; font-size: 0.75rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0; }
.la-queue-filter-btn:hover { color: #94a3b8; background: rgba(255,255,255,0.06); }

.la-queue-search { padding: 0.5rem 1.1rem; flex-shrink: 0; }
.la-qs-input { width: 100%; padding: 0.4rem 0.7rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; color: #e2e8f0; font-size: 0.75rem; font-family: inherit; outline: none; box-sizing: border-box; transition: all 0.2s; }
.la-qs-input:focus { border-color: rgba(129,140,248,0.3); }

.la-queue-list { flex: 1; overflow-y: auto; padding: 0.5rem 1.1rem 1rem; }
.la-queue-list::-webkit-scrollbar { width: 3px; }
.la-queue-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 99px; }

.la-queue-empty { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 2rem 0; color: #475569; font-size: 0.82rem; }
.la-queue-empty i { font-size: 1.5rem; }

.la-queue-item { padding: 0.7rem 0.75rem; border-radius: 12px; margin-bottom: 0.4rem; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; background: rgba(255,255,255,0.02); }
.la-queue-item:hover { background: rgba(255,255,255,0.04); }
.la-qi-highlight { border-color: rgba(129,140,248,0.2) !important; background: rgba(129,140,248,0.06) !important; }
.la-qi-pending { border-left: 3px solid rgba(129,140,248,0.25); }
.la-qi-approved { border-left: 3px solid rgba(52,211,153,0.25); }
.la-qi-rejected { border-left: 3px solid rgba(244,63,94,0.2); opacity: 0.65; }
.la-qi-top { }
.la-qi-title-row { display: flex; justify-content: space-between; align-items: center; gap: 0.3rem; margin-bottom: 0.25rem; }
.la-qi-title { font-size: 0.8rem; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.la-qi-priority { font-size: 0.55rem; font-weight: 700; padding: 0.1rem 0.35rem; border-radius: 4px; white-space: nowrap; text-transform: uppercase; letter-spacing: 0.03em; }
.la-pri-high { background: rgba(244,63,94,0.15); color: #fb7185; }
.la-pri-medium { background: rgba(251,191,36,0.12); color: #fbbf24; }
.la-pri-low { background: rgba(52,211,153,0.1); color: #34d399; }
.la-qi-meta { display: flex; gap: 0.65rem; font-size: 0.65rem; color: #64748b; margin-bottom: 1px; flex-wrap: wrap; }
.la-qi-meta i { margin-right: 0.25rem; font-size: 0.6rem; }
.la-qi-conflict { display: flex; align-items: center; gap: 0.3rem; font-size: 0.6rem; color: #fb7185; margin-top: 0.3rem; }
.la-qi-conflict i { font-size: 0.65rem; }

.la-qi-actions { display: flex; gap: 0.3rem; margin-top: 0.5rem; }
.la-qi-btn { padding: 0.25rem 0.55rem; border: none; border-radius: 6px; font-size: 0.62rem; font-weight: 700; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-qi-btn-review { background: rgba(255,255,255,0.06); color: #94a3b8; }
.la-qi-btn-review:hover { background: rgba(255,255,255,0.1); color: #cbd5e1; }
.la-qi-btn-approve { background: rgba(52,211,153,0.12); color: #34d399; }
.la-qi-btn-approve:hover { background: rgba(52,211,153,0.2); }
.la-qi-btn-reject { background: rgba(244,63,94,0.12); color: #fb7185; }
.la-qi-btn-reject:hover { background: rgba(244,63,94,0.2); }
.la-qi-done { font-size: 0.6rem; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; padding: 0.25rem 0.5rem; }

/* ── Review Slide-over ── */
.la-overlay { position: fixed; inset: 0; background: rgba(7,11,20,0.6); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); z-index: 500; display: flex; align-items: center; justify-content: center; }
.la-overlay:has(.la-slide) { justify-content: flex-end; }
.la-slide { width: 460px; max-width: 92vw; height: 100%; background: rgba(9,11,22,0.98); border-left: 1px solid rgba(255,255,255,0.06); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); display: flex; flex-direction: column; overflow: hidden; }
.la-slide-top { flex-shrink: 0; }
.la-slide-banner { height: 160px; background-size: cover; background-position: center; position: relative; }
.la-slide-banner-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(7,11,20,0.2), rgba(7,11,20,0.6)); display: flex; justify-content: space-between; align-items: flex-start; padding: 0.75rem; }
.la-slide-close { width: 30px; height: 30px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: rgba(7,11,20,0.4); color: #94a3b8; font-size: 0.65rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; backdrop-filter: blur(4px); }
.la-slide-close:hover { color: #f1f5f9; background: rgba(7,11,20,0.6); }
.la-slide-badge { font-size: 0.6rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.04em; }
.la-badge-approved { background: rgba(52,211,153,0.15); color: #34d399; }
.la-badge-pending { background: rgba(129,140,248,0.15); color: #818cf8; }
.la-badge-rejected { background: rgba(244,63,94,0.15); color: #fb7185; }
.la-slide-header { padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
.la-slide-title { font-size: 1.05rem; font-weight: 800; color: #f1f5f9; margin: 0 0 0.2rem; }
.la-slide-organizer { font-size: 0.78rem; color: #64748b; margin: 0; }
.la-slide-body { flex: 1; overflow-y: auto; padding-bottom: 1rem; }
.la-slide-body::-webkit-scrollbar { width: 3px; }
.la-slide-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 99px; }
.la-ss { padding: 1rem 1.25rem; }
.la-ss-title { font-size: 0.72rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.6rem; display: flex; align-items: center; }
.la-ss-desc { font-size: 0.8rem; color: #94a3b8; line-height: 1.65; margin: 0; }
.la-ss-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.la-ss-item { display: flex; flex-direction: column; gap: 0.1rem; }
.la-ss-lbl { font-size: 0.6rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.03em; }
.la-ss-val { font-size: 0.78rem; color: #e2e8f0; font-weight: 600; }

.la-ca-list { display: flex; flex-direction: column; gap: 0.35rem; }
.la-ca-item { display: flex; align-items: center; font-size: 0.75rem; padding: 0.45rem 0.7rem; border-radius: 8px; }
.la-ca-ok { background: rgba(52,211,153,0.05); color: #34d399; }
.la-ca-warn { background: rgba(244,63,94,0.05); color: #fb7185; }

.la-slide-actions { display: flex; gap: 0.5rem; padding: 0.85rem 1.25rem; border-top: 1px solid rgba(255,255,255,0.05); flex-shrink: 0; }
.la-slide-btn { padding: 0.45rem 0.9rem; border: none; border-radius: 8px; font-size: 0.72rem; font-weight: 700; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-slide-btn-primary { background: rgba(52,211,153,0.12); color: #34d399; }
.la-slide-btn-primary:hover { background: rgba(52,211,153,0.2); }
.la-slide-btn-danger { background: rgba(244,63,94,0.12); color: #fb7185; }
.la-slide-btn-danger:hover { background: rgba(244,63,94,0.2); }
.la-slide-btn-ghost { background: rgba(255,255,255,0.04); color: #94a3b8; border: 1px solid rgba(255,255,255,0.06); }
.la-slide-btn-ghost:hover { background: rgba(255,255,255,0.07); color: #cbd5e1; }

/* ── Modal ── */
.la-modal { width: 100%; background: rgba(15,23,42,0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); box-shadow: 0 24px 64px rgba(0,0,0,0.4); padding: 1.5rem; }
.la-modal-icon-box { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; font-size: 1.2rem; }
.la-modal-icon-success { background: rgba(52,211,153,0.1); color: #34d399; }
.la-modal-icon-danger { background: rgba(244,63,94,0.1); color: #fb7185; }
.la-modal-title { text-align: center; font-size: 1rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.2rem; }
.la-modal-sub { text-align: center; font-size: 0.78rem; color: #64748b; margin: 0 0 1rem; line-height: 1.5; }
.la-modal-summary { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 0.6rem 0.85rem; margin-bottom: 0.75rem; }
.la-ms-row { display: flex; justify-content: space-between; padding: 0.3rem 0; font-size: 0.78rem; }
.la-ms-row:not(:last-child) { border-bottom: 1px solid rgba(255,255,255,0.04); }
.la-ms-lbl { color: #64748b; }
.la-ms-val { color: #e2e8f0; font-weight: 600; }
.la-modal-note { margin-bottom: 0.75rem; }
.la-note-lbl { display: block; font-size: 0.72rem; font-weight: 600; color: rgba(255,255,255,0.92); margin-bottom: 0.25rem; }
.la-note-inp { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07); border-radius: 10px; color: #e2e8f0; font-size: 0.8rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; }
.la-note-inp:focus { border-color: rgba(129,140,248,0.3); }
.la-note-inp::placeholder { color: rgba(255,255,255,0.5); }
.la-modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.la-btn { padding: 0.45rem 1rem; border-radius: 10px; font-size: 0.78rem; font-weight: 700; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.la-btn-ghost { border: 1px solid rgba(255,255,255,0.1); background: transparent; color: #94a3b8; }
.la-btn-ghost:hover { background: rgba(255,255,255,0.04); color: #e2e8f0; }
.la-btn-primary { border: none; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; box-shadow: 0 4px 16px rgba(99,102,241,0.2); }
.la-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(99,102,241,0.3); }
.la-btn-danger { border: none; background: rgba(244,63,94,0.15); color: #fb7185; }
.la-btn-danger:hover { background: rgba(244,63,94,0.25); }
.la-btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Modal Form ── */
.la-modal-form { display: flex; flex-direction: column; gap: 0.65rem; margin-bottom: 0.75rem; }
.la-mf-group { }
.la-mf-lbl { display: block; font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.92); margin-bottom: 0.2rem; }
.la-mf-select { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07); border-radius: 10px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; appearance: none; -webkit-appearance: none; cursor: pointer; }
.la-mf-select:focus { border-color: rgba(129,140,248,0.3); }
.la-mf-select option { background: #0f172a; color: #e2e8f0; }
.la-mf-input { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07); border-radius: 10px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; }
.la-mf-input:focus { border-color: rgba(129,140,248,0.3); }
.la-mf-input::placeholder { color: rgba(255,255,255,0.5); }
.la-mf-textarea { width: 100%; padding: 0.45rem 0.75rem; background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.07); border-radius: 10px; color: #e2e8f0; font-size: 0.78rem; font-family: inherit; outline: none; transition: all 0.2s; box-sizing: border-box; resize: vertical; line-height: 1.5; }
.la-mf-textarea:focus { border-color: rgba(129,140,248,0.3); }
.la-mf-textarea::placeholder { color: rgba(255,255,255,0.5); }
.required { color: #fb7185; }

/* ── Toast ── */
.la-toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: center; gap: 0.6rem; padding: 0.65rem 1.1rem; border-radius: 14px; font-size: 0.8rem; font-weight: 600; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); z-index: 999; }
.la-toast-success { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.18); color: #34d399; }
.la-toast-danger { background: rgba(244,63,94,0.12); border: 1px solid rgba(244,63,94,0.18); color: #fb7185; }
.la-toast-info { background: rgba(129,140,248,0.12); border: 1px solid rgba(129,140,248,0.18); color: #818cf8; }

/* ── Transitions ── */
.la-slide-over-enter-active, .la-slide-over-leave-active { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.la-slide-over-enter-from, .la-slide-over-leave-to { opacity: 0; }
.la-slide-over-enter-from .la-slide { transform: translateX(100%); }
.la-slide-over-leave-to .la-slide { transform: translateX(100%); }
.la-slide { transition: transform 0.3s cubic-bezier(0.4,0,0.2,1); }
.la-modal-fade-enter-active, .la-modal-fade-leave-active { transition: all 0.2s ease; }
.la-modal-fade-enter-from, .la-modal-fade-leave-to { opacity: 0; transform: scale(0.95); }
.la-toast-fade-enter-active, .la-toast-fade-leave-active { transition: all 0.3s ease; }
.la-toast-fade-enter-from, .la-toast-fade-leave-to { opacity: 0; transform: translateY(16px); }
</style>
