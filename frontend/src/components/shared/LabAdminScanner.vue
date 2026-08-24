<template>
  <div class="las-container">
    <!-- Top Header & Mode Toggles -->
    <div class="las-header">
      <div>
        <h4 class="las-title"><i class="bi bi-qr-code-scan me-2 text-primary"></i>Event Pass Scanner & Attendance</h4>
        <p class="las-subtitle">Scan student event pass QR codes via webcam or manual ID to mark attendance as Present.</p>
      </div>
      <div class="las-tabs">
        <button
          class="las-tab-btn"
          :class="{ active: scanMode === 'camera' }"
          @click="setMode('camera')"
        >
          <i class="bi bi-camera-video-fill me-1"></i>Webcam Scanner
        </button>
        <button
          class="las-tab-btn"
          :class="{ active: scanMode === 'upload' }"
          @click="setMode('upload')"
        >
          <i class="bi bi-file-earmark-image-fill me-1"></i>Upload QR Image
        </button>
        <button
          class="las-tab-btn"
          :class="{ active: scanMode === 'manual' }"
          @click="setMode('manual')"
        >
          <i class="bi bi-keyboard-fill me-1"></i>Manual Entry
        </button>
      </div>
    </div>

    <div class="row g-4">
      <!-- Left Column: Scanner Area -->
      <div class="col-lg-7">
        <div class="las-card">
          <!-- 1. Webcam Scanner -->
          <div v-if="scanMode === 'camera'" class="las-camera-wrap">
            <div class="las-video-box">
              <video ref="videoEl" class="las-video" playsinline muted></video>
              <canvas ref="canvasEl" class="d-none"></canvas>

              <!-- Viewfinder Overlay -->
              <div v-if="isCameraActive" class="las-viewfinder">
                <div class="las-corner tl"></div>
                <div class="las-corner tr"></div>
                <div class="las-corner bl"></div>
                <div class="las-corner br"></div>
                <div class="las-laser"></div>
                <span class="las-guide-text">Align QR code within frame</span>
              </div>

              <!-- Camera Offline State -->
              <div v-if="!isCameraActive" class="las-camera-offline">
                <div class="las-offline-icon">
                  <i class="bi bi-camera-video-off"></i>
                </div>
                <h5>Camera is Turned Off</h5>
                <p>Click below to initialize your webcam and begin scanning event passes.</p>
                <button class="las-btn-primary" @click="startCamera">
                  <i class="bi bi-camera-video me-2"></i>Start Webcam Scanner
                </button>
              </div>

              <!-- Loading State -->
              <div v-if="isInitializing" class="las-camera-offline">
                <div class="spinner-border text-primary mb-3" role="status"></div>
                <h5>Accessing Camera...</h5>
                <p>Please allow camera permissions in your browser prompt.</p>
              </div>
            </div>

            <!-- Camera Controls Bar -->
            <div v-if="isCameraActive" class="las-cam-controls">
              <button class="las-btn-ctrl" @click="stopCamera">
                <i class="bi bi-stop-circle me-1"></i>Stop Camera
              </button>
              <button class="las-btn-ctrl" @click="switchCamera">
                <i class="bi bi-arrow-repeat me-1"></i>Flip Camera
              </button>
              <button class="las-btn-ctrl" :class="{ active: soundEnabled }" @click="soundEnabled = !soundEnabled">
                <i :class="soundEnabled ? 'bi bi-volume-up-fill' : 'bi bi-volume-mute-fill'" class="me-1"></i>
                {{ soundEnabled ? 'Sound On' : 'Muted' }}
              </button>
            </div>
          </div>

          <!-- 2. File Upload Scanner -->
          <div v-else-if="scanMode === 'upload'" class="las-upload-wrap">
            <div
              class="las-dropzone"
              :class="{ dragging: isDragging }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleFileDrop"
              @click="$refs.fileInput.click()"
            >
              <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="handleFileSelect" />
              <div class="las-upload-icon"><i class="bi bi-cloud-arrow-up-fill"></i></div>
              <h5>Drop QR Code Image Here</h5>
              <p>or click to browse from your device (PNG, JPG, SVG)</p>
            </div>
          </div>

          <!-- 3. Manual Entry Input -->
          <div v-else-if="scanMode === 'manual'" class="las-manual-wrap">
            <label class="las-label">Registration ID / UUID / Pass URL</label>
            <div class="las-input-group">
              <input
                v-model="manualInput"
                type="text"
                class="las-input"
                placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000 or /api/.../verify"
                @keyup.enter="handleManualSubmit"
              />
              <button class="las-btn-primary" :disabled="isVerifying || !manualInput.trim()" @click="handleManualSubmit">
                <span v-if="isVerifying" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-search me-2"></i>Verify Pass
              </button>
            </div>
            <span class="las-hint">You can find the registration UUID on the student's digital pass or event pass card.</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Verification Result Card -->
      <div class="col-lg-5">
        <div class="las-card h-100">
          <div class="las-card-header">
            <h5 class="m-0"><i class="bi bi-person-check-fill me-2 text-primary"></i>Verification Result</h5>
            <span v-if="lastResult" class="las-time-tag">{{ formatTime(lastResult.scanned_at) }}</span>
          </div>

          <!-- Processing State -->
          <div v-if="isVerifying" class="las-result-empty">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <h5>Verifying Pass...</h5>
            <p>Connecting to backend and checking registration status.</p>
          </div>

          <!-- Active Result -->
          <div v-else-if="lastResult" class="las-result-body">
            <!-- Alert Banner -->
            <div
              class="las-status-banner"
              :class="lastResult.already_marked ? 'banner-amber' : (lastResult.success ? 'banner-green' : 'banner-red')"
            >
              <i :class="lastResult.already_marked ? 'bi bi-exclamation-triangle-fill' : (lastResult.success ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill')"></i>
              <div>
                <strong>{{ lastResult.message }}</strong>
                <span class="d-block small">{{ lastResult.already_marked ? 'Attendance was recorded previously.' : 'Attendance successfully marked as PRESENT.' }}</span>
              </div>
            </div>

            <!-- Student Profile Summary -->
            <div class="las-student-box">
              <div class="d-flex align-items-center gap-3 mb-3">
                <div class="las-avatar">{{ getInitials(lastResult.registration?.student?.name) }}</div>
                <div>
                  <h5 class="las-student-name m-0">{{ lastResult.registration?.student?.name || 'Student Member' }}</h5>
                  <span class="las-student-dept">{{ formatDepartment(lastResult.registration?.student?.department) }}</span>
                </div>
              </div>

              <div class="las-info-grid">
                <div class="las-info-item">
                  <span class="las-info-label">Student ID</span>
                  <span class="las-info-val">{{ lastResult.registration?.student?.student_id || '—' }}</span>
                </div>
                <div class="las-info-item">
                  <span class="las-info-label">Team / Reg Name</span>
                  <span class="las-info-val">{{ lastResult.registration?.team_name || 'Individual' }}</span>
                </div>
                <div class="las-info-item">
                  <span class="las-info-label">Email</span>
                  <span class="las-info-val text-truncate">{{ lastResult.registration?.student?.email || '—' }}</span>
                </div>
                <div class="las-info-item">
                  <span class="las-info-label">Attendance</span>
                  <span class="badge bg-success text-light px-2 py-1"><i class="bi bi-check2 me-1"></i>Present</span>
                </div>
              </div>
            </div>

            <!-- Event Details -->
            <div class="las-event-box">
              <h6 class="las-event-title"><i class="bi bi-calendar-event me-2 text-primary"></i>{{ lastResult.registration?.event?.name }}</h6>
              <div class="las-event-meta">
                <span><i class="bi bi-calendar3 me-1"></i>{{ formatDate(lastResult.registration?.event?.date || lastResult.registration?.event?.event_date) }}</span>
                <span><i class="bi bi-geo-alt me-1"></i>{{ formatVenue(lastResult.registration?.event?.venue) }}</span>
              </div>
            </div>
          </div>

          <!-- Error Result -->
          <div v-else-if="scanError" class="las-result-body">
            <div class="las-status-banner banner-red">
              <i class="bi bi-x-circle-fill"></i>
              <div>
                <strong>Verification Failed</strong>
                <span class="d-block small">{{ scanError }}</span>
              </div>
            </div>
          </div>

          <!-- Empty Initial State -->
          <div v-else class="las-result-empty">
            <div class="las-empty-icon"><i class="bi bi-upc-scan"></i></div>
            <h5>Ready for Scanning</h5>
            <p>Point camera at student QR pass or enter registration ID on the left.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Section: Attendance Log Table -->
    <div class="las-card mt-4">
      <div class="las-card-header">
        <div>
          <h5 class="m-0"><i class="bi bi-clock-history me-2 text-primary"></i>Scanned Attendance Log</h5>
          <span class="las-subtitle">{{ scanLog.length }} student{{ scanLog.length !== 1 ? 's' : '' }} scanned in this session</span>
        </div>
        <button v-if="scanLog.length > 0" class="las-btn-clear" @click="scanLog = []">
          <i class="bi bi-trash3 me-1"></i>Clear Log
        </button>
      </div>

      <div v-if="scanLog.length === 0" class="p-4 text-center text-muted">
        <span>No scans recorded in this session yet.</span>
      </div>

      <div v-else class="table-responsive">
        <table class="table las-table align-middle">
          <thead>
            <tr>
              <th>Time</th>
              <th>Student Name</th>
              <th>Student ID</th>
              <th>Department</th>
              <th>Event</th>
              <th>Team</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in scanLog" :key="idx">
              <td class="text-secondary small">{{ formatTime(item.timestamp) }}</td>
              <td><strong>{{ item.name }}</strong></td>
              <td><code>{{ item.student_id }}</code></td>
              <td>{{ formatDepartment(item.department) }}</td>
              <td>{{ item.event_name }}</td>
              <td>{{ item.team_name || 'Individual' }}</td>
              <td>
                <span class="badge bg-success bg-opacity-20 text-success px-2 py-1">
                  <i class="bi bi-check-circle-fill me-1"></i>Present
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { store } from '../../store/mockData';
import { verifyRegistrationPassApi } from '../../api/qr';

const scanMode = ref('camera');
const isCameraActive = ref(false);
const isInitializing = ref(false);
const isVerifying = ref(false);
const isDragging = ref(false);
const manualInput = ref('');
const scanError = ref('');
const lastResult = ref(null);
const scanLog = ref([]);
const soundEnabled = ref(true);

const videoEl = ref(null);
const canvasEl = ref(null);
const fileInput = ref(null);

let stream = null;
let scanInterval = null;
let currentFacingMode = 'environment';
let lastScannedCode = null;
let lastScanTime = 0;

const loadJsQrScript = () => {
  if (typeof window !== 'undefined' && window.jsQR) return Promise.resolve(window.jsQR);
  return new Promise((resolve) => {
    if (typeof document === 'undefined') return resolve(null);
    const existing = document.getElementById('jsqr-cdn-script');
    if (existing) {
      if (window.jsQR) return resolve(window.jsQR);
      existing.addEventListener('load', () => resolve(window.jsQR));
      return;
    }
    const script = document.createElement('script');
    script.id = 'jsqr-cdn-script';
    script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
    script.onload = () => resolve(window.jsQR);
    script.onerror = () => resolve(null);
    document.head.appendChild(script);
  });
};

const decodeQrFromCanvas = (ctx, width, height) => {
  try {
    if (typeof window === 'undefined' || !window.jsQR) return null;
    const imageData = ctx.getImageData(0, 0, width, height);
    const code = window.jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: 'attemptBoth',
    });
    return code ? code.data : null;
  } catch {
    return null;
  }
};

const setMode = (mode) => {
  scanMode.value = mode;
  scanError.value = '';
  if (mode !== 'camera') {
    stopCamera();
  } else {
    startCamera();
  }
};

const playChime = () => {
  if (!soundEnabled.value) return;
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
    osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.15); // A6
    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.25);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.25);
  } catch {}
};

const startCamera = async () => {
  if (isCameraActive.value) return;
  isInitializing.value = true;
  scanError.value = '';

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: currentFacingMode,
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
    });

    if (videoEl.value) {
      videoEl.value.srcObject = stream;
      await videoEl.value.play();
      isCameraActive.value = true;
      startScanLoop();
    }
  } catch (err) {
    console.error('Camera initialization failed:', err);
    scanError.value = 'Could not access webcam. Please check browser permissions or switch to Manual Entry.';
  } finally {
    isInitializing.value = false;
  }
};

const stopCamera = () => {
  if (scanInterval) {
    clearInterval(scanInterval);
    scanInterval = null;
  }
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }
  if (videoEl.value) {
    videoEl.value.srcObject = null;
  }
  isCameraActive.value = false;
};

const switchCamera = async () => {
  stopCamera();
  currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
  await startCamera();
};

const startScanLoop = () => {
  if (scanInterval) clearInterval(scanInterval);

  const canvas = canvasEl.value || document.createElement('canvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true });

  scanInterval = setInterval(async () => {
    if (!videoEl.value || !isCameraActive.value || isVerifying.value) return;
    if (videoEl.value.readyState < (videoEl.value.HAVE_CURRENT_DATA || 2)) return;

    const vw = videoEl.value.videoWidth;
    const vh = videoEl.value.videoHeight;
    if (!vw || !vh) return;

    // 1. Check BarcodeDetector API
    if ('BarcodeDetector' in window) {
      try {
        const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
        const barcodes = await detector.detect(videoEl.value);
        if (barcodes && barcodes.length > 0 && barcodes[0].rawValue) {
          onQrDetected(barcodes[0].rawValue);
          return;
        }
      } catch {}
    }

    // 2. Fallback to jsQR
    canvas.width = vw;
    canvas.height = vh;
    ctx.drawImage(videoEl.value, 0, 0, vw, vh);
    const code = decodeQrFromCanvas(ctx, vw, vh);
    if (code) {
      onQrDetected(code);
    }
  }, 200);
};

const onQrDetected = async (qrData) => {
  const now = Date.now();
  // Prevent duplicate trigger for same code within 3 seconds
  if (lastScannedCode === qrData && now - lastScanTime < 3000) return;
  lastScannedCode = qrData;
  lastScanTime = now;

  await verifyPass(qrData);
};

const verifyPass = async (payloadOrId) => {
  isVerifying.value = true;
  scanError.value = '';

  const token = store.token || localStorage.getItem('driven_token');

  try {
    const res = await verifyRegistrationPassApi(payloadOrId, token);
    lastResult.value = res;
    playChime();

    // Append to session log
    const reg = res.registration || {};
    const student = reg.student || {};
    const event = reg.event || {};

    scanLog.value.unshift({
      timestamp: res.scanned_at || new Date(),
      name: student.name || 'Student Member',
      student_id: student.student_id || '—',
      department: student.department || '—',
      event_name: event.name || 'Event',
      team_name: reg.team_name || 'Individual',
      status: 'Present',
    });
  } catch (err) {
    scanError.value = err.message || 'Invalid or unverified registration pass.';
    lastResult.value = null;
  } finally {
    isVerifying.value = false;
  }
};

const handleManualSubmit = () => {
  if (!manualInput.value.trim()) return;
  verifyPass(manualInput.value.trim());
};

const handleFileSelect = (e) => {
  const file = e.target.files?.[0];
  if (file) processImageFile(file);
};

const handleFileDrop = (e) => {
  isDragging.value = false;
  const file = e.dataTransfer.files?.[0];
  if (file) processImageFile(file);
};

const processImageFile = async (file) => {
  isVerifying.value = true;
  scanError.value = '';

  const img = new Image();
  const url = URL.createObjectURL(file);
  img.onload = async () => {
    try {
      // 1. Native BarcodeDetector
      if ('BarcodeDetector' in window) {
        try {
          const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
          const barcodes = await detector.detect(img);
          if (barcodes && barcodes.length > 0 && barcodes[0].rawValue) {
            URL.revokeObjectURL(url);
            await verifyPass(barcodes[0].rawValue);
            return;
          }
        } catch {}
      }

      // 2. Canvas + jsQR with full image and multi-crop passes
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      const w = img.naturalWidth || img.width;
      const h = img.naturalHeight || img.height;
      canvas.width = w;
      canvas.height = h;
      ctx.drawImage(img, 0, 0);

      // Pass 1: Full image
      let foundCode = decodeQrFromCanvas(ctx, w, h);

      // Pass 2: Center crop (if image is framed / has surrounding content)
      if (!foundCode && w > 100 && h > 100) {
        const cropCanvas = document.createElement('canvas');
        const cropCtx = cropCanvas.getContext('2d', { willReadFrequently: true });
        const cw = Math.floor(w * 0.7);
        const ch = Math.floor(h * 0.7);
        const cx = Math.floor((w - cw) / 2);
        const cy = Math.floor((h - ch) / 2);
        cropCanvas.width = cw;
        cropCanvas.height = ch;
        cropCtx.drawImage(img, cx, cy, cw, ch, 0, 0, cw, ch);
        foundCode = decodeQrFromCanvas(cropCtx, cw, ch);
      }

      // Pass 3: Downscaled image (for very high-res camera photos)
      if (!foundCode && Math.max(w, h) > 800) {
        const scaleCanvas = document.createElement('canvas');
        const scaleCtx = scaleCanvas.getContext('2d', { willReadFrequently: true });
        const scale = 600 / Math.max(w, h);
        const sw = Math.floor(w * scale);
        const sh = Math.floor(h * scale);
        scaleCanvas.width = sw;
        scaleCanvas.height = sh;
        scaleCtx.drawImage(img, 0, 0, sw, sh);
        foundCode = decodeQrFromCanvas(scaleCtx, sw, sh);
      }

      URL.revokeObjectURL(url);

      if (foundCode) {
        await verifyPass(foundCode);
      } else {
        scanError.value = 'No QR code detected in the uploaded image. Please ensure the QR code is clear.';
        isVerifying.value = false;
      }
    } catch (err) {
      URL.revokeObjectURL(url);
      scanError.value = 'Failed to process image: ' + (err.message || err);
      isVerifying.value = false;
    }
  };
  img.onerror = () => {
    URL.revokeObjectURL(url);
    scanError.value = 'Failed to load image file.';
    isVerifying.value = false;
  };
  img.src = url;
};

const formatDepartment = (dept) => {
  if (!dept) return '—';
  return String(dept).replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
};

const formatVenue = (v) => {
  if (!v) return 'Campus Lab';
  return String(v).replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
};

const formatDate = (d) => {
  if (!d) return 'TBD';
  try {
    const dateObj = new Date(d);
    if (!isNaN(dateObj.getTime())) {
      return `${dateObj.getDate()} ${dateObj.toLocaleDateString('en-US', { month: 'short' })} ${dateObj.getFullYear()}`;
    }
  } catch {}
  return d;
};

const formatTime = (t) => {
  if (!t) return '';
  const d = new Date(t);
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

const getInitials = (name) => {
  if (!name) return 'ST';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
};

onMounted(() => {
  loadJsQrScript();
  startCamera();
});

onUnmounted(() => {
  stopCamera();
});
</script>

<style scoped>
.las-container {
  animation: lasFadeIn 0.3s ease;
}

.las-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.las-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0;
}

.las-subtitle {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0.2rem 0 0;
}

.las-tabs {
  display: flex;
  background: rgba(18, 27, 48, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}

.las-tab-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.45rem 0.95rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.las-tab-btn:hover {
  color: #ffffff;
}
.las-tab-btn.active {
  background: rgba(99, 102, 241, 0.25);
  color: #c7d2fe;
  border: 1px solid rgba(129, 140, 248, 0.3);
}

.las-card {
  background: rgba(15, 23, 42, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
}

.las-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  color: #f1f5f9;
}

/* Video Box & Viewfinder */
.las-video-box {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #020617;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.las-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.las-viewfinder {
  position: absolute;
  width: 220px;
  height: 220px;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.las-corner {
  position: absolute;
  width: 28px;
  height: 28px;
  border-color: #818cf8;
  border-style: solid;
}
.las-corner.tl { top: 0; left: 0; border-width: 4px 0 0 4px; border-top-left-radius: 8px; }
.las-corner.tr { top: 0; right: 0; border-width: 4px 4px 0 0; border-top-right-radius: 8px; }
.las-corner.bl { bottom: 0; left: 0; border-width: 0 0 4px 4px; border-bottom-left-radius: 8px; }
.las-corner.br { bottom: 0; right: 0; border-width: 0 4px 4px 0; border-bottom-right-radius: 8px; }

.las-laser {
  position: absolute;
  top: 0;
  left: 5%;
  width: 90%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #818cf8, #38bdf8, transparent);
  box-shadow: 0 0 12px #818cf8;
  animation: lasScanLaser 2s ease-in-out infinite;
}

.las-guide-text {
  position: absolute;
  bottom: -32px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #c7d2fe;
  background: rgba(15, 23, 42, 0.85);
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  white-space: nowrap;
}

@keyframes lasScanLaser {
  0% { top: 5%; opacity: 0.2; }
  50% { top: 90%; opacity: 1; }
  100% { top: 5%; opacity: 0.2; }
}

.las-camera-offline {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
}

.las-offline-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.las-cam-controls {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.las-btn-ctrl {
  flex: 1;
  padding: 0.55rem 0.85rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.las-btn-ctrl:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}
.las-btn-ctrl.active {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(129, 140, 248, 0.3);
  color: #c7d2fe;
}

/* Dropzone */
.las-dropzone {
  border: 2px dashed rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 3.5rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.02);
}
.las-dropzone:hover,
.las-dropzone.dragging {
  border-color: #818cf8;
  background: rgba(99, 102, 241, 0.06);
}
.las-upload-icon {
  font-size: 2.5rem;
  color: #818cf8;
  margin-bottom: 0.75rem;
}

/* Manual Entry */
.las-manual-wrap {
  padding: 1.5rem 0;
}
.las-label {
  font-size: 0.84rem;
  font-weight: 600;
  color: #cbd5e1;
  margin-bottom: 0.5rem;
  display: block;
}
.las-input-group {
  display: flex;
  gap: 0.75rem;
}
.las-input {
  flex: 1;
  background: rgba(18, 27, 48, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 0.7rem 1rem;
  font-size: 0.88rem;
  color: #f1f5f9;
  outline: none;
}
.las-input:focus {
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15);
}
.las-hint {
  font-size: 0.78rem;
  color: #64748b;
  margin-top: 0.6rem;
  display: block;
}

/* Results & Student Box */
.las-result-empty {
  padding: 3.5rem 2rem;
  text-align: center;
  color: #64748b;
}
.las-empty-icon {
  font-size: 3rem;
  color: #334155;
  margin-bottom: 0.75rem;
}

.las-status-banner {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.9rem 1.1rem;
  border-radius: 14px;
  margin-bottom: 1.25rem;
  font-size: 0.88rem;
}
.las-status-banner i { font-size: 1.4rem; }
.banner-green { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); color: #86efac; }
.banner-amber { background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); color: #fcd34d; }
.banner-red { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }

.las-student-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.las-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1rem;
}
.las-student-name { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; }
.las-student-dept { font-size: 0.8rem; color: #94a3b8; }

.las-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.las-info-item {
  display: flex;
  flex-direction: column;
}
.las-info-label { font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.las-info-val { font-size: 0.85rem; font-weight: 600; color: #e2e8f0; }

.las-event-box {
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 12px;
  padding: 1rem;
}
.las-event-title { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.4rem; }
.las-event-meta { font-size: 0.78rem; color: #94a3b8; display: flex; gap: 1rem; }

.las-time-tag { font-size: 0.75rem; color: #64748b; font-family: monospace; }

/* Table */
.las-table {
  color: #cbd5e1;
  margin: 0;
}
.las-table th {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.75rem 1rem;
}
.las-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.85rem;
}

.las-btn-primary {
  padding: 0.65rem 1.25rem;
  border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.las-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
}

.las-btn-clear {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 0.78rem;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.las-btn-clear:hover {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

@keyframes lasFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
