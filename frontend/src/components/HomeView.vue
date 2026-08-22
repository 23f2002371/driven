<template>
  <div class="home-wrapper">
    <!-- Navbar -->
    <nav class="home-navbar" :class="{ 'navbar-scrolled': scrolled }">
      <div class="container d-flex justify-content-between align-items-center">
        <div class="home-brand">DRIVEN</div>
        <div class="d-flex align-items-center gap-3">
          <button class="nav-btn-outline" @click="showAuthModal('login')">Login</button>
          <button class="nav-btn-primary" @click="showAuthModal('register')">Get Started</button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section" ref="heroRef">
      <div class="hero-bg">
        <canvas ref="particleCanvas" class="hero-particle-canvas"></canvas>
        <div class="hero-gradient-overlay"></div>
      </div>
      <div class="container hero-content">
        <div class="row align-items-center g-5">
          <div class="col-lg-7">
            <span class="hero-badge">
              <i class="bi bi-lightning-fill me-2"></i>
              College Tech Club Platform
            </span>
            <h1 class="hero-title">
              <span class="hero-title-line">Build. Manage.</span>
              <span class="hero-title-gradient">Innovate.</span>
            </h1>
            <p class="hero-description">The all-in-one platform for college tech clubs — manage events, track inventory, book lab slots, and collaborate seamlessly. From ideation to execution, DRIVEN powers your club's journey.</p>
            <div class="hero-cta">
              <button class="cta-primary" @click="showAuthModal('register')">
                Start Building <i class="bi bi-arrow-right ms-2"></i>
              </button>
              <button class="cta-secondary" @click="scrollTo('features')">
                Explore <i class="bi bi-chevron-down ms-1"></i>
              </button>
            </div>
            <div class="hero-stats">
              <div class="hero-stat-item">
                <span class="hero-stat-value">500+</span>
                <span class="hero-stat-label">Students</span>
              </div>
              <div class="hero-stat-item">
                <span class="hero-stat-value">50+</span>
                <span class="hero-stat-label">Events</span>
              </div>
              <div class="hero-stat-item">
                <span class="hero-stat-value">200+</span>
                <span class="hero-stat-label">Projects</span>
              </div>
            </div>
          </div>
          <div class="col-lg-5">
            <div class="hero-visual">
              <div class="hero-code-window">
                <div class="code-header">
                  <span class="code-dot red"></span>
                  <span class="code-dot yellow"></span>
                  <span class="code-dot green"></span>
                </div>
                <div class="code-body">
                  <div class="code-line"><span class="code-keyword">import</span> <span class="code-str">'{ innovation }'</span></div>
                  <div class="code-line"><span class="code-keyword">from</span> <span class="code-str">'@driven/club'</span>;</div>
                  <div class="code-line">&nbsp;</div>
                  <div class="code-line"><span class="code-var">const</span> <span class="code-fn">club</span> = <span class="code-keyword">await</span> <span class="code-fn">DRIVEN</span>();</div>
                  <div class="code-line"><span class="code-var">const</span> event = <span class="code-keyword">await</span> club.<span class="code-fn">createEvent</span>({</div>
                  <div class="code-line indent">name: <span class="code-str">"Hackathon 2026"</span>,</div>
                  <div class="code-line indent">venue: <span class="code-str">"Auditorium"</span>,</div>
                  <div class="code-line indent">slots: <span class="code-num">120</span></div>
                  <div class="code-line">});</div>
                  <div class="code-line">&nbsp;</div>
                  <div class="code-line typing-line">
                    <span class="code-comment">// Innovation starts here</span>
                    <span class="typing-cursor"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="section features-section" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">What We Offer</span>
          <h2 class="section-title">Everything Your Club Needs</h2>
          <p class="section-subtitle">From event planning to AI-powered insights, DRIVEN provides a complete toolkit for college tech clubs.</p>
        </div>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card" :style="{ '--card-glow': '#818cf8' }" @mouseenter="hoveredFeature = 1" @mouseleave="hoveredFeature = null">
              <div class="feature-icon purple-glow">
                <i class="bi bi-calendar-event-fill"></i>
              </div>
              <h4 class="feature-title">Event Management</h4>
              <p class="feature-desc">Create, approve, and manage club events with seamless lab slot booking and real-time registration tracking.</p>
              <div class="feature-link" @click="scrollTo('events')">
                Learn more <i class="bi bi-arrow-right ms-1"></i>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card" :style="{ '--card-glow': '#22d3ee' }" @mouseenter="hoveredFeature = 2" @mouseleave="hoveredFeature = null">
              <div class="feature-icon cyan-glow">
                <i class="bi bi-box-seam-fill"></i>
              </div>
              <h4 class="feature-title">Inventory Tracking</h4>
              <p class="feature-desc">Borrow and return lab equipment with full visibility on stock levels. QR-based checkout for instant logging.</p>
              <div class="feature-link" @click="scrollTo('events')">
                Learn more <i class="bi bi-arrow-right ms-1"></i>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card" :style="{'--card-glow': '#fbbf24'}" @mouseenter="hoveredFeature = 3" @mouseleave="hoveredFeature = null">
              <div class="feature-icon orange-glow">
                <i class="bi bi-chat-dots-fill"></i>
              </div>
              <h4 class="feature-title">Smart Support Desk</h4>
              <p class="feature-desc">AI-categorized ticket routing with fuzzy search that suggests resolved threads before you submit.</p>
              <div class="feature-link" @click="scrollTo('events')">
                Learn more <i class="bi bi-arrow-right ms-1"></i>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card" :style="{'--card-glow': '#f472b6'}" @mouseenter="hoveredFeature = 4" @mouseleave="hoveredFeature = null">
              <div class="feature-icon pink-glow">
                <i class="bi bi-trophy-fill"></i>
              </div>
              <h4 class="feature-title">Club Leaderboards</h4>
              <p class="feature-desc">Gamified rankings with points for attendance, zero missing inventory, and event participation.</p>
              <div class="feature-link" @click="scrollTo('leaderboard')">
                Learn more <i class="bi bi-arrow-right ms-1"></i>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card" :style="{'--card-glow': '#34d399'}" @mouseenter="hoveredFeature = 5" @mouseleave="hoveredFeature = null">
              <div class="feature-icon green-glow">
                <i class="bi bi-qr-code"></i>
              </div>
              <h4 class="feature-title">QR Badge Check-in</h4>
              <p class="feature-desc">Generate dynamic QR tickets for events. Club admins scan at the door for instant attendance.</p>
              <div class="feature-link" @click="scrollTo('events')">
                Learn more <i class="bi bi-arrow-right ms-1"></i>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card" :style="{'--card-glow': '#818cf8'}" @mouseenter="hoveredFeature = 6" @mouseleave="hoveredFeature = null">
              <div class="feature-icon indigo-glow">
                <i class="bi bi-map-fill"></i>
              </div>
              <h4 class="feature-title">Live Lab Map</h4>
              <p class="feature-desc">Visual 2D campus map showing real-time lab occupancy. Green = available, Red = booked.</p>
              <div class="feature-link" @click="scrollTo('labmap')">
                Learn more <i class="bi bi-arrow-right ms-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Upcoming Events Section -->
    <section id="events" class="section events-section" :style="{'--card-glow': '#818cf8'}" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Upcoming</span>
          <h2 class="section-title">Events & Workshops</h2>
          <p class="section-subtitle">Stay ahead with our curated lineup of tech events, workshops, and hackathons.</p>
        </div>
        <div class="row g-4">
          <div v-for="event in approvedEvents" :key="event.id" class="col-md-6 col-lg-4">
            <div class="event-card glass" @click="openEventDetails(event)" style="cursor: pointer;">
              <div class="event-card-image" :style="{ backgroundImage: `url(${event.image})` }">
                <div class="event-image-overlay">
                  <span class="event-date-badge"><i class="bi bi-calendar-event-fill me-1"></i>{{ formatDate(event.event_date || event.date) }}</span>
                  <span class="event-venue-tag"><i class="bi bi-geo-alt-fill me-1"></i>{{ venueLabel(event.venue) }}</span>
                </div>
              </div>
              <div class="event-card-body">
                <span class="event-club-tag">{{ event.category ? (event.category.charAt(0).toUpperCase() + event.category.slice(1)) : 'Event' }}</span>
                <h5 class="event-card-title">{{ event.name }}</h5>
              </div>
              <div class="event-card-footer">
                <span class="event-participants"><i class="bi bi-people-fill me-1"></i>{{ event.participants || event.max_participants || 50 }} seats</span>
                <span class="event-deadline-tag"><i class="bi bi-hourglass-split me-1 text-warning"></i>Deadline: {{ formatDeadline(event.registration_deadline || event.deadline, event.event_date || event.date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Event Winners Section -->
    <section id="winners" class="section leaderboard-section" :style="{'--card-glow': '#f472b6'}" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Winners</span>
          <h2 class="section-title">Latest Event Winners</h2>
          <p class="section-subtitle">Teams that took the podium at the most recent event.</p>
        </div>
        <div class="leaderboard-podium">
          <div class="podium-item second" @click="selectedWinner = latestWinners.second">
            <div class="podium-avatar" style="background: linear-gradient(135deg, #94a3b8, #cbd5e1)">
              <span>{{ latestWinners.second.initials }}</span>
            </div>
            <div class="podium-name">{{ latestWinners.second.team }}</div>
            <div class="podium-points">{{ latestWinners.second.project }}</div>
            <div class="podium-bar second-bar"></div>
          </div>
          <div class="podium-item first" @click="selectedWinner = latestWinners.first">
            <div class="podium-avatar" style="background: linear-gradient(135deg, #f59e0b, #fbbf24)">
              <span>{{ latestWinners.first.initials }}</span>
            </div>
            <div class="podium-name">{{ latestWinners.first.team }}</div>
            <div class="podium-points">{{ latestWinners.first.project }}</div>
            <div class="podium-bar first-bar"></div>
          </div>
          <div class="podium-item third" @click="selectedWinner = latestWinners.third">
            <div class="podium-avatar" style="background: linear-gradient(135deg, #d97706, #f59e0b)">
              <span>{{ latestWinners.third.initials }}</span>
            </div>
            <div class="podium-name">{{ latestWinners.third.team }}</div>
            <div class="podium-points">{{ latestWinners.third.project }}</div>
            <div class="podium-bar third-bar"></div>
          </div>
        </div>
        <div class="leaderboard-list glass">
          <div class="lb-header">
            <span>Event</span>
            <span>1st Place</span>
            <span>2nd Place</span>
            <span>3rd Place</span>
          </div>
          <div v-for="(w, i) in store.eventWinners" :key="w.id" class="lb-row" :class="{ 'lb-row-top': i < 3 }">
            <div class="lb-rank">{{ w.eventDate }}</div>
            <div class="lb-name-cell">
              <span class="lb-dot" style="background: #f59e0b"></span>
              <span>{{ w.first.team }}</span>
            </div>
            <div class="lb-members">{{ w.second.team }}</div>
            <div class="lb-points">{{ w.third.team }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Live Lab Map Section -->
    <section id="labmap" class="section labmap-section" :style="{'--card-glow': '#22d3ee'}" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Live</span>
          <h2 class="section-title">Lab Occupancy Map</h2>
          <p class="section-subtitle">Real-time view of campus lab availability. Green rooms are free to book.</p>
        </div>
        <div class="lab-map-container glass">
          <div class="lab-map-grid">
            <div v-for="lab in store.labSlots" :key="lab.id" class="lab-room" :class="lab.status === 'booked' ? 'lab-booked' : 'lab-available'" @click="selectedLab = lab">
              <div class="lab-room-indicator">
                <span class="lab-dot" :class="lab.status"></span>
                <span class="lab-status-text">{{ lab.status === 'booked' ? 'Occupied' : 'Available' }}</span>
              </div>
              <div class="lab-room-name">{{ lab.name }}</div>
              <div class="lab-room-capacity"><i class="bi bi-people-fill me-1"></i>{{ lab.capacity }}</div>
              <div v-if="lab.status === 'booked'" class="lab-room-event">
                <div class="lab-event-name">{{ lab.event }}</div>
                <div class="lab-event-time">{{ lab.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Gallery Section -->
    <section id="gallery" class="section gallery-section" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Moments</span>
          <h2 class="section-title">Event Gallery</h2>
          <p class="section-subtitle">Captured moments from our hackathons, workshops, and tech talks.</p>
        </div>
        <div class="gallery-grid">
          <div v-for="(item, i) in store.gallery" :key="item.id" class="gallery-item" :class="{ 'gallery-span-2': i === 0 || i === 3 }" @click="openLightbox(item)">
            <div class="gallery-image-wrapper">
              <img :src="item.image" :alt="item.caption" loading="lazy" />
              <div class="gallery-overlay">
                <div class="gallery-caption">{{ item.caption }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Lightbox -->
      <div v-if="lightboxImage" class="lightbox-overlay" @click.self="lightboxImage = null">
        <div class="lightbox-content">
          <button class="lightbox-close" @click="lightboxImage = null"><i class="bi bi-x-lg"></i></button>
          <img :src="lightboxImage.image" :alt="lightboxImage.caption" />
          <div class="lightbox-caption">{{ lightboxImage.caption }}</div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="section stats-section" data-reveal data-animate-stats>
      <div class="container">
        <div class="row g-4 text-center">
          <div class="col-6 col-lg-3">
            <div class="stat-item">
              <span class="stat-number">{{ statCounts.students }}+</span>
              <span class="stat-label">Active Students</span>
            </div>
          </div>
          <div class="col-6 col-lg-3">
            <div class="stat-item">
              <span class="stat-number">{{ statCounts.events }}+</span>
              <span class="stat-label">Events Organized</span>
            </div>
          </div>
          <div class="col-6 col-lg-3">
            <div class="stat-item">
              <span class="stat-number">{{ statCounts.projects }}+</span>
              <span class="stat-label">Projects Built</span>
            </div>
          </div>
          <div class="col-6 col-lg-3">
            <div class="stat-item">
              <span class="stat-number">{{ statCounts.satisfaction }}%</span>
              <span class="stat-label">Satisfaction Rate</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Reviews Section -->
    <section id="reviews" class="section reviews-section" :style="{'--card-glow': '#22d3ee'}" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Testimonials</span>
          <h2 class="section-title">What Students Say</h2>
          <p class="section-subtitle">Hear from the club leads, admins, and students who use DRIVEN every day.</p>
        </div>
        <div class="row g-4">
          <div v-for="review in store.reviews" :key="review.id" class="col-md-6 col-lg-4">
            <div class="review-card glass">
              <div class="review-stars">
                <i v-for="i in 5" :key="i" class="bi" :class="i <= review.rating ? 'bi-star-fill text-warning' : 'bi-star text-muted'"></i>
              </div>
              <p class="review-text">"{{ review.text }}"</p>
              <div class="review-author">
                <div class="review-avatar">{{ review.avatar }}</div>
                <div>
                  <div class="review-name">{{ review.name }}</div>
                  <div class="review-role">{{ review.role }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Projects / Gallery Section -->
    <section id="projects" class="section projects-section" :style="{'--card-glow': '#a78bfa'}" data-reveal>
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Showcase</span>
          <h2 class="section-title">Built at DRIVEN Events</h2>
          <p class="section-subtitle">Innovative projects built by students during our hackathons and workshops.</p>
        </div>
        <div class="row g-4">
          <div v-for="project in store.projects" :key="project.id" class="col-md-6 col-lg-4">
            <div class="project-card glass">
              <div class="project-image" :style="{ backgroundImage: `url(${project.image})` }">
                <div class="project-overlay">
                  <span class="project-event-tag">{{ project.event }}</span>
                </div>
              </div>
              <div class="project-body">
                <h5 class="project-title">{{ project.title }}</h5>
                <p class="project-team"><i class="bi bi-people-fill me-1"></i>{{ project.team }}</p>
                <p class="project-desc">{{ project.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section cta-section" :style="{'--card-glow': '#818cf8'}" data-reveal>
      <div class="container">
        <div class="cta-box glass">
          <h2 class="cta-title">Ready to Power Your Club?</h2>
          <p class="cta-text">Join hundreds of students already using DRIVEN to manage clubs, build projects, and make an impact.</p>
          <button class="cta-primary cta-large" @click="showAuthModal('register')">
            Get Started Free <i class="bi bi-rocket-takeoff-fill ms-2"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="home-footer" data-reveal>
      <div class="container">
        <div class="row g-4">
          <div class="col-md-4">
            <div class="footer-brand">DRIVEN</div>
            <p class="footer-text">Empowering college tech clubs with smart management tools. Built by students, for students.</p>
            <div class="footer-social">
              <a href="#" class="social-link"><i class="bi bi-github"></i></a>
              <a href="#" class="social-link"><i class="bi bi-twitter-x"></i></a>
              <a href="#" class="social-link"><i class="bi bi-linkedin"></i></a>
              <a href="#" class="social-link"><i class="bi bi-instagram"></i></a>
            </div>
          </div>
          <div class="col-md-2">
            <h6 class="footer-heading">Platform</h6>
            <ul class="footer-links">
              <li><a href="#" @click.prevent="scrollTo('features')">Features</a></li>
              <li><a href="#" @click.prevent="scrollTo('events')">Events</a></li>
              <li><a href="#" @click.prevent="scrollTo('projects')">Projects</a></li>
              <li><a href="#" @click.prevent="scrollTo('reviews')">Reviews</a></li>
            </ul>
          </div>

          <div class="col-md-4">
            <h6 class="footer-heading">Contact</h6>
            <ul class="footer-links">
              <li><i class="bi bi-envelope-fill me-2"></i>hello@driven.club</li>
              <li><i class="bi bi-geo-alt-fill me-2"></i>Tech Campus, Innovation Lab</li>
              <li><i class="bi bi-clock-fill me-2"></i>Mon - Fri: 9 AM - 6 PM</li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 DRIVEN Platform. All rights reserved. Made with <i class="bi bi-heart-fill text-danger"></i> for college tech clubs.</p>
        </div>
      </div>
    </footer>

    <!-- Auth Modal -->
    <div v-if="activeModal" class="auth-overlay" @click.self="activeModal = null; authPromptMessage = ''">
      <div class="auth-card glass-modal">
        <div class="auth-card-header">
          <div class="auth-tabs">
            <button class="auth-tab" :class="{ active: authMode === 'login' }" @click="switchAuthMode('login')">Sign In</button>
            <button class="auth-tab" :class="{ active: authMode === 'signup' }" @click="switchAuthMode('signup')">Sign Up</button>
          </div>
          <button class="auth-close" @click="activeModal = null; authPromptMessage = ''"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="auth-card-body">
          <div v-if="authPromptMessage" class="auth-prompt-banner">
            <i class="bi bi-shield-lock-fill me-2"></i>{{ authPromptMessage }}
          </div>
          <form v-if="authMode === 'login'" @submit.prevent="handleLogin" class="auth-form">
            <div class="auth-field">
              <label class="auth-label">Email</label>
              <input v-model="loginForm.email" type="email" class="auth-input" placeholder="you@university.edu" required />
            </div>
            <div class="auth-field">
              <label class="auth-label">Password</label>
              <input v-model="loginForm.password" type="password" class="auth-input" placeholder="Enter your password" minlength="6" required />
            </div>
            <div v-if="authError" class="auth-error">{{ authError }}</div>
            <div class="auth-forgot">
              <a href="#" @click.prevent>Forgot password?</a>
            </div>
            <button type="submit" class="auth-submit" :disabled="authLoading">
              <span v-if="authLoading" class="spinner-border spinner-border-sm me-2"></span>
              Sign In <i v-if="!authLoading" class="bi bi-arrow-right ms-2"></i>
            </button>
          </form>
          <form v-else @submit.prevent="handleSignup" class="auth-form">
            <div class="auth-field">
              <label class="auth-label">Full Name</label>
              <input v-model="signupForm.name" type="text" class="auth-input" placeholder="John Doe" required />
            </div>
            <div class="auth-field">
              <label class="auth-label">Email</label>
              <input v-model="signupForm.email" type="email" class="auth-input" placeholder="you@university.edu" required />
            </div>
            <div class="auth-field">
              <label class="auth-label">Password</label>
              <input v-model="signupForm.password" type="password" class="auth-input" placeholder="Create a password (min 6 chars)" minlength="6" required />
            </div>
            <div v-if="authError" class="auth-error">{{ authError }}</div>
            <button type="submit" class="auth-submit" :disabled="authLoading">
              <span v-if="authLoading" class="spinner-border spinner-border-sm me-2"></span>
              Create Account <i v-if="!authLoading" class="bi bi-rocket-takeoff-fill ms-2"></i>
            </button>
          </form>
          <div class="auth-divider">
            <span>or continue with</span>
          </div>
          <div class="auth-oauth">
            <button class="auth-oauth-btn google-btn" @click="handleOAuth('google')">
              <i class="bi bi-google"></i> Google
            </button>
            <button class="auth-oauth-btn github-btn" @click="handleOAuth('github')">
              <i class="bi bi-github"></i> GitHub
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast" class="toast-notification glass-toast">
      <i class="bi bi-check-circle-fill text-success me-2"></i>
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store/mockData';
import * as api from '../api/auth';

const router = useRouter();

onMounted(() => {
  store.fetchEvents();
});

const activeModal = ref(null);
const authMode = ref('login');
const scrolled = ref(false);
const hoveredFeature = ref(null);
const selectedWinner = ref(null);
const selectedLab = ref(null);
const lightboxImage = ref(null);
const toast = ref('');
const authLoading = ref(false);
const authError = ref('');

const authPromptMessage = ref('');
const targetEventAfterLogin = ref(null);

const loginForm = reactive({ email: '', password: '' });
const signupForm = reactive({ name: '', email: '', password: '' });

const approvedEvents = computed(() => {
  return store.events
    .filter(e => e.status !== 'Rejected' && e.rawStatus !== 'rejected')
    .slice(0, 6);
});

const latestWinners = computed(() => store.eventWinners[0]);

const showAuthModal = (type, customPrompt = '') => {
  authMode.value = type;
  activeModal.value = type;
  authPromptMessage.value = customPrompt || (type === 'login' ? authPromptMessage.value : '');
  authError.value = '';
  loginForm.email = '';
  loginForm.password = '';
  signupForm.name = '';
  signupForm.email = '';
  signupForm.password = '';
};

const switchAuthMode = (type) => {
  authMode.value = type;
  authError.value = '';
};

const roleHome = {
  student: '/student-dashboard',
  club_admin: '/clubAdmin-dashboard',
  lab_admin: '/labAdmin-dashboard'
};

const formatAuthError = (err) => {
  if (!err) return 'Something went wrong. Please try again.';
  let msg = '';
  if (typeof err === 'string') msg = err;
  else if (typeof err.message === 'string' && err.message !== '[object Object]') msg = err.message;
  else if (typeof err.detail === 'string') msg = err.detail;
  else return 'Incorrect email or password. Please try again.';

  if (msg.startsWith('String should have')) {
    msg = `Password ${msg.slice(7)}`;
  }
  return msg;
};

const handleLogin = async () => {
  authError.value = '';
  authLoading.value = true;
  try {
    const { access_token } = await api.login(loginForm.email, loginForm.password);
    const user = await api.me(access_token);
    store.setAuth(access_token, user);
    activeModal.value = null;
    toast.value = `Welcome back, ${user.full_name}!`;
    
    if (targetEventAfterLogin.value) {
      const ev = targetEventAfterLogin.value;
      targetEventAfterLogin.value = null;
      authPromptMessage.value = '';
      router.push({ name: 'event-details', params: { eventName: encodeURIComponent(ev.name) } });
    } else {
      router.replace(roleHome[user.role] || '/home');
    }
  } catch (err) {
    authError.value = formatAuthError(err);
  } finally {
    authLoading.value = false;
  }
};

const handleSignup = async () => {
  authError.value = '';
  if (signupForm.password.length < 6) {
    authError.value = 'Password must be at least 6 characters long.';
    return;
  }
  authLoading.value = true;
  try {
    const user = await api.register(signupForm.name, signupForm.email, signupForm.password);
    const { access_token } = await api.login(signupForm.email, signupForm.password);
    store.setAuth(access_token, user);
    activeModal.value = null;
    toast.value = `Account created! Welcome to DRIVEN, ${user.full_name}.`;
    
    if (targetEventAfterLogin.value) {
      const ev = targetEventAfterLogin.value;
      targetEventAfterLogin.value = null;
      authPromptMessage.value = '';
      router.push({ name: 'event-details', params: { eventName: encodeURIComponent(ev.name) } });
    } else {
      router.replace(roleHome[user.role] || '/home');
    }
  } catch (err) {
    authError.value = formatAuthError(err);
  } finally {
    authLoading.value = false;
  }
};

const handleOAuth = (provider) => {
  api.oauthLogin(provider);
};

const onOAuthMessage = async (event) => {
  if (event.data && event.data.type === 'OAUTH_SUCCESS' && event.data.token) {
    const token = event.data.token;
    authLoading.value = true;
    try {
      const user = await api.me(token);
      store.setAuth(token, user);
      activeModal.value = null;
      toast.value = `Welcome, ${user.full_name}!`;
      
      if (targetEventAfterLogin.value) {
        const ev = targetEventAfterLogin.value;
        targetEventAfterLogin.value = null;
        authPromptMessage.value = '';
        router.push({ name: 'event-details', params: { eventName: encodeURIComponent(ev.name) } });
      } else {
        router.replace(roleHome[user.role] || '/home');
      }
    } catch (err) {
      authError.value = formatAuthError(err);
    } finally {
      authLoading.value = false;
    }
  }
};

const scrollTo = (id) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'TBD';
  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) {
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  }
  return dateStr;
};

const formatDeadline = (deadlineStr, fallbackDateStr) => {
  const target = deadlineStr || fallbackDateStr;
  if (!target) return 'TBD';
  const d = new Date(target);
  if (!isNaN(d.getTime())) {
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  }
  return target;
};

const venueLabel = (val) => {
  if (!val) return 'Campus Venue';
  return val.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const openEventDetails = (event) => {
  if (store.isAuthenticated) {
    router.push({ name: 'event-details', params: { eventName: encodeURIComponent(event.name) } });
  } else {
    targetEventAfterLogin.value = event;
    authPromptMessage.value = 'Sign in to see the details';
    showAuthModal('login', 'Sign in to see the details');
  }
};
const handleRegister = (event) => {
  toast.value = `Registered for ${event.name}! Check your email for the QR ticket.`;
  setTimeout(() => { toast.value = ''; }, 3500);
};

const openLightbox = (item) => {
  lightboxImage.value = item;
};

// ── Scroll Reveal (IntersectionObserver) ──
let revealObserver = null;
let statObserver = null;

const statCounts = reactive({
  students: 0, events: 0, projects: 0, satisfaction: 0
});
const statTargets = { students: 500, events: 50, projects: 200, satisfaction: 98 };
const statsVisible = ref(false);

function animateCounters() {
  if (statsVisible.value) return;
  statsVisible.value = true;
  const duration = 2000;
  const start = performance.now();
  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    statCounts.students = Math.round(ease * statTargets.students);
    statCounts.events = Math.round(ease * statTargets.events);
    statCounts.projects = Math.round(ease * statTargets.projects);
    statCounts.satisfaction = Math.round(ease * statTargets.satisfaction);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

onMounted(() => {
  window.addEventListener('message', onOAuthMessage);
  window.addEventListener('scroll', () => { scrolled.value = window.scrollY > 50; }, { passive: true });
  initParticleCanvas();
  const el = heroRef.value;
  if (el) {
    el.addEventListener('mousemove', onParticleMouse);
    el.addEventListener('mouseleave', onParticleLeave);
  }

  revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  statObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounters();
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  requestAnimationFrame(() => {
    document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el));
    document.querySelectorAll('[data-animate-stats]').forEach(el => statObserver.observe(el));
  });
});

onUnmounted(() => {
  window.removeEventListener('message', onOAuthMessage);
  if (particleCleanup) particleCleanup();
  const el = heroRef.value;
  if (el) {
    el.removeEventListener('mousemove', onParticleMouse);
    el.removeEventListener('mouseleave', onParticleLeave);
  }
  if (revealObserver) revealObserver.disconnect();
  if (statObserver) statObserver.disconnect();
});

// ── Particle Network Background (GPU Canvas, single-path strokes) ──
const heroRef = ref(null);
const particleCanvas = ref(null);
let particleCleanup = null;
let mouseX = -10000;
let mouseY = -10000;

function initParticleCanvas() {
  const canvas = particleCanvas.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const particles = [];
  const COUNT = 150;
  const CONNECT_DIST = 175;
  const CONNECT_DIST_SQ = CONNECT_DIST * CONNECT_DIST;
  const COLORS = ['79, 70, 229', '99, 102, 241', '129, 140, 248', '165, 180, 252'];
  let cw = 0;
  let ch = 0;
  let animId = null;

  function resize() {
    const parent = canvas.parentElement;
    if (!parent) return;
    const rect = parent.getBoundingClientRect();
    cw = rect.width;
    ch = rect.height;
    canvas.width = cw * dpr;
    canvas.height = ch * dpr;
  }

  for (let i = 0; i < COUNT; i++) {
    particles.push({
      x: 0, y: 0, vx: 0, vy: 0, r: 0, color: COLORS[0],
    });
  }

  function resetParticles() {
    for (const p of particles) {
      p.x = Math.random() * cw;
      p.y = Math.random() * ch;
      p.vx = (Math.random() - 0.5) * 1.2;
      p.vy = (Math.random() - 0.5) * 1.2;
      p.r = Math.random() * 1.5 + 1;
      p.color = COLORS[Math.floor(Math.random() * COLORS.length)];
    }
  }

  function draw() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cw, ch);

    const mx = mouseX;
    const my = mouseY;

    for (let i = 0; i < COUNT; i++) {
      const p = particles[i];
      const dx = p.x - mx;
      const dy = p.y - my;
      const dsq = dx * dx + dy * dy;
      if (dsq < 32400 && dsq > 1) {
        const d = Math.sqrt(dsq);
        const f = (180 - d) / 180;
        p.vx += (dx / d) * f * 0.2;
        p.vy += (dy / d) * f * 0.2;
      }
      p.vx *= 0.95;
      p.vy *= 0.95;
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < -20) p.x = cw + 20;
      else if (p.x > cw + 20) p.x = -20;
      if (p.y < -20) p.y = ch + 20;
      else if (p.y > ch + 20) p.y = -20;
    }

    ctx.beginPath();
    const connCount = new Array(COUNT).fill(0);
    for (let i = 0; i < COUNT; i++) {
      const p1 = particles[i];
      const neighbors = [];
      for (let j = i + 1; j < COUNT; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dsq = dx * dx + dy * dy;
        if (dsq < CONNECT_DIST_SQ) {
          neighbors.push({ j, dsq });
        }
      }
      neighbors.sort((a, b) => a.dsq - b.dsq);
      const limit = Math.min(2 - connCount[i], neighbors.length);
      for (let k = 0; k < limit; k++) {
        const j = neighbors[k].j;
        if (connCount[j] < 2) {
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(particles[j].x, particles[j].y);
          connCount[i]++;
          connCount[j]++;
        }
      }
    }
    ctx.strokeStyle = 'rgba(129, 140, 248, 0.2)';
    ctx.lineWidth = 0.8;
    ctx.stroke();

    for (let i = 0; i < COUNT; i++) {
      const p = particles[i];
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color}, 0.25)`;
      ctx.fill();
    }

    animId = requestAnimationFrame(draw);
  }

  resize();
  resetParticles();
  draw();

  const onResize = () => { resize(); };
  window.addEventListener('resize', onResize);

  particleCleanup = () => {
    window.removeEventListener('resize', onResize);
    if (animId) cancelAnimationFrame(animId);
  };
}

function onParticleMouse(e) {
  const el = heroRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;
}

function onParticleLeave() {
  mouseX = -10000;
  mouseY = -10000;
}
</script>

<style scoped>
.auth-prompt-banner {
  background: rgba(129, 140, 248, 0.14);
  border: 1px solid rgba(129, 140, 248, 0.35);
  color: #c7d2fe;
  padding: 0.65rem 0.95rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  margin-bottom: 1.1rem;
  backdrop-filter: blur(8px);
}

.event-date-badge {
  background: rgba(99, 102, 241, 0.45) !important;
  border: 1px solid rgba(165, 180, 252, 0.5) !important;
  color: #ffffff !important;
  padding: 0.35rem 0.85rem !important;
  border-radius: 999px !important;
  font-size: 0.825rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
  backdrop-filter: blur(10px) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 10px rgba(99, 102, 241, 0.3) !important;
}

.event-deadline-tag {
  font-size: 0.8rem;
  color: #cbd5e1;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
}
</style>
