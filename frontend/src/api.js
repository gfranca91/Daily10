const API_URL = import.meta.env.VITE_API_URL;

export function getToken() {
  return localStorage.getItem("daily10_token");
}

export function setToken(token) {
  localStorage.setItem("daily10_token", token);
}

export function clearToken() {
  localStorage.removeItem("daily10_token");
}

/** fetch autenticado pras rotas protegidas — inclui o token e desloga sozinho se ele expirar/for inválido. */
export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.location.reload();
    throw new Error("Sessão expirada");
  }

  return res;
}
