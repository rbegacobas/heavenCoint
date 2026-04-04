"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi, setToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.register({ email, password, full_name: fullName });
      const loginData = await authApi.login({ email, password });
      setToken(loginData.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al registrarse");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen" style={{ backgroundColor: "#1B1F3B" }}>

      {/* ── Left branding panel ── */}
      <div
        className="hidden lg:flex lg:flex-col"
        style={{ width: 640, minWidth: 640, backgroundColor: "#1E2148", padding: "48px 56px" }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center rounded-lg" style={{ width: 40, height: 40, backgroundColor: "#6366F1" }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <span style={{ color: "#FFFFFF", fontSize: 22, fontWeight: 700 }}>HeavenCoint</span>
          <span style={{ backgroundColor: "#2A2D52", color: "#A0A4B8", fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 4 }}>v2.0</span>
        </div>

        <div style={{ marginTop: 56 }}>
          <h1 style={{ color: "#FFFFFF", fontSize: 28, fontWeight: 600, lineHeight: 1.3, marginBottom: 12 }}>
            Únete a la plataforma
          </h1>
          <p style={{ color: "#A0A4B8", fontSize: 15, lineHeight: 1.6 }}>
            Crea tu cuenta gratuita y empieza a operar con herramientas cuantitativas profesionales.
          </p>
        </div>

        <div className="flex flex-col gap-4" style={{ marginTop: 48 }}>
          {[
            { label: "Análisis de activos con +50 KPIs profesionales", color: "#22C55E" },
            { label: "Osciladores NetBrute e Intenciones en tiempo real", color: "#8B5CF6" },
            { label: "Asistente IA que nunca improvisa", color: "#3B82F6" },
            { label: "Gestión de riesgo matemática integrada", color: "#F59E0B" },
          ].map(({ label, color }) => (
            <div key={label} className="flex items-center gap-3">
              <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: color, flexShrink: 0 }} />
              <span style={{ color: "#A0A4B8", fontSize: 14 }}>{label}</span>
            </div>
          ))}
        </div>

        <p style={{ color: "#A0A4B8", fontSize: 12, marginTop: "auto", paddingTop: 48 }}>
          © 2026 HeavenCoint. Todos los derechos reservados.
        </p>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex flex-1 items-center justify-center" style={{ padding: "48px 24px" }}>
        <div style={{ width: "100%", maxWidth: 420 }}>

          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2" style={{ marginBottom: 40 }}>
            <div className="flex items-center justify-center rounded-lg" style={{ width: 32, height: 32, backgroundColor: "#6366F1" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" />
              </svg>
            </div>
            <span style={{ color: "#FFFFFF", fontSize: 18, fontWeight: 700 }}>HeavenCoint</span>
          </div>

          <div style={{ marginBottom: 32 }}>
            <h2 style={{ color: "#FFFFFF", fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Crear Cuenta</h2>
            <p style={{ color: "#A0A4B8", fontSize: 14 }}>Completa tus datos para empezar a operar</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 20 }}>

            {/* Full name */}
            <div>
              <label htmlFor="fullName" style={{ display: "block", color: "#FFFFFF", fontSize: 14, fontWeight: 500, marginBottom: 8 }}>
                Nombre completo
              </label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A0A4B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                  </svg>
                </span>
                <input
                  id="fullName" type="text" placeholder="Fernando Trader"
                  value={fullName} onChange={(e) => setFullName(e.target.value)} required
                  className="hc-input" style={{ paddingLeft: 42 }}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" style={{ display: "block", color: "#FFFFFF", fontSize: 14, fontWeight: 500, marginBottom: 8 }}>
                Email
              </label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A0A4B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                </span>
                <input
                  id="email" type="email" placeholder="trader@example.com"
                  value={email} onChange={(e) => setEmail(e.target.value)} required
                  className="hc-input" style={{ paddingLeft: 42 }}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" style={{ display: "block", color: "#FFFFFF", fontSize: 14, fontWeight: 500, marginBottom: 8 }}>
                Contraseña
              </label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A0A4B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect width="18" height="11" x="3" y="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  id="password" type={showPassword ? "text" : "password"} placeholder="Mínimo 8 caracteres"
                  value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8}
                  className="hc-input" style={{ paddingLeft: 42, paddingRight: 44 }}
                />
                <button
                  type="button" onClick={() => setShowPassword(!showPassword)}
                  style={{ position: "absolute", right: 14, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", padding: 0, lineHeight: 0 }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A0A4B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    {showPassword
                      ? <><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" /><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" /><line x1="1" y1="1" x2="23" y2="23" /></>
                      : <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></>
                    }
                  </svg>
                </button>
              </div>
            </div>

            {error && (
              <div style={{ backgroundColor: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 8, padding: "10px 14px", color: "#F87171", fontSize: 13 }}>
                {error}
              </div>
            )}

            <button
              type="submit" disabled={loading}
              className="flex items-center justify-center gap-2"
              style={{ height: 50, backgroundColor: loading ? "#2A2D52" : "#6366F1", border: "none", borderRadius: 8, color: "#FFFFFF", fontSize: 15, fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", width: "100%", transition: "background-color 0.15s" }}
            >
              {loading ? (
                <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56" /></svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><line x1="19" y1="8" x2="19" y2="14" /><line x1="22" y1="11" x2="16" y2="11" />
                </svg>
              )}
              {loading ? "Creando cuenta..." : "Crear Cuenta"}
            </button>

            <p className="text-center" style={{ color: "#A0A4B8", fontSize: 14 }}>
              ¿Ya tienes cuenta?{" "}
              <Link href="/login" style={{ color: "#6366F1", fontWeight: 600, textDecoration: "none" }}>
                Iniciar sesión
              </Link>
            </p>
          </form>
        </div>
      </div>

      <style>{`
        .hc-input {
          width: 100%;
          height: 48px;
          background-color: #2A2D52;
          border: 1px solid #2A2D52;
          border-radius: 8px;
          color: #FFFFFF;
          font-size: 14px;
          padding-right: 16px;
          outline: none;
          box-sizing: border-box;
          font-family: inherit;
          transition: border-color 0.15s;
        }
        .hc-input::placeholder { color: #A0A4B8; }
        .hc-input:focus { border-color: #6366F1; }
      `}</style>
    </div>
  );
}
