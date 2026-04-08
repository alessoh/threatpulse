"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User } from "@/types";
import { getMe } from "@/lib/api";

interface AuthCtx {
  user: User | null;
  token: string | null;
  loading: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx>({
  user: null, token: null, loading: true,
  setAuth: () => {}, logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("tp_token");
    if (saved) {
      setToken(saved);
      getMe()
        .then((u) => setUser(u))
        .catch(() => { localStorage.removeItem("tp_token"); })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  function setAuth(t: string, u: User) {
    localStorage.setItem("tp_token", t);
    setToken(t);
    setUser(u);
  }

  function logout() {
    localStorage.removeItem("tp_token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, setAuth, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
