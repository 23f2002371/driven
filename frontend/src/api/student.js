const PROD_API = 'https://student-club-management-backend.onrender.com/api';
const DEV_API = 'http://localhost:8000/api';

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? DEV_API : PROD_API);

function humanizeMsg(rawMsg, loc) {
  let msg = typeof rawMsg === 'string' ? rawMsg : '';
  if (!msg) return '';

  if (msg.startsWith('Value error, ')) {
    msg = msg.slice(13);
  }

  const field = Array.isArray(loc) && loc.length > 0 ? String(loc[loc.length - 1]) : '';
  if (field && field !== 'body') {
    const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
    if (msg.startsWith('String ')) {
      msg = `${fieldName} ${msg.slice(7)}`;
    } else if (msg === 'Field required') {
      msg = `${fieldName} is required`;
    }
  }

  return msg;
}

function extractErrorMessage(data) {
  const detail = data?.detail;
  if (typeof detail === 'string') {
    return humanizeMsg(detail);
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const formatted = detail
      .map((item) => humanizeMsg(item?.msg, item?.loc))
      .filter((msg) => typeof msg === 'string' && msg.length > 0)
      .join('. ');
    if (formatted) return formatted;
  }
  if (detail && typeof detail === 'object') {
    const msg = humanizeMsg(detail.msg, detail.loc);
    if (typeof msg === 'string' && msg.length > 0) return msg;
  }
  if (typeof data?.message === 'string') {
    return humanizeMsg(data.message);
  }
  return 'Failed to process student profile request. Please try again.';
}

/**
 * Fetch the authenticated student's profile.
 * @param {string} token
 */
export async function getMyStudentProfileApi(token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/students/me`, {
    headers,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 404) {
      return null;
    }
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Save or update the authenticated student's profile.
 * @param {object} payload
 * @param {string} token
 */
export async function saveMyStudentProfileApi(payload, token) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/students/me`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}
