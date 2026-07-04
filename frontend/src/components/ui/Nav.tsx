"use client";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useState } from "react";
import { login, register } from "@/lib/api";

export default function Nav() {
  const { user, setAuth, logout } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = isLogin
        ? await login(email, password)
        : await register(email, password, name, "");
      setAuth(res.access_token, res.user);
      setShowAuth(false);
      setEmail(""); setPassword(""); setName("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <>
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">T</div>
            <Link href="/" className="text-lg font-bold tracking-tight">ThreatPulse</Link>
          </div>
          <div className="flex items-center gap-1">
            <Link href="/dashboard" className="px-3 py-1.5 text-sm text-gray-600 hover:text-blue-600 rounded-md hover:bg-gray-50">Dashboard</Link>
            <Link href="/library" className="px-3 py-1.5 text-sm text-gray-600 hover:text-blue-600 rounded-md hover:bg-gray-50">Library</Link>
            <Link href="/pricing" className="px-3 py-1.5 text-sm text-gray-600 hover:text-blue-600 rounded-md hover:bg-gray-50">Pricing</Link>
            {user ? (
              <div className="flex items-center gap-2 ml-2">
                <span className="text-xs font-mono text-gray-400 uppercase tracking-wider px-2 py-0.5 bg-gray-100 rounded">{user.tier}</span>
                <button onClick={logout} className="text-sm text-gray-500 hover:text-red-500 ml-1">Sign Out</button>
              </div>
            ) : (
              <button onClick={() => setShowAuth(true)} className="ml-2 px-4 py-1.5 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700">Sign In</button>
            )}
          </div>
        </div>
      </nav>

      {showAuth && (
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[100] flex items-center justify-center" onClick={() => setShowAuth(false)}>
          <div className="bg-white rounded-2xl p-8 w-full max-w-sm shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-xl font-bold mb-4">{isLogin ? "Sign In" : "Create Account"}</h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              {!isLogin && (
                <input type="text" placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)}
                  className="border rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
              )}
              <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required
                className="border rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
              <input type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8}
                className="border rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
              {error && <p className="text-red-500 text-xs">{error}</p>}
              <button type="submit" className="bg-blue-600 text-white rounded-lg py-2.5 font-semibold hover:bg-blue-700">{isLogin ? "Sign In" : "Create Account"}</button>
            </form>
            <p className="text-center text-sm text-gray-500 mt-4">
              {isLogin ? "No account? " : "Already have one? "}
              <button onClick={() => { setIsLogin(!isLogin); setError(""); }} className="text-blue-600 font-medium">{isLogin ? "Sign Up" : "Sign In"}</button>
            </p>
          </div>
        </div>
      )}
    </>
  );
}
