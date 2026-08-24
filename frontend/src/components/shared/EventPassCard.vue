<template>
  <div class="epc-ticket" @click="$emit('open', event)">
    <div class="epc-ticket-inner">
      <div class="epc-left">
        <div class="epc-thumb" :style="{ backgroundImage: `url(${eventThumbImage})` }">
          <div class="epc-thumb-overlay"></div>
          <div class="epc-category">{{ category }}</div>
        </div>
        <div class="epc-info">
          <h3 class="epc-name">{{ event.name }}</h3>
          <div class="epc-meta">
            <span><i class="bi bi-calendar3"></i>{{ event.date }}</span>
            <span><i class="bi bi-clock"></i>09:00 AM – 05:00 PM</span>
            <span><i class="bi bi-geo-alt"></i>{{ formatVenue(event.venue) }}</span>
          </div>
        </div>
      </div>
      <div class="epc-center">
        <div class="epc-status">
          <span class="epc-status-dot"></span>
          {{ event.attendance_status === 'present' ? 'Present' : 'Confirmed' }}
        </div>
        <div class="epc-id">{{ passDisplayId }}</div>
      </div>
      <div class="epc-divider"><div class="epc-cut top"></div><div class="epc-cut btm"></div></div>
      <div class="epc-right">
        <div class="epc-qr">
          <img v-if="event.qr_code_url" :src="event.qr_code_url" alt="QR Pass" class="epc-qr-img" />
          <div v-else class="epc-qr-grid">
            <div v-for="i in 49" :key="i" class="epc-qr-cell" :class="{ 'epc-qr-on': (i * 7 + Math.floor(i / 7) * 3 + i % 13) % 3 !== 0 }"></div>
          </div>
          <div class="epc-qr-glow"></div>
        </div>
        <span class="epc-qr-label">Show this QR at the event entrance.</span>
      </div>
    </div>
    <div class="epc-actions">
      <button class="epc-btn" @click.stop="$emit('open', event)"><i class="bi bi-eye me-1"></i>View Pass</button>
      <button class="epc-btn" @click.stop="$emit('open', event)"><i class="bi bi-qr-code me-1"></i>QR Code</button>
      <button class="epc-btn epc-btn-cal" @click.stop="$emit('calendar', event)"><i class="bi bi-calendar-plus me-1"></i>Add to Calendar</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({ event: { type: Object, required: true } });
defineEmits(['open', 'download', 'calendar']);

const eventThumbImage = computed(() => {
  return props.event.cover_image_url || props.event.image || 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop';
});

const formatVenue = (v) => {
  if (!v) return 'Campus Facility';
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const passDisplayId = computed(() => {
  const regId = props.event.registration_id || props.event.id;
  return `PASS-${String(regId).slice(0, 8).toUpperCase()}`;
});

const category = computed(() => {
  const n = (props.event.name || '').toLowerCase();
  if (n.includes('hackathon')) return 'Hackathon';
  if (n.includes('bootcamp') || n.includes('workshop')) return 'Workshop';
  if (n.includes('seminar')) return 'Seminar';
  return 'Workshop';
});
</script>

<style scoped>
.epc-ticket {
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.epc-ticket:hover { transform: translateY(-6px); }

.epc-ticket-inner {
  display: flex;
  align-items: stretch;
  background: linear-gradient(135deg, rgba(15,23,42,0.85), rgba(25,20,50,0.8));
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(129,140,248,0.12);
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 30px rgba(0,0,0,0.2), 0 0 40px rgba(79,70,229,0.04);
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.epc-ticket:hover .epc-ticket-inner {
  border-color: rgba(129,140,248,0.25);
  box-shadow: 0 8px 40px rgba(0,0,0,0.3), 0 0 60px rgba(79,70,229,0.08);
}
.epc-ticket-inner::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1.5px;
  background: linear-gradient(135deg, rgba(129,140,248,0.2), transparent 40%, rgba(129,140,248,0.05));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.epc-left { display: flex; gap: 1rem; padding: 1.25rem; flex: 1; min-width: 0; align-items: center; }
.epc-thumb {
  width: 80px;
  height: 80px;
  border-radius: 14px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.epc-thumb-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(79,70,229,0.15), rgba(124,58,237,0.05));
}
.epc-category {
  position: absolute; bottom: 4px; left: 4px;
  font-size: 0.55rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.15rem 0.45rem; border-radius: 4px;
  background: rgba(0,0,0,0.6); color: #a5b4fc; backdrop-filter: blur(4px);
}
.epc-info { min-width: 0; }
.epc-name {
  font-size: 1.05rem; font-weight: 800; color: #f1f5f9;
  margin: 0 0 0.5rem; letter-spacing: -0.3px; line-height: 1.2;
}
.epc-meta { display: flex; flex-direction: column; gap: 0.2rem; }
.epc-meta span {
  font-size: 0.72rem; color: #64748b; display: flex; align-items: center; gap: 0.4rem;
}
.epc-meta span i { font-size: 0.65rem; width: 14px; color: #475569; }

.epc-center {
  padding: 1.25rem 1rem;
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; gap: 0.3rem; min-width: 130px;
  border-left: 1px dashed rgba(255,255,255,0.06);
}
.epc-status {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.78rem; font-weight: 700; color: #34d399;
}
.epc-status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,0.5);
}
.epc-id {
  font-size: 0.65rem; font-weight: 600; color: #475569;
  font-family: monospace; letter-spacing: 0.5px;
}
.epc-batch {
  font-size: 0.65rem; font-weight: 600; padding: 0.2rem 0.6rem;
  border-radius: 999px; background: rgba(129,140,248,0.1); color: #a5b4fc;
}

.epc-divider {
  position: relative; width: 20px; flex-shrink: 0;
  background: linear-gradient(180deg, rgba(129,140,248,0.05), rgba(129,140,248,0.1), rgba(129,140,248,0.05));
}
.epc-cut {
  position: absolute; left: -8px; width: 16px; height: 16px;
  border-radius: 50%; background: #070b14;
}
.epc-cut.top { top: -8px; }
.epc-cut.btm { bottom: -8px; }

.epc-right {
  padding: 1.25rem;
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 0.5rem; min-width: 110px;
}
.epc-qr {
  position: relative; width: 80px; height: 80px;
  background: #fff; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  padding: 6px;
}
.epc-qr-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.epc-qr-grid {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 2px; width: 100%; height: 100%;
}
.epc-qr-cell {
  border-radius: 1px; background: #e2e8f0;
}
.epc-qr-on { background: #1e293b; }
.epc-qr-glow {
  position: absolute; inset: -4px; border-radius: 14px;
  background: radial-gradient(circle at center, rgba(129,140,248,0.2), transparent 70%);
  pointer-events: none;
  transition: opacity 0.3s;
}
.epc-ticket:hover .epc-qr-glow { opacity: 0.5; }
.epc-qr-label {
  font-size: 0.58rem; color: #475569; text-align: center;
  max-width: 100px; line-height: 1.3;
}

.epc-actions {
  display: flex; gap: 0.5rem; padding: 0.75rem 1.25rem 1.25rem;
  justify-content: flex-end;
}
.epc-btn {
  padding: 0.4rem 0.85rem; border-radius: 8px;
  font-size: 0.7rem; font-weight: 600; font-family: inherit;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
  display: inline-flex; align-items: center;
}
.epc-btn:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; border-color: rgba(255,255,255,0.12); }
.epc-btn-cal { border-color: rgba(129,140,248,0.15); color: #818cf8; }
.epc-btn-cal:hover { background: rgba(129,140,248,0.1); border-color: rgba(129,140,248,0.25); color: #a5b4fc; }

@media (max-width: 768px) {
  .epc-ticket-inner { flex-direction: column; }
  .epc-center { border-left: none; border-top: 1px dashed rgba(255,255,255,0.06); padding: 0.75rem; }
  .epc-divider { display: none; }
  .epc-right { padding: 0.75rem; flex-direction: row; }
  .epc-actions { justify-content: center; }
}
</style>
