<template>
  <Teleport to="body">
    <div class="bpm-backdrop" @click.self="$emit('close')">
      <div class="bpm-modal" id="equipment-borrow-pass">
        <button class="bpm-close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        
        <div class="bpm-header-badge">
          <i class="bi bi-box-seam-fill me-1"></i>Equipment Borrow Pass
        </div>

        <div class="bpm-qr-wrap">
          <img v-if="qrImageSrc" :src="qrImageSrc" alt="Borrow Pass QR Code" class="bpm-qr-img" />
          <div v-else class="bpm-qr-placeholder">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          </div>
          <div class="bpm-qr-glow"></div>
        </div>

        <div class="bpm-item-preview" v-if="borrowData.equipment_image_url || borrowData.image">
          <img :src="borrowData.equipment_image_url || borrowData.image" :alt="borrowData.equipment_name || borrowData.name" class="bpm-item-thumb" />
          <div class="bpm-item-meta">
            <h3 class="bpm-item-title">{{ borrowData.equipment_name || borrowData.name || 'Equipment' }}</h3>
            <span class="bpm-item-cat">{{ formatCategory(borrowData.equipment_category || borrowData.category) }}</span>
          </div>
        </div>
        <h2 v-else class="bpm-title">{{ borrowData.equipment_name || borrowData.name || 'Equipment Pass' }}</h2>

        <div class="bpm-details">
          <div class="bpm-row">
            <span class="bpm-label">Student Name</span>
            <span class="bpm-value">{{ studentName }}</span>
          </div>
          <div v-if="studentRollNo" class="bpm-row">
            <span class="bpm-label">Roll Number</span>
            <span class="bpm-value bpm-mono">{{ studentRollNo }}</span>
          </div>
          <div class="bpm-row">
            <span class="bpm-label">Quantity Borrowed</span>
            <span class="bpm-value bpm-highlight">{{ borrowData.borrowed_quantity || 1 }} Unit{{ (borrowData.borrowed_quantity || 1) > 1 ? 's' : '' }}</span>
          </div>
          <div class="bpm-row">
            <span class="bpm-label">Requested Date</span>
            <span class="bpm-value">{{ formattedRequestDate }}</span>
          </div>
          <div class="bpm-row highlight-deadline">
            <span class="bpm-label"><i class="bi bi-calendar-event me-1"></i>Return Deadline</span>
            <span class="bpm-value bpm-deadline">
              {{ formattedReturnDate }}
              <span class="bpm-badge-days">3 Days</span>
            </span>
          </div>
          <div v-if="borrowData.storage_location || borrowData.location" class="bpm-row">
            <span class="bpm-label">Storage Location</span>
            <span class="bpm-value">{{ borrowData.storage_location || borrowData.location }}</span>
          </div>
          <div class="bpm-row">
            <span class="bpm-label">Pass ID</span>
            <span class="bpm-value bpm-mono bpm-copyable" title="Click to copy Pass ID" @click="copyPassId">
              {{ passDisplayId }} <i class="bi bi-copy ms-1"></i>
            </span>
          </div>
        </div>

        <div class="bpm-instruction">
          <i class="bi bi-qr-code-scan"></i>
          Present this QR code or Pass ID to the Club Administrator during checkout and return.
        </div>

        <div class="bpm-actions">
          <button class="bpm-btn-done" @click="$emit('close')">
            <i class="bi bi-check2-circle me-1"></i>Got It
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue';
import { store } from '../../store/mockData';

const props = defineProps({
  borrowData: {
    type: Object,
    required: true,
  },
});

defineEmits(['close']);

const studentName = computed(() => {
  return props.borrowData.student_name || store.user?.name || store.user?.full_name || 'Student';
});

const studentRollNo = computed(() => {
  return props.borrowData.student_roll_number || store.user?.roll_number || store.user?.id || '';
});

const passDisplayId = computed(() => {
  const raw = props.borrowData.id || props.borrowData.borrow_id || props.borrowData.pass_id || '';
  if (!raw) return 'BORROW-PASS';
  const clean = String(raw).replace(/-/g, '').toUpperCase();
  return `BORROW-${clean.slice(0, 8)}`;
});

const qrImageSrc = computed(() => {
  if (props.borrowData.qr_code_url) return props.borrowData.qr_code_url;
  const passId = passDisplayId.value;
  return `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(passId)}`;
});

const formattedRequestDate = computed(() => {
  const d = props.borrowData.requested_date ? new Date(props.borrowData.requested_date) : new Date();
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
});

const formattedReturnDate = computed(() => {
  if (props.borrowData.return_date) {
    const d = new Date(props.borrowData.return_date);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }
  const d = new Date();
  d.setDate(d.getDate() + 3);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
});

const formatCategory = (cat) => {
  if (!cat) return 'General';
  return String(cat).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const copyPassId = async () => {
  try {
    await navigator.clipboard.writeText(passDisplayId.value);
    const toast = document.createElement('div');
    toast.className = 'std-toast';
    toast.innerHTML = '<i class="bi bi-check-circle-fill me-2" style="color:#4ade80;"></i>Pass ID copied!';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  } catch {}
};
</script>

<style scoped>
.bpm-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 8, 20, 0.85);
  backdrop-filter: blur(12px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.bpm-modal {
  position: relative;
  background: linear-gradient(160deg, #111b2e 0%, #0a1120 100%);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 20px;
  width: 100%;
  max-width: 440px;
  padding: 2rem;
  box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: bpmPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes bpmPop {
  0% { transform: scale(0.9) translateY(20px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

.bpm-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bpm-close:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  transform: rotate(90deg);
}

.bpm-header-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.85rem;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1.25rem;
}

.bpm-qr-wrap {
  position: relative;
  width: 170px;
  height: 170px;
  background: #ffffff;
  padding: 10px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.bpm-qr-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.bpm-qr-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bpm-qr-glow {
  position: absolute;
  inset: -8px;
  border-radius: 24px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.4) 0%, transparent 70%);
  z-index: -1;
  opacity: 0.7;
}

.bpm-item-preview {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  margin-bottom: 1rem;
  text-align: left;
}

.bpm-item-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.bpm-item-meta {
  flex: 1;
  min-width: 0;
}

.bpm-item-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bpm-item-cat {
  font-size: 0.75rem;
  color: #38bdf8;
  font-weight: 600;
}

.bpm-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1rem 0;
}

.bpm-details {
  width: 100%;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.bpm-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.82rem;
}

.bpm-row.highlight-deadline {
  background: rgba(245, 158, 11, 0.1);
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  border: 1px dashed rgba(245, 158, 11, 0.3);
}

.bpm-label {
  color: #94a3b8;
}

.bpm-value {
  color: #e2e8f0;
  font-weight: 500;
}

.bpm-mono {
  font-family: 'SF Mono', Consolas, monospace;
}

.bpm-highlight {
  color: #38bdf8;
  font-weight: 700;
}

.bpm-deadline {
  color: #f59e0b;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.bpm-badge-days {
  background: #f59e0b;
  color: #000;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

.bpm-copyable {
  cursor: pointer;
  color: #38bdf8;
  transition: opacity 0.2s;
}

.bpm-copyable:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.bpm-instruction {
  font-size: 0.76rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  line-height: 1.35;
  text-align: left;
}

.bpm-actions {
  width: 100%;
}

.bpm-btn-done {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.bpm-btn-done:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}
</style>
