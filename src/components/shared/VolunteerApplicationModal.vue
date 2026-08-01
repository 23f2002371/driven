<template>
  <Teleport to="body">
    <div class="vam-overlay" @click.self="close">
      <div class="vam-card">
        <div class="vam-header">
          <div>
            <h3 class="vam-title">Volunteer Application</h3>
            <p class="vam-subtitle">Help organize this event by joining the volunteer team.</p>
          </div>
          <button class="vam-close" @click="close"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="vam-body">
          <form @submit.prevent="handleSubmit">
            <div class="vam-row">
              <div class="vam-field">
                <label class="vam-label">Full Name</label>
                <input v-model="form.name" type="text" class="vam-input" placeholder="Enter your full name" required />
              </div>
              <div class="vam-field">
                <label class="vam-label">Email Address</label>
                <input v-model="form.email" type="email" class="vam-input" placeholder="you@university.edu" required />
              </div>
            </div>
            <div class="vam-row">
              <div class="vam-field">
                <label class="vam-label">Contact Number</label>
                <input v-model="form.phone" type="tel" class="vam-input" placeholder="+91 98765 43210" required />
              </div>
              <div class="vam-field">
                <label class="vam-label">Student ID</label>
                <input v-model="form.studentId" type="text" class="vam-input" placeholder="CS2024001" required />
              </div>
            </div>
            <div class="vam-row">
              <div class="vam-field">
                <label class="vam-label">Department</label>
                <input v-model="form.department" type="text" class="vam-input" placeholder="Computer Science" required />
              </div>
              <div class="vam-field">
                <label class="vam-label">Academic Year</label>
                <select v-model="form.academicYear" class="vam-input" required>
                  <option value="" disabled>Select year</option>
                  <option value="1st Year">1st Year</option>
                  <option value="2nd Year">2nd Year</option>
                  <option value="3rd Year">3rd Year</option>
                  <option value="4th Year">4th Year</option>
                </select>
              </div>
            </div>
            <div class="vam-field">
              <label class="vam-label">Skills</label>
              <div class="vam-chips">
                <button v-for="skill in store.volunteerSkills" :key="skill" type="button" class="vam-chip" :class="{ active: selectedSkills.includes(skill) }" @click="toggleSkill(skill)">
                  {{ skill }}
                </button>
              </div>
            </div>
            <div class="vam-row">
              <div class="vam-field">
                <label class="vam-label">Availability</label>
                <select v-model="form.availability" class="vam-input" required>
                  <option value="" disabled>Select availability</option>
                  <option value="Morning">Morning</option>
                  <option value="Afternoon">Afternoon</option>
                  <option value="Full Day">Full Day</option>
                </select>
              </div>
            </div>
            <div class="vam-field">
              <label class="vam-label">Previous Volunteer Experience</label>
              <textarea v-model="form.experience" class="vam-input vam-textarea" rows="3" placeholder="Tell us about any prior volunteer work..."></textarea>
            </div>
            <div class="vam-field">
              <label class="vam-label">Why do you want to volunteer?</label>
              <textarea v-model="form.motivation" class="vam-input vam-textarea" rows="3" placeholder="What motivates you to volunteer for this event?"></textarea>
            </div>
            <div class="vam-checkbox">
              <input v-model="form.agree" id="vam-agree" type="checkbox" required />
              <label for="vam-agree">I agree to follow the event guidelines.</label>
            </div>
            <div class="vam-footer">
              <button type="button" class="vam-btn vam-btn-secondary" @click="close">Cancel</button>
              <button type="submit" class="vam-btn vam-btn-primary" :disabled="!form.agree">
                <i class="bi bi-send-fill me-2"></i>Submit Application
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { store } from '../../store/mockData';

const props = defineProps({
  event: { type: Object, required: true },
});
const emit = defineEmits(['close', 'submitted']);

const selectedSkills = ref([]);
const form = reactive({
  name: '',
  email: '',
  phone: '',
  studentId: '',
  department: '',
  academicYear: '',
  availability: '',
  experience: '',
  motivation: '',
  agree: false,
});

const toggleSkill = (skill) => {
  const idx = selectedSkills.value.indexOf(skill);
  if (idx >= 0) selectedSkills.value.splice(idx, 1);
  else selectedSkills.value.push(skill);
};

const close = () => emit('close');

const handleSubmit = () => {
  store.submitVolunteerApplication({
    eventId: props.event.id,
    eventName: props.event.name,
    clubName: props.event.organizedBy || 'TechNova',
    date: props.event.date,
    venue: props.event.venue,
    image: props.event.image || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop',
  });
  emit('submitted');
  close();
};
</script>
