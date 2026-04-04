// Auth state — token persistence in localStorage.

import { create } from "zustand";
import { setToken, clearToken } from "@/lib/api";

interface AuthState {
  isAuthenticated: boolean;
  login: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,

  login(accessToken, refreshToken) {
    setToken(accessToken);
    localStorage.setItem("hc_refresh_token", refreshToken);
    set({ isAuthenticated: true });
  },

  logout() {
    clearToken();
    set({ isAuthenticated: false });
  },

  // Called once on app mount to restore session from localStorage
  hydrate() {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("hc_access_token");
      set({ isAuthenticated: !!token });
    }
  },
}));
