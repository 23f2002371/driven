import { store } from '../store/mockData';

const PROD_API = 'https://student-club-management-backend.onrender.com/api';
const DEV_API = 'http://localhost:8000/api';

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? DEV_API : PROD_API);

function getAuthHeaders(isFormData = false, explicitToken = null) {
  const token = explicitToken || localStorage.getItem('driven_token') || localStorage.getItem('token') || store?.token;
  const headers = {};
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

function extractErrorMessage(data) {
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    return data.detail.map(d => d?.msg || JSON.stringify(d)).join('. ');
  }
  if (typeof data?.message === 'string') return data.message;
  return 'An unexpected error occurred';
}

/**
 * Fetch all equipment from backend
 */
export async function fetchEquipmentApi(token = null) {
  const res = await fetch(`${API_BASE}/equipment`, {
    method: 'GET',
    headers: getAuthHeaders(false, token),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to fetch equipment');
  }
  return await res.json();
}

/**
 * Create a new equipment item (Club Admin only)
 * Supports FormData or JSON payload
 */
export async function createEquipmentApi(payload, token = null) {
  const isFormData = payload instanceof FormData;
  const res = await fetch(`${API_BASE}/equipment`, {
    method: 'POST',
    headers: getAuthHeaders(isFormData, token),
    body: isFormData ? payload : JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to create equipment');
  }
  return await res.json();
}

/**
 * Increase stock for existing equipment
 */
export async function increaseEquipmentStockApi(equipmentId, incrementQuantity, token = null) {
  const res = await fetch(`${API_BASE}/equipment/stock/increase`, {
    method: 'POST',
    headers: getAuthHeaders(false, token),
    body: JSON.stringify({
      equipment_id: equipmentId,
      increment_quantity: incrementQuantity,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to increase stock');
  }
  return await res.json();
}

/**
 * Borrow equipment as student (Generates QR code with 3-day deadline)
 */
export async function borrowEquipmentApi({ equipmentId, quantity = 1, returnDate = null }, token = null) {
  const payload = {
    equipment_id: equipmentId,
    borrowed_quantity: Number(quantity) || 1,
  };
  if (returnDate) {
    payload.return_date = returnDate;
  }

  const res = await fetch(`${API_BASE}/equipment/borrow`, {
    method: 'POST',
    headers: getAuthHeaders(false, token),
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to borrow equipment');
  }
  return await res.json();
}

/**
 * Fetch all active borrow details (Admin view)
 */
export async function fetchBorrowDetailsApi(token = null) {
  const res = await fetch(`${API_BASE}/equipment/borrow-details`, {
    method: 'GET',
    headers: getAuthHeaders(false, token),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to fetch borrow records');
  }
  return await res.json();
}

/**
 * Fetch my active borrow passes (Student view)
 */
export async function fetchMyBorrowDetailsApi(token = null) {
  const res = await fetch(`${API_BASE}/equipment/borrow-details/me`, {
    method: 'GET',
    headers: getAuthHeaders(false, token),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to fetch my borrow records');
  }
  return await res.json();
}

/**
 * Verify an equipment borrow pass (QR scan or typed ID)
 */
export async function verifyBorrowPassApi({ qrCodeData, passId, borrowId }, token = null) {
  const res = await fetch(`${API_BASE}/equipment/borrow/verify`, {
    method: 'POST',
    headers: getAuthHeaders(false, token),
    body: JSON.stringify({
      qr_code_data: qrCodeData || null,
      pass_id: passId || null,
      borrow_id: borrowId || null,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to verify equipment pass');
  }
  return await res.json();
}

/**
 * Return borrowed equipment back to stock
 */
export async function returnBorrowedEquipmentApi(borrowId, token = null) {
  const res = await fetch(`${API_BASE}/equipment/borrow/${borrowId}/return`, {
    method: 'POST',
    headers: getAuthHeaders(false, token),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(errorData) || 'Failed to return equipment');
  }
  return await res.json();
}
