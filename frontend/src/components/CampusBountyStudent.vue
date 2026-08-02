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
          <div class="cbs-hero-actions">
            <button class="cbs-btn-primary" @click="scrollToBounties"><i class="bi bi-compass me-2"></i>Browse Opportunities</button>
            <button class="cbs-btn-glass" @click="activeSection = 'skills'"><i class="bi bi-diagram-3 me-2"></i>My Skills</button>
          </div>
        </div>
        <div class="cbs-hero-right">
          <div class="cbs-stat-grid">
            <div class="cbs-stat-card">
              <div class="cbs-stat-icon purple"><i class="bi bi-briefcase-fill"></i></div>
              <div class="cbs-stat-body">
                <span class="cbs-stat-value">{{ availableBounties }}</span>
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
                <span class="cbs-stat-value">{{ completedBounties }}</span>
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
      <button class="cbs-tab" :class="{ active: activeSection === 'skills' }" @click="activeSection = 'skills'"><i class="bi bi-diagram-3 me-2"></i>Skill Matrix</button>
      <button class="cbs-tab" :class="{ active: activeSection === 'portfolio' }" @click="activeSection = 'portfolio'"><i class="bi bi-award-fill me-2"></i>Verified Work</button>
      <button class="cbs-tab" :class="{ active: activeSection === 'applications' }" @click="activeSection = 'applications'"><i class="bi bi-send-fill me-2"></i>My Applications</button>
    </div>

    <!-- Bounties Section -->
    <div v-if="activeSection === 'bounties'" class="cbs-bounties-section">
      <!-- Search & Filters -->
      <div class="cbs-toolbar">
        <div class="cbs-search-wrap">
          <i class="bi bi-search"></i>
          <input v-model="searchQuery" type="text" placeholder="Search opportunities..." />
        </div>
        <select v-model="skillFilter" class="cbs-filter-select">
          <option value="All">All Skills</option>
          <option v-for="s in store.skillFilters.filter(s => s !== 'All')" :key="s" :value="s">{{ s }}</option>
        </select>
        <select v-model="categoryFilter" class="cbs-filter-select">
          <option v-for="c in store.categoryFilters" :key="c" :value="c">{{ c === 'All' ? 'All Categories' : c }}</option>
        </select>
        <select v-model="difficultyFilter" class="cbs-filter-select">
          <option value="All">All Difficulty</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Advanced">Advanced</option>
        </select>
        <select v-model="sortBy" class="cbs-filter-select">
          <option value="latest">Sort by Latest</option>
          <option value="reward">Sort by Reward</option>
          <option value="deadline">Sort by Deadline</option>
        </select>
      </div>

      <!-- Bounty Cards -->
      <div v-if="filteredBounties.length" class="cbs-card-grid">
        <div v-for="bounty in filteredBounties" :key="bounty.id" class="cbs-card" @mouseenter="hoveredCard = bounty.id" @mouseleave="hoveredCard = null">
          <div class="cbs-card-img" :style="{ backgroundImage: `url(${bounty.image})` }">
            <div class="cbs-card-img-overlay">
              <div class="cbs-card-club">
                <div class="cbs-club-avatar" :style="{ background: bounty.clubColor }">{{ bounty.clubLogo }}</div>
                <span class="cbs-club-name">{{ bounty.clubName }}</span>
              </div>
              <span class="cbs-difficulty-badge" :class="bounty.difficulty.toLowerCase()">{{ bounty.difficulty }}</span>
            </div>
          </div>
          <div class="cbs-card-body">
            <h3 class="cbs-card-title">{{ bounty.title }}</h3>
            <p class="cbs-card-desc">{{ bounty.description }}</p>
            <div class="cbs-skills-row">
              <span v-for="skill in bounty.skills.slice(0, 3)" :key="skill" class="cbs-skill-chip">{{ skill }}</span>
              <span v-if="bounty.skills.length > 3" class="cbs-skill-chip more">+{{ bounty.skills.length - 3 }}</span>
            </div>
            <div class="cbs-card-meta">
              <span><i class="bi bi-calendar3"></i>{{ bounty.deadline }}</span>
              <span><i class="bi bi-cash-stack"></i>{{ bounty.reward }}</span>
              <span><i class="bi bi-people"></i>{{ bounty.applicantsCount }} applied</span>
              <span><i class="bi bi-clock"></i>{{ bounty.timePosted }}</span>
            </div>
            <div class="cbs-card-actions">
              <button class="cbs-btn-outline" @click="viewBountyDetail(bounty)"><i class="bi bi-eye me-1"></i>View Details</button>
              <button class="cbs-btn-primary sm" @click="openApply(bounty)" :disabled="hasApplied(bounty.id)">{{ hasApplied(bounty.id) ? 'Applied' : 'Apply Now' }}</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="cbs-empty">
        <i class="bi bi-inbox"></i>
        <h3>No opportunities found</h3>
        <p>Try adjusting your filters or check back later.</p>
      </div>
    </div>

    <!-- Skills Section -->
    <div v-if="activeSection === 'skills'" class="cbs-skills-section">
      <div class="cbs-section-header">
        <h2><i class="bi bi-diagram-3 me-2" style="color:#818cf8;"></i>Skill Matrix</h2>
        <p>Showcase your expertise with proficiency indicators</p>
      </div>
      <div class="cbs-skills-grid">
        <div v-for="skill in store.studentSkills" :key="skill.name" class="cbs-skill-card">
          <div class="cbs-skill-top">
            <span class="cbs-skill-name">{{ skill.name }}</span>
            <button class="cbs-skill-edit" @click="editSkill(skill)"><i class="bi bi-pencil"></i></button>
          </div>
          <div class="cbs-skill-stars">
            <span v-for="i in 5" :key="i" class="cbs-star" :class="{ filled: i <= skill.level }" @click="updateSkillLevel(skill, i)">★</span>
          </div>
          <div class="cbs-skill-bar">
            <div class="cbs-skill-fill" :style="{ width: (skill.level / 5) * 100 + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Portfolio Section -->
    <div v-if="activeSection === 'portfolio'" class="cbs-portfolio-section">
      <div class="cbs-section-header">
        <h2><i class="bi bi-award-fill me-2" style="color:#818cf8;"></i>Verified Experience</h2>
        <p>Every completed bounty automatically creates a verified portfolio entry</p>
      </div>
      <div class="cbs-portfolio-grid">
        <div v-for="entry in store.portfolio" :key="entry.id" class="cbs-portfolio-card" @click="selectedPortfolio = entry">
          <div class="cbs-portfolio-badge">{{ entry.badge }}</div>
          <h3 class="cbs-portfolio-title">{{ entry.title }}</h3>
          <p class="cbs-portfolio-project">{{ entry.project }}</p>
          <div class="cbs-portfolio-club">
            <span class="cbs-portfolio-club-badge">{{ entry.clubName }}</span>
            <span class="cbs-portfolio-verified"><i class="bi bi-patch-check-fill"></i>Verified</span>
          </div>
          <div class="cbs-portfolio-duration"><i class="bi bi-clock-history me-1"></i>{{ entry.duration }}</div>
          <div class="cbs-portfolio-skills">
            <span v-for="s in entry.skills" :key="s" class="cbs-skill-chip">{{ s }}</span>
          </div>
        </div>
      </div>
      <!-- Portfolio Detail Modal -->
      <div v-if="selectedPortfolio" class="cbs-modal-overlay" @click.self="selectedPortfolio = null">
        <div class="cbs-modal">
          <div class="cbs-modal-header">
            <h3>Portfolio Entry</h3>
            <button class="cbs-modal-close" @click="selectedPortfolio = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="cbs-modal-body">
            <div class="cbs-portfolio-detail">
              <div class="cbs-pd-badge">{{ selectedPortfolio.badge }}</div>
              <h2>{{ selectedPortfolio.title }}</h2>
              <h4>{{ selectedPortfolio.project }}</h4>
              <div class="cbs-pd-meta">
                <span class="cbs-pd-club"><i class="bi bi-building"></i>{{ selectedPortfolio.clubName }}</span>
                <span class="cbs-pd-club verified"><i class="bi bi-patch-check-fill"></i>Verified</span>
                <span class="cbs-pd-club"><i class="bi bi-clock-history"></i>{{ selectedPortfolio.duration }}</span>
              </div>
              <p class="cbs-pd-desc">{{ selectedPortfolio.description }}</p>
              <div class="cbs-skills-row">
                <span v-for="s in selectedPortfolio.skills" :key="s" class="cbs-skill-chip">{{ s }}</span>
              </div>
              <div class="cbs-pd-actions">
                <button class="cbs-btn-primary sm"><i class="bi bi-download me-1"></i>Download Certificate</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- My Applications Section -->
    <div v-if="activeSection === 'applications'" class="cbs-apps-section">
      <div class="cbs-section-header">
        <h2><i class="bi bi-send-fill me-2" style="color:#818cf8;"></i>My Applications</h2>
        <p>Track your bounty applications and their status</p>
      </div>
      <div v-if="myApplications.length" class="cbs-apps-list">
        <div v-for="app in myApplications" :key="app.id" class="cbs-app-card">
          <div class="cbs-app-left">
            <div class="cbs-app-bounty-img" :style="{ backgroundImage: `url(${getBounty(app.bountyId)?.image})` }"></div>
            <div class="cbs-app-info">
              <h4>{{ getBounty(app.bountyId)?.title }}</h4>
              <span class="cbs-app-club">{{ getBounty(app.bountyId)?.clubName }}</span>
              <span class="cbs-app-date">Applied {{ app.submittedAt }}</span>
            </div>
          </div>
          <div class="cbs-app-right">
            <span class="cbs-app-status" :class="app.status">{{ app.status.charAt(0).toUpperCase() + app.status.slice(1) }}</span>
          </div>
        </div>
      </div>
      <div v-else class="cbs-empty">
        <i class="bi bi-send-x"></i>
        <h3>No applications yet</h3>
        <p>Browse opportunities and apply to start your journey.</p>
      </div>
    </div>

    <!-- Bounty Detail Modal -->
    <div v-if="selectedBounty" class="cbs-modal-overlay" @click.self="closeDetail">
      <div class="cbs-modal cbs-modal-wide">
        <div class="cbs-modal-header">
          <h3>Opportunity Details</h3>
          <button class="cbs-modal-close" @click="closeDetail"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cbs-modal-body">
          <div class="cbs-detail-hero" :style="{ backgroundImage: `url(${selectedBounty.image})` }">
            <div class="cbs-detail-hero-overlay">
              <div class="cbs-detail-hero-top">
                <div class="cbs-card-club">
                  <div class="cbs-club-avatar" :style="{ background: selectedBounty.clubColor }">{{ selectedBounty.clubLogo }}</div>
                  <div>
                    <span class="cbs-club-name">{{ selectedBounty.clubName }}</span>
                    <span class="cbs-club-email">{{ selectedBounty.clubEmail }}</span>
                  </div>
                </div>
                <span class="cbs-difficulty-badge" :class="selectedBounty.difficulty.toLowerCase()">{{ selectedBounty.difficulty }}</span>
              </div>
              <h2 class="cbs-detail-title">{{ selectedBounty.title }}</h2>
            </div>
          </div>
          <div class="cbs-detail-body">
            <div class="cbs-detail-main">
              <div class="cbs-detail-meta-row">
                <div class="cbs-detail-meta-item"><i class="bi bi-cash-stack"></i><span>Reward</span><strong>{{ selectedBounty.reward }}</strong></div>
                <div class="cbs-detail-meta-item"><i class="bi bi-calendar3"></i><span>Deadline</span><strong>{{ selectedBounty.deadline }}</strong></div>
                <div class="cbs-detail-meta-item"><i class="bi bi-clock-history"></i><span>Duration</span><strong>{{ selectedBounty.duration }}</strong></div>
                <div class="cbs-detail-meta-item"><i class="bi bi-people"></i><span>Applicants</span><strong>{{ selectedBounty.applicantsCount }}</strong></div>
              </div>
              <h4>Description</h4>
              <p>{{ selectedBounty.fullDescription }}</p>
              <h4>Responsibilities</h4>
              <ul class="cbs-detail-list">
                <li v-for="(r, i) in selectedBounty.responsibilities" :key="i"><i class="bi bi-check-circle-fill"></i>{{ r }}</li>
              </ul>
              <h4>Required Skills</h4>
              <div class="cbs-skills-row">
                <span v-for="s in selectedBounty.skills" :key="s" class="cbs-skill-chip">{{ s }}</span>
              </div>
              <h4>Deliverables</h4>
              <ul class="cbs-detail-list">
                <li v-for="(d, i) in selectedBounty.deliverables" :key="i"><i class="bi bi-file-earmark-check-fill"></i>{{ d }}</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="cbs-modal-footer">
          <button class="cbs-btn-glass" @click="closeDetail">Close</button>
          <button class="cbs-btn-primary" @click="openApply(selectedBounty)" :disabled="hasApplied(selectedBounty.id)">{{ hasApplied(selectedBounty.id) ? 'Already Applied' : 'Apply Now' }}</button>
        </div>
      </div>
    </div>

    <!-- Apply Modal -->
    <div v-if="showApplyModal" class="cbs-modal-overlay" @click.self="showApplyModal = false">
      <div class="cbs-modal">
        <div class="cbs-modal-header">
          <h3>Apply for Opportunity</h3>
          <button class="cbs-modal-close" @click="showApplyModal = false"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cbs-modal-body">
          <div class="cbs-apply-target">
            <div class="cbs-club-avatar sm" :style="{ background: applyTarget?.clubColor }">{{ applyTarget?.clubLogo }}</div>
            <div>
              <strong>{{ applyTarget?.title }}</strong>
              <span>{{ applyTarget?.clubName }}</span>
            </div>
          </div>
          <div class="cbs-form-grid">
            <div class="cbs-form-group">
              <label>Full Name</label>
              <input v-model="applyForm.name" type="text" class="cbs-input" />
            </div>
            <div class="cbs-form-group">
              <label>Student ID</label>
              <input v-model="applyForm.studentId" type="text" class="cbs-input" />
            </div>
            <div class="cbs-form-group">
              <label>Department</label>
              <input v-model="applyForm.department" type="text" class="cbs-input" />
            </div>
            <div class="cbs-form-group">
              <label>Email</label>
              <input v-model="applyForm.email" type="email" class="cbs-input" />
            </div>
          </div>
          <div class="cbs-form-group">
            <label>Why are you interested?</label>
            <textarea v-model="applyForm.why" class="cbs-input cbs-textarea" rows="3" placeholder="Tell us why you're the perfect fit..."></textarea>
          </div>
          <div class="cbs-form-group">
            <label>Relevant Experience</label>
            <textarea v-model="applyForm.experience" class="cbs-input cbs-textarea" rows="3" placeholder="Describe your relevant experience..."></textarea>
          </div>
          <div class="cbs-form-grid">
            <div class="cbs-form-group">
              <label>Portfolio / GitHub URL</label>
              <input v-model="applyForm.github" type="text" class="cbs-input" placeholder="https://github.com/yourname" />
            </div>
            <div class="cbs-form-group">
              <label>Availability</label>
              <select v-model="applyForm.availability" class="cbs-input">
                <option value="">Select availability</option>
                <option value="5 hrs/week">5 hrs/week</option>
                <option value="10 hrs/week">10 hrs/week</option>
                <option value="15 hrs/week">15 hrs/week</option>
                <option value="20 hrs/week">20 hrs/week</option>
                <option value="30+ hrs/week">30+ hrs/week</option>
              </select>
            </div>
          </div>
          <div class="cbs-form-group">
            <label>Resume Upload (optional)</label>
            <div class="cbs-upload-zone" @click="resumeInput?.click()">
              <input ref="resumeInput" type="file" accept=".pdf,.doc,.docx" hidden @change="handleResume" />
              <i class="bi bi-cloud-arrow-up"></i>
              <span v-if="!applyForm.resumeName">Click to upload resume</span>
              <span v-else><i class="bi bi-file-earmark-check me-1"></i>{{ applyForm.resumeName }}</span>
            </div>
          </div>
        </div>
        <div class="cbs-modal-footer">
          <button class="cbs-btn-glass" @click="showApplyModal = false">Cancel</button>
          <button class="cbs-btn-primary" @click="submitApplication">Submit Application <i class="bi bi-arrow-right ms-1"></i></button>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <div v-if="showToast" class="cbs-toast" :class="{ success: toastType === 'success' }">
      <i :class="toastType === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-info-circle-fill'"></i>
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { store } from '../store/mockData';

const activeSection = ref('bounties');
const searchQuery = ref('');
const skillFilter = ref('All');
const categoryFilter = ref('All');
const difficultyFilter = ref('All');
const sortBy = ref('latest');
const hoveredCard = ref(null);
const selectedBounty = ref(null);
const showApplyModal = ref(false);
const applyTarget = ref(null);
const selectedPortfolio = ref(null);
const resumeInput = ref(null);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('success');

const applyForm = reactive({
  name: store.studentProfile.fullName || '',
  studentId: store.studentProfile.studentId || '',
  department: store.studentProfile.department || '',
  email: store.studentProfile.email || '',
  why: '', experience: '', github: '', availability: '', resumeName: null, resumeData: null,
});

const availableBounties = computed(() => store.bounties.filter(b => b.status === 'open').length);
const completedBounties = computed(() => store.portfolio.length);
const portfolioPoints = computed(() => store.portfolio.length * 100 + store.studentSkills.reduce((acc, s) => acc + s.level * 10, 0));
const myApplications = computed(() => store.myApplications);

const filteredBounties = computed(() => {
  let result = store.bounties.filter(b => b.status === 'open');
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(b => b.title.toLowerCase().includes(q) || b.description.toLowerCase().includes(q) || b.clubName.toLowerCase().includes(q));
  }
  if (skillFilter.value !== 'All') result = result.filter(b => b.skills.includes(skillFilter.value));
  if (categoryFilter.value !== 'All') result = result.filter(b => b.category === categoryFilter.value);
  if (difficultyFilter.value !== 'All') result = result.filter(b => b.difficulty === difficultyFilter.value);
  if (sortBy.value === 'latest') result.sort((a, b) => new Date(b.id) - new Date(a.id));
  else if (sortBy.value === 'reward') result.sort((a, b) => parseInt(b.reward.replace(/[^0-9]/g, '')) - parseInt(a.reward.replace(/[^0-9]/g, '')));
  else if (sortBy.value === 'deadline') result.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
  return result;
});

const hasApplied = (bountyId) => store.myApplications.some(a => a.bountyId === bountyId);

const getBounty = (id) => store.bounties.find(b => b.id === id);

const viewBountyDetail = (bounty) => { selectedBounty.value = bounty; };

const closeDetail = () => { selectedBounty.value = null; };

const openApply = (bounty) => {
  applyTarget.value = bounty;
  showApplyModal.value = true;
};

const handleResume = (e) => {
  const file = e.target.files?.[0];
  if (file) {
    applyForm.resumeName = file.name;
    const reader = new FileReader();
    reader.onload = (ev) => { applyForm.resumeData = ev.target?.result; };
    reader.readAsDataURL(file);
  }
};

const submitApplication = () => {
  if (!applyForm.why || !applyForm.experience) return;
  const app = {
    id: Date.now(), bountyId: applyTarget.value.id, status: 'pending',
    submittedAt: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
    why: applyForm.why, experience: applyForm.experience,
    github: applyForm.github, portfolio: '', resume: applyForm.resumeData,
    availability: applyForm.availability, deliverables: null, submission: null,
  };
  store.myApplications.push(app);
  const bounty = store.bounties.find(b => b.id === applyTarget.value.id);
  if (bounty) bounty.applicantsCount++;
  showApplyModal.value = false;
  applyForm.why = ''; applyForm.experience = ''; applyForm.github = ''; applyForm.availability = ''; applyForm.resumeName = null; applyForm.resumeData = null;
  showToastMessage('Application submitted successfully!', 'success');
};

const updateSkillLevel = (skill, level) => { skill.level = level; };

const editSkill = (skill) => {};

const showToastMessage = (msg, type) => {
  toastMessage.value = msg;
  toastType.value = type;
  showToast.value = true;
  setTimeout(() => { showToast.value = false; }, 3000);
};

const scrollToBounties = () => { activeSection.value = 'bounties'; };
</script>

<style scoped>
.cbs {
  position: relative;
  z-index: 1;
  padding-bottom: 3rem;
}
.cbs-hero {
  position: relative;
  margin-bottom: 2rem;
  padding: 2.5rem 0 1.5rem;
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
  gap: 3rem;
  position: relative;
  z-index: 1;
}
.cbs-hero-left { flex: 1; min-width: 0; }
.cbs-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
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
.cbs-hero-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.8px;
  margin: 0 0 0.75rem;
  line-height: 1.15;
}
.cbs-hero-text {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0 0 1.5rem;
  max-width: 520px;
  line-height: 1.6;
}
.cbs-hero-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.cbs-btn-primary {
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
.cbs-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(99,102,241,0.5);
}
.cbs-btn-primary.sm { padding: 0.5rem 1.1rem; font-size: 0.8rem; }
.cbs-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.cbs-btn-glass {
  display: inline-flex;
  align-items: center;
  padding: 0.7rem 1.5rem;
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
  font-size: 0.88rem;
  font-weight: 600;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  font-family: inherit;
  white-space: nowrap;
}
.cbs-btn-glass:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.2);
  transform: translateY(-1px);
}
.cbs-btn-outline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.1rem;
  background: transparent;
  color: #94a3b8;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.cbs-btn-outline:hover {
  border-color: rgba(129,140,248,0.3);
  color: #a5b4fc;
  background: rgba(129,140,248,0.06);
}

/* Stats Grid */
.cbs-hero-right {
  flex-shrink: 0;
}
.cbs-stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  min-width: 360px;
}
.cbs-stat-card {
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
.cbs-stat-card:hover {
  border-color: rgba(129,140,248,0.15);
  transform: translateY(-2px);
}
.cbs-stat-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.cbs-stat-icon.purple { background: rgba(129,140,248,0.15); color: #818cf8; }
.cbs-stat-icon.blue { background: rgba(96,165,250,0.15); color: #60a5fa; }
.cbs-stat-icon.green { background: rgba(52,211,153,0.15); color: #34d399; }
.cbs-stat-icon.amber { background: rgba(251,191,36,0.15); color: #fbbf24; }
.cbs-stat-body { min-width: 0; }
.cbs-stat-value {
  display: block;
  font-size: 1.3rem;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.1;
}
.cbs-stat-label {
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 500;
  line-height: 1.3;
  display: block;
}

/* Tabs */
.cbs-tabs {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 1.5rem;
  padding: 0.35rem;
  background: rgba(15,23,42,0.3);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.04);
  width: fit-content;
}
.cbs-tab {
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
}
.cbs-tab:hover { color: #cbd5e1; background: rgba(255,255,255,0.04); }
.cbs-tab.active {
  background: rgba(129,140,248,0.12);
  color: #a5b4fc;
  box-shadow: 0 2px 8px rgba(129,140,248,0.08);
}

/* Toolbar */
.cbs-toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.cbs-search-wrap {
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
.cbs-search-wrap:focus-within { border-color: rgba(129,140,248,0.3); }
.cbs-search-wrap i { font-size: 0.75rem; color: #475569; pointer-events: none; }
.cbs-search-wrap input {
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255,255,255,0.95);
  font-size: 0.8rem;
  font-family: inherit;
  padding: 0.55rem 0.5rem;
  width: 100%;
}
.cbs-search-wrap input::placeholder { color: rgba(255,255,255,0.5); }
.cbs-filter-select {
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
.cbs-filter-select:focus { border-color: rgba(129,140,248,0.3); }
.cbs-filter-select option { background: #111827; color: #e2e8f0; }

/* Card Grid */
.cbs-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}
.cbs-card {
  display: flex;
  flex-direction: column;
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
  backdrop-filter: blur(14px);
}
.cbs-card:hover {
  transform: translateY(-4px);
  border-color: rgba(129,140,248,0.2);
  box-shadow: 0 12px 40px rgba(0,0,0,0.25), 0 0 20px rgba(129,140,248,0.06);
}
.cbs-card-body {
  flex: 1;
  padding: 1rem 1.1rem 1.1rem;
  display: flex;
  flex-direction: column;
  background: rgba(15,23,42,0.7);
  border-top: 1px solid rgba(255,255,255,0.06);
}
.cbs-card-img {
  height: 130px;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
  position: relative;
  transition: transform 0.5s ease;
}
.cbs-card:hover .cbs-card-img { transform: scale(1.03); }
.cbs-card-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7,11,20,0.1) 0%, rgba(7,11,20,0.6) 100%);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.85rem;
}
.cbs-card-club {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.cbs-club-avatar {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.6rem;
  color: #fff;
  flex-shrink: 0;
}
.cbs-club-avatar.sm { width: 36px; height: 36px; font-size: 0.7rem; border-radius: 10px; }
.cbs-club-name {
  font-size: 0.72rem;
  font-weight: 600;
  color: #e2e8f0;
  text-shadow: 0 1px 4px rgba(0,0,0,0.4);
}
.cbs-club-email {
  display: block;
  font-size: 0.6rem;
  color: #94a3b8;
  text-shadow: 0 1px 4px rgba(0,0,0,0.4);
}
.cbs-difficulty-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.cbs-difficulty-badge.easy { background: rgba(52,211,153,0.15); color: #34d399; }
.cbs-difficulty-badge.medium { background: rgba(251,191,36,0.15); color: #fbbf24; }
.cbs-difficulty-badge.intermediate { background: rgba(251,191,36,0.15); color: #fbbf24; }
.cbs-difficulty-badge.advanced { background: rgba(244,63,94,0.15); color: #fb7185; }
.cbs-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.4rem;
  letter-spacing: -0.2px;
}
.cbs-card-desc {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0 0 0.75rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cbs-skills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.85rem;
}
.cbs-skill-chip {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: rgba(129,140,248,0.08);
  color: #818cf8;
  border: 1px solid rgba(129,140,248,0.1);
}
.cbs-skill-chip.more { background: rgba(255,255,255,0.04); color: #64748b; border-color: rgba(255,255,255,0.06); }
.cbs-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  font-size: 0.7rem;
  color: #64748b;
  margin-bottom: 0.85rem;
}
.cbs-card-meta span { display: flex; align-items: center; gap: 0.3rem; }
.cbs-card-meta span i { font-size: 0.65rem; color: #475569; }
.cbs-card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}

/* Modal */
.cbs-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  animation: cbsFadeIn 0.2s ease;
}
.cbs-modal {
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5);
  animation: cbsSlideUp 0.3s cubic-bezier(0.16,1,0.3,1);
}
.cbs-modal-wide { max-width: 680px; }
.cbs-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.cbs-modal-header h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}
.cbs-modal-close {
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
.cbs-modal-close:hover { background: rgba(244,63,94,0.15); color: #fb7185; }
.cbs-modal-body { padding: 1.5rem; }
.cbs-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

/* Detail View */
.cbs-detail-hero {
  height: 200px;
  background-size: cover;
  background-position: center;
  border-radius: 14px;
  position: relative;
  margin-bottom: 1.5rem;
  overflow: hidden;
}
.cbs-detail-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7,11,20,0.2), rgba(7,11,20,0.85));
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1.25rem;
}
.cbs-detail-hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}
.cbs-detail-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
  letter-spacing: -0.3px;
}
.cbs-detail-body { }
.cbs-detail-body h4 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 1.25rem 0 0.6rem;
}
.cbs-detail-body p {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.7;
  margin: 0;
}
.cbs-detail-meta-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}
.cbs-detail-meta-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 0.85rem;
  text-align: center;
}
.cbs-detail-meta-item i { display: block; font-size: 1.1rem; color: #818cf8; margin-bottom: 0.3rem; }
.cbs-detail-meta-item span { display: block; font-size: 0.62rem; color: #64748b; font-weight: 500; margin-bottom: 0.2rem; text-transform: uppercase; letter-spacing: 0.3px; }
.cbs-detail-meta-item strong { font-size: 0.8rem; color: #f1f5f9; }
.cbs-detail-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.cbs-detail-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #94a3b8;
  padding: 0.35rem 0;
}
.cbs-detail-list li i { font-size: 0.75rem; color: #818cf8; flex-shrink: 0; }

/* Apply Form */
.cbs-apply-target {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  margin-bottom: 1.25rem;
}
.cbs-apply-target strong { display: block; font-size: 0.85rem; color: #f1f5f9; }
.cbs-apply-target span { font-size: 0.72rem; color: #64748b; }
.cbs-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}
.cbs-form-group {
  margin-bottom: 0.85rem;
}
.cbs-form-group label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin-bottom: 0.35rem;
}
.cbs-input {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: rgba(15,23,42,0.6);
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  color: rgba(255,255,255,0.95);
  font-size: 0.82rem;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}
.cbs-input:focus { border-color: rgba(129,140,248,0.35); box-shadow: 0 0 0 3px rgba(129,140,248,0.06); }
.cbs-input::placeholder { color: rgba(255,255,255,0.5); }
.cbs-input option { background: #111827; color: #e2e8f0; }
.cbs-textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
}
.cbs-upload-zone {
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
.cbs-upload-zone:hover { border-color: rgba(129,140,248,0.25); color: #818cf8; }
.cbs-upload-zone i { font-size: 1.5rem; }

/* Skills Section */
.cbs-section-header {
  margin-bottom: 1.5rem;
}
.cbs-section-header h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.3rem;
}
.cbs-section-header p {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0;
}
.cbs-skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.85rem;
}
.cbs-skill-card {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  transition: all 0.2s;
}
.cbs-skill-card:hover { border-color: rgba(129,140,248,0.1); }
.cbs-skill-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.cbs-skill-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
}
.cbs-skill-edit {
  width: 28px; height: 28px;
  border-radius: 6px;
  border: none;
  background: rgba(255,255,255,0.04);
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.65rem;
  transition: all 0.2s;
}
.cbs-skill-edit:hover { background: rgba(129,140,248,0.1); color: #818cf8; }
.cbs-skill-stars {
  display: flex;
  gap: 0.2rem;
  margin-bottom: 0.5rem;
}
.cbs-star {
  font-size: 1.2rem;
  color: rgba(255,255,255,0.08);
  cursor: pointer;
  transition: all 0.15s;
  line-height: 1;
}
.cbs-star.filled { color: #fbbf24; text-shadow: 0 0 8px rgba(251,191,36,0.3); }
.cbs-star:hover { transform: scale(1.2); }
.cbs-skill-bar {
  height: 4px;
  border-radius: 2px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
}
.cbs-skill-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #6366f1, #818cf8);
  transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* Portfolio Section */
.cbs-portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.cbs-portfolio-card {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}
.cbs-portfolio-card:hover {
  transform: translateY(-3px);
  border-color: rgba(129,140,248,0.15);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}
.cbs-portfolio-badge {
  position: absolute;
  top: 0.75rem; right: 0.75rem;
  font-size: 0.55rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: rgba(52,211,153,0.12);
  color: #34d399;
  border: 1px solid rgba(52,211,153,0.12);
}
.cbs-portfolio-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.2rem;
}
.cbs-portfolio-project {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0 0 0.75rem;
}
.cbs-portfolio-club {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.cbs-portfolio-club-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: rgba(129,140,248,0.08);
  color: #818cf8;
}
.cbs-portfolio-verified {
  font-size: 0.68rem;
  font-weight: 600;
  color: #34d399;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.cbs-portfolio-verified i { font-size: 0.75rem; }
.cbs-portfolio-duration {
  font-size: 0.72rem;
  color: #64748b;
  margin-bottom: 0.6rem;
}

/* Portfolio Detail */
.cbs-portfolio-detail { }
.cbs-pd-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 8px;
  background: rgba(52,211,153,0.12);
  color: #34d399;
  margin-bottom: 0.75rem;
}
.cbs-portfolio-detail h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.15rem;
}
.cbs-portfolio-detail h4 {
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 500;
  margin: 0 0 0.75rem;
}
.cbs-pd-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.cbs-pd-club {
  font-size: 0.78rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.cbs-pd-club i { font-size: 0.7rem; }
.cbs-pd-club.verified { color: #34d399; }
.cbs-pd-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 1rem;
}
.cbs-pd-actions {
  margin-top: 1.25rem;
}

/* Applications */
.cbs-apps-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.cbs-app-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  padding: 1rem 1.15rem;
  transition: all 0.2s;
}
.cbs-app-card:hover { border-color: rgba(129,140,248,0.1); }
.cbs-app-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}
.cbs-app-bounty-img {
  width: 48px; height: 48px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}
.cbs-app-info h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.15rem;
}
.cbs-app-club {
  font-size: 0.72rem;
  color: #64748b;
  display: block;
}
.cbs-app-date {
  font-size: 0.68rem;
  color: #475569;
}
.cbs-app-right { }
.cbs-app-status {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
}
.cbs-app-status.pending { background: rgba(251,191,36,0.12); color: #fbbf24; }
.cbs-app-status.accepted { background: rgba(52,211,153,0.12); color: #34d399; }
.cbs-app-status.rejected { background: rgba(244,63,94,0.12); color: #fb7185; }
.cbs-app-status.completed { background: rgba(129,140,248,0.12); color: #818cf8; }

/* Empty State */
.cbs-empty {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(15,23,42,0.3);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.04);
}
.cbs-empty i {
  font-size: 2.5rem;
  color: #475569;
  margin-bottom: 1rem;
}
.cbs-empty h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #94a3b8;
  margin: 0 0 0.4rem;
}
.cbs-empty p {
  font-size: 0.82rem;
  color: #475569;
  margin: 0;
}

/* Toast */
.cbs-toast {
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
  animation: cbsSlideUp 0.35s cubic-bezier(0.16,1,0.3,1);
}
.cbs-toast i { font-size: 1rem; }
.cbs-toast.success i { color: #4ade80; }
.cbs-toast.success { border-color: rgba(74,222,128,0.15); }

/* Animations */
@keyframes cbsFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes cbsSlideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Responsive */
@media (max-width: 992px) {
  .cbs-hero-inner { flex-direction: column; gap: 1.5rem; }
  .cbs-stat-grid { width: 100%; min-width: 0; }
  .cbs-hero-title { font-size: 1.7rem; }
  .cbs-tabs { width: 100%; overflow-x: auto; }
  .cbs-detail-meta-row { grid-template-columns: repeat(2, 1fr); }
  .cbs-form-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .cbs-toolbar { flex-direction: column; }
  .cbs-search-wrap { width: 100%; }
  .cbs-filter-select { width: 100%; }
  .cbs-card-grid { grid-template-columns: 1fr; }
  .cbs-skills-grid { grid-template-columns: 1fr; }
}
</style>
