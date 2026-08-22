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
  return 'Failed to process event request. Please try again.';
}

/**
 * Submit a multipart/form-data request to create a new event.
 * @param {FormData} formData
 * @param {string} token - Bearer JWT token
 */
export async function createEventApi(formData, token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/events`, {
    method: 'POST',
    headers,
    body: formData,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Fetch list of events.
 * If authenticated token is provided, fetches full private events list (with agendas, additional info, mentors).
 * Otherwise, fetches public approved events list.
 * @param {string|null} token
 */
export async function fetchEventsApi(token) {
  const endpoint = token ? `${API_BASE}/events/private` : `${API_BASE}/events`;
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const res = await fetch(endpoint, {
    headers,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return Array.isArray(data) ? data : [];
}

/**
 * Fetch a single event's private details (including agendas, additional_info, mentors).
 * @param {string} eventId
 * @param {string} token
 */
export async function getPrivateEventApi(eventId, token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/events/${eventId}/private`, {
    headers,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Fetch public event details.
 * @param {string} eventId
 */
export async function getEventApi(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}`);
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }
  return data;
}
