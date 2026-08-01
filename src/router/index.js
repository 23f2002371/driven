import { createRouter, createWebHistory } from 'vue-router'
import EventDetailsView from '../components/EventDetailsView.vue'
import ClubAdminView from '../components/ClubAdminView.vue'
import StudentView from '../components/StudentView.vue'
import LabAdminView from '../components/LabAdminView.vue'
import HomeView from '../components/HomeView.vue'
import { store } from '../store/mockData'

const routes = [
  {
    path: '/',
    redirect: () => {
      const map = {
        home: '/home',
        club_admin: '/clubAdmin-dashboard',
        student: '/student-dashboard',
        lab_admin: '/labAdmin-dashboard'
      }
      return map[store.currentUserRole] || '/home'
    }
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    beforeEnter: () => { store.currentUserRole = 'home'; }
  },
  {
    path: '/clubAdmin-dashboard',
    name: 'club-admin',
    component: ClubAdminView,
    beforeEnter: () => { store.currentUserRole = 'club_admin'; }
  },
  {
    path: '/student-dashboard',
    name: 'student',
    component: StudentView,
    beforeEnter: () => { store.currentUserRole = 'student'; }
  },
  {
    path: '/labAdmin-dashboard',
    name: 'lab-admin',
    component: LabAdminView,
    beforeEnter: () => { store.currentUserRole = 'lab_admin'; }
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

export default router
