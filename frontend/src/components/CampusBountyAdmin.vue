<template>
  <div class="cba">
    <section class="cba-hero">
      <div class="cba-hero-bg"></div>
      <div class="cba-hero-glow"></div>
      <div class="cba-hero-inner">
        <div class="cba-hero-left">
          <div class="cba-hero-badge">Bounty Dashboard</div>
          <h1 class="cba-hero-title">Campus Bounties</h1>
          <p class="cba-hero-text">Post short-term opportunities, find talented students, and manage verified work submissions — all in one place.</p>
          <button class="cba-btn-primary" @click="showCreateModal = true"><i class="bi bi-plus-lg me-2"></i>Create Bounty</button>
        </div>
        <div class="cba-hero-right">
          <div class="cba-stat-grid">
            <div class="cba-stat-card">
              <div class="cba-stat-icon purple"><i class="bi bi-briefcase-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ activeBounties }}</span><span class="cba-stat-label">Active Bounties</span></div>
            </div>
            <div class="cba-stat-card">
              <div class="cba-stat-icon blue"><i class="bi bi-people-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ totalApplicants }}</span><span class="cba-stat-label">Total Applicants</span></div>
            </div>
            <div class="cba-stat-card">
              <div class="cba-stat-icon green"><i class="bi bi-check-circle-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ completedCount }}</span><span class="cba-stat-label">Completed</span></div>
            </div>
            <div class="cba-stat-card">
              <div class="cba-stat-icon amber"><i class="bi bi-box-seam-fill"></i></div>
              <div class="cba-stat-body"><span class="cba-stat-value">{{ openPositions }}</span><span class="cba-stat-label">Open Positions</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="cba-tabs">
      <button class="cba-tab" :class="{ active: activeTab === 'bounties' }" @click="activeTab = 'bounties'"><i class="bi bi-grid-3x3-gap-fill me-2"></i>My Bounties</button>
      <button class="cba-tab" :class="{ active: activeTab === 'applicants', disabled: !selectedBountyApps }" @click="goToApplicantsTab"><i class="bi bi-people-fill me-2"></i>Applicants <span v-if="selectedBountyApps" class="cba-tab-count">{{ currentApplicants.length }}</span></button>
      <button class="cba-tab" :class="{ active: activeTab === 'workassign', disabled: !selectedBountyApps }" @click="goToWorkAssignTab"><i class="bi bi-briefcase-fill me-2"></i>Work Assign</button>
    </div>

    <!-- My Bounties Tab -->
    <div v-if="activeTab === 'bounties'" class="cba-bounties-section">
      <div class="cba-toolbar">
        <div class="cba-search-wrap">
          <i class="bi bi-search"></i>
          <input v-model="searchQuery" type="text" placeholder="Search bounties..." />
        </div>
        <select v-model="statusFilter" class="cba-filter-select">
          <option value="All">All Status</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
          <option value="draft">Draft</option>
        </select>
        <button class="cba-btn-primary sm" @click="showCreateModal = true"><i class="bi bi-plus-lg me-1"></i>New Bounty</button>
      </div>

      <div v-if="myBountyList.length" class="cba-bounty-list">
        <div v-for="bounty in myBountyList" :key="bounty.id" class="cba-bounty-row" :class="{ active: selectedBountyApps?.id === bounty.id }" @click="selectBounty(bounty)">
          <div class="cba-bounty-img" :style="{ backgroundImage: `url(${bounty.image})` }"></div>
          <div class="cba-bounty-info">
            <h4>{{ bounty.title }}</h4>
            <span class="cba-bounty-cat">{{ bounty.category }}</span>
            <div class="cba-bounty-meta">
              <span><i class="bi bi-cash-stack"></i>{{ bounty.reward }}</span>
              <span><i class="bi bi-calendar3"></i>{{ bounty.deadline }}</span>
              <span><i class="bi bi-people"></i>{{ bounty.applicantsCount }} applicants</span>
            </div>
          </div>
          <div class="cba-bounty-status">
            <span class="cba-status-badge" :class="bounty.status">{{ bounty.status.charAt(0).toUpperCase() + bounty.status.slice(1) }}</span>
            <span class="cba-bounty-apps-btn" @click.stop="selectBounty(bounty)">View Applicants <i class="bi bi-chevron-right ms-1"></i></span>
          </div>
        </div>
      </div>
      <div v-else class="cba-empty">
        <i class="bi bi-inbox"></i>
        <h3>No bounties yet</h3>
        <p>Create your first bounty to find talented students.</p>
        <button class="cba-btn-primary" @click="showCreateModal = true"><i class="bi bi-plus-lg me-1"></i>Create Bounty</button>
      </div>
    </div>

    <!-- Applicants Tab -->
    <div v-if="activeTab === 'applicants'" class="cba-applicants-section">
      <div v-if="selectedBountyApps" class="cba-apps-header">
        <button class="cba-back-btn" @click="selectedBountyApps = null; selectedApplicant = null"><i class="bi bi-arrow-left me-1"></i>Back</button>
        <h3>{{ selectedBountyApps.title }} — Applicants</h3>
        <span class="cba-apps-count">{{ currentApplicants.length }} total</span>
      </div>

      <div v-if="!selectedBountyApps" class="cba-apps-prompt">
        <i class="bi bi-hand-index-thumb"></i>
        <h3>Select a bounty</h3>
        <p>Click on a bounty from "My Bounties" tab to view its applicants.</p>
      </div>

      <div v-else-if="currentApplicants.length" class="cba-apps-list">
        <div v-for="app in currentApplicants" :key="app.id" class="cba-applicant-row" :class="{ rejected: app.status === 'rejected' }" @click="openWorkAssign(app)">
          <div class="cba-applicant-avatar" :class="{ green: app.status === 'accepted' || app.status === 'assigned', yellow: app.status === 'pending' }">
            {{ app.name?.charAt(0) || 'S' }}
          </div>
          <div class="cba-applicant-info">
            <h5>{{ app.name || 'Student' }}</h5>
            <span class="cba-app-dept">{{ app.department || 'Computer Science' }}</span>
          </div>
          <div class="cba-app-status-badge" :class="app.status">
            {{ app.status.charAt(0).toUpperCase() + app.status.slice(1) }}
          </div>
          <div class="cba-app-progress-compact">
            <div class="cba-compact-bar">
              <div class="cba-compact-fill" :style="{ width: progressPercent(app) + '%' }"></div>
            </div>
            <span class="cba-compact-label">{{ progressLabel(app) }}</span>
          </div>
          <div class="cba-app-actions" @click.stop>
            <button v-if="app.status === 'pending'" class="cba-btn-reject sm" @click="updateAppStatus(app.id, 'rejected')"><i class="bi bi-x-lg"></i></button>
            <button v-if="app.status === 'pending'" class="cba-btn-accept sm" @click="updateAppStatus(app.id, 'accepted')"><i class="bi bi-check-lg"></i></button>
            <button v-if="app.status === 'accepted' || app.status === 'assigned'" class="cba-btn-assign sm" @click="openWorkAssign(app)"><i class="bi bi-briefcase-fill me-1"></i>Assign Work</button>
          </div>
        </div>
      </div>

      <div v-else class="cba-empty">
        <i class="bi bi-people"></i>
        <h3>No applicants yet</h3>
        <p>Applicants will appear here once students apply.</p>
      </div>
    </div>

    <!-- Work Assign Tab -->
    <div v-if="activeTab === 'workassign'" class="cba-workassign-section">
      <div v-if="!selectedBountyApps" class="cba-apps-prompt">
        <i class="bi bi-hand-index-thumb"></i>
        <h3>Select a bounty first</h3>
        <p>Click on a bounty from "My Bounties" tab to manage work assignments.</p>
      </div>

      <div v-else-if="!selectedApplicant" class="cba-apps-prompt">
        <i class="bi bi-person-badge"></i>
        <h3>Select an applicant</h3>
        <p>Go to the Applicants tab and click on an applicant to assign work here.</p>
        <button class="cba-btn-primary sm" @click="activeTab = 'applicants'"><i class="bi bi-people-fill me-1"></i>View Applicants</button>
      </div>

      <div v-else class="cba-workassign-layout">
        <div class="cwa-main">
          <div class="cwa-header">
            <button class="cba-back-btn" @click="selectedApplicant = null"><i class="bi bi-arrow-left me-1"></i>Back</button>
            <div class="cwa-header-info">
              <div class="cwa-header-avatar">{{ selectedApplicant.name?.charAt(0) || 'S' }}</div>
              <div>
                <h4>{{ selectedApplicant.name || 'Student' }} — {{ selectedApplicant.assignedTask || 'No task assigned' }}</h4>
                <span>{{ selectedApplicant.department }} · {{ selectedBountyApps.title }}</span>
              </div>
              <span class="cba-work-status-badge" :class="selectedApplicant.progress || selectedApplicant.status">{{ progressLabel(selectedApplicant) }}</span>
            </div>
          </div>

          <div class="cwa-body">
            <!-- Progress -->
            <div class="cwa-progress-section">
              <div class="cwa-progress-track">
                <div class="cwa-progress-fill" :style="{ width: progressPercent(selectedApplicant) + '%' }"></div>
              </div>
              <div class="cwa-progress-steps">
                <div class="cwa-step" :class="{ active: progressLevel(selectedApplicant) >= 1 }"><i class="bi bi-person-check-fill"></i><span>Accepted</span></div>
                <div class="cwa-step" :class="{ active: progressLevel(selectedApplicant) >= 2 }"><i class="bi bi-briefcase-fill"></i><span>Assigned</span></div>
                <div class="cwa-step" :class="{ active: progressLevel(selectedApplicant) >= 3 }"><i class="bi bi-gear-fill"></i><span>In Progress</span></div>
                <div class="cwa-step" :class="{ active: progressLevel(selectedApplicant) >= 4 }"><i class="bi bi-check-circle-fill"></i><span>Completed</span></div>
              </div>
            </div>

            <!-- Assign Work Form -->
            <div v-if="!selectedApplicant.assignedTaskDescription" class="cwa-form-card">
              <h5><i class="bi bi-pencil-square me-2"></i>Describe & Assign Work</h5>
              <div class="cba-form-group">
                <label>Task Title</label>
                <input v-model="workForm.taskTitle" type="text" class="cba-input" placeholder="e.g. Build landing page hero section" />
              </div>
              <div class="cba-form-group">
                <label>Task Description</label>
                <textarea v-model="workForm.taskDescription" class="cba-input cba-textarea" rows="4" placeholder="Describe the work in detail, including expectations and deliverables..."></textarea>
              </div>
              <div class="cba-form-group">
                <label>Deliverables (one per line)</label>
                <textarea v-model="workForm.deliverables" class="cba-input cba-textarea" rows="3" placeholder="List expected deliverables..."></textarea>
              </div>
              <div class="cba-form-row">
                <div class="cba-form-group">
                  <label>Deadline</label>
                  <input v-model="workForm.deadline" type="text" class="cba-input" placeholder="e.g. Aug 20, 2026" />
                </div>
                <div class="cba-form-group">
                  <label>Priority</label>
                  <select v-model="workForm.priority" class="cba-input">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              <button class="cba-btn-primary" @click="assignWork"><i class="bi bi-send-fill me-2"></i>Assign Work</button>
            </div>

            <!-- Assigned Work View -->
            <div v-else class="cwa-assigned-section">
              <div class="cwa-assigned-card">
                <div class="cwa-assigned-title">
                  <i class="bi bi-briefcase-fill"></i>
                  <h5>{{ selectedApplicant.assignedTask }}</h5>
                  <span class="cba-priority-badge" :class="selectedApplicant.assignedPriority">{{ selectedApplicant.assignedPriority }}</span>
                </div>
                <div class="cwa-assigned-desc">
                  <strong>Description:</strong>
                  <p>{{ selectedApplicant.assignedTaskDescription }}</p>
                </div>
                <div v-if="selectedApplicant.deliverablesList?.length" class="cwa-assigned-deli">
                  <strong>Deliverables:</strong>
                  <ul>
                    <li v-for="(d, i) in selectedApplicant.deliverablesList" :key="i">{{ d }}</li>
                  </ul>
                </div>
                <div class="cwa-assigned-meta">
                  <span><i class="bi bi-calendar3"></i>Deadline: {{ selectedApplicant.assignedDeadline || 'TBD' }}</span>
                </div>
              </div>

              <div v-if="selectedApplicant.checklist?.length" class="cwa-checklist-card">
                <h5><i class="bi bi-list-check me-2"></i>Progress Checklist</h5>
                <div class="cwa-checklist">
                  <div v-for="item in selectedApplicant.checklist" :key="item.id" class="cwa-check-item" :class="{ done: item.completed }">
                    <i class="bi" :class="item.completed ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                    <span>{{ item.label }}</span>
                  </div>
                </div>
              </div>

              <!-- Submissions Section -->
              <div v-if="studentSubmission" class="cwa-submission-card">
                <h5><i class="bi bi-upload me-2"></i>Student Submission</h5>
                <div class="cwa-sub-top">
                  <p class="cwa-sub-notes">{{ studentSubmission.notes || 'No additional notes.' }}</p>
                </div>
                <div class="cba-sub-links">
                  <a v-if="studentSubmission.githubLink" :href="studentSubmission.githubLink" target="_blank" class="cba-link-btn"><i class="bi bi-github"></i> Repository</a>
                  <a v-if="studentSubmission.demoLink" :href="studentSubmission.demoLink" target="_blank" class="cba-link-btn"><i class="bi bi-link-45deg"></i> Live Demo</a>
                </div>
                <div v-if="studentSubmission.status === 'submitted'" class="cwa-sub-actions">
                  <button class="cba-btn-outline" @click="requestChanges(selectedApplicant)"><i class="bi bi-arrow-counterclockwise me-1"></i>Request Changes</button>
                  <button class="cba-btn-accept" @click="approveSubmission(selectedApplicant)"><i class="bi bi-check-lg me-1"></i>Approve</button>
                </div>
                <div v-if="studentSubmission.status === 'approved'" class="cwa-approved-banner">
                  <i class="bi bi-patch-check-fill"></i>
                  <span>Approved — Portfolio & certificate generated</span>
                </div>
                <div v-if="studentSubmission.status === 'changes_requested'" class="cwa-changes-banner">
                  <i class="bi bi-arrow-counterclockwise"></i>
                  <span>Changes requested — awaiting re-submission</span>
                </div>
              </div>

              <div v-else-if="selectedApplicant.assignedTaskDescription" class="cwa-mark-card">
                  <i class="bi bi-check2-square"></i>
                  <h5>All deliverables completed?</h5>
                  <p>Verify the checklist above and mark this work as completed.</p>
                  <button class="cba-btn-accept" @click="markCompleted(selectedApplicant)"><i class="bi bi-check-lg me-2"></i>Mark Completed</button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Bounty Modal -->
    <div v-if="showCreateModal" class="cba-modal-overlay" @click.self="showCreateModal = false">
      <div class="cba-modal cba-modal-wide">
        <div class="cba-modal-header">
          <h3>Create New Bounty</h3>
          <button class="cba-modal-close" @click="showCreateModal = false"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cba-modal-body">
          <div class="cba-form-row">
            <div class="cba-form-group flex-1">
              <label>Title</label>
              <input v-model="bountyForm.title" type="text" class="cba-input" placeholder="e.g. Build Hackathon Website" />
            </div>
            <div class="cba-form-group">
              <label>Category</label>
              <select v-model="bountyForm.category" class="cba-input">
                <option v-for="c in store.categoryFilters.filter(c => c !== 'All')" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
          <div class="cba-form-group">
            <label>Description</label>
            <textarea v-model="bountyForm.description" class="cba-input cba-textarea" rows="4" placeholder="Describe the opportunity in detail..."></textarea>
          </div>
          <div class="cba-form-group">
            <label>Required Skills</label>
            <div class="cba-chips">
              <button v-for="s in allSkills" :key="s" class="cba-chip" :class="{ active: bountyForm.skills.includes(s) }" @click="toggleSkill(s)">{{ s }}</button>
            </div>
          </div>
          <div class="cba-form-row">
            <div class="cba-form-group">
              <label>Reward</label>
              <input v-model="bountyForm.reward" type="text" class="cba-input" placeholder="e.g. ₹2,500" />
            </div>
            <div class="cba-form-group">
              <label>Difficulty</label>
              <select v-model="bountyForm.difficulty" class="cba-input">
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
          </div>
          <div class="cba-form-row">
            <div class="cba-form-group">
              <label>Deadline</label>
              <input v-model="bountyForm.deadline" type="text" class="cba-input" placeholder="e.g. Aug 15, 2026" />
            </div>
            <div class="cba-form-group">
              <label>Duration</label>
              <input v-model="bountyForm.duration" type="text" class="cba-input" placeholder="e.g. 2 Weeks" />
            </div>
          </div>
          <div class="cba-form-group">
            <label>Number of Students Needed</label>
            <div class="cba-stepper">
              <button class="cba-step-btn" @click="bountyForm.studentsNeeded > 1 && bountyForm.studentsNeeded--"><i class="bi bi-dash"></i></button>
              <span class="cba-step-val">{{ bountyForm.studentsNeeded }}</span>
              <button class="cba-step-btn" @click="bountyForm.studentsNeeded++"><i class="bi bi-plus"></i></button>
            </div>
          </div>
          <div class="cba-form-group">
            <label>Attachments (optional)</label>
            <div class="cba-upload-zone" @click="attachInput?.click()">
              <input ref="attachInput" type="file" hidden multiple @change="handleAttachments" />
              <i class="bi bi-paperclip"></i>
              <span v-if="!bountyForm.attachments.length">Click to add attachments</span>
              <span v-else><i class="bi bi-check-circle-fill me-1"></i>{{ bountyForm.attachments.length }} file(s) selected</span>
            </div>
          </div>
        </div>
        <div class="cba-modal-footer">
          <button class="cba-btn-glass" @click="saveDraft">Save Draft</button>
          <button class="cba-btn-primary" @click="publishBounty">Publish Bounty <i class="bi bi-arrow-right ms-1"></i></button>
        </div>
      </div>
    </div>

    <div v-if="showToast" class="cba-toast" :class="{ success: toastType === 'success', confetti: toastType === 'confetti' }">
      <i :class="toastType === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-star-fill'"></i>
      {{ toastMessage }}
    </div>
    <div v-if="showConfetti" class="cba-confetti-container">
      <div v-for="i in 30" :key="i" class="cba-confetti-piece" :style="{
        left: Math.random() * 100 + '%',
        animationDelay: Math.random() * 2 + 's',
        animationDuration: (2 + Math.random() * 2) + 's',
        background: ['#818cf8','#34d399','#fbbf24','#fb7185','#60a5fa','#a78bfa'][Math.floor(Math.random() * 6)]
      }"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { store } from '../store/mockData';

const activeTab = ref('bounties');
const searchQuery = ref('');
const statusFilter = ref('All');
const selectedBountyApps = ref(null);
const selectedApplicant = ref(null);
const showCreateModal = ref(false);
const attachInput = ref(null);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('success');
const showConfetti = ref(false);

const workForm = reactive({
  taskTitle: '',
  taskDescription: '',
  deliverables: '',
  deadline: '',
  priority: 'medium',
});

const allSkills = ['React', 'Vue.js', 'Node.js', 'Python', 'CSS', 'JavaScript', 'TypeScript', 'Figma', 'Solidity', 'MongoDB', 'Docker', 'UI Design', 'Prototyping', 'Responsive Design'];

const bountyForm = reactive({
  title: '', category: 'Web Development', description: '', skills: [], reward: '', difficulty: 'Medium',
  deadline: '', duration: '', studentsNeeded: 1, attachments: [],
});

const myBounties = computed(() => store.bounties);
const activeBounties = computed(() => myBounties.value.filter(b => b.status === 'open').length);
const totalApplicants = computed(() => myBounties.value.reduce((acc, b) => acc + (b.applicantsCount || 0), 0));
const completedCount = computed(() => store.portfolio.length);
const openPositions = computed(() => myBounties.value.filter(b => b.status === 'open').length);

const myBountyList = computed(() => {
  let result = myBounties.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(b => b.title.toLowerCase().includes(q) || b.category.toLowerCase().includes(q));
  }
  if (statusFilter.value !== 'All') result = result.filter(b => b.status === statusFilter.value);
  return result;
});

const currentApplicants = computed(() => {
  if (!selectedBountyApps.value) return [];
  return (store.bountyApplicants[selectedBountyApps.value.id] || []).map(a => ({
    ...a,
    matchScore: a.matchScore || Math.floor(60 + Math.random() * 35),
  }));
});

const studentSubmission = computed(() => {
  if (!selectedApplicant.value) return null;
  const app = selectedApplicant.value;
  if (!app.submission && !app.submissionStatus) return null;
  return {
    status: app.submissionStatus || 'submitted',
    notes: app.submission?.notes || '',
    githubLink: app.submission?.github || app.github,
    demoLink: app.submission?.demo,
  };
});

const progressLevel = (app) => {
  if (!app) return 0;
  if (app.submissionStatus === 'approved') return 4;
  if (app.submissionStatus === 'submitted' || app.progress === 'submitted') return 3;
  if (app.progress === 'in_progress') return 3;
  if (app.assignedTaskDescription) return 2;
  if (app.status === 'accepted' || app.status === 'assigned') return 1;
  return 0;
};

const progressLabel = (app) => {
  const levels = ['Accepted', 'Work Assigned', 'In Progress', 'Completed'];
  return levels[Math.min(progressLevel(app), 3)] || 'Accepted';
};

const progressPercent = (app) => {
  return (progressLevel(app) / 4) * 100;
};

const goToApplicantsTab = () => {
  if (selectedBountyApps.value) activeTab.value = 'applicants';
};

const goToWorkAssignTab = () => {
  if (selectedBountyApps.value) activeTab.value = 'workassign';
};

const openWorkAssign = (app) => {
  selectedApplicant.value = app;
  activeTab.value = 'workassign';
};

const selectBounty = (bounty) => {
  selectedBountyApps.value = bounty;
  selectedApplicant.value = null;
  const existing = store.bountyApplicants[bounty.id] || [];
  const existingStatus = {};
  existing.forEach(a => { existingStatus[a.id] = a.status; });
  const realApps = store.myApplications.filter(a => a.bountyId === bounty.id);
  if (realApps.length) {
    store.bountyApplicants[bounty.id] = realApps.map(a => ({
      id: a.id, name: store.studentProfile.fullName, department: store.studentProfile.department,
      why: a.why, github: a.github || '', portfolio: a.portfolio || '',
      resume: a.resume || null, availability: a.availability || 'N/A',
      completedBounties: store.portfolio.filter(p => p.clubName === bounty.clubName).length,
      matchScore: Math.floor(60 + Math.random() * 35),
      status: existingStatus[a.id] || a.status || 'pending',
      progress: a.progress || null,
      assignedTask: a.assignedTask || null,
      assignedTaskDescription: a.assignedTaskDescription || null,
      deliverablesList: a.deliverablesList || null,
      assignedDeadline: a.assignedDeadline || null,
      assignedPriority: a.assignedPriority || null,
      checklist: a.checklist || null,
      submissionStatus: a.submissionStatus || null,
      submission: a.submission || null,
    }));
  } else {
    store.bountyApplicants[bounty.id] = [];
  }
  activeTab.value = 'applicants';
};

const updateAppStatus = (appId, status) => {
  const apps = store.bountyApplicants[selectedBountyApps.value?.id];
  if (!apps) return;
  const app = apps.find(a => a.id === appId);
  if (app) {
    app.status = status;
    if (status === 'accepted') app.progress = 'accepted';
  }
  const myApp = store.myApplications.find(a => a.id === appId);
  if (myApp) myApp.status = status;
  if (status === 'accepted') {
    const bounty = selectedBountyApps.value;
    if (bounty) {
      store.volunteerApplications.unshift({
        id: Date.now(), eventId: bounty.id, status: 'accepted',
        eventName: bounty.title, clubName: bounty.clubName || 'Club',
        date: bounty.deadline || 'TBD', venue: 'Online',
        image: bounty.image || '', role: 'Bounty Contributor',
        assignedTask: bounty.title, taskDescription: bounty.description || '',
        assignedBy: 'Club Admin', reportingTime: 'Flexible', volunteerLead: 'Club Admin',
        priority: 'medium', completionDate: null, thankYouMessage: null, feedback: null,
        checklist: [
          { id: 1, label: 'Review bounty requirements', completed: false },
          { id: 2, label: 'Complete deliverables', completed: false },
          { id: 3, label: 'Submit work for review', completed: false },
        ],
        dressCode: 'Casual',
        notes: `You have been accepted for "${bounty.title}". Complete the work and submit it for approval.`,
      });
    }
  }
  showToastMessage(`Application ${status === 'accepted' ? 'accepted' : 'rejected'}`, 'success');
};

const assignWork = () => {
  if (!workForm.taskTitle || !workForm.taskDescription) return;
  const app = selectedApplicant.value;
  if (!app) return;
  const deliverables = workForm.deliverables.split('\n').filter(d => d.trim());
  app.assignedTask = workForm.taskTitle;
  app.assignedTaskDescription = workForm.taskDescription;
  app.deliverablesList = deliverables;
  app.assignedDeadline = workForm.deadline || 'TBD';
  app.assignedPriority = workForm.priority;
  app.status = 'assigned';
  app.progress = 'assigned';
  app.checklist = [
    { id: 1, label: 'Review assigned work', completed: false },
    { id: 2, label: 'Complete deliverables', completed: false },
    { id: 3, label: 'Submit work for review', completed: false },
  ];
  const apps = store.bountyApplicants[selectedBountyApps.value.id];
  const storeApp = apps?.find(a => a.id === app.id);
  if (storeApp) {
    storeApp.assignedTask = workForm.taskTitle;
    storeApp.assignedTaskDescription = workForm.taskDescription;
    storeApp.deliverablesList = deliverables;
    storeApp.assignedDeadline = workForm.deadline || 'TBD';
    storeApp.assignedPriority = workForm.priority;
    storeApp.status = 'assigned';
    storeApp.progress = 'assigned';
    storeApp.checklist = [...app.checklist];
  }
  const volApp = store.volunteerApplications.find(v => v.eventName === selectedBountyApps.value?.title && v.status === 'accepted');
  if (volApp) {
    volApp.assignedTask = workForm.taskTitle;
    volApp.taskDescription = workForm.taskDescription;
    volApp.checklist = [...app.checklist];
    volApp.notes = `Assigned work: ${workForm.taskTitle}. Deadline: ${workForm.deadline || 'TBD'}`;
  }
  workForm.taskTitle = '';
  workForm.taskDescription = '';
  workForm.deliverables = '';
  workForm.deadline = '';
  workForm.priority = 'medium';
  showToastMessage('Work assigned successfully!', 'success');
};

const requestChanges = (app) => {
  app.submissionStatus = 'changes_requested';
  app.progress = 'in_progress';
  const apps = store.bountyApplicants[selectedBountyApps.value?.id];
  const storeApp = apps?.find(a => a.id === app.id);
  if (storeApp) { storeApp.submissionStatus = 'changes_requested'; storeApp.progress = 'in_progress'; }
  showToastMessage('Changes requested', 'success');
};

const approveSubmission = (app) => {
  app.submissionStatus = 'approved';
  app.progress = 'completed';
  showConfetti.value = true;
  setTimeout(() => { showConfetti.value = false; }, 4000);
  const bountyTitle = selectedBountyApps.value?.title || 'Bounty Project';
  store.portfolio.push({
    id: Date.now(), title: app.name + "'s Work", project: bountyTitle,
    clubName: 'Your Club', verified: true, duration: new Date().toLocaleString('en-US', { month: 'short', year: 'numeric' }),
    description: 'Completed bounty project with excellence.',
    skills: selectedBountyApps.value?.skills || [], badge: 'Completed', certificateUrl: '#',
  });
  const volApp = store.volunteerApplications.find(v => v.eventName === bountyTitle && v.status === 'accepted');
  if (volApp) {
    volApp.status = 'completed';
    volApp.completionDate = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    volApp.thankYouMessage = 'Your work has been approved! A portfolio entry and certificate have been generated.';
    volApp.checklist.forEach(item => { item.completed = true; });
  }
  const apps = store.bountyApplicants[selectedBountyApps.value?.id];
  const storeApp = apps?.find(a => a.id === app.id);
  if (storeApp) { storeApp.submissionStatus = 'approved'; storeApp.progress = 'completed'; }
  const myApp = store.myApplications.find(a => a.bountyId === selectedBountyApps.value?.id);
  if (myApp) myApp.status = 'completed';
  showToastMessage('Submission approved! Portfolio entry & certificate generated!', 'confetti');
};

const toggleSkill = (skill) => {
  const idx = bountyForm.skills.indexOf(skill);
  if (idx >= 0) bountyForm.skills.splice(idx, 1);
  else bountyForm.skills.push(skill);
};

const handleAttachments = (e) => {
  bountyForm.attachments = Array.from(e.target.files || []);
};

const saveDraft = () => {
  showCreateModal.value = false;
  showToastMessage('Draft saved', 'success');
};

const publishBounty = () => {
  if (!bountyForm.title || !bountyForm.description) return;
  const club = { name: 'Your Club', logo: 'YC', color: '#818cf8' };
  const newBounty = {
    id: Date.now(), title: bountyForm.title, clubName: club.name, clubLogo: club.logo, clubColor: club.color,
    description: bountyForm.description, fullDescription: bountyForm.description, responsibilities: [],
    category: bountyForm.category, skills: [...bountyForm.skills], reward: bountyForm.reward || 'TBD',
    deadline: bountyForm.deadline || 'TBD', duration: bountyForm.duration || 'TBD',
    deliverables: [], difficulty: bountyForm.difficulty, applicantsCount: 0, timePosted: 'Just now',
    clubEmail: 'club@university.edu', status: 'open',
    image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop',
  };
  store.bounties.unshift(newBounty);
  showCreateModal.value = false;
  Object.assign(bountyForm, { title: '', category: 'Web Development', description: '', skills: [], reward: '', difficulty: 'Medium', deadline: '', duration: '', studentsNeeded: 1, attachments: [] });
  showToastMessage('Bounty published successfully!', 'success');
};

const openUrl = (url) => {
  if (url && !url.startsWith('http')) url = 'https://' + url;
  if (url) window.open(url, '_blank');
};

const showToastMessage = (msg, type) => {
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
  pointer-events: none;
  background:
    radial-gradient(ellipse 500px 350px at 78% 50%, rgba(129,140,248,0.07) 0%, transparent 65%),
    radial-gradient(ellipse 250px 250px at 65% 90%, rgba(99,102,241,0.04) 0%, transparent 70%);
}
.cba-hero-glow {
  position: absolute;
  top: -30%; right: -10%;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%);
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
.cba-hero-left { flex: 1; min-width: 0; }
.cba-hero-badge {
  display: inline-flex;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  background: rgba(129,140,248,0.1);
  border: 1px solid rgba(129,140,248,0.15);
  color: #a5b4fc;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  margin-bottom: 0.75rem;
}
.cba-hero-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.8px;
  margin: 0 0 0.75rem;
  line-height: 1.15;
}
.cba-hero-text {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0 0 1.5rem;
  max-width: 520px;
  line-height: 1.6;
}
.cba-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 0.88rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(99,102,241,0.35);
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  font-family: inherit;
  white-space: nowrap;
}
.cba-btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(99,102,241,0.5); }
.cba-btn-primary.sm { padding: 0.5rem 1.1rem; font-size: 0.8rem; }
.cba-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.cba-btn-glass {
  display: inline-flex;
  align-items: center;
  padding: 0.65rem 1.3rem;
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.cba-btn-glass:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); transform: translateY(-1px); }
.cba-btn-outline {
  display: inline-flex;
  align-items: center;
  padding: 0.45rem 0.9rem;
  background: transparent;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.cba-btn-outline:hover { border-color: rgba(129,140,248,0.3); color: #a5b4fc; }
.cba-hero-right { flex-shrink: 0; }
.cba-stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  min-width: 360px;
}
.cba-stat-card {
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 0.85rem 1rem;
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s;
}
.cba-stat-card:hover { border-color: rgba(129,140,248,0.15); transform: translateY(-2px); }
.cba-stat-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.cba-stat-icon.purple { background: rgba(129,140,248,0.15); color: #818cf8; }
.cba-stat-icon.blue { background: rgba(96,165,250,0.15); color: #60a5fa; }
.cba-stat-icon.green { background: rgba(52,211,153,0.15); color: #34d399; }
.cba-stat-icon.amber { background: rgba(251,191,36,0.15); color: #fbbf24; }
.cba-stat-body { min-width: 0; }
.cba-stat-value { display: block; font-size: 1.3rem; font-weight: 700; color: #f1f5f9; line-height: 1.1; }
.cba-stat-label { font-size: 0.68rem; color: #64748b; font-weight: 500; }
.cba-tabs {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 1.5rem;
  padding: 0.35rem;
  background: rgba(15,23,42,0.3);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.04);
  width: fit-content;
}
.cba-tab {
  padding: 0.5rem 1.1rem;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  white-space: nowrap;
  position: relative;
}
.cba-tab:hover { color: #cbd5e1; background: rgba(255,255,255,0.04); }
.cba-tab.active { background: rgba(129,140,248,0.12); color: #a5b4fc; }
.cba-tab.disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; }
.cba-tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  background: rgba(129,140,248,0.15);
  color: #818cf8;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0 4px;
  margin-left: 4px;
}
.cba-toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.cba-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(15,23,42,0.5);
  border: 1.5px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 0 0.75rem;
  min-width: 220px;
  flex: 1;
}
.cba-search-wrap:focus-within { border-color: rgba(129,140,248,0.3); }
.cba-search-wrap i { font-size: 0.75rem; color: #475569; }
.cba-search-wrap input {
  background: transparent; border: none; outline: none; color: rgba(255,255,255,0.95);
  font-size: 0.8rem; font-family: inherit; padding: 0.55rem 0.5rem; width: 100%;
}
.cba-search-wrap input::placeholder { color: rgba(255,255,255,0.5); }
.cba-filter-select {
  appearance: none;
  background: rgba(15,23,42,0.5);
  border: 1.5px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  color: #94a3b8;
  font-size: 0.75rem;
  font-family: inherit;
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='%23475569'%3E%3Cpath d='M1 1l4 4 4-4'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
}
.cba-bounty-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.cba-bounty-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  padding: 1rem 1.15rem;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-bounty-row:hover { border-color: rgba(129,140,248,0.15); transform: translateX(3px); }
.cba-bounty-row.active { border-color: rgba(129,140,248,0.3); background: rgba(129,140,248,0.06); }
.cba-bounty-img {
  width: 60px; height: 60px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}
.cba-bounty-info { flex: 1; min-width: 0; }
.cba-bounty-info h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.cba-bounty-cat {
  font-size: 0.7rem;
  color: #818cf8;
  font-weight: 600;
  margin-bottom: 0.3rem;
  display: inline-block;
}
.cba-bounty-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.7rem;
  color: #64748b;
}
.cba-bounty-meta span { display: flex; align-items: center; gap: 0.25rem; }
.cba-bounty-meta span i { font-size: 0.65rem; color: #475569; }
.cba-bounty-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
  flex-shrink: 0;
}
.cba-status-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
}
.cba-status-badge.open { background: rgba(52,211,153,0.12); color: #34d399; }
.cba-status-badge.closed { background: rgba(244,63,94,0.12); color: #fb7185; }
.cba-status-badge.draft { background: rgba(251,191,36,0.12); color: #fbbf24; }
.cba-bounty-apps-btn {
  font-size: 0.7rem;
  color: #818cf8;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}
.cba-bounty-apps-btn:hover { color: #a5b4fc; }
.cba-apps-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.cba-back-btn {
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  display: flex;
  align-items: center;
}
.cba-back-btn:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; }
.cba-apps-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  flex: 1;
}
.cba-apps-count {
  font-size: 0.78rem;
  color: #64748b;
}
.cba-apps-prompt {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(15,23,42,0.3);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.04);
}
.cba-apps-prompt i { font-size: 2.5rem; color: #475569; margin-bottom: 1rem; display: block; }
.cba-apps-prompt h3 { font-size: 1rem; font-weight: 700; color: #94a3b8; margin: 0 0 0.4rem; }
.cba-apps-prompt p { font-size: 0.82rem; color: #475569; margin: 0; }

/* Applicant List */
.cba-apps-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.cba-applicant-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  padding: 0.9rem 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-applicant-row:hover { border-color: rgba(129,140,248,0.15); background: rgba(129,140,248,0.04); }
.cba-applicant-row.rejected { opacity: 0.5; }
.cba-applicant-avatar {
  width: 40px; height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.cba-applicant-avatar.green { background: linear-gradient(135deg, #059669, #10b981); }
.cba-applicant-avatar.yellow { background: linear-gradient(135deg, #d97706, #f59e0b); }
.cba-applicant-info { flex: 1; min-width: 0; }
.cba-applicant-info h5 {
  font-size: 0.85rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.1rem;
}
.cba-app-dept {
  font-size: 0.7rem;
  color: #64748b;
}
.cba-app-status-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  flex-shrink: 0;
}
.cba-app-status-badge.pending { background: rgba(251,191,36,0.12); color: #fbbf24; }
.cba-app-status-badge.accepted { background: rgba(52,211,153,0.12); color: #34d399; }
.cba-app-status-badge.assigned { background: rgba(129,140,248,0.12); color: #818cf8; }
.cba-app-status-badge.rejected { background: rgba(244,63,94,0.12); color: #fb7185; }
.cba-app-progress-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  min-width: 120px;
}
.cba-compact-bar {
  width: 100%;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
}
.cba-compact-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #34d399);
  border-radius: 2px;
  transition: width 0.5s ease;
}
.cba-compact-label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #64748b;
}
.cba-app-actions {
  display: flex;
  gap: 0.35rem;
  flex-shrink: 0;
}
.cba-btn-accept.sm, .cba-btn-reject.sm {
  padding: 0.35rem 0.6rem;
  font-size: 0.65rem;
  border-radius: 6px;
}
.cba-btn-assign.sm {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.7rem;
  font-size: 0.65rem;
  font-weight: 600;
  font-family: inherit;
  border: 1.5px solid rgba(129,140,248,0.2);
  background: rgba(129,140,248,0.08);
  color: #818cf8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-btn-assign.sm:hover { background: rgba(129,140,248,0.15); border-color: rgba(129,140,248,0.3); }

/* Work Assign Tab */
.cba-workassign-section {
  min-height: 300px;
}
.cwa-main {
  max-width: 780px;
}
.cwa-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.cwa-header-info {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex: 1;
}
.cwa-header-avatar {
  width: 42px; height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
  flex-shrink: 0;
}
.cwa-header-info h4 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.1rem;
}
.cwa-header-info > div > span {
  font-size: 0.72rem;
  color: #64748b;
}
.cba-work-status-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
}
.cba-work-status-badge.accepted,
.cba-work-status-badge.accepted { background: rgba(52,211,153,0.12); color: #34d399; }
.cba-work-status-badge.assigned,
.cba-work-status-badge.assigned { background: rgba(129,140,248,0.12); color: #818cf8; }
.cba-work-status-badge.in_progress,
.cba-work-status-badge.in_progress { background: rgba(251,191,36,0.12); color: #fbbf24; }
/* Progress Section */
.cwa-progress-section {
  margin-bottom: 1.5rem;
}
.cwa-progress-track {
  height: 5px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.6rem;
}
.cwa-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #34d399);
  border-radius: 3px;
  transition: width 0.5s ease;
}
.cwa-progress-steps {
  display: flex;
  justify-content: space-between;
}
.cwa-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6rem;
  font-weight: 600;
  color: #475569;
  transition: color 0.3s;
}
.cwa-step i { font-size: 0.85rem; }
.cwa-step.active { color: #a5b4fc; }
.cwa-step.active i { color: #818cf8; }
.cwa-step span { white-space: nowrap; }
/* Form */
.cwa-form-card {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1.25rem;
}
.cwa-form-card h5 {
  font-size: 0.88rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 0 0 1rem;
}
.cba-form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.cba-form-group {
  margin-bottom: 0.75rem;
}
.cba-form-group label {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin-bottom: 0.3rem;
}
.cba-input {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: rgba(15,23,42,0.6);
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  color: rgba(255,255,255,0.95);
  font-size: 0.8rem;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}
.cba-input:focus { border-color: rgba(129,140,248,0.35); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); }
.cba-input::placeholder { color: rgba(255,255,255,0.5); }
.cba-input option { background: #111827; color: #e2e8f0; }
.cba-textarea { resize: vertical; min-height: 70px; line-height: 1.5; }

/* Assigned View */
.cwa-assigned-section {}
.cwa-assigned-card {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.cwa-assigned-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.85rem;
}
.cwa-assigned-title i { color: #818cf8; font-size: 1rem; }
.cwa-assigned-title h5 {
  font-size: 0.88rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  flex: 1;
}
.cba-priority-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}
.cba-priority-badge.low { background: rgba(52,211,153,0.1); color: #34d399; }
.cba-priority-badge.medium { background: rgba(251,191,36,0.1); color: #fbbf24; }
.cba-priority-badge.high { background: rgba(244,63,94,0.1); color: #fb7185; }
.cwa-assigned-desc { margin-bottom: 0.75rem; }
.cwa-assigned-desc strong, .cwa-assigned-deli strong {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  margin-bottom: 0.3rem;
  font-weight: 600;
}
.cwa-assigned-desc p {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}
.cwa-assigned-deli { margin-bottom: 0.75rem; }
.cwa-assigned-deli ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.cwa-assigned-deli li {
  font-size: 0.75rem;
  color: #64748b;
  padding: 0.2rem 0;
  padding-left: 1rem;
  position: relative;
}
.cwa-assigned-deli li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.5rem;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #818cf8;
}
.cwa-assigned-meta {
  font-size: 0.7rem;
  color: #64748b;
}
.cwa-assigned-meta span { display: flex; align-items: center; gap: 0.3rem; }
/* Checklist */
.cwa-checklist-card {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.cwa-checklist-card h5 {
  font-size: 0.82rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 0 0 0.65rem;
}
.cwa-checklist {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.cwa-check-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  background: rgba(255,255,255,0.02);
}
.cwa-check-item i { font-size: 0.75rem; color: #475569; }
.cwa-check-item.done { color: #34d399; }
.cwa-check-item.done i { color: #34d399; }
/* Submission */
.cwa-submission-card {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.cwa-submission-card h5 {
  font-size: 0.82rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 0 0 0.65rem;
}
.cwa-sub-notes {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0 0 0.65rem;
  line-height: 1.5;
}
.cba-sub-links {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}
.cba-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 600;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  font-family: inherit;
}
.cba-link-btn:hover { background: rgba(129,140,248,0.08); border-color: rgba(129,140,248,0.15); color: #a5b4fc; }
.cwa-sub-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255,255,255,0.04);
}
.cba-btn-accept {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 700;
  font-family: inherit;
  border: none;
  background: linear-gradient(135deg, #059669, #10b981);
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-btn-accept:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(5,150,105,0.3); }
.cba-btn-reject {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  font-family: inherit;
  border: 1px solid rgba(244,63,94,0.2);
  background: rgba(244,63,94,0.08);
  color: #fb7185;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-btn-reject:hover { background: rgba(244,63,94,0.15); }
.cwa-approved-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  background: rgba(52,211,153,0.08);
  border: 1px solid rgba(52,211,153,0.1);
  color: #34d399;
  font-size: 0.75rem;
  font-weight: 600;
}
.cwa-changes-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  background: rgba(251,191,36,0.08);
  border: 1px solid rgba(251,191,36,0.1);
  color: #fbbf24;
  font-size: 0.75rem;
  font-weight: 600;
}
.cwa-no-submission {
  text-align: center;
  padding: 2rem;
  background: rgba(15,23,42,0.3);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.04);
}
.cwa-no-submission i { font-size: 1.8rem; color: #475569; margin-bottom: 0.5rem; display: block; }
.cwa-no-submission p { font-size: 0.8rem; color: #64748b; margin: 0; }

/* Create Bounty Modal */
.cba-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  animation: cbaFadeIn 0.2s ease;
}
.cba-modal {
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5);
  animation: cbaSlideUp 0.3s cubic-bezier(0.16,1,0.3,1);
}
.cba-modal-wide { max-width: 640px; }
.cba-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.cba-modal-header h3 { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.cba-modal-close {
  width: 32px; height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(255,255,255,0.05);
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.75rem;
}
.cba-modal-close:hover { background: rgba(244,63,94,0.15); color: #fb7185; }
.cba-modal-body { padding: 1.5rem; }
.cba-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}
.cba-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.cba-chip {
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.07);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.cba-chip:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; }
.cba-chip.active { background: rgba(129,140,248,0.12); border-color: rgba(129,140,248,0.3); color: #a5b4fc; }
.cba-stepper {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem 1rem;
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  width: fit-content;
}
.cba-step-btn {
  width: 34px; height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.cba-step-btn:hover { background: rgba(129,140,248,0.1); color: #a5b4fc; }
.cba-step-val {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f1f5f9;
  min-width: 24px;
  text-align: center;
}
.cba-upload-zone {
  border: 2px dashed rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
  font-size: 0.78rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
}
.cba-upload-zone:hover { border-color: rgba(129,140,248,0.25); color: #818cf8; }
.cba-upload-zone i { font-size: 1.5rem; }
.cba-empty {
  text-align: center;
  padding: 3rem 2rem;
  background: rgba(15,23,42,0.3);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.04);
}
.cba-empty i { font-size: 2.2rem; color: #475569; margin-bottom: 0.85rem; display: block; }
.cba-empty h3 { font-size: 0.95rem; font-weight: 700; color: #94a3b8; margin: 0 0 0.3rem; }
.cba-empty p { font-size: 0.8rem; color: #475569; margin: 0 0 0.85rem; }
.cba-toast {
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
  gap: 0.6rem;
  background: rgba(15,23,42,0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 10px 40px rgba(0,0,0,0.4);
  animation: cbaSlideUp 0.35s cubic-bezier(0.16,1,0.3,1);
}
.cba-toast i { font-size: 1rem; }
.cba-toast.success i { color: #4ade80; }
.cba-toast.confetti i { color: #fbbf24; }
.cba-confetti-container {
  position: fixed;
  inset: 0;
  z-index: 100002;
  pointer-events: none;
  overflow: hidden;
}
.cba-confetti-piece {
  position: absolute;
  top: -10px;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  animation: cbaConfettiFall linear forwards;
}
@keyframes cbaConfettiFall {
  0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
}
@keyframes cbaFadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes cbaSlideUp { from { opacity: 0; transform: translateY(20px) scale(0.96); } to { opacity: 1; transform: translateY(0) scale(1); } }
@media (max-width: 992px) {
  .cba-hero-inner { flex-direction: column; gap: 1.5rem; }
  .cba-stat-grid { width: 100%; min-width: 0; }
  .cba-hero-title { font-size: 1.7rem; }
  .cba-tabs { width: 100%; overflow-x: auto; }
  .cba-form-row { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .cba-toolbar { flex-direction: column; }
  .cba-search-wrap { width: 100%; }
  .cba-filter-select { width: 100%; }
}
</style>