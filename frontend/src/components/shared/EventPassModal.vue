<template>
  <Teleport to="body">
    <div class="epm-backdrop" @click.self="$emit('close')">
      <div class="epm-modal">
        <button class="epm-close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        <div class="epm-qr-wrap">
          <div class="epm-qr">
            <div class="epm-qr-grid">
              <div v-for="i in 81" :key="i" class="epm-qr-cell" :class="{ 'epm-on': (i * 5 + Math.floor(i / 9) * 7) % 3 !== 0 }"></div>
            </div>
            <div class="epm-qr-glow"></div>
          </div>
        </div>
        <h2 class="epm-title">Event Pass Details</h2>
        <div class="epm-details">
          <div class="epm-row"><span class="epm-label">Event</span><span class="epm-value">{{ event.name }}</span></div>
          <div class="epm-row"><span class="epm-label">Date</span><span class="epm-value">{{ event.date }}</span></div>
          <div class="epm-row"><span class="epm-label">Venue</span><span class="epm-value">{{ event.venue }}</span></div>
          <div class="epm-row"><span class="epm-label">Organizer</span><span class="epm-value">TechNova Club</span></div>
          <div class="epm-row"><span class="epm-label">Registration No.</span><span class="epm-value epm-mono">DRV-2026-{{ String(event.id).padStart(5, '0') }}</span></div>
          <div class="epm-row"><span class="epm-label">Student Name</span><span class="epm-value">{{ store.studentProfile.fullName }}</span></div>
        </div>
        <div class="epm-instruction">
          <i class="bi bi-info-circle-fill"></i>
          Present this QR code at the entrance for attendance verification.
        </div>
        <button class="epm-dismiss" @click="$emit('close')">Close</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { store } from '../../store/mockData';

defineProps({ event: { type: Object, required: true } });
defineEmits(['close']);
</script>

<style scoped>
.epm-backdrop {
  position: fixed; inset: 0; z-index: 100000;
  background: rgba(3,5,12,0.7); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  animation: epmFade 0.2s ease;
}
.epm-modal {
  position: relative; width: 94%; max-width: 420px;
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(129,140,248,0.12);
  border-radius: 24px; padding: 2.5rem 1.75rem 1.75rem;
  text-align: center;
  animation: epmSlide 0.35s cubic-bezier(0.16,1,0.3,1);
  box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 40px rgba(79,70,229,0.08);
}
.epm-close {
  position: absolute; top: 0.75rem; right: 0.75rem;
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(0,0,0,0.3); color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s; font-size: 0.7rem;
}
.epm-close:hover { background: rgba(255,255,255,0.1); color: #f1f5f9; }

.epm-qr-wrap {
  margin: 0 auto 1.25rem; width: 130px; height: 130px;
  background: #fff; border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  padding: 8px; position: relative;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.epm-qr { width: 100%; height: 100%; position: relative; }
.epm-qr-grid {
  display: grid; grid-template-columns: repeat(9, 1fr);
  gap: 2px; width: 100%; height: 100%;
}
.epm-qr-cell { border-radius: 1px; background: #e2e8f0; }
.epm-on { background: #1e293b; }
.epm-qr-glow {
  position: absolute; inset: -8px; border-radius: 20px;
  background: radial-gradient(circle at center, rgba(129,140,248,0.3), transparent 70%);
  pointer-events: none; animation: epmPulse 2.5s ease-in-out infinite;
}
@keyframes epmPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

.epm-title {
  font-size: 1.25rem; font-weight: 800; color: #f1f5f9;
  margin: 0 0 1rem; letter-spacing: -0.3px;
}

.epm-details { text-align: left; margin-bottom: 1rem; }
.epm-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.epm-row:last-child { border-bottom: none; }
.epm-label { font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.3px; }
.epm-value { font-size: 0.82rem; font-weight: 600; color: #e2e8f0; text-align: right; }
.epm-mono { font-family: monospace; letter-spacing: 0.5px; color: #818cf8; }

.epm-instruction {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.65rem 0.85rem; border-radius: 10px;
  background: rgba(129,140,248,0.06); border: 1px solid rgba(129,140,248,0.1);
  font-size: 0.75rem; color: #94a3b8; margin-bottom: 1.25rem; text-align: left;
}
.epm-instruction i { color: #818cf8; font-size: 0.9rem; flex-shrink: 0; }

.epm-dismiss {
  width: 100%; padding: 0.65rem 1.5rem; border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none; color: #fff; font-size: 0.85rem; font-weight: 700;
  font-family: inherit; cursor: pointer;
  transition: all 0.25s;
}
.epm-dismiss:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(79,70,229,0.4); }

@keyframes epmFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes epmSlide { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
