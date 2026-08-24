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
  return 'Failed to process discussion request. Please try again.';
}

/**
 * Fetch all active discussion threads.
 * @param {string} token
 */
export async function fetchDiscussionThreadsApi(token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/discussion/threads`, {
    method: 'GET',
    headers,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return Array.isArray(data) ? data : [];
}

/**
 * Delete a discussion thread (Club Admin only).
 * @param {string} threadId
 * @param {string} token
 */
export async function deleteDiscussionThreadApi(threadId, token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/discussion/threads/${threadId}`, {
    method: 'DELETE',
    headers,
  });

  if (res.status === 204) {
    return true;
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return true;
}

/**
 * Fetch the discussion thread for an event.
 * @param {string} eventId
 * @param {string} token
 */
export async function getDiscussionThreadApi(eventId, token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/events/${eventId}/discussion`, {
    method: 'GET',
    headers,
  });

  if (res.status === 404) {
    return null;
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Create the single discussion thread for an event (Club Admin only).
 * @param {string} eventId
 * @param {string} title
 * @param {string} token
 */
export async function createDiscussionThreadApi(eventId, title, token) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/events/${eventId}/discussion`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ title }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Fetch all messages in a discussion thread as a nested reply tree.
 * @param {string} threadId
 * @param {string} token
 */
export async function getDiscussionMessagesApi(threadId, token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/discussion/${threadId}/messages`, {
    method: 'GET',
    headers,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return Array.isArray(data) ? data : [];
}

/**
 * Post a message (top-level or nested reply) in a discussion thread.
 * @param {string} threadId
 * @param {Object} payload - { message: string, parent_message_id?: string | null }
 * @param {string} token
 */
export async function createDiscussionMessageApi(threadId, { message, parent_message_id = null }, token) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const body = { message };
  if (parent_message_id) {
    body.parent_message_id = parent_message_id;
  }

  const res = await fetch(`${API_BASE}/discussion/${threadId}/messages`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Edit an existing message (owner only).
 * @param {string} messageId
 * @param {Object} payload - { message: string }
 * @param {string} token
 */
export async function updateDiscussionMessageApi(messageId, { message }, token) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/messages/${messageId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ message }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

/**
 * Soft-delete a discussion message (owner or Club Admin).
 * @param {string} messageId
 * @param {string} token
 */
export async function deleteDiscussionMessageApi(messageId, token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/messages/${messageId}`, {
    method: 'DELETE',
    headers,
  });

  if (res.status === 204) {
    return true;
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return true;
}
