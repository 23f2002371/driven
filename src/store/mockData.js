import { reactive } from 'vue';

export const store = reactive({
  currentUserRole: 'home',
  
  events: [
    { id: 1, name: 'IoT Workshop', date: 'Jul 15, 2026', venue: 'Lab A', status: 'Approved', participants: 45, description: 'Hands-on IoT building.' },
    { id: 2, name: 'Hackathon 2026', date: 'Jul 22, 2026', venue: 'Auditorium', status: 'Approved', participants: 120, description: 'Annual coding contest.' },
    { id: 3, name: 'Python Bootcamp', date: 'Jul 28, 2026', venue: 'Lab B', status: 'Approved', participants: 30, description: 'Introductory Python session.' },
    { id: 4, name: 'AI/ML Seminar', date: 'Jul 25, 2026', venue: 'Seminar Hall', status: 'Pending', participants: 60, description: 'Deep dive into neural nets.' }
  ],

  inventory: [
    { id: 1, name: 'Arduino Uno', category: 'Microcontroller', available: 12, borrowed: 3 },
    { id: 2, name: 'Raspberry Pi 4', category: 'SBC', available: 5, borrowed: 5 },
    { id: 3, name: 'Projector', category: 'AV Equipment', available: 2, borrowed: 1 },
    { id: 4, name: 'Sensors Kit', category: 'Components', available: 16, borrowed: 4 }
  ],

  tickets: [
    { id: 1, student: 'Rahul Sharma', subject: 'Unable to register for Hackathon - getting error', priority: 'High', status: 'Open', reply: '' },
    { id: 2, student: 'Priya Kaur', subject: 'Need Arduino returned by Friday for project', priority: 'Medium', status: 'Resolved', reply: 'We have extended your deadline to Monday.' }
  ],

  // July 2026
  bookedDates: [5, 10, 12, 15, 18, 22, 26],

  // Actions (Provisions for API hooks)
  addEvent(newEvent) {
    this.events.push({ id: Date.now(), ...newEvent, status: 'Pending' });
  },
  approveEvent(id) {
    const event = this.events.find(e => e.id === id);
    if (event) event.status = 'Approved';
  },
  addTicket(newTicket) {
    this.tickets.unshift({ id: Date.now(), student: 'Current Student', status: 'Open', reply: '', ...newTicket });
  },
  resolveTicket(id, replyText) {
    const ticket = this.tickets.find(t => t.id === id);
    if (ticket) {
      ticket.status = 'Resolved';
      ticket.reply = replyText;
    }
  }
});