<template>
  <div class="cc-card" @click="$emit('view', cert)">
    <div class="cc-thumb">
      <div class="cc-thumb-img" :style="{ backgroundImage: `url(${cert.image})` }"></div>
      <div class="cc-thumb-overlay"></div>
      <div class="cc-thumb-content">
        <div class="cc-seal"><i class="bi bi-award-fill"></i></div>
        <div class="cc-thumb-text">
          <span class="cc-thumb-label">Certificate of {{ cert.type }}</span>
          <span class="cc-thumb-name">{{ cert.eventName }}</span>
        </div>
      </div>
    </div>
    <div class="cc-body">
      <div class="cc-header">
        <h4 class="cc-title">{{ cert.eventName }}</h4>
        <span class="cc-badge" :class="'cc-badge--' + cert.type.toLowerCase()">{{ cert.type }}</span>
      </div>
      <div class="cc-meta">
        <span><i class="bi bi-calendar3"></i>{{ cert.issueDate }}</span>
        <span><i class="bi bi-building"></i>{{ cert.organizer }}</span>
      </div>
      <div class="cc-status-wrap">
        <span class="cc-status-dot"></span>
        <span>Available</span>
      </div>
      <div class="cc-actions">
        <button class="cc-btn cc-btn-primary" @click.stop="$emit('view', cert)"><i class="bi bi-eye"></i> View</button>
        <button class="cc-btn" @click.stop="$emit('download', cert)"><i class="bi bi-download"></i> Download</button>
        <button class="cc-btn" @click.stop="$emit('share', cert)"><i class="bi bi-share"></i> Share</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ cert: { type: Object, required: true } });
defineEmits(['view', 'download', 'share']);
</script>

<style scoped>
.cc-card {
  position: relative;
  z-index: 1;
  transform: translateZ(0);
  background: rgba(15,23,42,0.6);
  border: 1.5px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.cc-card:hover {
  transform: translateY(-6px) translateZ(0);
  border-color: rgba(129,140,248,0.2);
  box-shadow: 0 12px 40px rgba(0,0,0,0.2), 0 0 30px rgba(79,70,229,0.05);
}

.cc-thumb {
  position: relative;
  height: 130px;
  border-radius: 18px 18px 0 0;
  overflow: hidden;
}
.cc-thumb-img {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  transition: transform 0.5s cubic-bezier(0.4,0,0.2,1);
}
.cc-card:hover .cc-thumb-img { transform: scale(1.05); }
.cc-thumb-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(79,70,229,0.1) 0%, rgba(7,11,20,0.85) 100%);
}
.cc-thumb-content {
  position: absolute; inset: 0;
  display: flex; align-items: flex-end; gap: 0.65rem;
  padding: 0.85rem;
}
.cc-seal {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 1rem; flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(79,70,229,0.3);
}
.cc-thumb-text { display: flex; flex-direction: column; min-width: 0; }
.cc-thumb-label {
  font-size: 0.55rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; color: #a5b4fc;
}
.cc-thumb-name {
  font-size: 0.8rem; font-weight: 700; color: #f1f5f9;
}

.cc-body {
  position: relative;
  z-index: 1;
  padding: 0.75rem;
  flex: 1;
}
.cc-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 0.5rem; margin-bottom: 0.5rem;
}
.cc-title {
  font-size: 0.88rem; font-weight: 700; color: #f1f5f9;
  margin: 0; line-height: 1.2;
}
.cc-badge {
  font-size: 0.55rem; font-weight: 700; text-transform: uppercase;
  padding: 0.15rem 0.5rem; border-radius: 999px;
  white-space: nowrap; flex-shrink: 0;
}
.cc-badge--participation { background: rgba(129,140,248,0.12); color: #a5b4fc; }
.cc-badge--volunteer { background: rgba(52,211,153,0.12); color: #34d399; }
.cc-badge--organizer { background: rgba(251,191,36,0.12); color: #fbbf24; }
.cc-badge--winner { background: rgba(251,113,133,0.12); color: #fb7185; }

.cc-meta {
  display: flex; gap: 0.65rem; margin-bottom: 0.5rem;
}
.cc-meta span {
  font-size: 0.65rem; color: #64748b;
  display: flex; align-items: center; gap: 0.3rem;
}
.cc-meta span i { font-size: 0.55rem; }

.cc-status-wrap {
  display: flex; align-items: center; gap: 0.35rem;
  font-size: 0.68rem; font-weight: 600; color: #34d399;
  margin-bottom: 0.65rem;
}
.cc-status-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #34d399; box-shadow: 0 0 6px rgba(52,211,153,0.4);
}

.cc-actions {
  display: flex; gap: 0.3rem; flex-wrap: wrap;
}
.cc-btn {
  padding: 0.3rem 0.55rem; border-radius: 7px;
  font-size: 0.6rem; font-weight: 600; font-family: inherit;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
  display: inline-flex; align-items: center;
}
.cc-btn:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; border-color: rgba(255,255,255,0.12); }
.cc-btn-primary { border-color: rgba(129,140,248,0.15); color: #818cf8; }
.cc-btn-primary:hover { background: rgba(129,140,248,0.1); border-color: rgba(129,140,248,0.25); color: #a5b4fc; }
</style>
