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
    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      try {
        const data = await response.json()
        message = data.error || data.message || ''
      } catch (_) {
        // ignore parse error
      }
    }
    if (!message) {
      message = await response.text()
    }
    throw new Error(message || `Request failed: ${response.status}`)
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
