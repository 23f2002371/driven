import { createRouter, createWebHistory } from 'vue-router'
import EventDetailsView from '../components/EventDetailsView.vue'
import ClubAdminView from '../components/ClubAdminView.vue'
import StudentView from '../components/StudentView.vue'
import LabAdminView from '../components/LabAdminView.vue'
import HomeView from '../components/HomeView.vue'
import OAuthCallbackView from '../components/OAuthCallbackView.vue'
import { store } from '../store/mockData'

const routes = [
  {
    path: '/',
    redirect: () => {
      const token = localStorage.getItem('driven_token') || store.token
      if (token) {
        let role = store.currentUserRole
        if (!role || role === 'home') {
          try {
            const u = JSON.parse(localStorage.getItem('driven_user') || '{}')
            role = u.role || 'student'
          } catch {
            role = 'student'
          }
        }
        const map = {
          club_admin: '/clubAdmin-dashboard',
          student: '/student-dashboard',
          lab_admin: '/labAdmin-dashboard'
        }
        return map[role] || '/student-dashboard'
      }
      return '/home'
    }
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView
  },
  {
    path: '/auth/oauth-success',
    name: 'oauth-success',
    component: OAuthCallbackView
  },
  {
    path: '/clubAdmin-dashboard',
    name: 'club-admin',
    component: ClubAdminView,
    meta: { requiresAuth: true, roles: ['club_admin'] }
  },
  {
    path: '/student-dashboard',
    name: 'student',
    component: StudentView,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/labAdmin-dashboard',
    name: 'lab-admin',
    component: LabAdminView,
    meta: { requiresAuth: true, roles: ['lab_admin'] }
  },
  {
    path: '/event/:eventName',
    name: 'event-details',
    component: EventDetailsView
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

const roleRouteMap = {
  student: 'student',
  club_admin: 'club-admin',
  lab_admin: 'lab-admin'
}

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    return { name: 'home' }
  }

  if (to.name === 'home' && store.isAuthenticated) {
    const target = roleRouteMap[store.currentUserRole] || 'student'
    return { name: target }
  }

  if (to.meta.roles && !to.meta.roles.includes(store.currentUserRole)) {
    const target = roleRouteMap[store.currentUserRole] || 'student'
    return { name: target }
  }

  return true
})

export default router