<template>
  <div class="las-container">
    <!-- Top Header & Mode Toggles -->
    <div class="las-header">
      <div>
        <h4 class="las-title"><i class="bi bi-qr-code-scan me-2 text-primary"></i>Equipment Pass Scanner & Checkout</h4>
        <p class="las-subtitle">Scan student equipment borrow passes via webcam or manual Pass ID to verify checkout and process returns.</p>
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
                <span class="las-guide-text">Align Equipment QR code within frame</span>
              </div>

              <!-- Camera Offline State -->
              <div v-if="!isCameraActive && !isInitializing" class="las-camera-offline">
                <div class="las-offline-icon">
                  <i class="bi bi-camera-video-off"></i>
                </div>
                <h5>Camera is Turned Off</h5>
                <p>Click below to initialize your webcam and begin scanning student equipment passes.</p>
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
              <h5>Drop Equipment QR Code Image Here</h5>
              <p>or click to browse from your device (PNG, JPG, WebP)</p>
            </div>
          </div>

          <!-- 3. Manual Entry Input -->
          <div v-else-if="scanMode === 'manual'" class="las-manual-wrap">
            <label class="las-label">Borrow Pass ID / UUID / Code</label>
            <div class="las-input-group">
              <input
                v-model="manualInput"
                type="text"
                class="las-input"
                placeholder="e.g. BORROW-4963B821 or 4963b821-..."
                @keyup.enter="handleManualSubmit"
              />
              <button class="las-btn-primary" :disabled="isVerifying || !manualInput.trim()" @click="handleManualSubmit">
                <span v-if="isVerifying" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-search me-2"></i>Verify Pass
              </button>
            </div>
            <span class="las-hint">You can find the 8-character Pass ID or UUID on the student's digital borrow pass.</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Verification Result Card -->
      <div class="col-lg-5">
        <div class="las-card h-100">
          <div class="las-card-header">
            <h5 class="m-0"><i class="bi bi-box-seam-fill me-2 text-primary"></i>Verification Result</h5>
            <span v-if="lastResult" class="las-time-tag">{{ formatTime(lastResult.scanned_at) }}</span>
          </div>

          <!-- Processing State -->
          <div v-if="isVerifying" class="las-result-empty">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <h5>Verifying Pass...</h5>
            <p>Connecting to backend and validating equipment borrow record.</p>
          </div>

          <!-- Active Result -->
          <div v-else-if="lastResult" class="las-result-body">
            <!-- Alert Banner -->
            <div
              class="las-status-banner"
              :class="lastResult.is_overdue ? 'banner-amber' : (lastResult.valid ? 'banner-green' : 'banner-red')"
            >
              <i :class="lastResult.is_overdue ? 'bi bi-exclamation-triangle-fill' : (lastResult.valid ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill')"></i>
              <div>
                <strong>{{ lastResult.message || 'Valid Equipment Borrow Pass' }}</strong>
                <span class="d-block small">
                  {{ lastResult.is_overdue ? 'Pass is OVERDUE for return!' : 'Pass verified & ready for checkout / return.' }}
                </span>
              </div>
            </div>

            <!-- Student Profile Summary -->
            <div class="las-student-box">
              <div class="d-flex align-items-center gap-3 mb-3">
                <div class="las-avatar">{{ getInitials(lastResult.student_name) }}</div>
                <div>
                  <h5 class="las-student-name m-0">{{ lastResult.student_name || 'Student Member' }}</h5>
                  <span class="las-student-dept">{{ lastResult.student_email || 'Verified Student' }}</span>
                </div>
              </div>

              <div class="las-info-grid">
                <div class="las-info-item">
                  <span class="las-info-label">Roll Number</span>
                  <span class="las-info-val">{{ lastResult.student_roll_number || '—' }}</span>
                </div>
                <div class="las-info-item">
                  <span class="las-info-label">Quantity</span>
                  <span class="badge bg-primary text-light px-2 py-1">{{ lastResult.borrowed_quantity }} Unit(s)</span>
                </div>
                <div class="las-info-item">
                  <span class="las-info-label">Pass ID</span>
                  <span class="las-info-val text-info font-monospace">{{ lastResult.pass_id_code }}</span>
                </div>
                <div class="las-info-item">
                  <span class="las-info-label">Return Due</span>
                  <span class="las-info-val" :class="lastResult.is_overdue ? 'text-danger fw-bold' : 'text-warning fw-bold'">
                    {{ formatDate(lastResult.return_date) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Equipment Details Box -->
            <div class="las-event-box">
              <div class="d-flex align-items-center gap-3">
                <img
                  :src="lastResult.equipment_image_url || 'https://images.unsplash.com/photo-1581092335397-9583eb92d232?w=400&h=300&fit=crop'"
                  :alt="lastResult.equipment_name"
                  class="las-item-avatar"
                />
                <div>
                  <h6 class="las-event-title m-0">{{ lastResult.equipment_name }}</h6>
                  <div class="las-event-meta mt-1">
                    <span><i class="bi bi-tag me-1"></i>{{ formatCategory(lastResult.equipment_category) }}</span>
                    <span v-if="lastResult.storage_location"><i class="bi bi-geo-alt me-1"></i>{{ lastResult.storage_location }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="d-flex gap-2 mt-3">
              <button
                class="btn btn-warning flex-fill fw-bold py-2"
                :disabled="isReturning"
                @click="handleReturnItem(lastResult.borrow_id)"
              >
                <span v-if="isReturning" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-arrow-return-left me-1"></i>
                Mark Returned & Restock
              </button>
              <button class="btn btn-success flex-fill fw-bold py-2" @click="clearResult">
                <i class="bi bi-check2-circle me-1"></i>
                Approved / Clear
              </button>
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
            <div class="text-center mt-3">
              <button class="las-btn-primary" @click="clearResult">Try Another Pass</button>
            </div>
          </div>

          <!-- Empty Initial State -->
          <div v-else class="las-result-empty">
            <div class="las-empty-icon"><i class="bi bi-upc-scan"></i></div>
            <h5>Ready for Scanning</h5>
            <p>Point camera at student QR pass or enter Pass ID on the left.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Section: Equipment Scanned Log Table -->
    <div class="las-card mt-4">
      <div class="las-card-header">
        <div>
          <h5 class="m-0"><i class="bi bi-clock-history me-2 text-primary"></i>Scanned Equipment Log</h5>
          <span class="las-subtitle">{{ scanLog.length }} pass{{ scanLog.length !== 1 ? 'es' : '' }} scanned in this session</span>
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
              <th>Roll Number</th>
              <th>Equipment</th>
              <th>Qty</th>
              <th>Pass ID</th>
              <th>Return Deadline</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in scanLog" :key="idx">
              <td class="text-secondary small">{{ formatTime(item.timestamp) }}</td>
              <td><strong>{{ item.student_name }}</strong></td>
              <td><code>{{ item.student_roll_number || '—' }}</code></td>
              <td><span class="text-info">{{ item.equipment_name }}</span></td>
              <td><span class="badge bg-primary">{{ item.borrowed_quantity }} unit(s)</span></td>
              <td><code class="text-info">{{ item.pass_id_code }}</code></td>
              <td><span class="small text-warning">{{ formatDate(item.return_date) }}</span></td>
              <td>
                <span class="badge bg-success text-light px-2 py-1"><i class="bi bi-check2 me-1"></i>Verified</span>
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
import { verifyBorrowPassApi, returnBorrowedEquipmentApi } from '../../api/inventory';

const emit = defineEmits(['equipment-returned']);

const scanMode = ref('camera');
const videoEl = ref(null);
const canvasEl = ref(null);
const fileInput = ref(null);

const isCameraActive = ref(false);
const isInitializing = ref(false);
const currentFacingMode = ref('environment');
const soundEnabled = ref(true);

const isDragging = ref(false);
const manualInput = ref('');
const isVerifying = ref(false);
const isReturning = ref(false);

const lastResult = ref(null);
const scanError = ref('');
const scanLog = ref([]);

let stream = null;
let animFrameId = null;
let jsQrInstance = null;
let lastScannedCode = '';
let scanCooldown = false;

/* ── Dynamic jsQR script loader ── */
const loadJsQr = () => {
  return new Promise((resolve, reject) => {
    if (window.jsQR) {
      jsQrInstance = window.jsQR;
      return resolve(window.jsQR);
    }
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
    script.async = true;
    script.onload = () => {
      jsQrInstance = window.jsQR;
      resolve(window.jsQR);
    };
    script.onerror = () => reject(new Error('Failed to load jsQR'));
    document.head.appendChild(script);
  });
};

const setMode = (mode) => {
  scanMode.value = mode;
  if (mode !== 'camera') {
    stopCamera();
  } else {
    startCamera();
  }
};

const playBeep = () => {
  if (!soundEnabled.value) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
    osc.start();
    osc.stop(ctx.currentTime + 0.15);
  } catch {}
};

const startCamera = async () => {
  isInitializing.value = true;
  try {
    await loadJsQr();
    const constraints = {
      video: {
        facingMode: currentFacingMode.value,
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
    };
    stream = await navigator.mediaDevices.getUserMedia(constraints);
    if (videoEl.value) {
      videoEl.value.srcObject = stream;
      await videoEl.value.play();
      isCameraActive.value = true;
      requestAnimationFrame(scanLoop);
    }
  } catch (err) {
    // Camera not granted or available
    isCameraActive.value = false;
  } finally {
    isInitializing.value = false;
  }
};

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  if (animFrameId) {
    cancelAnimationFrame(animFrameId);
    animFrameId = null;
  }
  isCameraActive.value = false;
};

const switchCamera = () => {
  currentFacingMode.value = currentFacingMode.value === 'environment' ? 'user' : 'environment';
  stopCamera();
  startCamera();
};

const scanLoop = () => {
  if (!isCameraActive.value || !videoEl.value || !canvasEl.value) return;

  if (videoEl.value.readyState === videoEl.value.HAVE_ENOUGH_DATA) {
    const canvas = canvasEl.value;
    const ctx = canvas.getContext('2d');
    canvas.width = videoEl.value.videoWidth;
    canvas.height = videoEl.value.videoHeight;
    ctx.drawImage(videoEl.value, 0, 0, canvas.width, canvas.height);

    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    if (jsQrInstance) {
      const code = jsQrInstance(imgData.data, imgData.width, imgData.height, {
        inversionAttempts: 'dontInvert',
      });

      if (code && code.data && !scanCooldown) {
        if (code.data !== lastScannedCode) {
          lastScannedCode = code.data;
          scanCooldown = true;
          playBeep();
          verifyPass(code.data);
          setTimeout(() => { scanCooldown = false; }, 2500);
        }
      }
    }
  }
  animFrameId = requestAnimationFrame(scanLoop);
};

const verifyPass = async (passCode) => {
  isVerifying.value = true;
  scanError.value = '';
  lastResult.value = null;

  try {
    const res = await verifyBorrowPassApi({ passId: passCode, qrCodeData: passCode });
    res.scanned_at = new Date();
    lastResult.value = res;
    playBeep();

    // Append to session log
    scanLog.value.unshift({
      timestamp: new Date(),
      student_name: res.student_name || 'Student Member',
      student_roll_number: res.student_roll_number || '—',
      equipment_name: res.equipment_name || 'Equipment',
      borrowed_quantity: res.borrowed_quantity || 1,
      pass_id_code: res.pass_id_code || 'BORROW-PASS',
      return_date: res.return_date,
    });
  } catch (err) {
    scanError.value = err.message || 'Invalid or unverified equipment borrow pass.';
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
  const file = e.dataTransfer?.files?.[0];
  if (file) processImageFile(file);
};

const processImageFile = async (file) => {
  isVerifying.value = true;
  scanError.value = '';
  try {
    await loadJsQr();
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = async () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const imgData = ctx.getImageData(0, 0, img.width, img.height);
      const code = jsQrInstance(imgData.data, imgData.width, imgData.height);
      URL.revokeObjectURL(url);
      if (code && code.data) {
        await verifyPass(code.data);
      } else {
        scanError.value = 'Could not find a valid QR code in the uploaded image.';
        isVerifying.value = false;
      }
    };
    img.src = url;
  } catch (err) {
    scanError.value = 'Error reading image: ' + err.message;
    isVerifying.value = false;
  }
};

const handleReturnItem = async (borrowId) => {
  if (!borrowId) return;
  isReturning.value = true;
  try {
    const res = await returnBorrowedEquipmentApi(borrowId);
    emit('equipment-returned', res);
    clearResult();
  } catch (err) {
    alert(err.message || 'Failed to return equipment');
  } finally {
    isReturning.value = false;
  }
};

const clearResult = () => {
  lastResult.value = null;
  scanError.value = '';
  manualInput.value = '';
  lastScannedCode = '';
};

const getInitials = (name) => {
  if (!name) return 'ST';
  const p = name.trim().split(/\s+/);
  return p.length >= 2 ? (p[0][0] + p[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
};

const formatTime = (d) => {
  if (!d) return '';
  const dateObj = new Date(d);
  return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
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

const formatCategory = (cat) => {
  if (!cat) return 'General';
  return String(cat).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

onMounted(() => {
  // Start camera quietly on mount if possible
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
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  color: #f1f5f9;
  font-size: 0.9rem;
}
.las-input:focus {
  outline: none;
  border-color: #818cf8;
  background: rgba(255, 255, 255, 0.07);
}
.las-hint {
  display: block;
  font-size: 0.76rem;
  color: #64748b;
  margin-top: 0.6rem;
}

/* Result Cards & Panels */
.las-result-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  color: #94a3b8;
}
.las-empty-icon {
  font-size: 3rem;
  color: #475569;
  margin-bottom: 1rem;
}
.las-status-banner {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  margin-bottom: 1.25rem;
}
.banner-green {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.25);
  color: #4ade80;
}
.banner-amber {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.25);
  color: #fbbf24;
}
.banner-red {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
}

.las-student-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.las-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #ffffff;
}
.las-student-name {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
}
.las-student-dept {
  font-size: 0.78rem;
  color: #94a3b8;
}

.las-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.las-info-item {
  display: flex;
  flex-direction: column;
}
.las-info-label {
  font-size: 0.72rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
}
.las-info-val {
  font-size: 0.86rem;
  font-weight: 600;
  color: #cbd5e1;
}

.las-event-box {
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 14px;
  padding: 0.85rem 1rem;
}
.las-item-avatar {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.las-event-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
}
.las-event-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.78rem;
  color: #94a3b8;
}

.las-time-tag {
  font-size: 0.75rem;
  font-family: monospace;
  color: #64748b;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

/* Primary Button */
.las-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 10px;
  padding: 0.65rem 1.25rem;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.las-btn-primary:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}
.las-btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.las-btn-clear {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.8rem;
  cursor: pointer;
}
.las-btn-clear:hover {
  color: #ef4444;
}

/* Log Table */
.las-table {
  color: #cbd5e1;
  margin: 0;
}
.las-table th {
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(255, 255, 255, 0.06);
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
  padding: 0.75rem 1rem;
}
.las-table td {
  border-color: rgba(255, 255, 255, 0.04);
  padding: 0.75rem 1rem;
  font-size: 0.84rem;
}

@keyframes lasFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
