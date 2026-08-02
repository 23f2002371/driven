<template>
  <Teleport to="body">
    <div class="cpm-backdrop" @click.self="$emit('close')">
      <div class="cpm-modal">
        <button class="cpm-close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        <div class="cpm-icon-wrap"><i class="bi bi-calendar-plus-fill"></i></div>
        <h2 class="cpm-title">Add Event to Calendar</h2>
        <p class="cpm-sub">Choose how you'd like to add this event.</p>
        <div class="cpm-grid">
          <button class="cpm-card" @click="pick">
            <div class="cpm-card-icon" style="background:rgba(234,67,53,0.12);color:#ea4335;">
              <i class="bi bi-google"></i>
            </div>
            <span class="cpm-card-title">Google Calendar</span>
            <span class="cpm-card-desc">Sync with your Google account</span>
          </button>
          <button class="cpm-card" @click="pick">
            <div class="cpm-card-icon" style="background:rgba(255,255,255,0.06);color:#f1f5f9;">
              <i class="bi bi-apple"></i>
            </div>
            <span class="cpm-card-title">Apple Calendar</span>
            <span class="cpm-card-desc">Add to iCloud or macOS Calendar</span>
          </button>
          <button class="cpm-card" @click="pick">
            <div class="cpm-card-icon" style="background:rgba(0,120,212,0.12);color:#0078d4;">
              <i class="bi bi-microsoft"></i>
            </div>
            <span class="cpm-card-title">Outlook</span>
            <span class="cpm-card-desc">Add to Outlook Calendar</span>
          </button>
          <button class="cpm-card" @click="pick">
            <div class="cpm-card-icon" style="background:rgba(129,140,248,0.12);color:#818cf8;">
              <i class="bi bi-download"></i>
            </div>
            <span class="cpm-card-title">Download .ics</span>
            <span class="cpm-card-desc">Get a calendar file to import manually</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
const emit = defineEmits(['close', 'selected']);

const pick = () => {
  emit('selected');
  emit('close');
};
</script>

<style scoped>
.cpm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100000;
  background: rgba(3,5,12,0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: cpmFade 0.2s ease;
}
.cpm-modal {
  position: relative;
  width: 94%;
  max-width: 440px;
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  padding: 2.5rem 2rem 2rem;
  text-align: center;
  animation: cpmSlide 0.3s cubic-bezier(0.16,1,0.3,1);
  box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 40px rgba(79,70,229,0.08);
}
.cpm-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(0,0,0,0.3);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.7rem;
}
.cpm-close:hover { background: rgba(255,255,255,0.1); color: #f1f5f9; }
.cpm-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
  border: 1px solid rgba(129,140,248,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  color: #818cf8;
}
.cpm-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0 0 0.25rem;
  letter-spacing: -0.5px;
}
.cpm-sub {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 1.5rem;
}
.cpm-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.cpm-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 1rem 0.75rem;
  border-radius: 14px;
  background: rgba(255,255,255,0.03);
  border: 1.5px solid rgba(255,255,255,0.06);
  cursor: pointer;
  transition: all 0.25s;
  font-family: inherit;
  color: inherit;
}
.cpm-card:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(129,140,248,0.2);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.cpm-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}
.cpm-card-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #e2e8f0;
}
.cpm-card-desc {
  font-size: 0.6rem;
  color: #64748b;
}
@keyframes cpmFade {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes cpmSlide {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
