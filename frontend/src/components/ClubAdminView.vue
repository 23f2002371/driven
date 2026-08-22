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
          <div class="navbar-avatar">{{ adminInitials }}</div>
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
                  <p class="ce-page-sub">Design your next workshop, hackathon, or seminar. Fill in the core details, configure the agenda and mentors, and submit for approval.</p>
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
                      <div class="ce-holo-row"><div class="ce-holo-label">Event</div><div class="ce-holo-val">{{ formEvent.name || 'New Event' }}</div></div>
                      <div class="ce-holo-row"><div class="ce-holo-label">Date</div><div class="ce-holo-val">{{ formEvent.event_date || 'TBD' }}</div></div>
                      <div class="ce-holo-divider"></div>
                      <div class="ce-holo-status"><div class="ce-holo-pulse"></div>Step {{ createStep }}/2</div>
                    </div>
                    <div class="ce-holo-glow"></div>
                  </div>
                  <div class="ce-ill-card ce-ill-card-1">
                    <div class="ce-card-inner"><span class="ce-card-icon bi bi-calendar3"></span><span class="ce-card-text">{{ formEvent.event_date || 'Date' }}</span></div>
                  </div>
                  <div class="ce-ill-card ce-ill-card-2">
                    <div class="ce-card-inner"><span class="ce-card-icon bi bi-ticket"></span><span class="ce-card-text">{{ formEvent.max_participants }} seats</span></div>
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

          <div class="ce-layout mt-4">
            <div class="ce-left">
              <!-- ================= PAGE 1: BASIC INFORMATION ================= -->
              <div v-if="createStep === 1" class="ce-page-anim">
                <!-- Section 1: Event Information -->
                <section class="ce-section" data-idx="0">
                  <div class="ce-section-head">
                    <h3><i class="bi bi-info-circle-fill me-2 text-indigo"></i>Event Information</h3>
                    <p>Provide the primary title, short tagline, and category for your event.</p>
                  </div>
                  <div class="ce-field">
                    <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.name, 'ce-has-error': formErrors.name }">
                      <input v-model="formEvent.name" type="text" placeholder="e.g. Next-Gen IoT Architecture" maxlength="150" required />
                      <label>Event Name *</label>
                    </div>
                    <span v-if="formErrors.name" class="ce-field-error">{{ formErrors.name }}</span>
                  </div>

                  <div class="ce-field">
                    <div class="ce-input-wrap" :class="{ 'ce-has-value': formEvent.short_description, 'ce-has-error': formErrors.short_description }">
                      <input v-model="formEvent.short_description" type="text" placeholder="e.g. Hands-on sensor building & real-time telemetry" maxlength="255" required />
                      <label>Short Description *</label>
                    </div>
                    <span v-if="formErrors.short_description" class="ce-field-error">{{ formErrors.short_description }}</span>
                    <span v-else class="ce-helper">A brief 1-line summary displayed on event cards (max 255 characters).</span>
                  </div>

                  <div class="ce-field">
                    <label class="ce-field-label">Category *</label>
                    <div class="ce-chips">
                      <button
                        v-for="cat in categoryOptions"
                        :key="cat.value"
                        type="button"
                        class="ce-chip"
                        :class="{ active: formEvent.category === cat.value }"
                        @click="formEvent.category = cat.value"
                      >
                        <i :class="'bi bi-' + cat.icon + ' me-1'"></i>{{ cat.label }}
                      </button>
                    </div>
                  </div>
                </section>

                <div class="ce-divider"></div>

                <!-- Section 2: Date, Deadline, Venue & Max Participants -->
                <section class="ce-section" data-idx="1">
                  <div class="ce-section-head">
                    <h3><i class="bi bi-geo-alt-fill me-2 text-indigo"></i>Date, Deadline & Venue</h3>
                    <p>Specify the date of the event, registration cutoff timestamp, location, and capacity.</p>
                  </div>
                  <div class="ce-row">
                    <div class="ce-field">
                      <label class="ce-field-label">Event Date *</label>
                      <input v-model="formEvent.event_date" type="date" class="ce-standard-input" :class="{ 'ce-has-error': formErrors.event_date }" required />
                      <span v-if="formErrors.event_date" class="ce-field-error">{{ formErrors.event_date }}</span>
                    </div>

                    <div class="ce-field">
                      <label class="ce-field-label">Registration Deadline *</label>
                      <input v-model="formEvent.registration_deadline" type="datetime-local" class="ce-standard-input" :class="{ 'ce-has-error': formErrors.registration_deadline }" required />
                      <span v-if="formErrors.registration_deadline" class="ce-field-error">{{ formErrors.registration_deadline }}</span>
                    </div>
                  </div>

                  <div class="ce-field mt-2">
                    <label class="ce-field-label">Venue *</label>
                    <div class="ce-input-wrap ce-select-wrap" :class="{ 'ce-has-value': formEvent.venue }">
                      <select v-model="formEvent.venue">
                        <option v-for="v in venueOptions" :key="v.value" :value="v.value">{{ v.label }}</option>
                      </select>
                      <i class="bi bi-chevron-down ce-select-arrow"></i>
                    </div>
                  </div>

                  <div class="ce-field mt-3">
                    <label class="ce-field-label">Max Capacity *</label>
                    <div class="ce-stepper">
                      <button type="button" class="ce-step-btn" @click="formEvent.max_participants > 1 && formEvent.max_participants--" :disabled="formEvent.max_participants <= 1"><i class="bi bi-dash"></i></button>
                      <div class="ce-step-value">
                        <span class="ce-step-num">{{ formEvent.max_participants }}</span>
                        <span class="ce-step-unit">participants</span>
                      </div>
                      <button type="button" class="ce-step-btn" @click="formEvent.max_participants++" :disabled="formEvent.max_participants >= 5000"><i class="bi bi-plus"></i></button>
                    </div>
                    <span class="ce-helper">Maximum attendee capacity for this event.</span>
                  </div>
                </section>

                <div class="ce-divider"></div>

                <!-- Section 3: Full Description -->
                <section class="ce-section" data-idx="2">
                  <div class="ce-section-head">
                    <h3><i class="bi bi-text-paragraph me-2 text-indigo"></i>Detailed Description</h3>
                    <p>Explain the event background, objectives, and highlights for participants.</p>
                  </div>
                  <div class="ce-field">
                    <div class="ce-textarea-wrap" :class="{ 'ce-has-error': formErrors.description }">
                      <textarea v-model="formEvent.description" rows="5" placeholder="Write a comprehensive description of your event. Detail what participants will experience, workshop milestones, tools to be used, and practical takeaways..." required></textarea>
                      <div class="ce-textarea-bottom">
                        <span class="ce-helper">Detailed descriptions improve student interest and attendance rate.</span>
                        <span class="ce-char-count">{{ formEvent.description.length }} chars</span>
                      </div>
                    </div>
                    <span v-if="formErrors.description" class="ce-field-error">{{ formErrors.description }}</span>
                  </div>
                </section>

                <div class="ce-divider"></div>

                <!-- Section 4: Cover Image (Local Upload) -->
                <section class="ce-section" data-idx="3">
                  <div class="ce-section-head">
                    <h3><i class="bi bi-image-fill me-2 text-indigo"></i>Cover Image</h3>
                    <p>Upload a cover banner from your computer for your event card.</p>
                  </div>
                  <div class="ce-field">
                    <div class="ce-upload-zone" @click="fileInput?.click()" @dragover.prevent @drop.prevent="handleDrop" :class="{ 'ce-has-banner': formEvent.cover_image_preview || formEvent.cover_image_url }">
                      <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleFile" />
                      <template v-if="!(formEvent.cover_image_preview || formEvent.cover_image_url)">
                        <div class="ce-upload-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                        <p class="ce-upload-text">Drag & drop banner or <span>Browse files</span></p>
                        <p class="ce-upload-hint">PNG, JPG, WebP · Max 5MB</p>
                      </template>
                      <template v-else>
                        <img :src="formEvent.cover_image_preview || formEvent.cover_image_url" alt="Banner preview" class="ce-banner-img" />
                        <button type="button" class="ce-banner-remove" @click.stop="removeBanner" title="Remove"><i class="bi bi-x-lg"></i></button>
                      </template>
                    </div>
                  </div>
                </section>
              </div>

              <!-- ================= PAGE 2: AGENDAS, ADDITIONAL INFO, MENTORS ================= -->
              <div v-else-if="createStep === 2" class="ce-page-anim">
                <!-- Section 1: Agendas Schedule -->
                <section class="ce-section">
                  <div class="ce-section-head d-flex justify-content-between align-items-center">
                    <div>
                      <h3><i class="bi bi-clock-history me-2 text-indigo"></i>Event Agendas / Schedule</h3>
                      <p>Add time-boxed agenda slots to outline the flow of the event.</p>
                    </div>
                    <button type="button" class="ce-btn-add" @click="addAgendaItem">
                      <i class="bi bi-plus-circle-fill me-1"></i>Add Agenda Slot
                    </button>
                  </div>

                  <div v-if="formEvent.agendas.length === 0" class="ce-empty-box">
                    <i class="bi bi-calendar-range ce-empty-icon"></i>
                    <p class="ce-empty-text">No agenda slots added yet. Click below to add your first session!</p>
                    <button type="button" class="ce-btn-secondary btn-sm" @click="addAgendaItem">
                      <i class="bi bi-plus-lg me-1"></i>Add First Session
                    </button>
                  </div>

                  <div v-else class="ce-cards-stack">
                    <div v-for="(agenda, idx) in formEvent.agendas" :key="idx" class="ce-dynamic-card">
                      <div class="ce-dynamic-head">
                        <span class="ce-dynamic-num"><i class="bi bi-hourglass-split me-1"></i>Slot #{{ idx + 1 }}</span>
                        <button type="button" class="ce-btn-delete" @click="removeAgendaItem(idx)" title="Remove Slot">
                          <i class="bi bi-trash3-fill"></i>
                        </button>
                      </div>
                      <div class="ce-dynamic-body">
                        <div class="ce-row">
                          <div class="ce-field">
                            <label class="ce-field-label">Start Time</label>
                            <input v-model="agenda.start_time" type="time" class="ce-standard-input" />
                          </div>
                          <div class="ce-field">
                            <label class="ce-field-label">End Time</label>
                            <input v-model="agenda.end_time" type="time" class="ce-standard-input" />
                          </div>
                        </div>
                        <div class="ce-field">
                          <div class="ce-input-wrap" :class="{ 'ce-has-value': agenda.title }">
                            <input v-model="agenda.title" type="text" placeholder="e.g. Keynote & Sensor Setup" maxlength="150" />
                            <label>Session Title</label>
                          </div>
                        </div>
                        <div class="ce-field mb-0">
                          <div class="ce-textarea-wrap">
                            <textarea v-model="agenda.description" rows="2" placeholder="Brief outline of topics, demos, or activities in this slot..."></textarea>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>

                <div class="ce-divider"></div>

                <!-- Section 2: Additional Info (Learning, Requirement, Eligibility) -->
                <section class="ce-section">
                  <div class="ce-section-head">
                    <h3><i class="bi bi-card-checklist me-2 text-indigo"></i>Additional Event Information</h3>
                    <p>Add multiple bullet points for learning outcomes, prerequisites, and eligibility details.</p>
                  </div>

                  <div class="ce-info-grid">
                    <!-- Learning Outcomes -->
                    <div class="ce-info-box">
                      <div class="ce-info-header d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-2">
                          <div class="ce-info-icon-badge blue"><i class="bi bi-book-fill"></i></div>
                          <h5 class="ce-info-title">Learning Outcomes</h5>
                        </div>
                        <button type="button" class="ce-btn-add-sm" @click="addInfoItem('learning')">
                          <i class="bi bi-plus-lg me-1"></i>Add Outcome
                        </button>
                      </div>

                      <div v-if="getInfoItems('learning').length === 0" class="ce-empty-point-box">
                        <span class="text-muted small">No learning outcomes added. Click "+ Add Outcome" to add points.</span>
                      </div>
                      <div v-else class="ce-info-list">
                        <div v-for="(item, idx) in getInfoItems('learning')" :key="idx" class="ce-info-item-row">
                          <span class="ce-info-item-num">{{ idx + 1 }}</span>
                          <input
                            v-model="item.content"
                            type="text"
                            class="ce-info-item-input"
                            placeholder="e.g. Master Arduino GPIO and sensor telemetry"
                            @keydown.enter.prevent="addInfoItem('learning')"
                          />
                          <button type="button" class="ce-info-item-remove" @click="removeInfoItem(item)" title="Remove Point">
                            <i class="bi bi-trash3"></i>
                          </button>
                        </div>
                      </div>
                    </div>

                    <!-- Requirements & Prerequisites -->
                    <div class="ce-info-box">
                      <div class="ce-info-header d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-2">
                          <div class="ce-info-icon-badge purple"><i class="bi bi-laptop-fill"></i></div>
                          <h5 class="ce-info-title">Prerequisites & Requirements</h5>
                        </div>
                        <button type="button" class="ce-btn-add-sm" @click="addInfoItem('requirement')">
                          <i class="bi bi-plus-lg me-1"></i>Add Requirement
                        </button>
                      </div>

                      <div v-if="getInfoItems('requirement').length === 0" class="ce-empty-point-box">
                        <span class="text-muted small">No requirements added. Click "+ Add Requirement" to add points.</span>
                      </div>
                      <div v-else class="ce-info-list">
                        <div v-for="(item, idx) in getInfoItems('requirement')" :key="idx" class="ce-info-item-row">
                          <span class="ce-info-item-num">{{ idx + 1 }}</span>
                          <input
                            v-model="item.content"
                            type="text"
                            class="ce-info-item-input"
                            placeholder="e.g. Laptop with Node.js v18+ and VS Code installed"
                            @keydown.enter.prevent="addInfoItem('requirement')"
                          />
                          <button type="button" class="ce-info-item-remove" @click="removeInfoItem(item)" title="Remove Point">
                            <i class="bi bi-trash3"></i>
                          </button>
                        </div>
                      </div>
                    </div>

                    <!-- Eligibility Details -->
                    <div class="ce-info-box">
                      <div class="ce-info-header d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-2">
                          <div class="ce-info-icon-badge green"><i class="bi bi-person-check-fill"></i></div>
                          <h5 class="ce-info-title">Eligibility Details</h5>
                        </div>
                        <button type="button" class="ce-btn-add-sm" @click="addInfoItem('eligibility')">
                          <i class="bi bi-plus-lg me-1"></i>Add Eligibility
                        </button>
                      </div>

                      <div v-if="getInfoItems('eligibility').length === 0" class="ce-empty-point-box">
                        <span class="text-muted small">No eligibility details added. Click "+ Add Eligibility" to add points.</span>
                      </div>
                      <div v-else class="ce-info-list">
                        <div v-for="(item, idx) in getInfoItems('eligibility')" :key="idx" class="ce-info-item-row">
                          <span class="ce-info-item-num">{{ idx + 1 }}</span>
                          <input
                            v-model="item.content"
                            type="text"
                            class="ce-info-item-input"
                            placeholder="e.g. Open to 2nd & 3rd year engineering students, teams of 2-4"
                            @keydown.enter.prevent="addInfoItem('eligibility')"
                          />
                          <button type="button" class="ce-info-item-remove" @click="removeInfoItem(item)" title="Remove Point">
                            <i class="bi bi-trash3"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>

                <div class="ce-divider"></div>

                <!-- Section 3: Mentors -->
                <section class="ce-section">
                  <div class="ce-section-head d-flex justify-content-between align-items-center">
                    <div>
                      <h3><i class="bi bi-person-workspace me-2 text-indigo"></i>Mentors & Speakers</h3>
                      <p>Feature industry mentors, workshop leads, or guest speakers.</p>
                    </div>
                    <button type="button" class="ce-btn-add" @click="addMentorItem">
                      <i class="bi bi-person-plus-fill me-1"></i>Add Mentor
                    </button>
                  </div>

                  <div v-if="formEvent.mentors.length === 0" class="ce-empty-box">
                    <i class="bi bi-person-badge ce-empty-icon"></i>
                    <p class="ce-empty-text">No mentors added yet. Add industry experts guiding this event!</p>
                    <button type="button" class="ce-btn-secondary btn-sm" @click="addMentorItem">
                      <i class="bi bi-plus-lg me-1"></i>Add First Mentor
                    </button>
                  </div>

                  <div v-else class="ce-cards-stack">
                    <div v-for="(mentor, idx) in formEvent.mentors" :key="idx" class="ce-dynamic-card">
                      <div class="ce-dynamic-head">
                        <span class="ce-dynamic-num"><i class="bi bi-person-fill me-1"></i>Mentor #{{ idx + 1 }}</span>
                        <button type="button" class="ce-btn-delete" @click="removeMentorItem(idx)" title="Remove Mentor">
                          <i class="bi bi-trash3-fill"></i>
                        </button>
                      </div>
                      <div class="ce-dynamic-body">
                        <div class="ce-row">
                          <div class="ce-field">
                            <div class="ce-input-wrap" :class="{ 'ce-has-value': mentor.name }">
                              <input v-model="mentor.name" type="text" placeholder="e.g. Dr. Sarah Jenkins" maxlength="100" />
                              <label>Full Name</label>
                            </div>
                          </div>
                          <div class="ce-field">
                            <div class="ce-input-wrap" :class="{ 'ce-has-value': mentor.designation }">
                              <input v-model="mentor.designation" type="text" placeholder="e.g. Principal IoT Architect" maxlength="100" />
                              <label>Designation</label>
                            </div>
                          </div>
                        </div>

                        <div class="ce-row">
                          <div class="ce-field">
                            <div class="ce-input-wrap" :class="{ 'ce-has-value': mentor.company }">
                              <input v-model="mentor.company" type="text" placeholder="e.g. Robotics Innovation Labs" maxlength="150" />
                              <label>Company / Organization</label>
                            </div>
                          </div>
                          <div class="ce-field">
                            <div class="ce-input-wrap" :class="{ 'ce-has-value': mentor.email }">
                              <input v-model="mentor.email" type="email" placeholder="sarah.j@company.com" />
                              <label>Email Address</label>
                            </div>
                          </div>
                        </div>

                        <div class="ce-field mb-0">
                          <div class="ce-input-wrap" :class="{ 'ce-has-value': mentor.linkedin_url }">
                            <input v-model="mentor.linkedin_url" type="url" placeholder="https://linkedin.com/in/sarah-jenkins" />
                            <label>LinkedIn Profile URL</label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>

            <!-- Realtime Preview Sidebar -->
            <div class="ce-right">
              <div class="ce-sidebar">
                <div class="ce-preview-card glass">
                  <div class="ce-preview-img" :style="{ backgroundImage: `url(${previewImage})` }">
                    <div class="ce-preview-img-overlay">
                      <span class="ce-preview-date-tag"><i class="bi bi-calendar3 me-1"></i>{{ formEvent.event_date || 'Select Date' }}</span>
                    </div>
                  </div>
                  <div class="ce-preview-body">
                    <span class="ce-preview-cat">{{ categoryLabel(formEvent.category) }}</span>
                    <h4 class="ce-preview-title">{{ formEvent.name || 'Event Title' }}</h4>
                    <p v-if="formEvent.short_description" class="ce-preview-tagline">{{ formEvent.short_description }}</p>
                    <p class="ce-preview-desc">{{ formEvent.description ? (formEvent.description.length > 90 ? formEvent.description.slice(0, 90) + '...' : formEvent.description) : 'Your event description will appear here.' }}</p>
                  </div>
                  <div class="ce-preview-footer">
                    <span class="ce-preview-meta"><i class="bi bi-geo-alt me-1"></i>{{ venueLabel(formEvent.venue) }}</span>
                    <span class="ce-preview-meta"><i class="bi bi-people-fill me-1"></i>{{ formEvent.max_participants }} seats</span>
                  </div>
                </div>

                <div class="ce-summary glass">
                  <h5 class="ce-summary-title"><i class="bi bi-layers-fill me-2 text-indigo"></i>Event Summary</h5>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-tag me-2"></i>Category</span><span class="ce-summary-val">{{ categoryLabel(formEvent.category) }}</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-geo-alt me-2"></i>Venue</span><span class="ce-summary-val">{{ venueLabel(formEvent.venue) }}</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-people me-2"></i>Max Seats</span><span class="ce-summary-val">{{ formEvent.max_participants }}</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-clock me-2"></i>Agendas</span><span class="ce-summary-val">{{ formEvent.agendas.length }} slots</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-person-badge me-2"></i>Mentors</span><span class="ce-summary-val">{{ formEvent.mentors.length }} mentors</span></div>
                  <div class="ce-summary-row"><span class="ce-summary-label"><i class="bi bi-flag me-2"></i>Status</span><span class="ce-summary-val"><span class="ce-badge-draft">Pending Review</span></span></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Action Bar with Step Navigation -->
          <div class="ce-action-bar glass">
            <div class="ce-action-left">
              <button v-if="createStep === 2" type="button" class="ce-btn-secondary" @click="createStep = 1">
                <i class="bi bi-arrow-left me-2"></i>Back to Basic Details
              </button>
              <div v-else class="d-flex align-items-center gap-2">
                <i class="bi bi-info-circle text-indigo"></i>
                <span class="text-muted small">Step 1 of 2: Basic Information</span>
              </div>
            </div>
            <div class="ce-action-right">
              <button v-if="createStep === 1" type="button" class="ce-btn-primary" @click="goToStep2">
                Next: Agenda & Details <i class="bi bi-arrow-right ms-2"></i>
              </button>
              <button v-else type="button" class="ce-btn-primary submit-btn" :disabled="isSubmitting" @click="submitNewEvent">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                <i v-else class="bi bi-send-check-fill me-2"></i>
                {{ isSubmitting ? 'Submitting...' : 'Submit for Approval' }}
              </button>
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
import { ref, computed, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store/mockData';
import Sidebar from './shared/Sidebar.vue';
import InventoryGrid from './shared/InventoryGrid.vue';
import SupportDesk from './shared/SupportDesk.vue';
import CopilotRecommendation from './shared/CopilotRecommendation.vue';
import CalendarPickerModal from './shared/CalendarPickerModal.vue';
import CampusBountyAdmin from './CampusBountyAdmin.vue';
import { useCalendarToast } from '../composables/useCalendarToast';
import { createEventApi } from '../api/events';

onMounted(() => {
  store.fetchEvents();
});

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

const adminInitials = computed(() => {
  const name = store.currentUser?.full_name || 'Club Admin';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
});

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
  const r = heroRef.value?.getBoundingClientRect();
  if (!r) return;
  mouse.x = ((e.clientX - r.left) / r.width - 0.5) * 2;
  mouse.y = ((e.clientY - r.top) / r.height - 0.5) * 2;
};
const onHeroLeave = () => { mouse.x = 0; mouse.y = 0; };
const sceneParallax = computed(() => ({
  transform: `translateX(${mouse.x * 8}px) translateY(${mouse.y * 6}px)`
}));

const createStep = ref(1);

const categoryOptions = [
  { value: 'workshop', label: 'Workshop', icon: 'tools' },
  { value: 'hackathon', label: 'Hackathon', icon: 'code-slash' },
  { value: 'seminar', label: 'Seminar', icon: 'easel' },
  { value: 'competition', label: 'Competition', icon: 'trophy' },
  { value: 'bootcamp', label: 'Bootcamp', icon: 'lightning-charge' },
  { value: 'webinar', label: 'Webinar', icon: 'broadcast' },
  { value: 'robotics', label: 'Robotics', icon: 'robot' },
  { value: 'other', label: 'Other', icon: 'grid' },
];

const venueOptions = [
  { value: 'seminar_hall', label: 'Seminar Hall' },
  { value: 'auditorium', label: 'Auditorium' },
  { value: 'main_ground', label: 'Main Ground' },
  { value: 'computer_lab_1', label: 'Computer Lab 1' },
  { value: 'computer_lab_2', label: 'Computer Lab 2' },
  { value: 'robotics_lab', label: 'Robotics Lab' },
  { value: 'innovation_lab', label: 'Innovation Lab' },
  { value: 'conference_room', label: 'Conference Room' },
  { value: 'classroom', label: 'Classroom' },
  { value: 'online', label: 'Online' },
  { value: 'other', label: 'Other' },
];

const isSubmitting = ref(false);
const fileInput = ref(null);
const defaultBanner = 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=800&h=500&fit=crop';

const formEvent = reactive({
  name: '',
  short_description: '',
  category: 'workshop',
  event_date: '',
  registration_deadline: '',
  venue: 'seminar_hall',
  max_participants: 50,
  description: '',
  cover_image: null,
  cover_image_preview: null,
  cover_image_url: '',
  agendas: [],
  additional_info: [],
  mentors: []
});

const formErrors = reactive({
  name: '',
  short_description: '',
  event_date: '',
  registration_deadline: '',
  description: '',
});

const processImageFile = (file) => {
  if (!file) return;

  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  if (!validTypes.includes(file.type)) {
    triggerCalendarToast('Please upload a valid image file (JPG, PNG, WebP).');
    return;
  }

  const maxSize = 5 * 1024 * 1024; // 5 MB
  if (file.size > maxSize) {
    triggerCalendarToast('Image size exceeds 5MB limit. Please choose a smaller image.');
    return;
  }

  // Clean up previous blob URL to prevent memory leaks
  if (formEvent.cover_image_preview && formEvent.cover_image_preview.startsWith('blob:')) {
    URL.revokeObjectURL(formEvent.cover_image_preview);
  }

  // Preserve original JavaScript File object
  formEvent.cover_image = file;

  // Generate temporary preview URL
  formEvent.cover_image_preview = URL.createObjectURL(file);
};

const handleFile = (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  processImageFile(file);
};

const handleDrop = (e) => {
  const file = e.dataTransfer?.files?.[0];
  if (!file) return;
  processImageFile(file);
};

const removeBanner = () => {
  // Revoke object URL if it was created locally
  if (formEvent.cover_image_preview && formEvent.cover_image_preview.startsWith('blob:')) {
    URL.revokeObjectURL(formEvent.cover_image_preview);
  }
  formEvent.cover_image = null;
  formEvent.cover_image_preview = null;
  formEvent.cover_image_url = '';
  if (fileInput.value) fileInput.value.value = '';
};

const categoryLabel = (val) => {
  const match = categoryOptions.find(c => c.value === val);
  return match ? match.label : (val ? val.charAt(0).toUpperCase() + val.slice(1) : 'Event');
};

const venueLabel = (val) => {
  const match = venueOptions.find(v => v.value === val);
  return match ? match.label : (val || 'Venue');
};

const previewImage = computed(() => formEvent.cover_image_preview || formEvent.cover_image_url || defaultBanner);

const getInfoItems = (type) => {
  return formEvent.additional_info.filter(i => i.section_type === type);
};

const addInfoItem = (type) => {
  formEvent.additional_info.push({ section_type: type, content: '' });
};

const removeInfoItem = (item) => {
  const idx = formEvent.additional_info.indexOf(item);
  if (idx !== -1) {
    formEvent.additional_info.splice(idx, 1);
  }
};

const isStep2Filled = computed(() => {
  return formEvent.agendas.some(a => a.title?.trim()) ||
    formEvent.additional_info.some(i => i.content?.trim()) ||
    formEvent.mentors.some(m => m.name?.trim());
});

const addAgendaItem = () => {
  formEvent.agendas.push({ start_time: '', end_time: '', title: '', description: '' });
};

const removeAgendaItem = (idx) => {
  formEvent.agendas.splice(idx, 1);
};

const addMentorItem = () => {
  formEvent.mentors.push({ name: '', company: '', designation: '', email: '', linkedin_url: '' });
};

const removeMentorItem = (idx) => {
  formEvent.mentors.splice(idx, 1);
};

const validateStep1 = () => {
  let valid = true;
  formErrors.name = '';
  formErrors.short_description = '';
  formErrors.event_date = '';
  formErrors.registration_deadline = '';
  formErrors.description = '';

  if (!formEvent.name.trim()) {
    formErrors.name = 'Event name is required (max 150 chars).';
    valid = false;
  }
  if (!formEvent.short_description.trim()) {
    formErrors.short_description = 'Short description is required (max 255 chars).';
    valid = false;
  }
  if (!formEvent.event_date) {
    formErrors.event_date = 'Please select a valid event date.';
    valid = false;
  }
  if (!formEvent.registration_deadline) {
    formErrors.registration_deadline = 'Please choose a registration deadline.';
    valid = false;
  }
  if (!formEvent.description.trim()) {
    formErrors.description = 'Detailed description is required.';
    valid = false;
  }
  return valid;
};

const goToStep2 = () => {
  createStep.value = 2;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const submitNewEvent = async () => {
  if (isSubmitting.value) return;

  if (!validateStep1()) {
    createStep.value = 1;
    triggerCalendarToast('Please fill all required fields marked with * before submitting.');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }

  isSubmitting.value = true;

  try {
    // Format ISO registration deadline
    const deadlineIso = formEvent.registration_deadline
      ? (formEvent.registration_deadline.includes('T') && formEvent.registration_deadline.length === 16
          ? `${formEvent.registration_deadline}:00Z`
          : new Date(formEvent.registration_deadline).toISOString())
      : new Date().toISOString();

    // Prepare multipart/form-data payload
    const formData = new FormData();
    formData.append('name', formEvent.name.trim());
    formData.append('short_description', formEvent.short_description.trim());
    formData.append('category', formEvent.category);
    formData.append('event_date', formEvent.event_date);
    formData.append('registration_deadline', deadlineIso);
    formData.append('venue', formEvent.venue);
    formData.append('max_participants', String(parseInt(formEvent.max_participants) || 1));
    formData.append('description', formEvent.description.trim());

    if (formEvent.cover_image_url) {
      formData.append('cover_image_url', formEvent.cover_image_url);
    }

    const filteredAgendas = formEvent.agendas
      .filter(a => a.title?.trim() || a.start_time)
      .map(a => ({
        start_time: a.start_time ? (a.start_time.length === 5 ? `${a.start_time}:00` : a.start_time) : null,
        end_time: a.end_time ? (a.end_time.length === 5 ? `${a.end_time}:00` : a.end_time) : null,
        title: a.title?.trim() || null,
        description: a.description?.trim() || null,
      }));
    formData.append('agendas', JSON.stringify(filteredAgendas));

    const filteredAdditionalInfo = formEvent.additional_info
      .filter(i => i.content?.trim())
      .map(i => ({
        section_type: i.section_type,
        content: i.content.trim(),
      }));
    formData.append('additional_info', JSON.stringify(filteredAdditionalInfo));

    const filteredMentors = formEvent.mentors
      .filter(m => m.name?.trim())
      .map(m => ({
        name: m.name?.trim() || null,
        company: m.company?.trim() || null,
        designation: m.designation?.trim() || null,
        email: m.email?.trim() || null,
        linkedin_url: m.linkedin_url?.trim() || null,
      }));
    formData.append('mentors', JSON.stringify(filteredMentors));

    // Append cover image File object if uploaded
    if (formEvent.cover_image instanceof File) {
      formData.append('cover_image', formEvent.cover_image);
    }

    const token = store.token || localStorage.getItem('driven_token');
    const createdEvent = await createEventApi(formData, token);

    // Refresh live events from backend
    await store.fetchEvents();

    triggerCalendarToast(`Event "${createdEvent.name}" created and submitted for approval!`);

    // Clean up object URL
    if (formEvent.cover_image_preview && formEvent.cover_image_preview.startsWith('blob:')) {
      URL.revokeObjectURL(formEvent.cover_image_preview);
    }

    // Reset form to clean state
    Object.assign(formEvent, {
      name: '',
      short_description: '',
      category: 'workshop',
      event_date: '',
      registration_deadline: '',
      venue: 'seminar_hall',
      max_participants: 50,
      description: '',
      cover_image: null,
      cover_image_preview: null,
      cover_image_url: '',
      agendas: [],
      additional_info: [],
      mentors: [],
    });

    createStep.value = 1;
    currentTab.value = 'events';
  } catch (err) {
    triggerCalendarToast(err.message || 'Failed to create event. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
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
  position: relative;
  z-index: 1;
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
  position: relative;
  z-index: 2;
  padding: 0 2rem 3rem;
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

/* ── Standard Inputs (Date, Datetime, Time) ── */
.ce-standard-input {
  width: 100%;
  min-height: 52px;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1.5px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 0.92rem;
  font-family: inherit;
  outline: none;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  color-scheme: dark;
}
.ce-standard-input:focus {
  border-color: rgba(129, 140, 248, 0.4);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.08), 0 4px 20px rgba(0, 0, 0, 0.1);
}
.ce-standard-input.ce-has-error {
  border-color: rgba(248, 113, 113, 0.5) !important;
  background: rgba(239, 68, 68, 0.04) !important;
}

/* ── Page Animation ── */
.ce-page-anim {
  animation: ceFadeSlide 0.35s cubic-bezier(0.4, 0, 0.2, 1) both;
}
@keyframes ceFadeSlide {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Form Error Feedback ── */
.ce-field-error {
  display: block;
  font-size: 0.75rem;
  color: #f87171;
  margin-top: 0.35rem;
  font-weight: 500;
}
.ce-input-wrap.ce-has-error input,
.ce-input-wrap.ce-has-error select,
.ce-textarea-wrap.ce-has-error textarea {
  border-color: rgba(248, 113, 113, 0.5) !important;
  background: rgba(239, 68, 68, 0.04) !important;
}

/* ── Dynamic Form Cards (Agendas & Mentors) ── */
.ce-cards-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.ce-dynamic-card {
  background: rgba(15, 23, 42, 0.55);
  border: 1.5px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 1.2rem;
  transition: all 0.25s ease;
}
.ce-dynamic-card:hover {
  border-color: rgba(129, 140, 248, 0.2);
  background: rgba(15, 23, 42, 0.7);
}
.ce-dynamic-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.ce-dynamic-num {
  font-size: 0.82rem;
  font-weight: 700;
  color: #a5b4fc;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ce-dynamic-body {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.ce-btn-add {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #a5b4fc;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}
.ce-btn-add:hover {
  background: rgba(99, 102, 241, 0.25);
  border-color: #818cf8;
  color: #ffffff;
  transform: translateY(-1px);
}
.ce-btn-delete {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}
.ce-btn-delete:hover {
  background: rgba(239, 68, 68, 0.25);
  color: #fee2e2;
  transform: scale(1.08);
}
.ce-empty-box {
  background: rgba(15, 23, 42, 0.35);
  border: 2px dashed rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}
.ce-empty-icon {
  font-size: 2rem;
  color: #64748b;
}
.ce-empty-text {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
}

/* ── Additional Info Grid ── */
.ce-info-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.ce-info-box {
  background: rgba(15, 23, 42, 0.55);
  border: 1.5px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 1.25rem;
  transition: all 0.25s ease;
}
.ce-info-box:hover {
  border-color: rgba(129, 140, 248, 0.25);
}
.ce-info-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1rem;
}
.ce-info-icon-badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}
.ce-info-icon-badge.blue {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.25);
}
.ce-info-icon-badge.purple {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.25);
}
.ce-info-icon-badge.green {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.25);
}
.ce-info-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}
.ce-info-type {
  font-size: 0.72rem;
  color: #64748b;
  font-family: monospace;
}
.text-indigo { color: #818cf8 !important; }

.ce-btn-add-sm {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #a5b4fc;
  font-size: 0.76rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}
.ce-btn-add-sm:hover {
  background: rgba(99, 102, 241, 0.28);
  border-color: #818cf8;
  color: #ffffff;
}

.ce-info-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-top: 0.65rem;
}
.ce-info-item-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.ce-info-item-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ce-info-item-input {
  flex: 1;
  min-height: 44px;
  padding: 0.6rem 1rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1.5px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.ce-info-item-input:focus {
  border-color: rgba(129, 140, 248, 0.4);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.08);
}
.ce-info-item-remove {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #f87171;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.ce-info-item-remove:hover {
  background: rgba(239, 68, 68, 0.25);
  color: #fee2e2;
  transform: scale(1.06);
}
.ce-btn-add-point {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  color: #a5b4fc;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.5rem 0.85rem;
  cursor: pointer;
  margin-top: 0.75rem;
  transition: all 0.2s;
}
.ce-btn-add-point:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(129, 140, 248, 0.4);
  color: #ffffff;
  transform: translateY(-1px);
}
.ce-empty-point-box {
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 10px;
  border: 1px dashed rgba(255, 255, 255, 0.06);
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
