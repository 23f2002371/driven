/**
 * Frontend API client module for AI Agentic Copilot, Event Generation, and Smart Bounty Match Analysis.
 */

const PROD_API = 'https://student-club-management-backend.onrender.com/api';
const DEV_API = 'http://localhost:8000/api';

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? DEV_API : PROD_API);

function getHeaders(token) {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
}

function extractErrorMessage(data, defaultMsg = 'An AI error occurred.') {
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

export async function sendCopilotMessageApi(prompt, token) {
  const res = await fetch(`${API_BASE}/ai/copilot`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify({ prompt })
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, `Copilot request failed (${res.status})`));
  }
  return data;
}

export async function generateEventApi(prompt, token) {
  const res = await fetch(`${API_BASE}/ai/events/generate`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify({ prompt })
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, `Event generation failed (${res.status})`));
  }
  return data;
}

export async function analyzeApplicationApi(applicationId, token) {
  const res = await fetch(`${API_BASE}/ai/applications/${applicationId}/analyze`, {
    headers: getHeaders(token)
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, `Match analysis failed (${res.status})`));
  }
  return data;
}

export async function suggestEventDetailsApi(eventInfo, token) {
  const res = await fetch(`${API_BASE}/ai/events/suggest-details`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify(eventInfo)
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(extractErrorMessage(data, `Details suggestion failed (${res.status})`));
  }
  return data;
}
