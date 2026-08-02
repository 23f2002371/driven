<template>
  <div class="inv-page">
    <section class="inv-hero">
      <div class="inv-hero-bg"></div>
      <div class="inv-hero-inner">
        <div class="inv-hero-left">
          <div class="inv-hero-tag">Equipment</div>
          <h1 class="inv-hero-title">Inventory Management</h1>
          <p class="inv-hero-sub">Browse and borrow equipment available for your club events and workshops.</p>
        </div>
        <div class="inv-hero-right">
          <div class="inv-stat-card" v-for="stat in stats" :key="stat.label">
            <div class="inv-stat-icon" :style="{ background: stat.iconBg, color: stat.iconColor }">
              <i :class="'bi bi-' + stat.icon"></i>
            </div>
            <div class="inv-stat-body">
              <span class="inv-stat-value">{{ stat.value }}</span>
              <span class="inv-stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="inv-toolbar">
      <div class="inv-toolbar-left">
        <div class="inv-search-wrap">
          <i class="bi bi-search inv-search-icon"></i>
          <input v-model="searchQuery" type="text" class="inv-search-input" placeholder="Search equipment..." />
          <button v-if="searchQuery" class="inv-search-clear" @click="searchQuery = ''"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="inv-filter-group">
          <div class="inv-select-wrap">
            <i class="bi bi-tag inv-select-icon"></i>
            <select v-model="categoryFilter" class="inv-select">
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <button v-if="isAdmin" class="inv-btn-add" @click="showAddModal = true">
            <i class="bi bi-plus-lg"></i>
            <span>Add Inventory</span>
          </button>
        </div>
      </div>
      <div class="inv-toolbar-right">
        <span class="inv-result-count">{{ filteredItems.length }} items</span>
        <div class="inv-view-toggle">
          <button class="inv-view-btn" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'" title="Grid view">
            <i class="bi bi-grid-3x3-gap-fill"></i>
          </button>
          <button class="inv-view-btn" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'" title="List view">
            <i class="bi bi-list-ul"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="inv-grid" :class="viewMode">
      <div v-for="n in 6" :key="n" class="inv-card inv-skeleton">
        <div class="inv-card-image skeleton-pulse"></div>
        <div class="inv-card-body">
          <div class="skeleton-line skeleton-line-title"></div>
          <div class="skeleton-line skeleton-line-desc"></div>
          <div class="skeleton-line skeleton-line-desc short"></div>
          <div class="skeleton-bar"></div>
          <div class="skeleton-actions">
            <div class="skeleton-btn"></div>
            <div class="skeleton-btn small"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="filteredItems.length > 0" class="inv-grid" :class="viewMode">
      <div
        v-for="(item, index) in filteredItems"
        :key="item.id"
        class="inv-card"
        :class="{ 'inv-card-highlight': highlightedId === item.id }"
        :style="{ animationDelay: `${index * 0.06}s` }"
        @mouseenter="hoveredId = item.id"
        @mouseleave="hoveredId = null"
      >
        <div class="inv-card-image">
          <img :src="item.image" :alt="item.name" loading="lazy" />
          <div class="inv-card-image-overlay">
            <span class="inv-card-badge">{{ item.category }}</span>
            <span class="inv-card-avail-badge" :class="availBadgeClass(item)">
              <span class="inv-avail-dot" :class="availDotClass(item)"></span>
              {{ availLabel(item) }}
            </span>
          </div>
          <div class="inv-card-image-gradient"></div>
        </div>
        <div class="inv-card-body">
          <h3 class="inv-card-title">{{ item.name }}</h3>
          <p class="inv-card-desc">{{ item.description }}</p>
          <div class="inv-card-metrics">
            <div class="inv-metric">
              <span class="inv-metric-value">{{ item.available }}</span>
              <span class="inv-metric-label">Available</span>
            </div>
            <div class="inv-metric">
              <span class="inv-metric-value">{{ totalForItem(item) }}</span>
              <span class="inv-metric-label">Total</span>
            </div>
            <div class="inv-metric">
              <span class="inv-metric-value">{{ item.borrowed }}</span>
              <span class="inv-metric-label">Borrowed</span>
            </div>
          </div>
          <div class="inv-card-actions">
            <button
              v-if="isAdmin"
              class="inv-btn-borrow inv-btn-add"
              @click="openPanel(item, 'details')"
            >
              <span class="inv-btn-borrow-text">Add Stock</span>
              <i class="bi bi-plus-lg inv-btn-borrow-icon"></i>
            </button>
            <button
              v-else
              class="inv-btn-borrow"
              :disabled="item.available === 0"
              @click="openPanel(item, 'borrow')"
            >
              <span class="inv-btn-borrow-text">{{ item.available === 0 ? 'Unavailable' : 'Borrow' }}</span>
              <i class="bi bi-arrow-right inv-btn-borrow-icon"></i>
              <span v-if="item.available > 0" class="inv-btn-borrow-glow"></span>
            </button>
            <button v-if="isAdmin" class="inv-btn-details" @click="openPanel(item, 'details')">
              Quick Details
            </button>
            <button v-else class="inv-btn-return" @click="openPanel(item, 'return')">
              <i class="bi bi-arrow-return-left me-1"></i>Return
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="inv-empty">
      <div class="inv-empty-illustration">
        <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="30" y="20" width="140" height="100" rx="12" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" fill="rgba(255,255,255,0.02)"/>
          <rect x="50" y="40" width="100" height="8" rx="4" fill="rgba(255,255,255,0.06)"/>
          <rect x="50" y="56" width="70" height="8" rx="4" fill="rgba(255,255,255,0.04)"/>
          <rect x="50" y="72" width="85" height="8" rx="4" fill="rgba(255,255,255,0.04)"/>
          <rect x="50" y="88" width="40" height="8" rx="4" fill="rgba(255,255,255,0.04)"/>
          <circle cx="100" cy="140" r="20" stroke="rgba(255,255,255,0.06)" stroke-width="1.5" fill="none" stroke-dasharray="4 4"/>
          <path d="M94 140h12M100 134v12" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" stroke-linecap="round"/>
          <rect x="75" y="148" width="50" height="3" rx="1.5" fill="rgba(255,255,255,0.04)"/>
        </svg>
      </div>
      <h3 class="inv-empty-title">No equipment found</h3>
      <p class="inv-empty-text">Try adjusting your search or filter criteria to discover available equipment.</p>
      <button class="inv-empty-btn" @click="resetFilters">
        <i class="bi bi-arrow-counterclockwise me-2"></i>Reset Filters
      </button>
    </div>

    <Transition name="panel">
      <div v-if="panelItem" class="inv-panel-overlay" @click.self="closePanel">
        <div class="inv-panel">
          <button class="inv-panel-close" @click="closePanel">
            <i class="bi bi-x-lg"></i>
          </button>
          <div class="inv-panel-image">
            <img :src="panelItem.image" :alt="panelItem.name" />
            <div class="inv-panel-image-gradient"></div>
            <div class="inv-panel-image-content">
              <span class="inv-card-badge">{{ panelItem.category }}</span>
              <h2 class="inv-panel-title">{{ panelItem.name }}</h2>
            </div>
          </div>
          <div class="inv-panel-scroll">
            <div class="inv-panel-body">
              <div class="inv-panel-section">
                <h4 class="inv-panel-section-title">Description</h4>
                <p class="inv-panel-desc">{{ panelItem.description }}</p>
              </div>

              <div class="inv-panel-section">
                <h4 class="inv-panel-section-title">Specifications</h4>
                <div class="inv-panel-specs">
                  <div class="inv-panel-spec">
                    <span class="inv-spec-label">Category</span>
                    <span class="inv-spec-value">{{ panelItem.category }}</span>
                  </div>
                  <div class="inv-panel-spec">
                    <span class="inv-spec-label">Total Quantity</span>
                    <span class="inv-spec-value">{{ totalForItem(panelItem) }} units</span>
                  </div>
                  <div class="inv-panel-spec">
                    <span class="inv-spec-label">Available Now</span>
                    <span class="inv-spec-value" :class="panelItem.available > 0 ? 'text-success' : 'text-danger'">{{ panelItem.available }} units</span>
                  </div>
                  <div class="inv-panel-spec">
                    <span class="inv-spec-label">Currently Borrowed</span>
                    <span v-if="panelItem.borrowers && panelItem.borrowers.length" class="inv-spec-value inv-spec-clickable" @click="scrollToBorrowers">{{ panelItem.borrowed }} units <i class="bi bi-chevron-down ms-1" style="font-size:0.6rem;"></i></span>
                    <span v-else class="inv-spec-value">{{ panelItem.borrowed }} units</span>
                  </div>
                  <div class="inv-panel-spec">
                    <span class="inv-spec-label">Condition</span>
                    <span class="inv-spec-value"><span class="inv-cond-badge">Good</span></span>
                  </div>
                  <div class="inv-panel-spec">
                    <span class="inv-spec-label">Return Deadline</span>
                    <span class="inv-spec-value inv-deadline-value">{{ panelItem.returnDeadline || 'N/A' }}</span>
                  </div>
                </div>
              </div>

              <div class="inv-panel-section">
                <h4 class="inv-panel-section-title">Availability</h4>
                <div class="inv-avail-bar-wrapper">
                  <div class="inv-avail-bar">
                    <div class="inv-avail-bar-segment available" :style="{ flex: panelItem.available }"></div>
                    <div class="inv-avail-bar-segment borrowed" :style="{ flex: panelItem.borrowed }"></div>
                  </div>
                  <div class="inv-avail-bar-legend">
                    <span><span class="inv-legend-dot available"></span>{{ panelItem.available }} Available</span>
                    <span><span class="inv-legend-dot borrowed"></span>{{ panelItem.borrowed }} Borrowed</span>
                  </div>
                </div>
              </div>

              <div v-if="panelAction" class="inv-panel-section">
                <h4 class="inv-panel-section-title">{{ isAdmin ? 'Add Stock' : panelAction === 'borrow' ? 'Borrow' : 'Return' }} Quantity</h4>
                <div class="inv-panel-quantity">
                  <button class="inv-qty-btn" @click="panelQuantity > 1 && panelQuantity--" :disabled="panelQuantity <= 1"><i class="bi bi-dash"></i></button>
                  <span class="inv-qty-value">{{ panelQuantity }}</span>
                  <button class="inv-qty-btn" @click="panelQuantity < maxQuantity && panelQuantity++" :disabled="panelQuantity >= maxQuantity"><i class="bi bi-plus"></i></button>
                </div>
                <div class="inv-qty-hint" v-if="!isAdmin">{{ panelAction === 'borrow' ? panelItem.available : panelItem.borrowed }} unit{{ (panelAction === 'borrow' ? panelItem.available : panelItem.borrowed) !== 1 ? 's' : '' }} available</div>
              </div>

              <button
                v-if="!panelAction"
                class="inv-panel-borrow-btn"
                :class="{ 'inv-btn-add': isAdmin }"
                @click="handleAddStock(panelItem, 1)"
              >
                <i class="bi bi-plus-circle-fill me-2"></i>
                Add Stock +1
                <i class="bi bi-arrow-right ms-2"></i>
              </button>
              <button
                v-else-if="panelAction === 'borrow'"
                class="inv-panel-borrow-btn"
                :disabled="panelItem.available === 0"
                @click="confirmPanelAction"
              >
                <i class="bi bi-box-seam-fill me-2"></i>
                {{ panelItem.available === 0 ? 'Unavailable' : `Borrow ${panelQuantity} Unit${panelQuantity > 1 ? 's' : ''}` }}
                <i class="bi bi-arrow-right ms-2"></i>
              </button>
              <button
                v-else-if="isAdmin"
                class="inv-panel-borrow-btn inv-btn-add"
                @click="handleAddStock(panelItem, panelQuantity)"
              >
                <i class="bi bi-check-circle-fill me-2"></i>
                Save{{ panelQuantity > 1 ? ' ' + panelQuantity : '' }}
                <i class="bi bi-arrow-right ms-2"></i>
              </button>
              <button
                v-else
                class="inv-panel-borrow-btn inv-panel-return-btn"
                :disabled="panelItem.borrowed === 0"
                @click="confirmPanelAction"
              >
                <i class="bi bi-arrow-return-left me-2"></i>
                {{ panelItem.borrowed === 0 ? 'Nothing to Return' : `Return ${panelQuantity} Unit${panelQuantity > 1 ? 's' : ''}` }}
                <i class="bi bi-arrow-right ms-2"></i>
              </button>

              <div v-if="panelItem.borrowers && panelItem.borrowers.length" ref="borrowerSectionRef" class="inv-panel-section inv-borrower-section">
                <h4 class="inv-panel-section-title">Currently Borrowed By</h4>
                <div class="inv-borrower-list">
                  <div v-for="(b, i) in panelItem.borrowers" :key="i" class="inv-borrower-row">
                    <div class="inv-borrower-avatar">{{ b.name.charAt(0) }}{{ b.name.split(' ')[1]?.charAt(0) || '' }}</div>
                    <div class="inv-borrower-info">
                      <span class="inv-borrower-name">{{ b.name }}</span>
                      <span class="inv-borrower-email">{{ b.email }}</span>
                    </div>
                    <span class="inv-borrower-qty">{{ b.qty }} unit{{ b.qty > 1 ? 's' : '' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="modal">
      <div v-if="showAddModal" class="inv-modal-overlay" @click.self="closeAddModal">
        <div class="inv-modal">
          <div class="inv-modal-header">
            <div>
              <h2 class="inv-modal-title">Add New Inventory Item</h2>
              <p class="inv-modal-sub">Register new equipment that can be borrowed for club events.</p>
            </div>
            <button class="inv-modal-close" @click="closeAddModal"><i class="bi bi-x-lg"></i></button>
          </div>

          <div class="inv-modal-body">
            <div class="inv-modal-form">
              <div class="inv-form-section" data-idx="0">
                <h4 class="inv-form-section-title">Basic Information</h4>
                <div class="inv-form-row">
                  <div class="inv-form-group" :class="{ 'has-error': formErrors.name && formTouched.name }">
                    <label class="inv-form-label">Equipment Name <span class="required">*</span></label>
                    <input v-model="addForm.name" type="text" class="inv-form-input" placeholder="e.g. Arduino Uno R3" @blur="touchField('name')" />
                    <span v-if="formErrors.name && formTouched.name" class="inv-form-error">{{ formErrors.name }}</span>
                  </div>
                  <div class="inv-form-group" :class="{ 'has-error': formErrors.category && formTouched.category }">
                    <label class="inv-form-label">Category <span class="required">*</span></label>
                    <div class="inv-form-combo-wrap">
                      <input v-model="addForm.category" type="text" class="inv-form-input" list="cat-list" placeholder="Select or type..." @blur="touchField('category')" />
                      <i class="bi bi-chevron-down inv-form-combo-arrow"></i>
                    </div>
                    <datalist id="cat-list">
                      <option v-for="cat in existingCategories" :key="cat" :value="cat" />
                    </datalist>
                    <span v-if="formErrors.category && formTouched.category" class="inv-form-error">{{ formErrors.category }}</span>
                  </div>
                </div>
                <div class="inv-form-group" :class="{ 'has-error': formErrors.description && formTouched.description }">
                  <label class="inv-form-label">Description <span class="required">*</span></label>
                  <textarea v-model="addForm.description" class="inv-form-textarea" rows="3" placeholder="Describe the equipment and its typical use cases..." @blur="touchField('description')"></textarea>
                  <span v-if="formErrors.description && formTouched.description" class="inv-form-error">{{ formErrors.description }}</span>
                </div>
              </div>

              <div class="inv-form-section" data-idx="1">
                <h4 class="inv-form-section-title">Inventory Details</h4>
                <div class="inv-form-row three">
                  <div class="inv-form-group">
                    <label class="inv-form-label">Total Quantity</label>
                    <div class="inv-stepper">
                      <button class="inv-step-btn" @click="addForm.totalQuantity > 1 && addForm.totalQuantity--" :disabled="addForm.totalQuantity <= 1"><i class="bi bi-dash"></i></button>
                      <span class="inv-step-value">{{ addForm.totalQuantity }}</span>
                      <button class="inv-step-btn" @click="addForm.totalQuantity++"><i class="bi bi-plus"></i></button>
                    </div>
                  </div>
                  <div class="inv-form-group">
                    <label class="inv-form-label">Available Quantity</label>
                    <div class="inv-stepper">
                      <button class="inv-step-btn" @click="addForm.availableQuantity > 0 && addForm.availableQuantity--" :disabled="addForm.availableQuantity <= 0"><i class="bi bi-dash"></i></button>
                      <span class="inv-step-value">{{ addForm.availableQuantity }}</span>
                      <button class="inv-step-btn" @click="addForm.availableQuantity < addForm.totalQuantity && addForm.availableQuantity++" :disabled="addForm.availableQuantity >= addForm.totalQuantity"><i class="bi bi-plus"></i></button>
                    </div>
                  </div>
                  <div class="inv-form-group">
                    <label class="inv-form-label">Condition</label>
                    <select v-model="addForm.condition" class="inv-form-input">
                      <option value="Excellent">Excellent</option>
                      <option value="Good">Good</option>
                      <option value="Maintenance">Maintenance</option>
                      <option value="Damaged">Damaged</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="inv-form-section" data-idx="2">
                <h4 class="inv-form-section-title">Location</h4>
                <div class="inv-form-row">
                  <div class="inv-form-group" :class="{ 'has-error': formErrors.storageLocation && formTouched.storageLocation }">
                    <label class="inv-form-label">Storage Location <span class="required">*</span></label>
                    <input v-model="addForm.storageLocation" type="text" class="inv-form-input" placeholder="e.g. Lab A, Shelf 3" @blur="touchField('storageLocation')" />
                    <span v-if="formErrors.storageLocation && formTouched.storageLocation" class="inv-form-error">{{ formErrors.storageLocation }}</span>
                  </div>
                  <div class="inv-form-group">
                    <label class="inv-form-label">Shelf / Room Number</label>
                    <input v-model="addForm.shelfNumber" type="text" class="inv-form-input" placeholder="Optional" />
                  </div>
                </div>
              </div>

              <div class="inv-form-section" data-idx="3">
                <h4 class="inv-form-section-title">Media</h4>
                <div class="inv-form-group">
                  <label class="inv-form-label">Equipment Image</label>
                  <div class="inv-upload-zone" @click="fileInputRef?.click()" @dragover.prevent @drop.prevent="handleFileDrop" :class="{ 'has-image': imagePreview }">
                    <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleFileUpload" />
                    <template v-if="!imagePreview">
                      <div class="inv-upload-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                      <p class="inv-upload-text">Drag & drop image or <span>Browse files</span></p>
                      <p class="inv-upload-hint">PNG, JPG, WebP &middot; Max 5MB</p>
                    </template>
                    <template v-else>
                      <img :src="imagePreview" alt="Preview" class="inv-upload-preview" />
                      <button class="inv-upload-remove" @click.stop="removeImage"><i class="bi bi-x-lg"></i></button>
                    </template>
                  </div>
                </div>
              </div>

              <div class="inv-form-section" data-idx="4">
                <h4 class="inv-form-section-title">Additional Details</h4>
                <div class="inv-form-row">
                  <div class="inv-form-group">
                    <label class="inv-form-label">Serial Number</label>
                    <input v-model="addForm.serialNumber" type="text" class="inv-form-input" placeholder="Optional" />
                  </div>
                  <div class="inv-form-group">
                    <label class="inv-form-label">Purchase Date</label>
                    <input v-model="addForm.purchaseDate" type="text" class="inv-form-input" placeholder="e.g. Jan 15, 2026" />
                  </div>
                </div>
                <div class="inv-form-group">
                  <label class="inv-form-label">Notes</label>
                  <textarea v-model="addForm.notes" class="inv-form-textarea" rows="2" placeholder="Any additional information..."></textarea>
                </div>
              </div>
            </div>

            <div class="inv-modal-preview">
              <div class="inv-preview-sticky">
                <h4 class="inv-form-section-title" style="margin-bottom: 1rem;">Preview</h4>
                <div class="inv-preview-card">
                  <div class="inv-preview-card-image">
                    <img :src="formPreviewItem.image" :alt="formPreviewItem.name" />
                    <div class="inv-preview-card-overlay">
                      <span class="inv-card-badge">{{ formPreviewItem.category }}</span>
                      <span class="inv-card-avail-badge" :class="availBadgeClass(formPreviewItem)">
                        <span class="inv-avail-dot" :class="availDotClass(formPreviewItem)"></span>
                        {{ availLabel(formPreviewItem) }}
                      </span>
                    </div>
                    <div class="inv-card-image-gradient"></div>
                  </div>
                  <div class="inv-preview-card-body">
                    <h3 class="inv-card-title">{{ formPreviewItem.name }}</h3>
                    <p class="inv-card-desc">{{ formPreviewItem.description }}</p>
                    <div class="inv-card-metrics">
                      <div class="inv-metric">
                        <span class="inv-metric-value">{{ formPreviewItem.available }}</span>
                        <span class="inv-metric-label">Available</span>
                      </div>
                      <div class="inv-metric">
                        <span class="inv-metric-value">{{ addForm.totalQuantity }}</span>
                        <span class="inv-metric-label">Total</span>
                      </div>
                      <div class="inv-metric">
                        <span class="inv-metric-value">0</span>
                        <span class="inv-metric-label">Borrowed</span>
                      </div>
                    </div>
                    <div class="inv-preview-status-row">
                      <span class="inv-preview-condition">
                        <span class="inv-legend-dot" :class="conditionDotClass"></span>
                        {{ addForm.condition }}
                      </span>
                      <span v-if="addForm.storageLocation" class="inv-preview-location">
                        <i class="bi bi-geo-alt-fill me-1"></i>{{ addForm.storageLocation }}{{ addForm.shelfNumber ? ' - ' + addForm.shelfNumber : '' }}
                      </span>
                    </div>
                  </div>
                </div>
                <p class="inv-preview-hint">This preview reflects the live equipment card as it will appear in the inventory grid.</p>
              </div>
            </div>
          </div>

          <div class="inv-modal-footer">
            <div class="inv-modal-footer-left">
              <span class="inv-footer-required"><span class="required">*</span> Required fields</span>
            </div>
            <div class="inv-modal-footer-right">
              <button class="inv-btn-secondary" @click="closeAddModal">Cancel</button>
              <button class="inv-btn-secondary" @click="submitAddItem">Save as Draft</button>
              <button class="inv-btn-primary" :disabled="!isFormValid || isSubmitting" @click="submitAddItem">
                <i class="bi bi-plus-lg me-1"></i>
                {{ isSubmitting ? 'Adding...' : 'Add Inventory' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="toast">
      <div v-if="showSuccessToast" class="inv-toast">
        <i class="bi bi-check-circle-fill inv-toast-icon"></i>
        <div class="inv-toast-content">
          <strong>Equipment Added</strong>
          <span>{{ addForm.name }} has been added to inventory.</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { store } from '../../store/mockData';

const props = defineProps({
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  isAdmin: { type: Boolean, default: false }
});

const emit = defineEmits(['borrow', 'return', 'add-item', 'add-stock']);

const searchQuery = ref('');
const categoryFilter = ref('');
const viewMode = ref('grid');
const panelItem = ref(null);
const panelAction = ref(null);
const panelQuantity = ref(1);
const borrowerSectionRef = ref(null);

const scrollToBorrowers = () => {
  if (borrowerSectionRef.value) {
    borrowerSectionRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};
const highlightedId = ref(null);
const hoveredId = ref(null);

const showAddModal = ref(false);
const addForm = reactive({
  name: '',
  category: '',
  description: '',
  totalQuantity: 1,
  availableQuantity: 1,
  condition: 'Good',
  storageLocation: '',
  shelfNumber: '',
  image: null,
  serialNumber: '',
  purchaseDate: '',
  notes: ''
});
const formErrors = reactive({});
const formTouched = reactive({});
const showSuccessToast = ref(false);
const imagePreview = ref(null);
const fileInputRef = ref(null);
const isSubmitting = ref(false);

const categories = computed(() => {
  const cats = new Set(props.items.map(i => i.category));
  return [...cats];
});

const totalForItem = (item) => item.available + item.borrowed;

const availabilityPercent = (item) => {
  const total = totalForItem(item);
  if (total === 0) return 0;
  return Math.round((item.available / total) * 100);
};

const availLabel = (item) => {
  if (item.available === 0) return 'Out of Stock';
  const pct = availabilityPercent(item);
  if (pct <= 25) return 'Limited';
  return 'Available';
};

const availBadgeClass = (item) => {
  if (item.available === 0) return 'badge-out';
  const pct = availabilityPercent(item);
  if (pct <= 25) return 'badge-limited';
  return 'badge-avail';
};

const availDotClass = (item) => {
  if (item.available === 0) return 'dot-out';
  const pct = availabilityPercent(item);
  if (pct <= 25) return 'dot-limited';
  return 'dot-avail';
};

const filteredItems = computed(() => {
  let result = [...props.items];

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(i =>
      i.name.toLowerCase().includes(q) ||
      i.category.toLowerCase().includes(q) ||
      i.description.toLowerCase().includes(q)
    );
  }

  if (categoryFilter.value) {
    result = result.filter(i => i.category === categoryFilter.value);
  }

  return result;
});

const stats = computed(() => [
  {
    icon: 'box-seam-fill',
    value: props.items.length,
    label: 'Total Equipment',
    iconBg: 'linear-gradient(135deg, rgba(109,93,246,0.2), rgba(139,92,246,0.1))',
    iconColor: '#818cf8'
  },
  {
    icon: 'check-circle-fill',
    value: props.items.reduce((s, i) => s + i.available, 0),
    label: 'Available Today',
    iconBg: 'linear-gradient(135deg, rgba(52,211,153,0.2), rgba(16,185,129,0.1))',
    iconColor: '#34d399'
  },
  {
    icon: 'arrow-up-circle-fill',
    value: props.items.reduce((s, i) => s + i.borrowed, 0),
    label: 'Borrowed Items',
    iconBg: 'linear-gradient(135deg, rgba(251,191,36,0.2), rgba(245,158,11,0.1))',
    iconColor: '#fbbf24'
  },
  {
    icon: 'grid-3x3-gap-fill',
    value: categories.value.length,
    label: 'Categories',
    iconBg: 'linear-gradient(135deg, rgba(244,114,182,0.2), rgba(236,72,153,0.1))',
    iconColor: '#f472b6'
  }
]);

const borrowHistory = [
  { id: 1, action: 'Borrowed by Robotics Club', date: '2 days ago', type: 'borrow' },
  { id: 2, action: 'Returned by IoT Workshop', date: '1 week ago', type: 'return' },
  { id: 3, action: 'Borrowed by AI/ML Seminar', date: '2 weeks ago', type: 'borrow' },
];

const maxQuantity = computed(() => {
  if (!panelItem.value || !panelAction.value) return 1;
  if (props.isAdmin) return 100;
  return panelAction.value === 'borrow' ? panelItem.value.available : panelItem.value.borrowed;
});

const handleBorrow = (item, quantity = 1) => {
  emit('borrow', { item, quantity });
  highlightedId.value = item.id;
  setTimeout(() => { highlightedId.value = null; }, 1500);
};

const handleReturn = (item, quantity = 1) => {
  emit('return', { item, quantity });
  highlightedId.value = item.id;
  setTimeout(() => { highlightedId.value = null; }, 1500);
};

const handleAddStock = (item, qty = 1) => {
  emit('add-stock', item, qty);
  closePanel();
  highlightedId.value = item.id;
  setTimeout(() => { highlightedId.value = null; }, 1500);
};

const openPanel = (item, action = null) => {
  panelItem.value = item;
  panelAction.value = action;
  panelQuantity.value = 1;
};

const confirmPanelAction = () => {
  if (!panelItem.value || !panelAction.value) return;
  if (panelAction.value === 'borrow') {
    handleBorrow(panelItem.value, panelQuantity.value);
  } else if (panelAction.value === 'return') {
    handleReturn(panelItem.value, panelQuantity.value);
  }
  closePanel();
};

const closePanel = () => {
  panelItem.value = null;
  panelAction.value = null;
  panelQuantity.value = 1;
};

const resetFilters = () => {
  searchQuery.value = '';
  categoryFilter.value = '';
};

/* ── Add Inventory Form Logic ── */
const conditionDotClass = computed(() => {
  const c = addForm.condition;
  if (c === 'Excellent') return 'dot-avail';
  if (c === 'Good') return 'dot-limited';
  return 'dot-out';
});

const existingCategories = computed(() => {
  const cats = new Set(props.items.map(i => i.category));
  return [...cats];
});

const formPreviewItem = computed(() => ({
  name: addForm.name || 'New Equipment',
  category: addForm.category || 'Uncategorized',
  description: addForm.description || 'Equipment description will appear here.',
  available: addForm.availableQuantity,
  borrowed: 0,
  image: imagePreview.value || 'https://images.unsplash.com/photo-1581092335397-9583eb92d232?w=400&h=300&fit=crop'
}));

const requiredFields = computed(() => ['name', 'category', 'description', 'storageLocation']);

const isFormValid = computed(() => {
  return requiredFields.value.every(f => addForm[f] && addForm[f].toString().trim());
});

const validateField = (field) => {
  if (!formTouched[field]) return true;
  if (requiredFields.value.includes(field)) {
    return addForm[field] && addForm[field].toString().trim();
  }
  return true;
};

const touchField = (field) => {
  formTouched[field] = true;
  if (!validateField(field)) {
    formErrors[field] = 'This field is required';
  } else {
    delete formErrors[field];
  }
};

const handleFileUpload = (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    imagePreview.value = ev.target?.result || null;
    addForm.image = file;
  };
  reader.readAsDataURL(file);
};

const handleFileDrop = (e) => {
  e.preventDefault();
  const file = e.dataTransfer?.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    imagePreview.value = ev.target?.result || null;
    addForm.image = file;
  };
  reader.readAsDataURL(file);
};

const removeImage = () => {
  imagePreview.value = null;
  addForm.image = null;
};

const resetForm = () => {
  addForm.name = '';
  addForm.category = '';
  addForm.description = '';
  addForm.totalQuantity = 1;
  addForm.availableQuantity = 1;
  addForm.condition = 'Good';
  addForm.storageLocation = '';
  addForm.shelfNumber = '';
  addForm.image = null;
  addForm.serialNumber = '';
  addForm.purchaseDate = '';
  addForm.notes = '';
  imagePreview.value = null;
  Object.keys(formErrors).forEach(k => delete formErrors[k]);
  Object.keys(formTouched).forEach(k => delete formTouched[k]);
  isSubmitting.value = false;
};

const closeAddModal = () => {
  showAddModal.value = false;
  resetForm();
};

const submitAddItem = () => {
  Object.keys(requiredFields.value).forEach(k => touchField(requiredFields.value[k]));
  if (!isFormValid.value) return;

  isSubmitting.value = true;

  const newItem = {
    id: Date.now(),
    name: addForm.name,
    category: addForm.category,
    description: addForm.description,
    available: addForm.availableQuantity,
    borrowed: 0,
    image: imagePreview.value || `https://images.unsplash.com/photo-${1553408227 + Math.floor(Math.random() * 100)}?w=400&h=300&fit=crop`,
    condition: addForm.condition,
    location: addForm.storageLocation + (addForm.shelfNumber ? ` / ${addForm.shelfNumber}` : ''),
    serialNumber: addForm.serialNumber || null,
    purchaseDate: addForm.purchaseDate || null,
    notes: addForm.notes || null
  };

  emit('add-item', newItem);

  showSuccessToast.value = true;
  setTimeout(() => {
    showSuccessToast.value = false;
    closeAddModal();
    isSubmitting.value = false;
  }, 1200);
};
</script>

<style scoped>
.inv-page {
  position: relative;
}

/* ── Hero Section ── */
.inv-hero {
  position: relative;
  padding: 2rem 0 2.5rem;
  margin-bottom: 2.5rem;
  overflow: hidden;
}
.inv-hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 600px 400px at 70% 40%, rgba(129,140,248,0.07) 0%, transparent 65%),
    radial-gradient(ellipse 300px 300px at 30% 80%, rgba(99,102,241,0.04) 0%, transparent 70%);
}
.inv-hero-inner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 2.5rem;
  position: relative;
  z-index: 1;
}
.inv-hero-left {
  flex: 1;
  min-width: 0;
}
.inv-hero-tag {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(129,140,248,0.1);
  color: #a5b4fc;
  border: 1px solid rgba(129,140,248,0.12);
  margin-bottom: 1rem;
}
.inv-hero-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.8px;
  margin: 0 0 0.6rem;
  line-height: 1.15;
}
.inv-hero-sub {
  font-size: 0.92rem;
  color: #64748b;
  margin: 0;
  max-width: 480px;
  line-height: 1.6;
}
.inv-hero-right {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  flex-shrink: 0;
}
.inv-stat-card {
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 140px;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.inv-stat-card:hover {
  border-color: rgba(129,140,248,0.15);
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
  transform: translateY(-2px);
}
.inv-stat-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.inv-stat-body {
  display: flex;
  flex-direction: column;
}
.inv-stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.5px;
  line-height: 1.2;
}
.inv-stat-label {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
}

/* ── Toolbar ── */
.inv-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
  padding: 0.75rem 1rem;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  flex-wrap: wrap;
}
.inv-toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}
.inv-search-wrap {
  position: relative;
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}
.inv-search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #475569;
  font-size: 0.85rem;
  pointer-events: none;
}
.inv-search-input {
  width: 100%;
  padding: 0.55rem 0.85rem 0.55rem 2.3rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  color: rgba(255,255,255,0.95);
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
  transition: all 0.25s ease;
}
.inv-search-input:focus {
  border-color: rgba(129,140,248,0.3);
  box-shadow: 0 0 0 3px rgba(129,140,248,0.06);
  background: rgba(255,255,255,0.06);
}
.inv-search-input::placeholder {
  color: rgba(255,255,255,0.5);
}
.inv-search-clear {
  position: absolute;
  right: 0.65rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #475569;
  font-size: 0.6rem;
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 4px;
  transition: color 0.2s;
}
.inv-search-clear:hover { color: #94a3b8; }
.inv-filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.inv-select-wrap {
  position: relative;
}
.inv-select-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #475569;
  font-size: 0.75rem;
  pointer-events: none;
}
.inv-select {
  padding: 0.5rem 2rem 0.5rem 2rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  color: #94a3b8;
  font-size: 0.8rem;
  font-family: inherit;
  outline: none;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  transition: all 0.25s ease;
  min-width: 130px;
}
.inv-select:focus {
  border-color: rgba(129,140,248,0.3);
  box-shadow: 0 0 0 3px rgba(129,140,248,0.06);
  color: rgba(255,255,255,0.95);
}
.inv-select option {
  background: #0f172a;
  color: rgba(255,255,255,0.95);
}
.inv-toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}
.inv-result-count {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
}
.inv-view-toggle {
  display: flex;
  gap: 2px;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
  padding: 2px;
}
.inv-view-btn {
  width: 30px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  color: #475569;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.inv-view-btn.active {
  background: rgba(129,140,248,0.15);
  color: #818cf8;
}
.inv-view-btn:not(.active):hover {
  color: #94a3b8;
}

/* ── Grid Layout ── */
.inv-grid {
  display: grid;
  gap: 1.25rem;
  animation: invFadeIn 0.3s ease;
}
.inv-grid.grid {
  grid-template-columns: repeat(3, 1fr);
}
.inv-grid.list {
  grid-template-columns: 1fr;
}

/* ── Card ── */
.inv-card {
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
  opacity: 1;
  position: relative;
}
.inv-card:hover {
  transform: translateY(-6px);
  border-color: rgba(129,140,248,0.25);
  box-shadow: 0 12px 40px rgba(129,140,248,0.12), 0 4px 16px rgba(0,0,0,0.2);
  background: linear-gradient(145deg, rgba(15,23,42,0.7), rgba(30,41,59,0.6));
}
.inv-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(145deg, rgba(129,140,248,0), rgba(129,140,248,0));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  transition: all 0.4s ease;
}
.inv-card:hover::before {
  background: linear-gradient(145deg, rgba(129,140,248,0.3), rgba(139,92,246,0.1));
}
.inv-card-highlight {
  animation: cardHighlight 1.5s ease;
}
@keyframes cardHighlight {
  0%, 100% { box-shadow: 0 0 0 rgba(52,211,153,0); }
  20% { box-shadow: 0 0 24px rgba(52,211,153,0.25); border-color: rgba(52,211,153,0.3); }
  50% { box-shadow: 0 0 16px rgba(52,211,153,0.15); }
}
.inv-card-image {
  position: relative;
  height: 180px;
  overflow: hidden;
  background: rgba(0,0,0,0.3);
}
.inv-grid.list .inv-card-image {
  height: 140px;
  min-width: 220px;
}
.inv-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.4,0,0.2,1);
}
.inv-card:hover .inv-card-image img {
  transform: scale(1.06);
}
.inv-card-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.75rem;
  z-index: 2;
}
.inv-card-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  background: rgba(15,23,42,0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #cbd5e1;
  border: 1px solid rgba(255,255,255,0.08);
}
.inv-card-avail-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.inv-card-avail-badge.badge-avail {
  background: rgba(52,211,153,0.15);
  color: #34d399;
  border: 1px solid rgba(52,211,153,0.15);
}
.inv-card-avail-badge.badge-limited {
  background: rgba(251,191,36,0.15);
  color: #fbbf24;
  border: 1px solid rgba(251,191,36,0.15);
}
.inv-card-avail-badge.badge-out {
  background: rgba(244,63,94,0.15);
  color: #fb7185;
  border: 1px solid rgba(244,63,94,0.15);
}
.inv-avail-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
}
.inv-avail-dot.dot-avail { background: #34d399; box-shadow: 0 0 6px rgba(52,211,153,0.4); }
.inv-avail-dot.dot-limited { background: #fbbf24; box-shadow: 0 0 6px rgba(251,191,36,0.4); }
.inv-avail-dot.dot-out { background: #fb7185; box-shadow: 0 0 6px rgba(244,63,94,0.4); }
.inv-card-image-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60%;
  background: linear-gradient(transparent, rgba(15,23,42,0.7));
  pointer-events: none;
}
.inv-card-body {
  padding: 1rem 1.1rem 1.1rem;
}
.inv-grid.list .inv-card {
  display: flex;
}
.inv-grid.list .inv-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 1.25rem;
}
.inv-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.35rem;
  letter-spacing: -0.3px;
}
.inv-card-desc {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0 0 0.75rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.inv-card-metrics {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.65rem;
}
.inv-metric {
  display: flex;
  flex-direction: column;
}
.inv-metric-value {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
  line-height: 1.2;
}
.inv-metric-label {
  font-size: 0.62rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* ── Card Actions ── */
.inv-card-actions {
  display: flex;
  gap: 0.75rem;
}
.inv-btn-borrow {
  position: relative;
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  overflow: hidden;
}
.inv-btn-borrow:hover:not(:disabled) {
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(99,102,241,0.4);
}
.inv-btn-borrow:active:not(:disabled) {
  transform: scale(0.98);
}
.inv-btn-borrow:disabled {
  background: rgba(255,255,255,0.06);
  color: #475569;
  cursor: not-allowed;
}
.inv-btn-borrow-text {
  position: relative;
  z-index: 1;
}
.inv-btn-borrow-icon {
  position: relative;
  z-index: 1;
  font-size: 0.75rem;
  transition: transform 0.3s ease;
}
.inv-btn-borrow:hover:not(:disabled) .inv-btn-borrow-icon {
  transform: translateX(4px);
}
.inv-btn-borrow-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 10px;
}
.inv-btn-borrow:hover:not(:disabled) .inv-btn-borrow-glow {
  opacity: 1;
}
.inv-btn-add {
  background: linear-gradient(135deg, #059669, #10b981) !important;
  padding: 0.6rem 0.85rem !important;
  flex: 0 1 auto !important;
}
.inv-btn-add:hover:not(:disabled) {
  box-shadow: 0 4px 20px rgba(5, 150, 105, 0.4) !important;
}
.inv-btn-details {
  padding: 0.6rem 1rem;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  transition: all 0.25s ease;
  white-space: nowrap;
}
.inv-btn-details:hover {
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.95);
  border-color: rgba(255,255,255,0.15);
}
.inv-btn-return {
  display: inline-flex;
  align-items: center;
  padding: 0.6rem 0.85rem;
  border: 1px solid rgba(251,191,36,0.2);
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  background: rgba(251,191,36,0.08);
  color: #fbbf24;
  transition: all 0.25s ease;
  white-space: nowrap;
}
.inv-btn-return:hover {
  background: rgba(251,191,36,0.15);
  color: #fcd34d;
  border-color: rgba(251,191,36,0.35);
}

/* ── Empty State ── */
.inv-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}
.inv-empty-illustration {
  width: 160px;
  height: 160px;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}
.inv-empty-illustration svg {
  width: 100%;
  height: 100%;
}
.inv-empty-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #94a3b8;
  margin: 0 0 0.5rem;
}
.inv-empty-text {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 1.5rem;
  max-width: 360px;
  line-height: 1.5;
}
.inv-empty-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.6rem 1.4rem;
  border: 1px solid rgba(129,140,248,0.2);
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  background: rgba(129,140,248,0.08);
  color: #a5b4fc;
  transition: all 0.25s ease;
}
.inv-empty-btn:hover {
  background: rgba(129,140,248,0.15);
  border-color: rgba(129,140,248,0.3);
  transform: translateY(-2px);
}

/* ── Slide-Over Panel ── */
.inv-panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  justify-content: flex-end;
}
.inv-panel {
  width: 480px;
  max-width: 100vw;
  height: 100vh;
  background: rgba(10,15,28,0.97);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255,255,255,0.06);
  box-shadow: -8px 0 40px rgba(0,0,0,0.4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.inv-panel-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(15,23,42,0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.1);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}
.inv-panel-close:hover {
  background: rgba(244,63,94,0.15);
  color: #fb7185;
  border-color: rgba(244,63,94,0.2);
}
.inv-panel-image {
  position: relative;
  height: 260px;
  flex-shrink: 0;
  overflow: hidden;
}
.inv-panel-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.inv-panel-image-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 70%;
  background: linear-gradient(transparent, rgba(10,15,28,0.95));
  pointer-events: none;
}
.inv-panel-image-content {
  position: absolute;
  bottom: 1.25rem;
  left: 1.25rem;
  right: 1.25rem;
  z-index: 2;
}
.inv-panel-image-content .inv-card-badge {
  display: inline-block;
  margin-bottom: 0.5rem;
}
.inv-panel-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: -0.5px;
}
.inv-panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}
.inv-panel-scroll::-webkit-scrollbar {
  width: 4px;
}
.inv-panel-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.inv-panel-scroll::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.08);
  border-radius: 2px;
}
.inv-panel-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.inv-panel-section {
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.inv-panel-section:last-of-type {
  border-bottom: none;
}
.inv-panel-section-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.75rem;
}
.inv-panel-desc {
  font-size: 0.88rem;
  color: #cbd5e1;
  line-height: 1.7;
  margin: 0;
}
.inv-panel-specs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.inv-panel-spec {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.inv-spec-label {
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 500;
}
.inv-spec-value {
  font-size: 0.82rem;
  color: rgba(255,255,255,0.95);
  font-weight: 600;
}
.inv-spec-clickable {
  cursor: pointer;
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 2px;
  text-decoration-style: dotted;
  transition: color 0.2s;
}
.inv-spec-clickable:hover {
  color: #a5b4fc;
}
.inv-deadline-value {
  color: #f87171;
}
.inv-borrower-section {
  scroll-margin-top: 1rem;
}
.inv-cond-badge {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: rgba(52,211,153,0.12);
  color: #34d399;
}

/* ── Availability Bar in Panel ── */
.inv-avail-bar-wrapper {
  margin-top: 0.75rem;
}
.inv-avail-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: rgba(255,255,255,0.04);
}
.inv-avail-bar-segment.available {
  background: linear-gradient(90deg, #34d399, #10b981);
  transition: flex 0.5s ease;
}
.inv-avail-bar-segment.borrowed {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  transition: flex 0.5s ease;
}
.inv-avail-bar-legend {
  display: flex;
  gap: 1.25rem;
  margin-top: 0.5rem;
  font-size: 0.72rem;
  color: #64748b;
}
.inv-legend-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 0.35rem;
}
.inv-legend-dot.available { background: #34d399; }
.inv-legend-dot.borrowed { background: #fbbf24; }

/* ── Borrower List ── */
.inv-borrower-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.inv-borrower-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0.65rem;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
}
.inv-borrower-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(129,140,248,0.2), rgba(99,102,241,0.1));
  color: #a5b4fc;
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.inv-borrower-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.inv-borrower-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: #e2e8f0;
}
.inv-borrower-email {
  font-size: 0.65rem;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.inv-borrower-qty {
  font-size: 0.7rem;
  font-weight: 700;
  color: #fbbf24;
  flex-shrink: 0;
}

/* ── Panel Borrow History ── */
.inv-panel-history {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.inv-history-item {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}
.inv-history-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 0.35rem;
  flex-shrink: 0;
}
.inv-history-dot.borrow { background: #fbbf24; box-shadow: 0 0 6px rgba(251,191,36,0.3); }
.inv-history-dot.return { background: #34d399; box-shadow: 0 0 6px rgba(52,211,153,0.3); }
.inv-history-content {
  display: flex;
  flex-direction: column;
}
.inv-history-action {
  font-size: 0.82rem;
  color: #cbd5e1;
  font-weight: 500;
}
.inv-history-date {
  font-size: 0.7rem;
  color: #64748b;
}

/* ── Panel Borrow Button ── */
.inv-panel-borrow-btn {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.85rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  margin-top: 0.5rem;
}
.inv-panel-borrow-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99,102,241,0.4);
}
.inv-panel-borrow-btn:disabled {
  background: rgba(255,255,255,0.06);
  color: #475569;
  cursor: not-allowed;
}
.inv-panel-return-btn {
  background: linear-gradient(135deg, #d97706, #f59e0b) !important;
}
.inv-panel-return-btn:hover:not(:disabled) {
  box-shadow: 0 8px 24px rgba(217, 119, 6, 0.4) !important;
}

.inv-panel-quantity {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}
.inv-qty-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}
.inv-qty-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.1);
  border-color: rgba(129,140,248,0.3);
}
.inv-qty-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.inv-qty-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #f1f5f9;
  min-width: 2rem;
  text-align: center;
}
.inv-qty-hint {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.4);
}

/* ── Skeleton ── */
.inv-skeleton {
  pointer-events: none;
}
.skeleton-pulse {
  background: linear-gradient(90deg, rgba(255,255,255,0.02) 25%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.02) 75%);
  background-size: 200% 100%;
  animation: skeletonShimmer 1.5s ease infinite;
}
.skeleton-line {
  height: 12px;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  background: rgba(255,255,255,0.04);
}
.skeleton-line-title {
  width: 60%;
  height: 14px;
}
.skeleton-line-desc {
  width: 90%;
}
.skeleton-line-desc.short {
  width: 50%;
}
.skeleton-bar {
  height: 4px;
  border-radius: 2px;
  margin: 0.75rem 0;
  background: rgba(255,255,255,0.04);
}
.skeleton-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.skeleton-btn {
  height: 36px;
  border-radius: 10px;
  flex: 1;
  background: rgba(255,255,255,0.04);
}
.skeleton-btn.small {
  flex: 0.5;
}
@keyframes skeletonShimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* ── Animations ── */
@keyframes invFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
/* ── Panel Transition ── */
.panel-enter-active,
.panel-leave-active {
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.panel-enter-from,
.panel-leave-to {
  opacity: 0;
}
.panel-enter-from .inv-panel,
.panel-leave-to .inv-panel {
  transform: translateX(100%);
}
.panel-enter-active .inv-panel,
.panel-leave-active .inv-panel {
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
}

/* ── Add Inventory Button ── */
.inv-btn-add {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.5rem 1.1rem;
  border: none;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  box-shadow: 0 4px 16px rgba(99,102,241,0.25);
  white-space: nowrap;
}
.inv-btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(99,102,241,0.4);
}
.inv-btn-add:active {
  transform: translateY(0);
}

/* ── Add Inventory Modal ── */
.inv-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}
.inv-modal {
  width: 860px;
  max-width: 100vw;
  max-height: 90vh;
  background: rgba(10,15,28,0.97);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 24px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.inv-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  flex-shrink: 0;
}
.inv-modal-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0 0 0.25rem;
  letter-spacing: -0.5px;
}
.inv-modal-sub {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0;
}
.inv-modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.7rem;
  flex-shrink: 0;
  transition: all 0.2s ease;
}
.inv-modal-close:hover {
  background: rgba(244,63,94,0.12);
  color: #fb7185;
  border-color: rgba(244,63,94,0.2);
}
.inv-modal-body {
  display: flex;
  gap: 2rem;
  padding: 1.5rem 2rem;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}
.inv-modal-body::-webkit-scrollbar {
  width: 4px;
}
.inv-modal-body::-webkit-scrollbar-track {
  background: transparent;
}
.inv-modal-body::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.08);
  border-radius: 2px;
}
.inv-modal-form {
  flex: 1;
  min-width: 0;
}
.inv-modal-preview {
  width: 280px;
  flex-shrink: 0;
}
.inv-preview-sticky {
  position: sticky;
  top: 0;
}
.inv-preview-card {
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.inv-preview-card-image {
  position: relative;
  height: 140px;
  overflow: hidden;
  background: rgba(0,0,0,0.3);
}
.inv-preview-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.inv-preview-card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.65rem;
  z-index: 2;
}
.inv-preview-card-body {
  padding: 0.85rem;
}
.inv-preview-status-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
  font-size: 0.72rem;
  color: #64748b;
}
.inv-preview-condition {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.inv-preview-location {
  display: flex;
  align-items: center;
}
.inv-preview-hint {
  font-size: 0.7rem;
  color: rgba(255,255,255,0.4);
  margin: 0.75rem 0 0;
  line-height: 1.4;
}

/* ── Modal Form ── */
.inv-form-section {
  animation: invFormFade 0.4s ease both;
}
.inv-form-section:nth-child(1) { animation-delay: 0s; }
.inv-form-section:nth-child(2) { animation-delay: 0.08s; }
.inv-form-section:nth-child(3) { animation-delay: 0.16s; }
.inv-form-section:nth-child(4) { animation-delay: 0.24s; }
.inv-form-section:nth-child(5) { animation-delay: 0.32s; }
@keyframes invFormFade {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.inv-form-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.inv-form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}
.inv-form-section-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 1rem;
}
.inv-form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.inv-form-row.three {
  grid-template-columns: 1fr 1fr 1fr;
}
.inv-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.inv-form-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
}
.required {
  color: #fb7185;
}
.inv-form-input {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  color: rgba(255,255,255,0.95);
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  box-sizing: border-box;
}
.inv-form-input:focus {
  border-color: rgba(129,140,248,0.35);
  box-shadow: 0 0 0 3px rgba(129,140,248,0.06);
  background: rgba(255,255,255,0.06);
}
.inv-form-input::placeholder {
  color: rgba(255,255,255,0.5);
}
select.inv-form-input { appearance: none; -webkit-appearance: none; padding-right: 2rem; cursor: pointer; }
select.inv-form-input option { background: #0f172a; color: #e2e8f0; }
.has-error .inv-form-input {
  border-color: rgba(244,63,94,0.3);
  box-shadow: 0 0 0 3px rgba(244,63,94,0.06);
}
.inv-form-error {
  font-size: 0.7rem;
  color: #fb7185;
  font-weight: 500;
}
.inv-form-combo-wrap {
  position: relative;
}
.inv-form-combo-arrow {
  position: absolute;
  right: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #475569;
  font-size: 0.65rem;
  pointer-events: none;
}
.inv-form-textarea {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  color: rgba(255,255,255,0.95);
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
  transition: all 0.25s ease;
  resize: vertical;
  min-height: 60px;
  box-sizing: border-box;
  line-height: 1.5;
}
.inv-form-textarea:focus {
  border-color: rgba(129,140,248,0.35);
  box-shadow: 0 0 0 3px rgba(129,140,248,0.06);
  background: rgba(255,255,255,0.06);
}
.inv-form-textarea::placeholder {
  color: rgba(255,255,255,0.5);
}
.has-error .inv-form-textarea {
  border-color: rgba(244,63,94,0.3);
}

/* ── Stepper ── */
.inv-stepper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 0.35rem;
}
.inv-step-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: none;
  background: rgba(255,255,255,0.06);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.7rem;
  transition: all 0.2s ease;
}
.inv-step-btn:hover:not(:disabled) {
  background: rgba(129,140,248,0.15);
  color: #818cf8;
}
.inv-step-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.inv-step-value {
  min-width: 24px;
  text-align: center;
  font-size: 0.9rem;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
}

/* ── Upload Zone ── */
.inv-upload-zone {
  border: 1.5px dashed rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
}
.inv-upload-zone:hover {
  border-color: rgba(129,140,248,0.25);
  background: rgba(129,140,248,0.03);
}
.inv-upload-zone.has-image {
  padding: 0;
  border-style: solid;
  border-color: rgba(255,255,255,0.06);
  overflow: hidden;
}
.inv-upload-icon {
  font-size: 1.5rem;
  color: #475569;
  margin-bottom: 0.5rem;
}
.inv-upload-text {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0 0 0.25rem;
}
.inv-upload-text span {
  color: #818cf8;
  font-weight: 600;
}
.inv-upload-hint {
  font-size: 0.7rem;
  color: rgba(255,255,255,0.4);
  margin: 0;
}
.inv-upload-preview {
  width: 100%;
  max-height: 140px;
  object-fit: cover;
  display: block;
}
.inv-upload-remove {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(15,23,42,0.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.1);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.6rem;
  transition: all 0.2s ease;
}
.inv-upload-remove:hover {
  background: rgba(244,63,94,0.15);
  color: #fb7185;
}

/* ── Modal Footer ── */
.inv-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 2rem;
  border-top: 1px solid rgba(255,255,255,0.05);
  flex-shrink: 0;
  background: rgba(10,15,28,0.5);
}
.inv-modal-footer-left {
  font-size: 0.72rem;
  color: #475569;
}
.inv-modal-footer-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.inv-btn-secondary {
  padding: 0.55rem 1.2rem;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  transition: all 0.25s ease;
}
.inv-btn-secondary:hover {
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.95);
  border-color: rgba(255,255,255,0.15);
}
.inv-btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 0.55rem 1.4rem;
  border: none;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  box-shadow: 0 4px 16px rgba(99,102,241,0.25);
}
.inv-btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(99,102,241,0.35);
}
.inv-btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* ── Success Toast ── */
.inv-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 5000;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  background: rgba(15,23,42,0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(52,211,153,0.2);
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.inv-toast-icon {
  font-size: 1.2rem;
  color: #34d399;
}
.inv-toast-content {
  display: flex;
  flex-direction: column;
}
.inv-toast-content strong {
  font-size: 0.85rem;
  color: #f1f5f9;
  font-weight: 700;
}
.inv-toast-content span {
  font-size: 0.75rem;
  color: #64748b;
}

/* ── Modal Transition ── */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .inv-modal,
.modal-leave-to .inv-modal {
  transform: scale(0.95) translateY(10px);
}
.modal-enter-active .inv-modal,
.modal-leave-active .inv-modal {
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
}

/* ── Toast Transition ── */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(16px);
}

/* ── Responsive ── */
@media (max-width: 1200px) {
  .inv-grid.grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 992px) {
  .inv-hero-inner { flex-direction: column; }
  .inv-hero-right { width: 100%; }
  .inv-grid.grid { grid-template-columns: repeat(2, 1fr); }
  .inv-panel { width: 100%; }
}
@media (max-width: 768px) {
  .inv-grid.grid { grid-template-columns: 1fr; }
  .inv-grid.list .inv-card { flex-direction: column; }
  .inv-grid.list .inv-card-image { min-width: 0; width: 100%; }
  .inv-toolbar-left { flex-direction: column; align-items: stretch; }
  .inv-search-wrap { max-width: none; }
  .inv-filter-group { flex-direction: column; }
  .inv-select { width: 100%; }
}
</style>
