import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Attach JWT token to every request if the user is logged in
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("tripscope_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function fetchDestinations({ q = "", sortBy = "popularity", limit = 20, offset = 0 } = {}) {
  const { data } = await apiClient.get("/destinations", {
    params: { q: q || undefined, sort_by: sortBy, limit, offset },
  });
  return data;
}

export async function fetchDestination(id) {
  const { data } = await apiClient.get(`/destinations/${id}`);
  return data;
}

export async function login(email, password) {
  const { data } = await apiClient.post("/auth/login", { email, password });
  return data;
}

export async function register(email, password) {
  const { data } = await apiClient.post("/auth/register", { email, password });
  return data;
}

export async function fetchFavorites() {
  const { data } = await apiClient.get("/favorites");
  return data;
}

export async function addFavorite(destinationId) {
  const { data } = await apiClient.post("/favorites", { destination_id: destinationId });
  return data;
}

export async function removeFavorite(destinationId) {
  await apiClient.delete(`/favorites/${destinationId}`);
}
