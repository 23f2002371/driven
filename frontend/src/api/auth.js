const PROD_API = 'https://student-club-management-backend.onrender.com/api'
const DEV_API = 'http://localhost:8000/api'

// Derive the API base the same way the backend derives its OAuth callback:
// prefer an explicit VITE_API_URL when set, otherwise use the local backend in
// dev and the deployed backend in production builds.
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? DEV_API : PROD_API)

// FastAPI error bodies vary: detail can be a plain string, an object, or an
// array of validation-error objects (422). Always reduce it to a readable string.
function humanizeMsg(rawMsg, loc) {
  let msg = typeof rawMsg === 'string' ? rawMsg : ''
  if (!msg) return ''

  if (msg.startsWith('Value error, ')) {
    msg = msg.slice(13)
  }

  const field = Array.isArray(loc) && loc.length > 0 ? String(loc[loc.length - 1]) : ''
  if (field && field !== 'body') {
    const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ')
    if (msg.startsWith('String ')) {
      msg = `${fieldName} ${msg.slice(7)}`
    } else if (msg === 'Field required') {
      msg = `${fieldName} is required`
    }
  } else if (msg.startsWith('String should have')) {
    msg = `Password ${msg.slice(7)}`
  }

  return msg
}

// FastAPI error bodies vary: detail can be a plain string, an object, or an
// array of validation-error objects (422). Always reduce it to a readable string.
function extractErrorMessage(data) {
  const detail = data?.detail
  if (typeof detail === 'string') {
    return humanizeMsg(detail)
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const formatted = detail
      .map((item) => humanizeMsg(item?.msg, item?.loc))
      .filter((msg) => typeof msg === 'string' && msg.length > 0)
      .join(' ')
    if (formatted) return formatted
  }
  if (detail && typeof detail === 'object') {
    const msg = humanizeMsg(detail.msg, detail.loc)
    if (typeof msg === 'string' && msg.length > 0) return msg
  }
  if (typeof data?.message === 'string') {
    return humanizeMsg(data.message)
  }
  return 'Something went wrong. Please try again.'
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const data = await res.json().catch(() => null)

  if (!res.ok) {
    throw new Error(extractErrorMessage(data))
  }

  return data
}

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function register(fullName, email, password) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ full_name: fullName, email, password }),
  })
}

export function me(token) {
  return request('/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
}

export function oauthLogin(provider) {
  const width = 500
  const height = 600
  const left = window.screenX + (window.outerWidth - width) / 2
  const top = window.screenY + (window.outerHeight - height) / 2
  const popup = window.open(
    `${API_BASE}/auth/${provider}/login`,
    `oauth_${provider}`,
    `width=${width},height=${height},left=${left},top=${top},menubar=no,status=no,scrollbars=yes`
  )
  if (!popup || popup.closed || typeof popup.closed === 'undefined') {
    // Fallback if popup is blocked by browser
    window.location.replace(`${API_BASE}/auth/${provider}/login`)
  }
}