const API_BASE = import.meta.env.VITE_API_BASE || ''

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    let message = ''
    let fieldErrors = null
    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      try {
        const data = await response.json()
        message = data.error || data.message || ''
        if (data.fieldErrors && typeof data.fieldErrors === 'object') {
          fieldErrors = data.fieldErrors
        }
      } catch (_) {
        // ignore parse error
      }
    }
    if (!message) {
      message = await response.text()
    }
    const error = new Error(message || `Request failed: ${response.status}`)
    if (fieldErrors) {
      error.fieldErrors = fieldErrors
    }
    throw error
  }

  return response.json()
}

export function get(path) {
  return request(path)
}

export function post(path, payload) {
  return request(path, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function patch(path, payload) {
  return request(path, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}
