/**
 * Frontend API client module for Campus Bounties, Applications, Work Assignment, and Volunteering.
 */

const PROD_API = 'https://student-club-management-backend.onrender.com/api';
const DEV_API = 'http://localhost:8000/api';

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? DEV_API : PROD_API);

function getHeaders(token, isJson = true) {
  const headers = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

function extractErrorMessage(data, defaultMsg = 'An error occurred.') {
  if (!data) return defaultMsg;
  if (typeof data === 'string') return data;
  if (data.detail) {
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map(d => d.msg || JSON.stringify(d)).join(', ');
    }
  }
  if (data.message) return data.message;
  return defaultMsg;
}

/**
 * Fetch all bounties with optional status and domain filters.
 */
export async function fetchBountiesApi(params = {}, token) {
  const query = new URLSearchParams();
  if (params.status && params.status !== 'All') query.append('status', params.status);
  if (params.domain_id && params.domain_id !== 'All') query.append('domain_id', params.domain_id);

  const url = `${API_BASE}/bounties${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await fetch(url, {
    method: 'GET',
    headers: getHeaders(token, false),
  });

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch bounties.'));
  }
  return Array.isArray(data) ? data : [];
}

/**
 * Fetch a single bounty by ID.
 */
export async function fetchBountyDetailsApi(bountyId, token) {
  const res = await fetch(`${API_BASE}/bounties/${bountyId}`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch bounty details.'));
  }
  return data;
}

/**
 * Create a new bounty (Club Admin only).
 */
export async function createBountyApi(payload, token) {
  console.log('[API] Creating bounty payload:', payload);
  const headers = getHeaders(token, true);
  const res = await fetch(`${API_BASE}/bounties`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    console.error('[API] Create bounty error response:', res.status, data);
    throw new Error(extractErrorMessage(data, `Failed to create bounty (${res.status}).`));
  }
  console.log('[API] Create bounty success:', data);
  return data;
}

/**
 * Update an existing bounty (Club Admin only).
 */
export async function updateBountyApi(bountyId, payload, token) {
  const res = await fetch(`${API_BASE}/bounties/${bountyId}`, {
    method: 'PATCH',
    headers: getHeaders(token, true),
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to update bounty.'));
  }
  return data;
}

/**
 * Delete a bounty (Club Admin only).
 */
export async function deleteBountyApi(bountyId, token) {
  const res = await fetch(`${API_BASE}/bounties/${bountyId}`, {
    method: 'DELETE',
    headers: getHeaders(token, false),
  });
  if (res.status === 204) return true;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to delete bounty.'));
  }
  return true;
}

/**
 * Apply to a bounty (Student only).
 */
export async function applyToBountyApi(bountyId, payload, token) {
  const res = await fetch(`${API_BASE}/bounties/${bountyId}/applications`, {
    method: 'POST',
    headers: getHeaders(token, true),
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to submit application.'));
  }
  return data;
}

/**
 * List all applications for a bounty (Club Admin only).
 */
export async function fetchBountyApplicationsApi(bountyId, token) {
  const res = await fetch(`${API_BASE}/bounties/${bountyId}/applications`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch applicants.'));
  }
  return Array.isArray(data) ? data : [];
}

/**
 * List student's own submitted applications (Student only).
 */
export async function fetchMyApplicationsApi(token) {
  const res = await fetch(`${API_BASE}/applications/me`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch my applications.'));
  }
  return Array.isArray(data) ? data : [];
}

/**
 * Update application status (Club Admin only: accepted / rejected).
 */
export async function updateApplicationStatusApi(applicationId, status, token) {
  const res = await fetch(`${API_BASE}/applications/${applicationId}`, {
    method: 'PATCH',
    headers: getHeaders(token, true),
    body: JSON.stringify({ status }),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to update application status.'));
  }
  return data;
}

/**
 * Delete a rejected application (Student owner only).
 */
export async function deleteRejectedApplicationApi(applicationId, token) {
  const res = await fetch(`${API_BASE}/applications/${applicationId}`, {
    method: 'DELETE',
    headers: getHeaders(token, false),
  });
  if (res.status === 204) return true;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to delete application.'));
  }
  return true;
}

/**
 * Assign work to an accepted application (Club Admin only).
 */
export async function assignWorkApi(applicationId, payload, token) {
  const res = await fetch(`${API_BASE}/applications/${applicationId}/work`, {
    method: 'POST',
    headers: getHeaders(token, true),
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to assign work.'));
  }
  return data;
}

/**
 * Fetch assigned work for an application.
 */
export async function fetchAssignedWorkApi(applicationId, token) {
  const res = await fetch(`${API_BASE}/applications/${applicationId}/work`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  if (res.status === 404) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch assigned work.'));
  }
  return data;
}

/**
 * Update assigned work (Admin: full update, Student: status & deliverables progress).
 */
export async function updateAssignedWorkApi(applicationId, payload, token) {
  const res = await fetch(`${API_BASE}/applications/${applicationId}/work`, {
    method: 'PATCH',
    headers: getHeaders(token, true),
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to update work.'));
  }
  return data;
}

/**
 * Fetch student's assigned work and volunteering tasks (Student only).
 */
export async function fetchMyWorkApi(token) {
  const res = await fetch(`${API_BASE}/work/me`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch assigned tasks.'));
  }
  return Array.isArray(data) ? data : [];
}

/**
 * Fetch student's declared skills (Student only).
 */
export async function fetchMySkillsApi(token) {
  const res = await fetch(`${API_BASE}/students/me/skills`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch student skills.'));
  }
  return Array.isArray(data) ? data : [];
}

/**
 * Fetch all available domains and technologies.
 */
export async function fetchDomainsAndTechsApi(token) {
  const res = await fetch(`${API_BASE}/domains`, {
    method: 'GET',
    headers: getHeaders(token, false),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to fetch domains and technologies.'));
  }
  return Array.isArray(data) ? data : [];
}

/**
 * Upload a bounty cover image (Cloudinary).
 */
export async function uploadBountyImageApi(file, token) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/bounties/upload-image`, {
    method: 'POST',
    headers: getHeaders(token, false),
    body: formData,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, 'Failed to upload image.'));
  }
  return data?.image_url;
}

