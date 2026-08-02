<template>
  <Teleport to="body">
    <div class="cpm-backdrop" @click.self="$emit('close')">
      <div class="cpm-modal">
        <button class="cpm-close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>

        <div class="cpm-preview">
          <div class="cpm-preview-bg"></div>
          <div class="cpm-preview-inner">
            <div class="cpm-preview-seal"><i class="bi bi-award-fill"></i></div>
            <div class="cpm-preview-label">Certificate of {{ cert.type }}</div>
            <h2 class="cpm-preview-name">{{ store.studentProfile.fullName }}</h2>
            <div class="cpm-preview-divider"></div>
            <div class="cpm-preview-event">For participating in <strong>{{ cert.eventName }}</strong></div>
            <div class="cpm-preview-club">{{ cert.organizer }}</div>
            <div class="cpm-preview-sigs">
              <div class="cpm-sig"><div class="cpm-sig-line"></div><span>Faculty Coordinator</span></div>
              <div class="cpm-sig"><div class="cpm-sig-line"></div><span>Club Lead</span></div>
            </div>
            <div class="cpm-preview-qr">
              <div class="cpm-qr-grid">
                <div v-for="i in 49" :key="i" class="cpm-qr-cell" :class="{ 'cpm-qr-on': (i * 7 + Math.floor(i / 7) * 3) % 3 !== 0 }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="cpm-info">
          <div class="cpm-row"><span class="cpm-label">Student Name</span><span class="cpm-value">{{ store.studentProfile.fullName }}</span></div>
          <div class="cpm-row"><span class="cpm-label">Event</span><span class="cpm-value">{{ cert.eventName }}</span></div>
          <div class="cpm-row"><span class="cpm-label">Issue Date</span><span class="cpm-value">{{ cert.issueDate }}</span></div>
          <div class="cpm-row"><span class="cpm-label">Certificate ID</span><span class="cpm-value cpm-mono">CERT-DRV-{{ String(cert.id).padStart(5, '0') }}</span></div>
          <div class="cpm-row"><span class="cpm-label">Organizer</span><span class="cpm-value">{{ cert.organizer }}</span></div>
        </div>

        <div class="cpm-actions">
          <button class="cpm-btn cpm-btn-primary" @click="$emit('download', cert)"><i class="bi bi-download me-2"></i>Download PDF</button>
          <button class="cpm-btn" @click="$emit('share', cert)"><i class="bi bi-share me-2"></i>Share</button>
          <button class="cpm-btn" @click="$emit('close')">Close</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { store } from '../../store/mockData';
defineProps({ cert: { type: Object, required: true } });
defineEmits(['close', 'download', 'share']);
</script>

<style scoped>
.cpm-backdrop {
  position: fixed; inset: 0; z-index: 100000;
  background: rgba(3,5,12,0.7); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  animation: cpmFade 0.2s ease;
}
.cpm-modal {
  position: relative; width: 94%; max-width: 460px;
  max-height: 90vh; overflow-y: auto;
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(129,140,248,0.1);
  border-radius: 24px; padding: 2rem 1.75rem 1.5rem;
  animation: cpmSlide 0.35s cubic-bezier(0.16,1,0.3,1);
  box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 40px rgba(79,70,229,0.08);
}
.cpm-close {
  position: absolute; top: 0.75rem; right: 0.75rem;
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(0,0,0,0.3); color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s; font-size: 0.7rem;
}
.cpm-close:hover { background: rgba(255,255,255,0.1); color: #f1f5f9; }

.cpm-preview {
  position: relative;
  background: linear-gradient(135deg, #0f172a, #1a1040);
  border: 1.5px solid rgba(129,140,248,0.12);
  border-radius: 16px;
  padding: 2rem 1.5rem;
  margin-bottom: 1.25rem;
  text-align: center;
  overflow: hidden;
}
.cpm-preview-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 30% 20%, rgba(129,140,248,0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(124,58,237,0.04) 0%, transparent 50%);
  pointer-events: none;
}
.cpm-preview-inner { position: relative; z-index: 1; }
.cpm-preview-seal {
  width: 48px; height: 48px; border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.75rem;
  color: #fff; font-size: 1.3rem;
  box-shadow: 0 4px 15px rgba(79,70,229,0.3);
}
.cpm-preview-label {
  font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 1px; color: #a5b4fc; margin-bottom: 0.5rem;
}
.cpm-preview-name {
  font-size: 1.3rem; font-weight: 800; color: #f1f5f9;
  margin: 0 0 0.75rem; letter-spacing: -0.5px;
}
.cpm-preview-divider {
  width: 60px; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(129,140,248,0.4), transparent);
  margin: 0 auto 0.75rem;
}
.cpm-preview-event {
  font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.25rem;
}
.cpm-preview-event strong { color: #e2e8f0; }
.cpm-preview-club {
  font-size: 0.72rem; color: #818cf8; font-weight: 600;
  margin-bottom: 1.25rem;
}
.cpm-preview-sigs {
  display: flex; justify-content: center; gap: 2rem;
  margin-bottom: 1rem;
}
.cpm-sig { text-align: center; }
.cpm-sig-line {
  width: 80px; height: 1.5px;
  background: rgba(255,255,255,0.15); margin-bottom: 0.25rem;
}
.cpm-sig span { font-size: 0.55rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }

.cpm-preview-qr {
  width: 56px; height: 56px;
  background: #fff; border-radius: 8px;
  padding: 4px; margin: 0 auto;
}
.cpm-qr-grid {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 1.5px; width: 100%; height: 100%;
}
.cpm-qr-cell { border-radius: 1px; background: #e2e8f0; }
.cpm-qr-on { background: #1e293b; }

.cpm-info { margin-bottom: 1.25rem; }
.cpm-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.4rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.cpm-row:last-child { border-bottom: none; }
.cpm-label { font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.3px; }
.cpm-value { font-size: 0.8rem; font-weight: 600; color: #e2e8f0; text-align: right; }
.cpm-mono { font-family: monospace; letter-spacing: 0.5px; color: #818cf8; }

.cpm-actions { display: flex; gap: 0.5rem; }
.cpm-btn {
  padding: 0.55rem 1rem; border-radius: 10px;
  font-size: 0.78rem; font-weight: 700; font-family: inherit;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
  display: inline-flex; align-items: center; justify-content: center;
  flex: 1;
}
.cpm-btn:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; }
.cpm-btn-primary {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none; color: #fff;
}
.cpm-btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(79,70,229,0.4); }

@keyframes cpmFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes cpmSlide { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
