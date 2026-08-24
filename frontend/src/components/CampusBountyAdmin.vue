<template>
  <div class="cba">
    <!-- Hero Section -->
    <section class="cba-hero">
      <div class="cba-hero-bg"></div>
      <div class="cba-hero-glow"></div>
      <div class="cba-hero-inner">
        <div class="cba-hero-left">
          <div class="cba-hero-badge">Bounty Dashboard</div>
          <h1 class="cba-hero-title">Campus Bounties</h1>
          <p class="cba-hero-text">Post short-term opportunities, find talented students, and manage verified work submissions — all in one place.</p>
          <button class="cba-btn-primary" @click="openCreateModal"><i class="bi bi-plus-lg me-2"></i>Create Bounty</button>
        </div>
        <div class="cba-hero-right">
          <div class="cba-stat-grid">
            <div class="cba-stat-card">
              <div class="cba-stat-icon purple"><i class="bi bi-briefcase-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ activeBountiesCount }}</span><span class="cba-stat-label">Active Bounties</span></div>
            </div>
            <div class="cba-stat-card">
              <div class="cba-stat-icon blue"><i class="bi bi-people-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ totalApplicantsCount }}</span><span class="cba-stat-label">Total Applicants</span></div>
            </div>
            <div class="cba-stat-card">
              <div class="cba-stat-icon green"><i class="bi bi-check-circle-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ completedBountiesCount }}</span><span class="cba-stat-label">Completed</span></div>
            </div>
            <div class="cba-stat-card">
              <div class="cba-stat-icon amber"><i class="bi bi-box-seam-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ openSeatsCount }}</span><span class="cba-stat-label">Open Seats</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Tabs -->
    <div class="cba-tabs">
      <button class="cba-tab" :class="{ active: activeTab === 'bounties' }" @click="activeTab = 'bounties'">
        <i class="bi bi-grid-3x3-gap-fill me-2"></i>My Bounties
      </button>
      <button class="cba-tab" :class="{ active: activeTab === 'applicants', disabled: !selectedBountyApps }" @click="goToApplicantsTab">
        <i class="bi bi-people-fill me-2"></i>Applicants
        <span v-if="selectedBountyApps" class="cba-tab-count">{{ currentApplicants.length }}</span>
      </button>
      <button class="cba-tab" :class="{ active: activeTab === 'workassign', disabled: !selectedBountyApps }" @click="goToWorkAssignTab">
        <i class="bi bi-briefcase-fill me-2"></i>Work Assign
      </button>
    </div>

    <!-- ─── My Bounties Tab ─── -->
    <div v-if="activeTab === 'bounties'" class="cba-bounties-section">
      <div class="cba-toolbar">
        <div class="cba-search-wrap">
          <i class="bi bi-search"></i>
          <input v-model="searchQuery" type="text" placeholder="Search bounties..." />
        </div>
        <select v-model="statusFilter" class="cba-filter-select">
          <option value="All">All Status</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="closed">Closed</option>
        </select>
        <button class="cba-btn-primary sm" @click="openCreateModal"><i class="bi bi-plus-lg me-1"></i>New Bounty</button>
      </div>

      <div v-if="isLoadingBounties" class="cba-loading">
        <span class="spinner-border spinner-border-sm me-2"></span>Loading bounties...
      </div>

      <div v-else-if="myBountyList.length" class="cba-bounty-list">
        <div
          v-for="bounty in myBountyList"
          :key="bounty.id"
          class="cba-bounty-row"
          :class="{ active: selectedBountyApps?.id === bounty.id }"
          @click="selectBounty(bounty)"
        >
          <div class="cba-bounty-icon-box" :style="bounty.image_url ? { backgroundImage: `url(${bounty.image_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : {}">
            <i v-if="!bounty.image_url" class="bi bi-briefcase-fill"></i>
          </div>
          <div class="cba-bounty-info">
            <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
              <h4 class="m-0">{{ bounty.title }}</h4>
              <span class="cba-bounty-cat">{{ formatDomainName(bounty.domain?.name) }}</span>
            </div>
            <p class="cba-bounty-desc-preview">{{ bounty.description }}</p>
            <div class="cba-bounty-meta">
              <span><i class="bi bi-cash-stack text-success"></i>₹{{ bounty.reward }}</span>
              <span><i class="bi bi-calendar3 text-primary"></i>Deadline: {{ formatDisplayDate(bounty.application_deadline) }}</span>
              <span><i class="bi bi-people text-info"></i>{{ bounty.student_seats }} Seats</span>
              <span><i class="bi bi-hourglass-split text-warning"></i>{{ bounty.duration }}</span>
              <span v-if="bounty.technologies?.length" class="text-secondary"><i class="bi bi-cpu text-info"></i>{{ bounty.technologies.map(t => t.name).join(', ') }}</span>
            </div>
          </div>
          <div class="cba-bounty-status" @click.stop>
            <span class="cba-status-badge" :class="bounty.status">{{ (bounty.status || 'open').toUpperCase() }}</span>
            <div class="d-flex align-items-center gap-2 mt-2">
              <button class="cba-bounty-apps-btn" @click="selectBounty(bounty)">
                View Applicants <i class="bi bi-chevron-right ms-1"></i>
              </button>
              <button class="cba-btn-delete-sm" title="Delete Bounty" @click="handleDeleteBounty(bounty)">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="cba-empty">
        <i class="bi bi-inbox"></i>
        <h3>No bounties yet</h3>
        <p>Create your first bounty to find talented students and delegate project work.</p>
        <button class="cba-btn-primary" @click="openCreateModal"><i class="bi bi-plus-lg me-1"></i>Create Bounty</button>
      </div>
    </div>

    <!-- ─── Applicants Tab ─── -->
    <div v-if="activeTab === 'applicants'" class="cba-applicants-section">
      <div v-if="selectedBountyApps" class="cba-apps-header">
        <button class="cba-back-btn" @click="selectedBountyApps = null; selectedApplicant = null"><i class="bi bi-arrow-left me-1"></i>Back</button>
        <div>
          <h3 class="m-0">{{ selectedBountyApps.title }} — Applicants</h3>
          <span class="text-secondary small">Seats: {{ selectedBountyApps.student_seats }}</span>
        </div>
        <span class="cba-apps-count ms-auto">{{ currentApplicants.length }} Total Applicants</span>
      </div>

      <div v-if="!selectedBountyApps" class="cba-apps-prompt">
        <i class="bi bi-hand-index-thumb"></i>
        <h3>Select a bounty</h3>
        <p>Click on a bounty from "My Bounties" tab to view its applicants.</p>
      </div>

      <div v-else-if="isLoadingApplicants" class="cba-loading">
        <span class="spinner-border spinner-border-sm me-2"></span>Loading applicants...
      </div>

      <div v-else-if="currentApplicants.length" class="cba-apps-list">
        <div
          v-for="app in currentApplicants"
          :key="app.id"
          class="cba-applicant-row"
          :class="{ rejected: app.status === 'rejected', accepted: app.status === 'accepted' }"
          @click="openWorkAssign(app)"
        >
          <div class="cba-applicant-avatar" :class="{ green: app.status === 'accepted', yellow: app.status === 'pending', red: app.status === 'rejected' }">
            {{ getInitials(app.student?.name) }}
          </div>
          <div class="cba-applicant-info">
            <h5>{{ app.student?.name || 'Student' }} <small class="text-muted">({{ app.student?.student_id }})</small></h5>
            <span class="cba-app-dept"><i class="bi bi-mortarboard me-1"></i>{{ formatDept(app.student?.department) }} · {{ app.student?.email }}</span>
            <div class="d-flex align-items-center gap-2 flex-wrap mt-1">
              <span class="badge bg-secondary-subtle text-light" style="font-size: 0.72rem;">Availability: {{ app.availability }}</span>
              <span v-if="app.matched_technologies?.length" class="badge bg-primary-subtle text-primary" style="font-size: 0.72rem;">
                Matches: {{ app.matched_technologies.join(', ') }}
              </span>
              <a v-if="app.resume" :href="app.resume" target="_blank" class="text-info small text-decoration-none" @click.stop>
                <i class="bi bi-link-45deg"></i>Resume / Portfolio
              </a>
            </div>
          </div>
          <div class="cba-app-status-badge" :class="app.status">
            {{ (app.status || 'pending').toUpperCase() }}
          </div>
          <div class="cba-app-actions" @click.stop>
            <button v-if="app.status === 'pending'" class="cba-btn-reject sm" title="Reject Application" @click="handleUpdateAppStatus(app.id, 'rejected')">
              <i class="bi bi-x-lg"></i>
            </button>
            <button v-if="app.status === 'pending'" class="cba-btn-accept sm" title="Accept Application" @click="handleUpdateAppStatus(app.id, 'accepted')">
              <i class="bi bi-check-lg"></i>
            </button>
            <button v-if="app.status === 'accepted'" class="cba-btn-assign sm" @click="openWorkAssign(app)">
              <i class="bi bi-briefcase-fill me-1"></i>Assign / View Work
            </button>
          </div>
        </div>
      </div>

      <div v-else class="cba-empty">
        <i class="bi bi-people"></i>
        <h3>No applicants yet</h3>
        <p>Students who apply to this bounty will appear here.</p>
      </div>
    </div>

    <!-- ─── Work Assign Tab ─── -->
    <div v-if="activeTab === 'workassign'" class="cba-workassign-section">
      <div v-if="!selectedBountyApps" class="cba-apps-prompt">
        <i class="bi bi-hand-index-thumb"></i>
        <h3>Select a bounty first</h3>
        <p>Click on a bounty from "My Bounties" tab to manage work assignments.</p>
      </div>

      <div v-else-if="!selectedApplicant" class="cba-apps-prompt">
        <i class="bi bi-person-badge"></i>
        <h3>Select an accepted applicant</h3>
        <p>Go to the Applicants tab and click on an accepted applicant to assign work here.</p>
        <button class="cba-btn-primary sm" @click="activeTab = 'applicants'"><i class="bi bi-people-fill me-1"></i>View Applicants</button>
      </div>

      <div v-else class="cba-workassign-layout">
        <div class="cwa-main">
          <div class="cwa-header">
            <button class="cba-back-btn" @click="selectedApplicant = null"><i class="bi bi-arrow-left me-1"></i>Back</button>
            <div class="cwa-header-info">
              <div class="cwa-header-avatar">{{ getInitials(selectedApplicant.student?.name) }}</div>
              <div>
                <h4 class="m-0">{{ selectedApplicant.student?.name || 'Student' }} — {{ assignedWorkData?.title || 'Assign Work' }}</h4>
                <span class="text-secondary small">{{ selectedApplicant.student?.department }} · {{ selectedBountyApps.title }}</span>
              </div>
              <span v-if="assignedWorkData" class="cba-work-status-badge ms-auto" :class="assignedWorkData.status">
                {{ (assignedWorkData.status || 'assigned').toUpperCase() }}
              </span>
            </div>
          </div>

          <div class="cwa-body">
            <!-- Progress Tracker -->
            <div class="cwa-progress-section">
              <div class="cwa-progress-track">
                <div class="cwa-progress-fill" :style="{ width: workProgressPercent + '%' }"></div>
              </div>
              <div class="cwa-progress-steps">
                <div class="cwa-step" :class="{ active: workProgressLevel >= 1 }"><i class="bi bi-person-check-fill"></i><span>Accepted</span></div>
                <div class="cwa-step" :class="{ active: workProgressLevel >= 2 }"><i class="bi bi-briefcase-fill"></i><span>Assigned</span></div>
                <div class="cwa-step" :class="{ active: workProgressLevel >= 3 }"><i class="bi bi-gear-fill"></i><span>In Progress</span></div>
                <div class="cwa-step" :class="{ active: workProgressLevel >= 4 }"><i class="bi bi-check-circle-fill"></i><span>Completed</span></div>
              </div>
            </div>

            <!-- Assign Work Form (if no work assigned yet) -->
            <div v-if="!assignedWorkData" class="cwa-form-card">
              <h5><i class="bi bi-pencil-square me-2 text-indigo"></i>Describe & Assign Work</h5>
              <p class="text-secondary small mb-3">Define the specific assignment, deadlines, and expected deliverables for {{ selectedApplicant.student?.name }}.</p>

              <div class="cba-form-group">
                <label>Task Title *</label>
                <input v-model="workForm.taskTitle" type="text" class="cba-input" placeholder="e.g. Develop Responsive Hero Section & Telemetry Visualizer" />
              </div>
              <div class="cba-form-group">
                <label>Task Description *</label>
                <textarea v-model="workForm.taskDescription" class="cba-input cba-textarea" rows="4" placeholder="Describe the task instructions, requirements, and milestones..."></textarea>
              </div>
              <div class="cba-form-group">
                <label>Deliverables (one per line) *</label>
                <textarea v-model="workForm.deliverables" class="cba-input cba-textarea" rows="3" placeholder="Setup frontend repo and components&#10;Implement live websocket chart&#10;Submit PR and documentation"></textarea>
              </div>
              <div class="cba-form-group">
                <label>Deadline *</label>
                <input v-model="workForm.deadline" type="datetime-local" class="cba-input" />
              </div>
              <button class="cba-btn-primary mt-3" :disabled="isSubmittingWork" @click="handleAssignWork">
                <span v-if="isSubmittingWork" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-send-fill me-2"></i>Assign Work to Student
              </button>
            </div>

            <!-- Existing Assigned Work View -->
            <div v-else class="cwa-assigned-section">
              <div class="cwa-assigned-card">
                <div class="cwa-assigned-title">
                  <i class="bi bi-briefcase-fill text-primary"></i>
                  <h5 class="m-0">{{ assignedWorkData.title }}</h5>
                </div>
                <div class="cwa-assigned-desc mt-2">
                  <strong>Description:</strong>
                  <p class="mt-1 text-light">{{ assignedWorkData.task_description }}</p>
                </div>
                <div class="cwa-assigned-meta mt-2">
                  <span><i class="bi bi-calendar3 me-1 text-info"></i>Deadline: {{ formatDisplayDate(assignedWorkData.deadline) }}</span>
                </div>
              </div>

              <!-- Deliverables Checklist -->
              <div v-if="assignedWorkData.deliverables?.length" class="cwa-checklist-card">
                <h5><i class="bi bi-list-check me-2 text-success"></i>Deliverables Checklist</h5>
                <div class="cwa-checklist">
                  <div
                    v-for="d in assignedWorkData.deliverables"
                    :key="d.id"
                    class="cwa-check-item"
                    :class="{ done: d.status === 'completed' }"
                    @click="toggleDeliverableStatus(d)"
                  >
                    <i class="bi" :class="d.status === 'completed' ? 'bi-check-circle-fill text-success' : 'bi-circle'"></i>
                    <span>{{ d.title }}</span>
                    <span class="badge ms-auto" :class="d.status === 'completed' ? 'bg-success' : 'bg-secondary'">{{ d.status }}</span>
                  </div>
                </div>
              </div>

              <!-- Admin Status Actions -->
              <div class="cwa-mark-card">
                <div class="d-flex align-items-center justify-content-between flex-wrap gap-2">
                  <div>
                    <h5 class="m-0"><i class="bi bi-patch-check-fill text-primary me-2"></i>Task Status Control</h5>
                    <span class="text-secondary small">Current Status: <strong class="text-light">{{ (assignedWorkData.status || '').toUpperCase() }}</strong></span>
                  </div>
                  <div class="d-flex gap-2">
                    <button
                      v-if="assignedWorkData.status !== 'in_progress'"
                      class="cba-btn-outline sm"
                      @click="handleUpdateWorkStatus('in_progress')"
                    >
                      <i class="bi bi-gear-fill me-1"></i>Set In Progress
                    </button>
                    <button
                      v-if="assignedWorkData.status !== 'completed'"
                      class="cba-btn-accept sm"
                      @click="handleUpdateWorkStatus('completed')"
                    >
                      <i class="bi bi-check-circle-fill me-1"></i>Mark Completed
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Create Bounty Modal ─── -->
    <div v-if="showCreateModal" class="cba-modal-overlay" @click.self="showCreateModal = false">
      <div class="cba-modal cba-modal-wide">
        <div class="cba-modal-header">
          <h3>Create New Campus Bounty</h3>
          <button class="cba-modal-close" @click="showCreateModal = false"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cba-modal-body">
          <!-- Title -->
          <div class="cba-form-group">
            <label>Bounty Title *</label>
            <input v-model="bountyForm.title" type="text" class="cba-input" placeholder="e.g. Build Real-Time IoT Telemetry Dashboard" />
          </div>

          <!-- Multiple Domains Selection -->
          <div class="cba-form-group">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <label class="m-0">Domains / Categories * <small class="text-secondary">({{ bountyForm.domain_ids.length }} selected)</small></label>
              <div class="d-flex gap-2">
                <button type="button" class="cba-link-btn" @click="selectAllDomains">Select All</button>
                <button type="button" class="cba-link-btn" @click="clearDomains">Reset</button>
              </div>
            </div>
            <div class="cba-chips cba-domain-chips">
              <button
                v-for="d in availableDomains"
                :key="d.id"
                type="button"
                class="cba-chip"
                :class="{ active: bountyForm.domain_ids.includes(d.id) }"
                @click="toggleDomain(d.id)"
              >
                <i class="bi" :class="bountyForm.domain_ids.includes(d.id) ? 'bi-check-circle-fill text-primary' : 'bi-plus'"></i>
                {{ formatDomainName(d.name) }}
              </button>
            </div>
          </div>

          <!-- Description -->
          <div class="cba-form-group">
            <label>Description *</label>
            <textarea v-model="bountyForm.description" class="cba-input cba-textarea" rows="3" placeholder="Describe the bounty objectives, deliverables, and student requirements..."></textarea>
          </div>

          <!-- Technologies (Filtered across all chosen domains) -->
          <div class="cba-form-group">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <label class="m-0">Required Technologies * <small class="text-secondary">({{ bountyForm.technologies.length }} selected)</small></label>
              <div v-if="selectedDomainTechs.length" class="d-flex gap-2">
                <button type="button" class="cba-link-btn" @click="selectAllTechs">Select All</button>
                <button type="button" class="cba-link-btn" @click="bountyForm.technologies = []">Clear</button>
              </div>
            </div>
            <div v-if="selectedDomainTechs.length" class="cba-chips">
              <button
                v-for="tech in selectedDomainTechs"
                :key="tech.id"
                type="button"
                class="cba-chip"
                :class="{ active: bountyForm.technologies.includes(tech.id) }"
                @click="toggleTech(tech.id)"
              >
                <i class="bi" :class="bountyForm.technologies.includes(tech.id) ? 'bi-check-circle-fill text-primary' : 'bi-plus'"></i>
                {{ tech.name }}
              </button>
            </div>
            <div v-else class="text-secondary small fst-italic">
              Select at least one Domain above to view and assign required technologies.
            </div>
          </div>

          <!-- Cover Image Upload (Cloudinary) -->
          <div class="cba-form-group">
            <label>Bounty Cover Image (Cloudinary)</label>
            <div class="cba-upload-zone" @click="fileInputRef?.click()" @dragover.prevent @drop.prevent="handleFileDrop" :class="{ 'has-image': bountyForm.image_preview }">
              <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden @change="handleFileUpload" />
              <template v-if="!bountyForm.image_preview">
                <div class="cba-upload-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                <p class="cba-upload-text">Drag & drop cover image or <span>Browse files</span></p>
                <p class="cba-upload-hint">PNG, JPG, WebP &middot; Uploaded directly to Cloudinary</p>
              </template>
              <template v-else>
                <img :src="bountyForm.image_preview" alt="Cover Preview" class="cba-upload-preview" />
                <button type="button" class="cba-upload-remove" @click.stop="removeImage" title="Remove image"><i class="bi bi-x-lg"></i></button>
              </template>
            </div>
          </div>

          <!-- Reward & Duration -->
          <div class="cba-form-row">
            <div class="cba-form-group">
              <label>Reward (₹) *</label>
              <input v-model="bountyForm.reward" type="number" min="0" class="cba-input" placeholder="e.g. 2500" />
            </div>
            <div class="cba-form-group">
              <label>Duration *</label>
              <input v-model="bountyForm.duration" type="text" class="cba-input" placeholder="e.g. 2 Weeks" />
            </div>
          </div>

          <!-- Deadline & Seats -->
          <div class="cba-form-row">
            <div class="cba-form-group">
              <label>Application Deadline *</label>
              <input v-model="bountyForm.deadline" type="datetime-local" class="cba-input" />
            </div>
            <div class="cba-form-group">
              <label>Student Seats Needed *</label>
              <div class="cba-stepper">
                <button type="button" class="cba-step-btn" @click="bountyForm.studentsNeeded > 1 && bountyForm.studentsNeeded--"><i class="bi bi-dash"></i></button>
                <span class="cba-step-val">{{ bountyForm.studentsNeeded }}</span>
                <button type="button" class="cba-step-btn" @click="bountyForm.studentsNeeded++"><i class="bi bi-plus"></i></button>
              </div>
            </div>
          </div>

          <!-- Key Responsibilities (One input per box) -->
          <div class="cba-form-group">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <label class="m-0">Key Responsibilities (One per box) *</label>
              <button type="button" class="cba-btn-add-resp" @click="addResponsibility">
                <i class="bi bi-plus-lg me-1"></i>Add Responsibility
              </button>
            </div>
            <div class="cba-resp-list">
              <div v-for="(resp, index) in bountyForm.responsibilities" :key="index" class="cba-resp-row">
                <span class="cba-resp-num">{{ index + 1 }}</span>
                <input
                  v-model="bountyForm.responsibilities[index]"
                  type="text"
                  class="cba-input flex-1"
                  :placeholder="`Responsibility ${index + 1} (e.g. Design UI wireframes in Figma)`"
                  @keydown.enter.prevent="addResponsibility"
                />
                <button
                  type="button"
                  class="cba-btn-delete-sm"
                  :disabled="bountyForm.responsibilities.length <= 1"
                  title="Remove responsibility"
                  @click="removeResponsibility(index)"
                >
                  <i class="bi bi-trash3"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="cba-modal-footer">
          <button class="cba-btn-glass" @click="showCreateModal = false">Cancel</button>
          <button class="cba-btn-primary" :disabled="isSubmittingBounty" @click="publishBounty">
            <span v-if="isSubmittingBounty" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-send-check-fill me-1"></i>Publish Bounty
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="showToast" class="cba-toast" :class="{ success: toastType === 'success', error: toastType === 'error' }">
      <i :class="toastType === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'"></i>
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';
import { store } from '../store/mockData';
import {
  fetchBountiesApi,
  createBountyApi,
  deleteBountyApi,
  fetchBountyApplicationsApi,
  updateApplicationStatusApi,
  assignWorkApi,
  fetchAssignedWorkApi,
  updateAssignedWorkApi,
  fetchDomainsAndTechsApi,
  uploadBountyImageApi,
} from '../api/bounty';

const DEFAULT_DOMAINS = [
  {
    id: 'web-dev',
    name: 'WEB_DEVELOPMENT',
    technologies: [
      { id: 'tech-react', name: 'REACT' },
      { id: 'tech-vue', name: 'VUE_JS' },
      { id: 'tech-next', name: 'NEXT_JS' },
      { id: 'tech-nuxt', name: 'NUXT_JS' },
      { id: 'tech-html', name: 'HTML' },
      { id: 'tech-css', name: 'CSS' },
      { id: 'tech-tailwind', name: 'TAILWIND_CSS' },
      { id: 'tech-bootstrap', name: 'BOOTSTRAP' },
      { id: 'tech-angular', name: 'ANGULAR' },
      { id: 'tech-svelte', name: 'SVELTE' },
    ],
  },
  {
    id: 'backend-dev',
    name: 'BACKEND_DEVELOPMENT',
    technologies: [
      { id: 'tech-fastapi', name: 'FASTAPI' },
      { id: 'tech-nodejs', name: 'NODE_JS' },
      { id: 'tech-express', name: 'EXPRESS_JS' },
      { id: 'tech-django', name: 'DJANGO' },
      { id: 'tech-flask', name: 'FLASK' },
      { id: 'tech-spring', name: 'SPRING_BOOT' },
      { id: 'tech-nest', name: 'NEST_JS' },
      { id: 'tech-laravel', name: 'LARAVEL' },
      { id: 'tech-graphql', name: 'GRAPHQL' },
      { id: 'tech-rest', name: 'REST_API' },
    ],
  },
  {
    id: 'ai-ml',
    name: 'AI_ML',
    technologies: [
      { id: 'tech-numpy', name: 'NUMPY' },
      { id: 'tech-pandas', name: 'PANDAS' },
      { id: 'tech-scikit', name: 'SCIKIT_LEARN' },
      { id: 'tech-tf', name: 'TENSORFLOW' },
      { id: 'tech-pytorch', name: 'PYTORCH' },
      { id: 'tech-keras', name: 'KERAS' },
      { id: 'tech-opencv', name: 'OPENCV' },
      { id: 'tech-langchain', name: 'LANGCHAIN' },
      { id: 'tech-huggingface', name: 'HUGGING_FACE' },
      { id: 'tech-openai', name: 'OPENAI_API' },
    ],
  },
  {
    id: 'app-dev',
    name: 'APP_DEVELOPMENT',
    technologies: [
      { id: 'tech-flutter', name: 'FLUTTER' },
      { id: 'tech-reactnative', name: 'REACT_NATIVE' },
      { id: 'tech-android', name: 'ANDROID' },
      { id: 'tech-jetpack', name: 'JETPACK_COMPOSE' },
      { id: 'tech-swiftui', name: 'SWIFT_UI' },
    ],
  },
  {
    id: 'cloud-comp',
    name: 'CLOUD_COMPUTING',
    technologies: [
      { id: 'tech-aws', name: 'AWS' },
      { id: 'tech-azure', name: 'AZURE' },
      { id: 'tech-gcp', name: 'GOOGLE_CLOUD' },
      { id: 'tech-firebase', name: 'FIREBASE' },
      { id: 'tech-supabase', name: 'SUPABASE' },
    ],
  },
  {
    id: 'devops',
    name: 'DEVOPS',
    technologies: [
      { id: 'tech-docker', name: 'DOCKER' },
      { id: 'tech-k8s', name: 'KUBERNETES' },
      { id: 'tech-jenkins', name: 'JENKINS' },
      { id: 'tech-githubactions', name: 'GITHUB_ACTIONS' },
      { id: 'tech-terraform', name: 'TERRAFORM' },
      { id: 'tech-ansible', name: 'ANSIBLE' },
      { id: 'tech-nginx', name: 'NGINX' },
      { id: 'tech-linux', name: 'LINUX' },
    ],
  },
  {
    id: 'database',
    name: 'DATABASE',
    technologies: [
      { id: 'tech-postgres', name: 'POSTGRESQL' },
      { id: 'tech-mysql', name: 'MYSQL' },
      { id: 'tech-mongodb', name: 'MONGODB' },
      { id: 'tech-redis', name: 'REDIS' },
      { id: 'tech-sqlite', name: 'SQLITE' },
    ],
  },
  {
    id: 'ui-ux',
    name: 'UI_UX_DESIGN',
    technologies: [
      { id: 'tech-figma', name: 'FIGMA' },
      { id: 'tech-adobexd', name: 'ADOBE_XD' },
      { id: 'tech-canva', name: 'CANVA' },
      { id: 'tech-photoshop', name: 'PHOTOSHOP' },
      { id: 'tech-illustrator', name: 'ILLUSTRATOR' },
    ],
  },
  {
    id: 'blockchain',
    name: 'BLOCKCHAIN',
    technologies: [
      { id: 'tech-solidity', name: 'SOLIDITY' },
      { id: 'tech-hardhat', name: 'HARDHAT' },
      { id: 'tech-foundry', name: 'FOUNDRY' },
      { id: 'tech-ethers', name: 'ETHERS_JS' },
      { id: 'tech-web3', name: 'WEB3_JS' },
    ],
  },
  {
    id: 'iot',
    name: 'IOT',
    technologies: [
      { id: 'tech-esp32', name: 'ESP32' },
      { id: 'tech-mqtt', name: 'MQTT' },
    ],
  },
  {
    id: 'robotics',
    name: 'ROBOTICS',
    technologies: [
      { id: 'tech-ros', name: 'ROS' },
      { id: 'tech-arduino-rob', name: 'ARDUINO' },
      { id: 'tech-raspi-rob', name: 'RASPBERRY_PI' },
    ],
  },
  {
    id: 'cyber-sec',
    name: 'CYBER_SECURITY',
    technologies: [
      { id: 'tech-kali', name: 'KALI_LINUX' },
      { id: 'tech-wireshark', name: 'WIRESHARK' },
      { id: 'tech-burp', name: 'BURP_SUITE' },
      { id: 'tech-nmap', name: 'NMAP' },
      { id: 'tech-metasploit', name: 'METASPLOIT' },
      { id: 'tech-owasp', name: 'OWASP' },
    ],
  },
];

const activeTab = ref('bounties');
const searchQuery = ref('');
const statusFilter = ref('All');
const selectedBountyApps = ref(null);
const selectedApplicant = ref(null);
const assignedWorkData = ref(null);
const showCreateModal = ref(false);
const fileInputRef = ref(null);

const liveBounties = ref([]);
const availableDomains = ref([...DEFAULT_DOMAINS]);
const isLoadingBounties = ref(false);
const isLoadingApplicants = ref(false);
const isSubmittingBounty = ref(false);
const isSubmittingWork = ref(false);

const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('success');

const currentApplicants = ref([]);

const workForm = reactive({
  taskTitle: '',
  taskDescription: '',
  deliverables: '',
  deadline: '',
});

const bountyForm = reactive({
  title: '',
  domain_ids: [DEFAULT_DOMAINS[0].id],
  description: '',
  technologies: [],
  reward: '2500',
  deadline: '',
  duration: '2 Weeks',
  studentsNeeded: 1,
  image_file: null,
  image_preview: null,
  image_url: '',
  responsibilities: ['Design and implement core features', 'Submit pull request with clean tests'],
});

const getToken = () => store.token || localStorage.getItem('driven_token');

// ── Metrics ──
const activeBountiesCount = computed(() => liveBounties.value.filter(b => b.status === 'open').length);
const totalApplicantsCount = computed(() => liveBounties.value.reduce((acc, b) => acc + (b.student_seats || 0), 0));
const completedBountiesCount = computed(() => liveBounties.value.filter(b => b.status === 'completed').length);
const openSeatsCount = computed(() => liveBounties.value.filter(b => b.status === 'open').reduce((acc, b) => acc + (b.student_seats || 0), 0));

const myBountyList = computed(() => {
  let result = liveBounties.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(b => (b.title || '').toLowerCase().includes(q) || (b.description || '').toLowerCase().includes(q));
  }
  if (statusFilter.value !== 'All') {
    result = result.filter(b => b.status === statusFilter.value);
  }
  return result;
});

// All technologies belonging to all selected domains
const selectedDomainTechs = computed(() => {
  if (!bountyForm.domain_ids.length) return [];
  const techs = [];
  const seen = new Set();
  availableDomains.value.forEach(d => {
    if (bountyForm.domain_ids.includes(d.id)) {
      d.technologies?.forEach(t => {
        if (!seen.has(t.id)) {
          seen.add(t.id);
          techs.push(t);
        }
      });
    }
  });
  return techs;
});

const workProgressLevel = computed(() => {
  if (!assignedWorkData.value) {
    if (selectedApplicant.value?.status === 'accepted') return 1;
    return 0;
  }
  if (assignedWorkData.value.status === 'completed') return 4;
  if (assignedWorkData.value.status === 'in_progress') return 3;
  if (assignedWorkData.value.status === 'assigned') return 2;
  return 1;
});

const workProgressPercent = computed(() => (workProgressLevel.value / 4) * 100);

// ── Lifecycle & Data Loading ──
onMounted(async () => {
  await Promise.all([loadBounties(), loadDomains()]);
});

const loadBounties = async () => {
  isLoadingBounties.value = true;
  try {
    const data = await fetchBountiesApi({}, getToken());
    liveBounties.value = data;
  } catch (err) {
    console.error('Failed to load bounties:', err);
  } finally {
    isLoadingBounties.value = false;
  }
};

const loadDomains = async () => {
  try {
    const data = await fetchDomainsAndTechsApi(getToken());
    if (data && data.length) {
      availableDomains.value = data;
      if (
        !bountyForm.domain_ids.length ||
        !availableDomains.value.some(d => d.id === bountyForm.domain_ids[0])
      ) {
        bountyForm.domain_ids = [data[0].id];
      }
    }
  } catch (err) {
    console.error('Failed to load domains from backend, using defaults:', err);
  }
};

const openCreateModal = async () => {
  await loadDomains();
  if (availableDomains.value.length && (!bountyForm.domain_ids.length || !availableDomains.value.some(d => d.id === bountyForm.domain_ids[0]))) {
    bountyForm.domain_ids = [availableDomains.value[0].id];
  }
  // Default deadline 14 days ahead
  const defaultDate = new Date();
  defaultDate.setDate(defaultDate.getDate() + 14);
  bountyForm.deadline = defaultDate.toISOString().slice(0, 16);
  if (!bountyForm.responsibilities.length) {
    bountyForm.responsibilities = ['Design and implement core features', 'Submit pull request with clean tests'];
  }
  showCreateModal.value = true;
};

// ── Multi-domain toggle ──
const toggleDomain = (domainId) => {
  const idx = bountyForm.domain_ids.indexOf(domainId);
  if (idx > -1) {
    if (bountyForm.domain_ids.length > 1) {
      bountyForm.domain_ids.splice(idx, 1);
    }
  } else {
    bountyForm.domain_ids.push(domainId);
  }
};

const selectAllDomains = () => {
  bountyForm.domain_ids = availableDomains.value.map(d => d.id);
};

const clearDomains = () => {
  if (availableDomains.value.length) {
    bountyForm.domain_ids = [availableDomains.value[0].id];
    bountyForm.technologies = [];
  }
};

const toggleTech = (techId) => {
  const idx = bountyForm.technologies.indexOf(techId);
  if (idx > -1) bountyForm.technologies.splice(idx, 1);
  else bountyForm.technologies.push(techId);
};

const selectAllTechs = () => {
  bountyForm.technologies = selectedDomainTechs.value.map(t => t.id);
};

// ── Responsibilities Dynamic Inputs ──
const addResponsibility = () => {
  bountyForm.responsibilities.push('');
};

const removeResponsibility = (index) => {
  if (bountyForm.responsibilities.length > 1) {
    bountyForm.responsibilities.splice(index, 1);
  }
};

// ── Image Upload Handling (Cloudinary) ──
const handleFileUpload = (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  bountyForm.image_file = file;
  const reader = new FileReader();
  reader.onload = (ev) => {
    bountyForm.image_preview = ev.target?.result || null;
  };
  reader.readAsDataURL(file);
};

const handleFileDrop = (e) => {
  e.preventDefault();
  const file = e.dataTransfer?.files?.[0];
  if (!file) return;
  bountyForm.image_file = file;
  const reader = new FileReader();
  reader.onload = (ev) => {
    bountyForm.image_preview = ev.target?.result || null;
  };
  reader.readAsDataURL(file);
};

const removeImage = () => {
  bountyForm.image_file = null;
  bountyForm.image_preview = null;
  bountyForm.image_url = '';
  if (fileInputRef.value) fileInputRef.value.value = '';
};

const isUUID = (str) => typeof str === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);

// ── Publish Bounty ──
const publishBounty = async () => {
  console.log('[CampusBountyAdmin] publishBounty clicked with form:', JSON.parse(JSON.stringify(bountyForm)));

  if (!bountyForm.title || !bountyForm.title.trim()) {
    displayToast('Please enter a Bounty Title.', 'error');
    return;
  }
  if (!bountyForm.domain_ids || !bountyForm.domain_ids.length) {
    displayToast('Please select at least one Domain / Category.', 'error');
    return;
  }
  if (!bountyForm.description || !bountyForm.description.trim()) {
    displayToast('Please enter a Bounty Description.', 'error');
    return;
  }
  if (!bountyForm.deadline) {
    displayToast('Please specify an Application Deadline.', 'error');
    return;
  }

  isSubmittingBounty.value = true;
  try {
    // 1. Upload cover image to Cloudinary if file provided
    let imageUrl = bountyForm.image_url || null;
    if (bountyForm.image_file) {
      try {
        imageUrl = await uploadBountyImageApi(bountyForm.image_file, getToken());
      } catch (err) {
        console.warn('Cloudinary upload warning:', err);
      }
    }

    const validResponsibilities = bountyForm.responsibilities
      .map(r => (typeof r === 'string' ? r.trim() : ''))
      .filter(Boolean);

    // 2. Safe parse deadline
    let deadlineIso = '';
    const parsedDate = new Date(bountyForm.deadline);
    if (!isNaN(parsedDate.getTime())) {
      deadlineIso = parsedDate.toISOString();
    } else {
      const fallbackDate = new Date();
      fallbackDate.setDate(fallbackDate.getDate() + 14);
      deadlineIso = fallbackDate.toISOString();
    }

    // 3. Resolve primary domain ID to a real UUID
    let primaryDomainId = bountyForm.domain_ids[0];
    let foundDomain = availableDomains.value.find(d => isUUID(d.id) && (d.id === primaryDomainId || d.name === primaryDomainId));
    if (!foundDomain) {
      await loadDomains();
      foundDomain = availableDomains.value.find(d => isUUID(d.id) && (d.id === primaryDomainId || d.name === primaryDomainId)) || availableDomains.value.find(d => isUUID(d.id));
    }
    if (foundDomain) {
      primaryDomainId = foundDomain.id;
    }

    // 4. Resolve technologies to real UUIDs
    const validTechIds = bountyForm.technologies
      .map(tId => {
        if (isUUID(tId)) return tId;
        for (const d of availableDomains.value) {
          const match = d.technologies?.find(t => isUUID(t.id) && (t.id === tId || t.name === tId));
          if (match) return match.id;
        }
        return null;
      })
      .filter(Boolean);

    const payload = {
      title: bountyForm.title.trim(),
      domain_id: primaryDomainId,
      description: bountyForm.description.trim(),
      reward: Number(bountyForm.reward) || 0,
      application_deadline: deadlineIso,
      duration: (bountyForm.duration && bountyForm.duration.trim()) || '2 Weeks',
      student_seats: Math.max(1, Number(bountyForm.studentsNeeded) || 1),
      image_url: imageUrl,
      technologies: validTechIds,
      responsibilities: validResponsibilities.length ? validResponsibilities : ['Active project execution and delivery'],
    };

    console.log('[CampusBountyAdmin] Submitting create bounty payload:', payload);
    const token = getToken();
    const result = await createBountyApi(payload, token);
    console.log('[CampusBountyAdmin] Bounty created response:', result);

    showCreateModal.value = false;
    displayToast('Campus Bounty created successfully!', 'success');
    await loadBounties();
  } catch (err) {
    console.error('Failed to create bounty:', err);
    displayToast(err.message || 'Failed to create bounty.', 'error');
  } finally {
    isSubmittingBounty.value = false;
  }
};

const handleDeleteBounty = async (bounty) => {
  if (!confirm(`Are you sure you want to delete "${bounty.title}"?`)) return;
  try {
    await deleteBountyApi(bounty.id, getToken());
    displayToast('Bounty deleted.', 'success');
    if (selectedBountyApps.value?.id === bounty.id) {
      selectedBountyApps.value = null;
      selectedApplicant.value = null;
    }
    await loadBounties();
  } catch (err) {
    displayToast(err.message || 'Failed to delete bounty.', 'error');
  }
};

// ── Select Bounty & Load Applicants ──
const selectBounty = async (bounty) => {
  selectedBountyApps.value = bounty;
  selectedApplicant.value = null;
  assignedWorkData.value = null;
  activeTab.value = 'applicants';
  await loadBountyApplicants(bounty.id);
};

const loadBountyApplicants = async (bountyId) => {
  isLoadingApplicants.value = true;
  try {
    const apps = await fetchBountyApplicationsApi(bountyId, getToken());
    currentApplicants.value = apps;
  } catch (err) {
    displayToast(err.message || 'Failed to load applicants.', 'error');
  } finally {
    isLoadingApplicants.value = false;
  }
};

const handleUpdateAppStatus = async (appId, status) => {
  try {
    await updateApplicationStatusApi(appId, status, getToken());
    displayToast(`Application ${status} successfully.`, 'success');
    if (selectedBountyApps.value) {
      await loadBountyApplicants(selectedBountyApps.value.id);
    }
  } catch (err) {
    displayToast(err.message || 'Failed to update application status.', 'error');
  }
};

// ── Work Assign Tab ──
const openWorkAssign = async (app) => {
  selectedApplicant.value = app;
  activeTab.value = 'workassign';
  try {
    const work = await fetchAssignedWorkApi(app.id, getToken());
    assignedWorkData.value = work;
  } catch {
    assignedWorkData.value = null;
  }

  if (!assignedWorkData.value) {
    workForm.taskTitle = `Complete ${selectedBountyApps.value?.title || 'Bounty Project'}`;
    workForm.taskDescription = selectedBountyApps.value?.description || '';
    workForm.deliverables = (selectedBountyApps.value?.responsibilities || []).map(r => r.title).join('\n');
    const d = new Date();
    d.setDate(d.getDate() + 7);
    workForm.deadline = d.toISOString().slice(0, 16);
  }
};

const handleAssignWork = async () => {
  if (!workForm.taskTitle.trim() || !workForm.taskDescription.trim() || !workForm.deadline) {
    displayToast('Please fill in task title, description, and deadline.', 'error');
    return;
  }

  isSubmittingWork.value = true;
  try {
    const deliverables = workForm.deliverables
      .split('\n')
      .map(d => d.trim())
      .filter(Boolean)
      .map(title => ({ title }));

    const payload = {
      title: workForm.taskTitle.trim(),
      task_description: workForm.taskDescription.trim(),
      deadline: new Date(workForm.deadline).toISOString(),
      event_id: null,
      deliverables: deliverables.length ? deliverables : [{ title: 'Main Project Deliverable' }],
    };

    const work = await assignWorkApi(selectedApplicant.value.id, payload, getToken());
    assignedWorkData.value = work;
    displayToast('Work assigned successfully to student!', 'success');
  } catch (err) {
    displayToast(err.message || 'Failed to assign work.', 'error');
  } finally {
    isSubmittingWork.value = false;
  }
};

const handleUpdateWorkStatus = async (newStatus) => {
  if (!selectedApplicant.value) return;
  try {
    const work = await updateAssignedWorkApi(selectedApplicant.value.id, { status: newStatus }, getToken());
    assignedWorkData.value = work;
    displayToast(`Task marked as ${newStatus}.`, 'success');
  } catch (err) {
    displayToast(err.message || 'Failed to update work status.', 'error');
  }
};

const toggleDeliverableStatus = async (deliverable) => {
  if (!selectedApplicant.value || !assignedWorkData.value) return;
  const newStatus = deliverable.status === 'completed' ? 'in_progress' : 'completed';
  try {
    const work = await updateAssignedWorkApi(
      selectedApplicant.value.id,
      {
        deliverables: [{ id: deliverable.id, status: newStatus }],
      },
      getToken()
    );
    assignedWorkData.value = work;
  } catch (err) {
    displayToast(err.message || 'Failed to update deliverable.', 'error');
  }
};

// ── Tab navigation ──
const goToApplicantsTab = () => {
  if (selectedBountyApps.value) activeTab.value = 'applicants';
};

const goToWorkAssignTab = () => {
  if (selectedBountyApps.value) activeTab.value = 'workassign';
};

// ── Helpers ──
const formatDomainName = (name) => {
  if (!name) return 'General';
  return String(name).replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
};

const formatDept = (dept) => {
  if (!dept) return 'Engineering';
  return String(dept).replace(/_/g, ' ').toUpperCase();
};

const formatDisplayDate = (d) => {
  if (!d) return 'TBD';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const getInitials = (name) => {
  if (!name) return 'S';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
};

const displayToast = (msg, type = 'success') => {
  toastMessage.value = msg;
  toastType.value = type;
  showToast.value = true;
  setTimeout(() => { showToast.value = false; }, 3000);
};
</script>

<style scoped>
.cba {
  position: relative;
  z-index: 1;
  padding-bottom: 3rem;
}

.cba-hero {
  position: relative;
  margin-bottom: 2rem;
  padding: 2.5rem 0 1.5rem;
  overflow: hidden;
}
.cba-hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.04) 0%, rgba(15, 23, 42, 0.4) 100%);
  border-radius: 20px;
}
.cba-hero-glow {
  position: absolute;
  top: -20%;
  right: -5%;
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, rgba(129, 140, 248, 0.08) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
}
.cba-hero-inner {
  display: flex;
  align-items: center;
  gap: 3rem;
  position: relative;
  z-index: 1;
}
.cba-hero-left {
  flex: 1;
  min-width: 0;
}
.cba-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(129, 140, 248, 0.25);
  font-size: 0.75rem;
  font-weight: 700;
  color: #818cf8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.85rem;
}
.cba-hero-title {
  font-size: 2.2rem;
  font-weight: 900;
  color: #f1f5f9;
  margin: 0 0 0.6rem;
  letter-spacing: -0.5px;
}
.cba-hero-text {
  font-size: 0.95rem;
  color: #94a3b8;
  line-height: 1.6;
  margin: 0 0 1.5rem;
}
.cba-hero-right {
  flex-shrink: 0;
}

.cba-stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
.cba-stat-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem 1.25rem;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  min-width: 170px;
}
.cba-stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
  flex-shrink: 0;
}
.cba-stat-icon.purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.cba-stat-icon.blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.cba-stat-icon.green { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.cba-stat-icon.amber { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

.cba-stat-body {
  display: flex;
  flex-direction: column;
}
.cba-stat-value {
  font-size: 1.35rem;
  font-weight: 800;
  color: #f1f5f9;
  line-height: 1.2;
}
.cba-stat-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

/* Tabs */
.cba-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.5rem;
}
.cba-tab {
  display: inline-flex;
  align-items: center;
  padding: 0.65rem 1.2rem;
  border-radius: 10px;
  background: transparent;
  border: 1px solid transparent;
  color: #94a3b8;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-tab:hover {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.04);
}
.cba-tab.active {
  color: #ffffff;
  background: rgba(99, 102, 241, 0.18);
  border-color: rgba(129, 140, 248, 0.35);
}
.cba-tab.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.cba-tab-count {
  background: #6366f1;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  margin-left: 0.5rem;
}

/* Toolbar */
.cba-toolbar {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.cba-search-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
}
.cba-search-wrap i {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.88rem;
}
.cba-search-wrap input {
  width: 100%;
  padding: 0.65rem 0.9rem 0.65rem 2.4rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
}
.cba-filter-select {
  padding: 0.65rem 1rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
}
.cba-filter-select option {
  background-color: #0f172a;
  color: #f1f5f9;
}

/* Bounty Rows */
.cba-bounty-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.cba-bounty-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.15rem 1.35rem;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}
.cba-bounty-row:hover {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(129, 140, 248, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}
.cba-bounty-row.active {
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3);
}
.cba-bounty-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #818cf8;
  flex-shrink: 0;
}
.cba-bounty-info {
  flex: 1;
  min-width: 0;
}
.cba-bounty-cat {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.25);
  color: #c7d2fe;
}
.cba-bounty-desc-preview {
  font-size: 0.84rem;
  color: #94a3b8;
  margin: 0 0 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cba-bounty-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.78rem;
  color: #cbd5e1;
  flex-wrap: wrap;
}
.cba-bounty-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}
.cba-status-badge {
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.cba-status-badge.open { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
.cba-status-badge.in_progress { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
.cba-status-badge.completed { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
.cba-status-badge.closed { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }

.cba-bounty-apps-btn {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.3);
  border-radius: 8px;
  padding: 0.35rem 0.75rem;
  color: #c7d2fe;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.cba-bounty-apps-btn:hover {
  background: rgba(99, 102, 241, 0.3);
  color: #ffffff;
}

.cba-btn-delete-sm {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.15s;
}
.cba-btn-delete-sm:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.3);
  color: #ffffff;
}
.cba-btn-delete-sm:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Applicants list */
.cba-apps-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.cba-apps-count {
  font-size: 0.84rem;
  font-weight: 700;
  color: #818cf8;
}
.cba-apps-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.cba-applicant-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.1rem 1.25rem;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s;
}
.cba-applicant-row:hover {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(129, 140, 248, 0.3);
}
.cba-applicant-avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
  color: #ffffff;
  flex-shrink: 0;
}
.cba-applicant-avatar.yellow { background: linear-gradient(135deg, #f59e0b, #d97706); }
.cba-applicant-avatar.green { background: linear-gradient(135deg, #10b981, #059669); }
.cba-applicant-avatar.red { background: linear-gradient(135deg, #ef4444, #dc2626); }

.cba-applicant-info {
  flex: 1;
  min-width: 0;
}
.cba-applicant-info h5 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.cba-app-dept {
  font-size: 0.78rem;
  color: #94a3b8;
}
.cba-app-status-badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  text-transform: uppercase;
}
.cba-app-status-badge.pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.cba-app-status-badge.accepted { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.cba-app-status-badge.rejected { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.cba-app-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
.cba-btn-reject {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
}
.cba-btn-reject:hover { background: rgba(239, 68, 68, 0.3); }
.cba-btn-accept {
  background: rgba(52, 211, 153, 0.15);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #34d399;
  border-radius: 8px;
  padding: 0.4rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}
.cba-btn-accept:hover { background: rgba(52, 211, 153, 0.3); }
.cba-btn-assign {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.3);
  color: #c7d2fe;
  border-radius: 8px;
  padding: 0.4rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}
.cba-btn-assign:hover { background: rgba(99, 102, 241, 0.3); color: #ffffff; }

/* Work Assign Layout */
.cba-workassign-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.cwa-main {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 1.5rem;
  backdrop-filter: blur(12px);
}
.cwa-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 1.5rem;
}
.cwa-header-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #ffffff;
}
.cba-work-status-badge {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.2);
  color: #c7d2fe;
  border: 1px solid rgba(129, 140, 248, 0.3);
}

/* Progress Section */
.cwa-progress-section {
  margin-bottom: 2rem;
}
.cwa-progress-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 1rem;
}
.cwa-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #34d399);
  transition: width 0.3s ease;
}
.cwa-progress-steps {
  display: flex;
  justify-content: space-between;
}
.cwa-step {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
}
.cwa-step.active {
  color: #34d399;
}

/* Form & Assigned Cards */
.cwa-form-card, .cwa-assigned-card, .cwa-checklist-card, .cwa-mark-card {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}
.cwa-assigned-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.cwa-checklist {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.85rem;
}
.cwa-check-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  font-size: 0.88rem;
  color: #e2e8f0;
  transition: all 0.15s;
}
.cwa-check-item:hover {
  background: rgba(255, 255, 255, 0.05);
}
.cwa-check-item.done {
  color: #94a3b8;
  text-decoration: line-through;
}

/* Form Controls */
.cba-form-group {
  margin-bottom: 1.15rem;
}
.cba-form-group label {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  color: #cbd5e1;
  margin-bottom: 0.35rem;
}
.cba-form-row {
  display: flex;
  gap: 1rem;
}
.cba-form-row .cba-form-group {
  flex: 1;
}
.cba-input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
}
.cba-input:focus {
  border-color: #818cf8;
}
select.cba-input {
  cursor: pointer;
}
select.cba-input option {
  background-color: #0f172a;
  color: #f1f5f9;
  padding: 0.5rem;
}
.cba-textarea {
  resize: vertical;
}

/* Chips */
.cba-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-height: 180px;
  overflow-y: auto;
  padding: 0.6rem;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.cba-domain-chips {
  max-height: 140px;
}
.cba-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.4rem 0.85rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.cba-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}
.cba-chip.active {
  background: rgba(99, 102, 241, 0.25);
  border-color: #818cf8;
  color: #ffffff;
}

.cba-link-btn {
  background: transparent;
  border: none;
  color: #818cf8;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
}
.cba-link-btn:hover {
  text-decoration: underline;
}

/* Responsibilities List */
.cba-resp-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 220px;
  overflow-y: auto;
}
.cba-resp-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.cba-resp-num {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.2);
  color: #c7d2fe;
  font-size: 0.75rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.cba-btn-add-resp {
  background: rgba(99, 102, 241, 0.15);
  border: 1px dashed rgba(129, 140, 248, 0.4);
  color: #c7d2fe;
  border-radius: 8px;
  padding: 0.35rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.cba-btn-add-resp:hover {
  background: rgba(99, 102, 241, 0.3);
  color: #ffffff;
}

/* Cover Image Upload (Cloudinary) */
.cba-upload-zone {
  border: 2px dashed rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 1.25rem 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(15, 23, 42, 0.5);
  position: relative;
  min-height: 110px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.cba-upload-zone:hover {
  border-color: rgba(129, 140, 248, 0.5);
  background: rgba(15, 23, 42, 0.8);
}
.cba-upload-zone.has-image {
  padding: 0.5rem;
  border-style: solid;
  border-color: rgba(99, 102, 241, 0.4);
}
.cba-upload-icon {
  font-size: 1.8rem;
  color: #818cf8;
  margin-bottom: 0.25rem;
}
.cba-upload-text {
  font-size: 0.82rem;
  color: #cbd5e1;
  margin: 0 0 0.15rem;
}
.cba-upload-text span {
  color: #818cf8;
  font-weight: 700;
  text-decoration: underline;
}
.cba-upload-hint {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0;
}
.cba-upload-preview {
  width: 100%;
  max-height: 160px;
  object-fit: cover;
  border-radius: 8px;
}
.cba-upload-remove {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  cursor: pointer;
}
.cba-upload-remove:hover {
  background: #ef4444;
}

/* Stepper */
.cba-stepper {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 0.25rem 0.5rem;
}
.cba-step-btn {
  background: transparent;
  border: none;
  color: #cbd5e1;
  font-size: 1rem;
  cursor: pointer;
}
.cba-step-val {
  font-weight: 800;
  color: #f1f5f9;
  font-size: 0.9rem;
}

/* Modals */
.cba-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1.5rem;
}
.cba-modal {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 24px;
  width: 100%;
  max-width: 880px;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75);
}
.cba-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cba-modal-header h3 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0;
}
.cba-modal-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
}
.cba-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}
.cba-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Buttons */
.cba-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1.2rem;
  color: #ffffff;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}
.cba-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}
.cba-btn-primary.sm {
  padding: 0.5rem 0.9rem;
  font-size: 0.82rem;
}

.cba-btn-glass {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.6rem 1.1rem;
  color: #cbd5e1;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
}
.cba-btn-outline {
  background: transparent;
  border: 1px solid rgba(129, 140, 248, 0.35);
  color: #c7d2fe;
  border-radius: 8px;
  padding: 0.4rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}

.cba-back-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  border-radius: 8px;
  padding: 0.35rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.cba-empty, .cba-apps-prompt, .cba-loading {
  text-align: center;
  padding: 3.5rem 1.5rem;
  color: #64748b;
}
.cba-empty i, .cba-apps-prompt i {
  font-size: 2.5rem;
  color: #475569;
  margin-bottom: 0.75rem;
  display: block;
}

/* Toast */
.cba-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 0.88rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 1100;
}
.cba-toast.success { border-color: #34d399; }
.cba-toast.error { border-color: #ef4444; }
.cba-toast.success i { color: #34d399; }
.cba-toast.error i { color: #ef4444; }
</style>