<template>
  <div class="cbs">
    <!-- Hero Section -->
    <section class="cbs-hero">
      <div class="cbs-hero-glow"></div>
      <div class="cbs-hero-inner">
        <div class="cbs-hero-left">
          <div class="cbs-hero-badge">Campus Bounty Board</div>
          <h1 class="cbs-hero-title">Opportunity Hub</h1>
          <p class="cbs-hero-text">Discover short-term opportunities posted by clubs. Complete real projects, earn verified experience, and build your placement portfolio.</p>
        </div>
        <div class="cbs-hero-right">
          <div class="cbs-stat-grid">
            <div class="cbs-stat-card">
              <div class="cbs-stat-icon purple"><i class="bi bi-briefcase-fill"></i></div>
              <div class="cbs-stat-body">
                <span class="cbs-stat-value">{{ availableBountiesCount }}</span>
                <span class="cbs-stat-label">Available Opportunities</span>
              </div>
            </div>
            <div class="cbs-stat-card">
              <div class="cbs-stat-icon blue"><i class="bi bi-send-fill"></i></div>
              <div class="cbs-stat-body">
                <span class="cbs-stat-value">{{ myApplications.length }}</span>
                <span class="cbs-stat-label">Applications Submitted</span>
              </div>
            </div>
            <div class="cbs-stat-card">
              <div class="cbs-stat-icon green"><i class="bi bi-check-circle-fill"></i></div>
              <div class="cbs-stat-body">
                <span class="cbs-stat-value">{{ completedBountiesCount }}</span>
                <span class="cbs-stat-label">Completed Bounties</span>
              </div>
            </div>
            <div class="cbs-stat-card">
              <div class="cbs-stat-icon amber"><i class="bi bi-star-fill"></i></div>
              <div class="cbs-stat-body">
                <span class="cbs-stat-value">{{ portfolioPoints }}</span>
                <span class="cbs-stat-label">Portfolio Points</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section Tabs -->
    <div class="cbs-tabs">
      <button class="cbs-tab" :class="{ active: activeSection === 'bounties' }" @click="activeSection = 'bounties'"><i class="bi bi-grid-3x3-gap-fill me-2"></i>Opportunities</button>
      <button class="cbs-tab" :class="{ active: activeSection === 'skills' }" @click="activeSection = 'skills'"><i class="bi bi-diagram-3 me-2"></i>Skill Matrix <span class="cbs-tab-badge">{{ interactiveSkills.length }}</span></button>
      <button class="cbs-tab" :class="{ active: activeSection === 'portfolio' }" @click="activeSection = 'portfolio'"><i class="bi bi-award-fill me-2"></i>Verified Work <span v-if="verifiedWorkList.length" class="cbs-tab-badge">{{ verifiedWorkList.length }}</span></button>
      <button class="cbs-tab" :class="{ active: activeSection === 'applications' }" @click="activeSection = 'applications'"><i class="bi bi-send-fill me-2"></i>My Applications <span v-if="myApplications.length" class="cbs-tab-badge">{{ myApplications.length }}</span></button>
    </div>

    <!-- ─── Bounties Section ─── -->
    <div v-if="activeSection === 'bounties'" class="cbs-bounties-section">
      <!-- Search & Filters -->
      <div class="cbs-toolbar">
        <div class="cbs-search-wrap">
          <i class="bi bi-search"></i>
          <input v-model="searchQuery" type="text" placeholder="Search opportunities by title or description..." />
        </div>
        <select v-model="domainFilter" class="cbs-filter-select">
          <option value="All">All Domains</option>
          <option v-for="d in availableDomains" :key="d.id" :value="d.id">{{ formatDomainName(d.name) }}</option>
        </select>
        <select v-model="sortBy" class="cbs-filter-select">
          <option value="latest">Sort by Latest</option>
          <option value="reward">Sort by Reward</option>
          <option value="deadline">Sort by Deadline</option>
        </select>
      </div>

      <div v-if="isLoadingBounties" class="cbs-loading">
        <span class="spinner-border spinner-border-sm me-2"></span>Loading opportunities...
      </div>

      <!-- Bounty Cards Grid -->
      <div v-else-if="filteredBounties.length" class="cbs-card-grid">
        <div v-for="bounty in filteredBounties" :key="bounty.id" class="cbs-card">
          <div class="cbs-card-header-bar">
            <div class="cbs-card-club">
              <div class="cbs-club-avatar"><i class="bi bi-briefcase-fill"></i></div>
              <span class="cbs-club-name">{{ formatDomainName(bounty.domain?.name) }}</span>
            </div>
            <div class="d-flex align-items-center gap-2">
              <span v-if="getMatchedSkills(bounty).length" class="cbs-match-pill" title="Matches your declared technical skills">
                <i class="bi bi-stars text-warning me-1"></i>Skill Match
              </span>
              <span class="cbs-seats-badge"><i class="bi bi-people me-1"></i>{{ bounty.student_seats }} seats</span>
            </div>
          </div>

          <div class="cbs-card-body">
            <h3 class="cbs-card-title">{{ bounty.title }}</h3>
            <p class="cbs-card-desc">{{ bounty.description }}</p>

            <div class="cbs-skills-row" v-if="bounty.technologies?.length">
              <span
                v-for="tech in bounty.technologies"
                :key="tech.id"
                class="cbs-skill-chip"
                :class="{ 'cbs-skill-matched': isTechMatched(tech.name) }"
                :title="isTechMatched(tech.name) ? 'Matches your skill matrix' : ''"
              >
                <i v-if="isTechMatched(tech.name)" class="bi bi-check2 me-1"></i>
                {{ tech.name }}
              </span>
            </div>

            <div class="cbs-card-meta">
              <span><i class="bi bi-cash-stack text-success"></i>₹{{ bounty.reward }}</span>
              <span><i class="bi bi-calendar3 text-primary"></i>{{ formatDisplayDate(bounty.application_deadline) }}</span>
              <span><i class="bi bi-hourglass-split text-warning"></i>{{ bounty.duration }}</span>
            </div>

            <div class="cbs-card-actions">
              <button class="cbs-btn-outline" @click="viewBountyDetail(bounty)"><i class="bi bi-eye me-1"></i>View Details</button>
              <button class="cbs-btn-primary sm" :disabled="hasApplied(bounty.id)" @click="openApply(bounty)">
                {{ hasApplied(bounty.id) ? 'Applied' : 'Apply Now' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="cbs-empty">
        <i class="bi bi-briefcase text-secondary" style="font-size: 2.2rem;"></i>
        <h3>No Matching Opportunities</h3>
        <p v-if="interactiveSkills.length === 0" class="text-secondary small">
          You haven't declared any technical skills in your Profile or Skill Matrix yet. Declare your skills to see matching opportunities!
        </p>
        <p v-else class="text-secondary small">
          No open campus bounties currently match your declared skills. Check back soon as new bounties are posted!
        </p>
        <button v-if="interactiveSkills.length === 0" class="cbs-btn-primary sm mt-2" @click="activeSection = 'skills'">
          <i class="bi bi-diagram-3 me-1"></i>Declare Skills in Skill Matrix
        </button>
      </div>
    </div>

    <!-- ─── Skill Matrix Section ─── -->
    <div v-if="activeSection === 'skills'" class="cbs-skills-section">
      <div class="cbs-section-header mb-4">
        <h2><i class="bi bi-diagram-3 me-2" style="color:#818cf8;"></i>Skill Matrix</h2>
        <p class="text-secondary small">Your declared skill proficiencies categorized by domain with interactive 5-star proficiency ratings</p>
      </div>

      <div v-if="interactiveSkills.length === 0" class="cbs-empty-state">
        <i class="bi bi-diagram-3"></i>
        <h3>No Skills Declared Yet</h3>
        <p>You haven't declared any skills yet. Select your skills and domains in your Profile to populate your Matrix!</p>
      </div>

      <div v-else class="cbs-skills-grid">
        <div v-for="skill in interactiveSkills" :key="skill.name" class="cbs-skill-card">
          <div class="cbs-skill-top">
            <div>
              <span class="cbs-skill-name">{{ skill.name }}</span>
              <span class="cbs-skill-domain-tag">{{ skill.domain }}</span>
            </div>
            <span class="cbs-skill-level-text">{{ skill.level }} / 5</span>
          </div>

          <div class="cbs-skill-stars">
            <span
              v-for="i in 5"
              :key="i"
              class="cbs-star"
              :class="{ filled: i <= skill.level }"
              @click="updateSkillLevel(skill, i)"
              title="Click to rate proficiency"
            >★</span>
          </div>

          <div class="cbs-skill-bar">
            <div class="cbs-skill-fill" :style="{ width: (skill.level / 5) * 100 + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Verified Work (Portfolio) Section ─── -->
    <div v-if="activeSection === 'portfolio'" class="cbs-portfolio-section">
      <div class="cbs-section-header mb-4">
        <h2><i class="bi bi-award-fill me-2" style="color:#818cf8;"></i>Verified Experience & Tasks</h2>
        <p class="text-secondary small">Your assigned tasks, milestones, and completed project deliverables</p>
      </div>

      <div v-if="isLoadingWork" class="cbs-loading">
        <span class="spinner-border spinner-border-sm me-2"></span>Loading tasks...
      </div>

      <div v-else-if="verifiedWorkList.length" class="cbs-portfolio-grid">
        <div v-for="work in verifiedWorkList" :key="work.id" class="cbs-portfolio-card" @click="selectedWorkDetail = work">
          <div class="d-flex justify-content-between align-items-start mb-2 w-100">
            <span class="cbs-portfolio-badge verified"><i class="bi bi-patch-check-fill me-1"></i>VERIFIED &bull; COMPLETED</span>
            <span class="text-secondary small"><i class="bi bi-calendar-check me-1"></i>Completed: {{ formatDisplayDate(work.updated_at || work.deadline) }}</span>
          </div>
          <h3 class="cbs-portfolio-title">{{ work.title }}</h3>
          <p class="cbs-portfolio-project">{{ work.task_description }}</p>

          <div v-if="work.deliverables?.length" class="mt-2 w-100">
            <span class="text-secondary small">Deliverables:</span>
            <div class="cbs-skills-row mt-1">
              <span v-for="d in work.deliverables" :key="d.id" class="cbs-skill-chip" :class="{ verified: d.status === 'completed' }">
                <i class="bi" :class="d.status === 'completed' ? 'bi-check-circle-fill' : 'bi-circle'"></i> {{ d.title }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="cbs-empty">
        <i class="bi bi-award"></i>
        <h3>No verified work completed yet</h3>
        <p>Assigned project work will appear in your verified portfolio only after you complete all deliverables and the club admin approves and marks it as completed.</p>
      </div>

      <!-- Work Detail Modal -->
      <div v-if="selectedWorkDetail" class="cbs-modal-overlay" @click.self="selectedWorkDetail = null">
        <div class="cbs-modal">
          <div class="cbs-modal-header">
            <h3>Assigned Work Details</h3>
            <button class="cbs-modal-close" @click="selectedWorkDetail = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="cbs-modal-body">
            <div class="cbs-portfolio-detail">
              <span class="cbs-portfolio-badge mb-2">{{ (selectedWorkDetail.status || 'assigned').toUpperCase() }}</span>
              <h2>{{ selectedWorkDetail.title }}</h2>
              <p class="text-light mt-2">{{ selectedWorkDetail.task_description }}</p>
              <div class="cbs-pd-meta mt-3">
                <span class="cbs-pd-club"><i class="bi bi-calendar3"></i>Deadline: {{ formatDisplayDate(selectedWorkDetail.deadline) }}</span>
                <span v-if="selectedWorkDetail.event" class="cbs-pd-club"><i class="bi bi-building"></i>{{ selectedWorkDetail.event.name }}</span>
              </div>
              <div v-if="selectedWorkDetail.deliverables?.length" class="mt-3">
                <h4>Deliverables</h4>
                <ul class="cbs-detail-list">
                  <li v-for="d in selectedWorkDetail.deliverables" :key="d.id">
                    <i class="bi" :class="d.status === 'completed' ? 'bi-check-circle-fill text-success' : 'bi-clock text-warning'"></i>
                    {{ d.title }} ({{ d.status }})
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div class="cbs-modal-footer">
            <button class="cbs-btn-glass" @click="selectedWorkDetail = null">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── My Applications Section ─── -->
    <div v-if="activeSection === 'applications'" class="cbs-apps-section">
      <div class="cbs-section-header mb-4">
        <h2><i class="bi bi-send-fill me-2" style="color:#818cf8;"></i>My Applications</h2>
        <p class="text-secondary small">Track your submitted bounty applications and review status</p>
      </div>

      <div v-if="isLoadingApplications" class="cbs-loading">
        <span class="spinner-border spinner-border-sm me-2"></span>Loading applications...
      </div>

      <div v-else-if="myApplications.length" class="cbs-apps-list">
        <div v-for="app in myApplications" :key="app.id" class="cbs-app-card">
          <div class="cbs-app-left">
            <div class="cbs-app-icon-box">
              <i class="bi bi-briefcase-fill"></i>
            </div>
            <div class="cbs-app-info">
              <h4>{{ app.bounty?.title || 'Bounty Application' }}</h4>
              <span class="cbs-app-club"><i class="bi bi-tag me-1"></i>{{ formatDomainName(app.bounty?.domain?.name) }} · ₹{{ app.bounty?.reward }}</span>
              <span class="cbs-app-date"><i class="bi bi-clock-history me-1"></i>Applied: {{ formatDisplayDate(app.created_at) }}</span>
            </div>
          </div>
          <div class="cbs-app-right">
            <span class="cbs-app-status" :class="app.status">{{ (app.status || 'pending').toUpperCase() }}</span>
            <!-- Direct to Volunteering Tab for Accepted Applications -->
            <button
              v-if="app.status === 'accepted'"
              class="cbs-btn-assigned-work mt-2"
              title="Go to My Volunteering to view your assigned work and deliverables"
              @click="goToVolunteering"
            >
              <i class="bi bi-briefcase-fill me-1"></i>Assigned Work
            </button>
            <!-- Delete Rejected Application -->
            <button
              v-if="app.status === 'rejected'"
              class="cbs-btn-delete-app mt-2"
              title="Delete rejected application"
              @click="handleDeleteRejectedApp(app.id)"
            >
              <i class="bi bi-trash3 me-1"></i>Delete
            </button>
          </div>
        </div>
      </div>

      <div v-else class="cbs-empty">
        <i class="bi bi-send-x"></i>
        <h3>No applications yet</h3>
        <p>Browse opportunities and apply to gain hands-on club experience.</p>
      </div>
    </div>

    <!-- ─── Bounty Detail Modal ─── -->
    <div v-if="selectedBounty" class="cbs-modal-overlay" @click.self="closeDetail">
      <div class="cbs-modal cbs-modal-wide">
        <div class="cbs-modal-header">
          <h3>Opportunity Details</h3>
          <button class="cbs-modal-close" @click="closeDetail"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cbs-modal-body">
          <div class="cbs-detail-header">
            <div class="d-flex align-items-center gap-2 mb-2">
              <span class="cbs-skill-chip active">{{ formatDomainName(selectedBounty.domain?.name) }}</span>
              <span class="badge bg-secondary">{{ selectedBounty.student_seats }} Seats</span>
            </div>
            <h2 class="cbs-detail-title">{{ selectedBounty.title }}</h2>
          </div>
          <div class="cbs-detail-body">
            <div class="cbs-detail-main">
              <div class="cbs-detail-meta-row">
                <div class="cbs-detail-meta-item"><i class="bi bi-cash-stack text-success"></i><span>Reward</span><strong>₹{{ selectedBounty.reward }}</strong></div>
                <div class="cbs-detail-meta-item"><i class="bi bi-calendar3 text-primary"></i><span>Deadline</span><strong>{{ formatDisplayDate(selectedBounty.application_deadline) }}</strong></div>
                <div class="cbs-detail-meta-item"><i class="bi bi-hourglass-split text-warning"></i><span>Duration</span><strong>{{ selectedBounty.duration }}</strong></div>
              </div>
              <h4 class="mt-3">Description</h4>
              <p class="text-light">{{ selectedBounty.description }}</p>

              <div v-if="selectedBounty.responsibilities?.length" class="mt-3">
                <h4>Responsibilities</h4>
                <ul class="cbs-detail-list">
                  <li v-for="r in selectedBounty.responsibilities" :key="r.id"><i class="bi bi-check-circle-fill text-primary"></i>{{ r.title }}</li>
                </ul>
              </div>

              <div v-if="selectedBounty.technologies?.length" class="mt-3">
                <h4>Required Technologies</h4>
                <div class="cbs-skills-row">
                  <span v-for="t in selectedBounty.technologies" :key="t.id" class="cbs-skill-chip">{{ t.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="cbs-modal-footer">
          <button class="cbs-btn-glass" @click="closeDetail">Close</button>
          <button class="cbs-btn-primary" @click="openApply(selectedBounty)" :disabled="hasApplied(selectedBounty.id)">
            {{ hasApplied(selectedBounty.id) ? 'Already Applied' : 'Apply Now' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ─── Apply Modal ─── -->
    <div v-if="showApplyModal" class="cbs-modal-overlay" @click.self="showApplyModal = false">
      <div class="cbs-modal">
        <div class="cbs-modal-header">
          <h3>Apply for Opportunity</h3>
          <button class="cbs-modal-close" @click="showApplyModal = false"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cbs-modal-body">
          <div class="cbs-apply-target mb-3">
            <div class="cbs-club-avatar sm"><i class="bi bi-briefcase-fill"></i></div>
            <div>
              <strong>{{ applyTarget?.title }}</strong>
              <span class="text-secondary small d-block">{{ formatDomainName(applyTarget?.domain?.name) }} · ₹{{ applyTarget?.reward }}</span>
            </div>
          </div>

          <div class="cbs-form-group">
            <label>Weekly Availability *</label>
            <select v-model="applyForm.availability" class="cbs-input">
              <option value="5-10 hrs/week">5-10 hrs/week</option>
              <option value="10-15 hrs/week">10-15 hrs/week</option>
              <option value="15-20 hrs/week">15-20 hrs/week</option>
              <option value="20+ hrs/week">20+ hrs/week</option>
            </select>
          </div>

          <div class="cbs-form-group">
            <label>Resume Link / Portfolio / GitHub URL (Optional)</label>
            <input v-model="applyForm.resumeLink" type="url" class="cbs-input" placeholder="https://github.com/yourusername or drive link" />
          </div>
        </div>
        <div class="cbs-modal-footer">
          <button class="cbs-btn-glass" @click="showApplyModal = false">Cancel</button>
          <button class="cbs-btn-primary" :disabled="isSubmittingApp" @click="submitApplication">
            <span v-if="isSubmittingApp" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-send-check-fill me-1"></i>Submit Application
          </button>
        </div>
      </div>
    </div>

    <!-- Success / Error Toast -->
    <div v-if="showToast" class="cbs-toast" :class="{ success: toastType === 'success', error: toastType === 'error' }">
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
  applyToBountyApi,
  fetchMyApplicationsApi,
  deleteRejectedApplicationApi,
  fetchMySkillsApi,
  fetchMyWorkApi,
  fetchDomainsAndTechsApi,
} from '../api/bounty';

const emit = defineEmits(['navigate']);

const activeSection = ref('bounties');
const searchQuery = ref('');
const domainFilter = ref('All');
const sortBy = ref('latest');

const liveBounties = ref([]);
const availableDomains = ref([]);
const myApplications = ref([]);
const myWorkList = ref([]);

const interactiveSkills = ref([]);

const isLoadingBounties = ref(false);
const isLoadingApplications = ref(false);
const isLoadingWork = ref(false);
const isSubmittingApp = ref(false);

const selectedBounty = ref(null);
const showApplyModal = ref(false);
const applyTarget = ref(null);
const selectedWorkDetail = ref(null);

const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('success');

const applyForm = reactive({
  availability: '10-15 hrs/week',
  resumeLink: '',
});

const getToken = () => store.token || localStorage.getItem('driven_token');

const normalizeSkillString = (str) => String(str || '').toLowerCase().replace(/[^a-z0-9]/g, '');

const isTechMatched = (techName) => {
  if (!techName || !interactiveSkills.value?.length) return false;
  const target = normalizeSkillString(techName);
  return interactiveSkills.value.some(s => normalizeSkillString(s.name) === target);
};

const getMatchedSkills = (bounty) => {
  if (!bounty || !interactiveSkills.value?.length) return [];
  const matched = [];
  if (Array.isArray(bounty.technologies)) {
    bounty.technologies.forEach(t => {
      const tName = t.name || t.technology || '';
      if (isTechMatched(tName)) {
        matched.push(tName);
      }
    });
  }
  return matched;
};

const isBountySkillMatched = (bounty) => {
  if (!interactiveSkills.value || interactiveSkills.value.length === 0) {
    return false;
  }

  const studentTechs = new Set(interactiveSkills.value.map(s => normalizeSkillString(s.name)));
  const studentDomains = new Set(interactiveSkills.value.map(s => normalizeSkillString(s.domain)));

  // Check 1: Direct technology match
  if (Array.isArray(bounty.technologies) && bounty.technologies.length > 0) {
    const hasTechMatch = bounty.technologies.some(t => {
      const techNorm = normalizeSkillString(t.name || t.technology);
      return studentTechs.has(techNorm);
    });
    if (hasTechMatch) return true;
  }

  // Check 2: Domain match
  const bountyDomainNorm = normalizeSkillString(bounty.domain?.name || bounty.domain || bounty.category);
  if (bountyDomainNorm && studentDomains.has(bountyDomainNorm)) {
    return true;
  }

  return false;
};

const availableBountiesCount = computed(() => liveBounties.value.filter(b => b.status === 'open' && isBountySkillMatched(b)).length);
const verifiedWorkList = computed(() => myWorkList.value.filter(w => w.status === 'completed'));
const completedBountiesCount = computed(() => verifiedWorkList.value.length);
const portfolioPoints = computed(() => completedBountiesCount.value * 100 + interactiveSkills.value.reduce((acc, s) => acc + s.level * 10, 0));

const filteredBounties = computed(() => {
  let result = liveBounties.value.filter(b => b.status === 'open' && isBountySkillMatched(b));
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(b => (b.title || '').toLowerCase().includes(q) || (b.description || '').toLowerCase().includes(q));
  }
  if (domainFilter.value !== 'All') {
    result = result.filter(b => b.domain?.id === domainFilter.value || b.domain_id === domainFilter.value);
  }
  if (sortBy.value === 'latest') {
    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  } else if (sortBy.value === 'reward') {
    result.sort((a, b) => Number(b.reward || 0) - Number(a.reward || 0));
  } else if (sortBy.value === 'deadline') {
    result.sort((a, b) => new Date(a.application_deadline) - new Date(b.application_deadline));
  }
  return result;
});

const hasApplied = (bountyId) => myApplications.value.some(a => a.bounty_id === bountyId || a.bountyId === bountyId);

const goToVolunteering = () => {
  emit('navigate', 'volunteering');
};

// ── Lifecycle ──
onMounted(async () => {
  await Promise.all([
    loadBounties(),
    loadDomains(),
    loadMyApplications(),
    loadMySkills(),
    loadMyWork(),
  ]);
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
    availableDomains.value = data;
  } catch (err) {
    console.error('Failed to load domains:', err);
  }
};

const loadMyApplications = async () => {
  isLoadingApplications.value = true;
  try {
    const data = await fetchMyApplicationsApi(getToken());
    myApplications.value = data;
  } catch (err) {
    console.error('Failed to load my applications:', err);
  } finally {
    isLoadingApplications.value = false;
  }
};

const loadMySkills = async () => {
  try {
    const data = await fetchMySkillsApi(getToken());
    const list = [];
    if (Array.isArray(data) && data.length) {
      data.forEach(d => {
        d.technologies?.forEach(t => {
          const rawTech = t.technology || t.name || '';
          if (rawTech) {
            const techName = rawTech.replace(/_/g, ' ');
            if (!list.some(s => s.name.toLowerCase() === techName.toLowerCase())) {
              list.push({
                name: techName,
                domain: formatDomainName(d.domain || d.name),
                level: 4,
              });
            }
          }
        });
      });
    }
    interactiveSkills.value = list;
  } catch (err) {
    console.error('Failed to load skills:', err);
    interactiveSkills.value = [];
  }
};

const updateSkillLevel = (skill, level) => {
  skill.level = level;
  displayToast(`Updated ${skill.name} proficiency to ${level} stars!`, 'success');
};

const loadMyWork = async () => {
  isLoadingWork.value = true;
  try {
    const data = await fetchMyWorkApi(getToken());
    myWorkList.value = data;
  } catch (err) {
    console.error('Failed to load work:', err);
  } finally {
    isLoadingWork.value = false;
  }
};

const viewBountyDetail = (bounty) => {
  selectedBounty.value = bounty;
};

const closeDetail = () => {
  selectedBounty.value = null;
};

const openApply = (bounty) => {
  applyTarget.value = bounty;
  showApplyModal.value = true;
};

const submitApplication = async () => {
  if (!applyTarget.value) return;
  isSubmittingApp.value = true;
  try {
    const payload = {
      availability: applyForm.availability || '10-15 hrs/week',
      resume: applyForm.resumeLink?.trim() || null,
    };
    await applyToBountyApi(applyTarget.value.id, payload, getToken());
    showApplyModal.value = false;
    selectedBounty.value = null;
    displayToast('Application submitted successfully!', 'success');
    await loadMyApplications();
  } catch (err) {
    displayToast(err.message || 'Failed to submit application.', 'error');
  } finally {
    isSubmittingApp.value = false;
  }
};

const handleDeleteRejectedApp = async (appId) => {
  if (!confirm('Delete this rejected application?')) return;
  try {
    await deleteRejectedApplicationApi(appId, getToken());
    displayToast('Application deleted.', 'success');
    await loadMyApplications();
  } catch (err) {
    displayToast(err.message || 'Failed to delete application.', 'error');
  }
};

const scrollToBounties = () => {
  activeSection.value = 'bounties';
};

const formatDomainName = (name) => {
  if (!name) return 'General';
  return String(name).replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
};

const formatDisplayDate = (d) => {
  if (!d) return 'TBD';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const displayToast = (msg, type = 'success') => {
  toastMessage.value = msg;
  toastType.value = type;
  showToast.value = true;
  setTimeout(() => { showToast.value = false; }, 3000);
};
</script>

<style scoped>
.cbs {
  position: relative;
  z-index: 1;
  padding-bottom: 3rem;
}

.cbs-hero {
  position: relative;
  margin-bottom: 1.25rem;
  padding: 1rem 0 0.85rem;
  overflow: hidden;
}
.cbs-hero-glow {
  position: absolute;
  top: -30%; right: -10%;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
}
.cbs-hero-inner {
  display: flex;
  align-items: center;
  gap: 2.5rem;
  position: relative;
  z-index: 1;
}
.cbs-hero-left { flex: 1; min-width: 0; }
.cbs-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(129, 140, 248, 0.25);
  font-size: 0.72rem;
  font-weight: 700;
  color: #818cf8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}
.cbs-hero-title {
  font-size: 2.1rem;
  font-weight: 900;
  color: #f1f5f9;
  margin: 0 0 0.4rem;
  letter-spacing: -0.5px;
}
.cbs-hero-text {
  font-size: 0.92rem;
  color: #94a3b8;
  line-height: 1.55;
  margin: 0;
}

.cbs-hero-right { flex-shrink: 0; }
.cbs-stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
.cbs-stat-card {
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
.cbs-stat-icon {
  width: 42px; height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
}
.cbs-stat-icon.purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.cbs-stat-icon.blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.cbs-stat-icon.green { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.cbs-stat-icon.amber { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

.cbs-stat-body { display: flex; flex-direction: column; }
.cbs-stat-value { font-size: 1.35rem; font-weight: 800; color: #f1f5f9; line-height: 1.2; }
.cbs-stat-label { font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; }

/* Tabs */
.cbs-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.5rem;
}
.cbs-tab {
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
.cbs-tab:hover { color: #f1f5f9; background: rgba(255, 255, 255, 0.04); }
.cbs-tab.active {
  color: #ffffff;
  background: rgba(99, 102, 241, 0.18);
  border-color: rgba(129, 140, 248, 0.35);
}
.cbs-tab-badge {
  background: #6366f1;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  margin-left: 0.5rem;
}

/* Toolbar */
.cbs-toolbar {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.cbs-search-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
}
.cbs-search-wrap i {
  position: absolute; left: 0.9rem; top: 50%;
  transform: translateY(-50%); color: #64748b; font-size: 0.88rem;
}
.cbs-search-wrap input {
  width: 100%;
  padding: 0.65rem 0.9rem 0.65rem 2.4rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
}
.cbs-filter-select {
  padding: 0.65rem 1rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
}

/* Card Grid */
.cbs-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}
.cbs-card {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}
.cbs-card:hover {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(129, 140, 248, 0.4);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}
.cbs-card-header-bar {
  padding: 1rem 1.25rem 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.cbs-card-club {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.cbs-club-avatar {
  width: 32px; height: 32px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}
.cbs-club-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: #c7d2fe;
}
.cbs-seats-badge {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 600;
}
.cbs-card-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.cbs-card-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0 0 0.5rem;
  line-height: 1.35;
}
.cbs-card-desc {
  font-size: 0.84rem;
  color: #94a3b8;
  line-height: 1.5;
  margin: 0 0 0.85rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cbs-skills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}
.cbs-skill-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}
.cbs-skill-chip.active {
  background: rgba(99, 102, 241, 0.18);
  border-color: rgba(129, 140, 248, 0.35);
  color: #c7d2fe;
}
.cbs-skill-chip.verified {
  background: rgba(52, 211, 153, 0.15);
  border-color: rgba(52, 211, 153, 0.3);
  color: #34d399;
}
.cbs-skill-chip.cbs-skill-matched {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(52, 211, 153, 0.4);
  color: #34d399;
  font-weight: 700;
}
.cbs-match-pill {
  background: rgba(99, 102, 241, 0.18);
  border: 1px solid rgba(129, 140, 248, 0.4);
  color: #a5b4fc;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}
.cbs-card-meta {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  font-size: 0.78rem;
  color: #cbd5e1;
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.cbs-card-actions {
  display: flex;
  gap: 0.5rem;
}

/* Skills matrix */
.cbs-skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}
.cbs-skill-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}
.cbs-skill-card:hover {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(129, 140, 248, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}
.cbs-skill-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.cbs-skill-name {
  font-size: 1rem;
  font-weight: 800;
  color: #f1f5f9;
  display: block;
}
.cbs-skill-domain-tag {
  font-size: 0.72rem;
  color: #818cf8;
  font-weight: 600;
  display: block;
  margin-top: 2px;
}
.cbs-skill-level-text {
  font-size: 0.75rem;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
}
.cbs-skill-stars {
  display: flex;
  gap: 0.35rem;
  font-size: 1.25rem;
  color: #475569;
  cursor: pointer;
  user-select: none;
}
.cbs-star {
  transition: transform 0.15s, color 0.15s;
}
.cbs-star:hover {
  transform: scale(1.2);
}
.cbs-star.filled {
  color: #fbbf24;
  text-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}
.cbs-skill-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
}
.cbs-skill-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #34d399);
  border-radius: 999px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Applications & Portfolio list */
.cbs-apps-list, .cbs-portfolio-grid {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.cbs-app-card, .cbs-portfolio-card {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 1.15rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.cbs-portfolio-card {
  flex-direction: column;
  align-items: flex-start;
  cursor: pointer;
}
.cbs-portfolio-card:hover {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(129, 140, 248, 0.3);
}
.cbs-app-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.cbs-app-icon-box {
  width: 42px; height: 42px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}
.cbs-app-info h4, .cbs-portfolio-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.cbs-app-club {
  font-size: 0.78rem;
  color: #cbd5e1;
  display: block;
}
.cbs-app-date, .cbs-portfolio-project {
  font-size: 0.75rem;
  color: #94a3b8;
}
.cbs-app-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.cbs-app-status, .cbs-portfolio-badge {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.2rem 0.65rem;
  border-radius: 6px;
  text-transform: uppercase;
}
.cbs-app-status.pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.cbs-app-status.accepted, .cbs-portfolio-badge { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.cbs-app-status.rejected { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.cbs-btn-delete-app {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #ef4444;
  border-radius: 6px;
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}
.cbs-btn-delete-app:hover { background: rgba(239, 68, 68, 0.25); }

.cbs-btn-assigned-work {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(52, 211, 153, 0.35);
  color: #34d399;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
}
.cbs-btn-assigned-work:hover {
  background: rgba(16, 185, 129, 0.28);
  border-color: #34d399;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

/* Modals */
.cbs-modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1050; padding: 1.5rem;
}
.cbs-modal {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  width: 100%; max-width: 600px;
  max-height: 90vh; display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}
.cbs-modal.cbs-modal-wide { max-width: 700px; }
.cbs-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex; align-items: center; justify-content: space-between;
}
.cbs-modal-header h3 { font-size: 1.15rem; font-weight: 800; color: #f1f5f9; margin: 0; }
.cbs-modal-close { background: transparent; border: none; color: #94a3b8; font-size: 1rem; cursor: pointer; }
.cbs-modal-body { padding: 1.5rem; overflow-y: auto; flex: 1; }
.cbs-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex; justify-content: flex-end; gap: 0.75rem;
}

.cbs-detail-header {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.cbs-detail-title { font-size: 1.35rem; font-weight: 800; color: #f1f5f9; margin: 0; }
.cbs-detail-meta-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}
.cbs-detail-meta-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  display: flex; flex-direction: column;
}
.cbs-detail-meta-item span { font-size: 0.72rem; color: #94a3b8; }
.cbs-detail-meta-item strong { font-size: 0.95rem; color: #f1f5f9; }
.cbs-detail-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.cbs-detail-list li {
  display: flex; align-items: center; gap: 0.6rem;
  font-size: 0.88rem; color: #cbd5e1;
}

.cbs-form-group { margin-bottom: 1rem; }
.cbs-form-group label { display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem; }
.cbs-input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
}
.cbs-input:focus { border-color: #818cf8; }

/* Buttons */
.cbs-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none; border-radius: 10px;
  padding: 0.6rem 1.2rem; color: #ffffff;
  font-size: 0.88rem; font-weight: 700;
  cursor: pointer; transition: all 0.2s;
  display: inline-flex; align-items: center;
}
.cbs-btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}
.cbs-btn-primary.sm { padding: 0.45rem 0.9rem; font-size: 0.82rem; }
.cbs-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.cbs-btn-glass {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px; padding: 0.6rem 1.1rem;
  color: #cbd5e1; font-size: 0.88rem; font-weight: 600; cursor: pointer;
}
.cbs-btn-outline {
  background: transparent;
  border: 1px solid rgba(129, 140, 248, 0.35);
  color: #c7d2fe; border-radius: 8px;
  padding: 0.45rem 0.85rem; font-size: 0.82rem; font-weight: 700; cursor: pointer;
}

.cbs-empty, .cbs-loading {
  text-align: center;
  padding: 3.5rem 1.5rem;
  color: #64748b;
}
.cbs-empty i { font-size: 2.5rem; color: #475569; margin-bottom: 0.75rem; display: block; }

.cbs-toast {
  position: fixed; bottom: 2rem; right: 2rem;
  padding: 0.75rem 1.25rem; border-radius: 12px;
  background: #1e293b; border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff; font-size: 0.88rem; font-weight: 600;
  display: flex; align-items: center; gap: 0.6rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 1100;
}
.cbs-toast.success { border-color: #34d399; }
.cbs-toast.error { border-color: #ef4444; }
.cbs-toast.success i { color: #34d399; }
.cbs-toast.error i { color: #ef4444; }
</style>
