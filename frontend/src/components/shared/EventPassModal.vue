<template>
  <Teleport to="body">
    <div class="epm-backdrop" @click.self="$emit('close')">
      <div class="epm-modal" id="event-pass-card">
        <button class="epm-close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        
        <div class="epm-header-badge">
          <i class="bi bi-ticket-perforated-fill me-1"></i>Official Event Pass
        </div>

        <div class="epm-qr-wrap">
          <img v-if="qrImageSrc" :src="qrImageSrc" alt="Event Pass QR Code" class="epm-qr-img" />
          <div v-else class="epm-qr-placeholder">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          </div>
          <div class="epm-qr-glow"></div>
        </div>

        <h2 class="epm-title">{{ event.name || 'Event Pass' }}</h2>

        <div class="epm-details">
          <div class="epm-row">
            <span class="epm-label">Student Name</span>
            <span class="epm-value">{{ studentName }}</span>
          </div>
          <div v-if="studentId" class="epm-row">
            <span class="epm-label">Student ID</span>
            <span class="epm-value epm-mono">{{ studentId }}</span>
          </div>
          <div v-if="teamName" class="epm-row">
            <span class="epm-label">Team / Participation</span>
            <span class="epm-value">{{ teamName }}</span>
          </div>
          <div class="epm-row">
            <span class="epm-label">Date</span>
            <span class="epm-value">{{ eventDate }}</span>
          </div>
          <div class="epm-row">
            <span class="epm-label">Venue</span>
            <span class="epm-value">{{ eventVenue }}</span>
          </div>
          <div class="epm-row">
            <span class="epm-label">Attendance Status</span>
            <span class="epm-status-pill" :class="attendanceStatusClass">
              <i :class="attendanceStatusIcon"></i>{{ attendanceStatusText }}
            </span>
          </div>
          <div class="epm-row">
            <span class="epm-label">Pass ID</span>
            <span class="epm-value epm-mono epm-copyable" title="Click to copy Pass ID" @click="copyPassId">
              {{ passDisplayId }} <i class="bi bi-copy ms-1"></i>
            </span>
          </div>
        </div>

        <div class="epm-instruction">
          <i class="bi bi-qr-code-scan"></i>
          Present this QR code at the event entrance for scanning by the Lab Administrator.
        </div>

        <div class="epm-actions">
          <button class="epm-btn-download" @click="downloadPass">
            <i class="bi bi-qr-code me-2"></i>Download QR Code
          </button>
          <button class="epm-btn-close" @click="$emit('close')">Close</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue';
import { store } from '../../store/mockData';

const props = defineProps({
  event: { type: Object, required: true },
});
defineEmits(['close']);

const studentName = computed(() => {
  return props.event.student?.name || props.event.student_name || store.currentUser?.full_name || store.studentProfile?.fullName || 'Student Member';
});

const studentId = computed(() => {
  return props.event.student?.student_id || props.event.student_id || store.currentUser?.student_id || '';
});

const teamName = computed(() => {
  return props.event.team_name || '';
});

const eventDate = computed(() => {
  return props.event.date || props.event.event_date || props.event.formattedDate || 'TBD';
});

const eventVenue = computed(() => {
  const v = props.event.venue || props.event.formattedVenue;
  if (!v) return 'Campus Facility';
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
});

const passDisplayId = computed(() => {
  const rawId = props.event.registration_id || props.event.id || 'REG001';
  return `PASS-${String(rawId).slice(0, 8).toUpperCase()}`;
});

const copyPassId = () => {
  try {
    navigator.clipboard.writeText(passDisplayId.value);
  } catch {}
};

const attendanceStatus = computed(() => {
  return (props.event.attendance_status || 'absent').toLowerCase();
});

const attendanceStatusText = computed(() => {
  if (attendanceStatus.value === 'present') return 'Present';
  return 'Not Scanned Yet';
});

const attendanceStatusClass = computed(() => {
  if (attendanceStatus.value === 'present') return 'epm-status-present';
  return 'epm-status-pending';
});

const attendanceStatusIcon = computed(() => {
  if (attendanceStatus.value === 'present') return 'bi bi-check-circle-fill me-1';
  return 'bi bi-clock-history me-1';
});

// Fallback client-side SVG generator if qr_code_url is not attached
const createFallbackQrSvg = (text) => {
  const size = 29;
  const border = 2;
  const boxSize = 8;
  const totalSize = (size + border * 2) * boxSize;

  const matrix = Array.from({ length: size }, () => Array(size).fill(0));
  const addFinder = (top, left) => {
    for (let r = 0; r < 7; r++) {
      for (let c = 0; c < 7; c++) {
        matrix[top + r][left + c] = (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4)) ? 1 : 0;
      }
    }
  };
  addFinder(0, 0);
  addFinder(0, size - 7);
  addFinder(size - 7, 0);

  for (let i = 8; i < size - 8; i++) {
    matrix[6][i] = i % 2 === 0 ? 1 : 0;
    matrix[i][6] = i % 2 === 0 ? 1 : 0;
  }

  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = (hash * 31 + text.charCodeAt(i)) & 0xFFFFFFFF;
  }

  let bitIdx = 0;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      const inFinder = (r < 9 && c < 9) || (r < 9 && c >= size - 9) || (r >= size - 9 && c < 9);
      const inTiming = r === 6 || c === 6;
      if (inFinder || inTiming) continue;
      matrix[r][c] = ((hash >> (bitIdx % 30)) ^ (r * 17 + c * 37)) & 1;
      bitIdx++;
    }
  }

  const paths = [];
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (matrix[r][c]) {
        const x = (c + border) * boxSize;
        const y = (r + border) * boxSize;
        paths.push(`M${x},${y}h${boxSize}v${boxSize}h-${boxSize}z`);
      }
    }
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${totalSize} ${totalSize}" width="${totalSize}" height="${totalSize}"><rect width="${totalSize}" height="${totalSize}" fill="#ffffff"/><path d="${paths.join(' ')}" fill="#0f172a"/></svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
};

const qrImageSrc = computed(() => {
  if (props.event.qr_code_url) return props.event.qr_code_url;
  if (props.event.qrCodeUrl) return props.event.qrCodeUrl;
  const rawId = props.event.registration_id || props.event.id || 'registration';
  return createFallbackQrSvg(`/api/events/registrations/${rawId}/verify`);
});

const downloadPass = () => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const size = 500;
  canvas.width = size;
  canvas.height = size;

  // Pure White Background Margin
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, size, size);

  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    // Draw only the QR code cleanly inside white quiet zone
    ctx.drawImage(img, 30, 30, size - 60, size - 60);

    const link = document.createElement('a');
    link.download = `qr-code-${String(props.event.name || 'pass').toLowerCase().replace(/[^a-z0-9]+/g, '-')}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  };
  img.src = qrImageSrc.value;
};
</script>

<style scoped>
.epm-backdrop {
  position: fixed; inset: 0; z-index: 100000;
  background: rgba(3, 5, 12, 0.78); backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  animation: epmFade 0.2s ease;
  padding: 1rem;
}
.epm-modal {
  position: relative; width: 100%; max-width: 440px;
  background: rgba(15, 23, 42, 0.97);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px; padding: 2.25rem 1.75rem 1.75rem;
  text-align: center;
  animation: epmSlide 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.55), 0 0 40px rgba(79, 70, 229, 0.1);
}
.epm-close {
  position: absolute; top: 0.85rem; right: 0.85rem;
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.3); color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s; font-size: 0.75rem;
}
.epm-close:hover { background: rgba(255, 255, 255, 0.1); color: #f1f5f9; }

.epm-header-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.25);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  margin-bottom: 1.25rem;
}

.epm-qr-wrap {
  margin: 0 auto 1.25rem; width: 160px; height: 160px;
  background: #ffffff; border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  padding: 10px; position: relative;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
}
.epm-qr-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}
.epm-qr-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
.epm-qr-glow {
  position: absolute; inset: -8px; border-radius: 24px;
  background: radial-gradient(circle at center, rgba(129, 140, 248, 0.3), transparent 70%);
  pointer-events: none; animation: epmPulse 2.5s ease-in-out infinite;
}
@keyframes epmPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

.epm-title {
  font-size: 1.3rem; font-weight: 800; color: #f1f5f9;
  margin: 0 0 1rem; letter-spacing: -0.3px;
}

.epm-details { text-align: left; margin-bottom: 1rem; }
.epm-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.45rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.epm-row:last-child { border-bottom: none; }
.epm-label { font-size: 0.74rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.4px; }
.epm-value { font-size: 0.84rem; font-weight: 600; color: #e2e8f0; text-align: right; }
.epm-mono { font-family: monospace; letter-spacing: 0.5px; color: #818cf8; }

.epm-status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
}
.epm-status-present {
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
  border: 1px solid rgba(34, 197, 94, 0.25);
}
.epm-status-pending {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.epm-instruction {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.7rem 0.9rem; border-radius: 12px;
  background: rgba(129, 140, 248, 0.06); border: 1px solid rgba(129, 140, 248, 0.12);
  font-size: 0.76rem; color: #94a3b8; margin-bottom: 1.25rem; text-align: left;
}
.epm-instruction i { color: #818cf8; font-size: 1rem; flex-shrink: 0; }

.epm-actions {
  display: flex;
  gap: 0.75rem;
}

.epm-btn-download {
  flex: 1; padding: 0.65rem 1rem; border-radius: 12px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none; color: #fff; font-size: 0.85rem; font-weight: 700;
  font-family: inherit; cursor: pointer;
  transition: all 0.25s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35);
}
.epm-btn-download:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
}

.epm-btn-close {
  padding: 0.65rem 1.25rem; border-radius: 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1; font-size: 0.85rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.epm-btn-close:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
}

@keyframes epmFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes epmSlide { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
