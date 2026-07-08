import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ClubAdminDashboard from '../views/ClubAdminDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import LabAdminDashboard from '../views/LabAdminDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/club-admin', name: 'club-admin', component: ClubAdminDashboard },
    { path: '/student', name: 'student', component: StudentDashboard },
    { path: '/lab-admin', name: 'lab-admin', component: LabAdminDashboard }
  ]
})
export default router