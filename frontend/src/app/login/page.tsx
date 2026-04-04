"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
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
      const data = await authApi.login({ email, password });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error de autenticación");
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
        {/* Logo row */}
        <div className="flex items-center gap-3">
          <div
            className="flex items-center justify-center rounded-lg"
            style={{ width: 40, height: 40, backgroundColor: "#6366F1" }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <span style={{ color: "#FFFFFF", fontSize: 22, fontWeight: 700, letterSpacing: "-0.3px" }}>
            HeavenCoint
          </span>
          <span style={{ backgroundColor: "#2A2D52", color: "#A0A4B8", fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 4 }}>
            v2.0
          </span>
        </div>

        {/* Tagline */}
        <div style={{ marginTop: 56 }}>
          <h1 style={{ color: "#FFFFFF", fontSize: 28, fontWeight: 600, lineHeight: 1.3, marginBottom: 12 }}>
            Trading Cuantitativo Profesional
          </h1>
          <p style={{ color: "#A0A4B8", fontSize: 15, lineHeight: 1.6 }}>
            Herramientas de nivel institucional para el trader retail. Sin improvisar, con matemática pura.
          </p>
        </div>

        {/* Feature cards */}
        <div className="flex flex-col gap-4" style={{ marginTop: 48 }}>
          {[
            {
              bg: "#2E3163", iconColor: "#8B5CF6",
              title: "Osciladores Propietarios",
              desc: "NetBrute e Intenciones — flujo institucional y psicología de masa.",
              icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 3v18h18" /><path d="M18 17V9" /><path d="M13 17V5" /><path d="M8 17v-3" />
                </svg>
              ),
            },
            {
              bg: "#1A3A2A", iconColor: "#22C55E",
              title: "Gestión de Riesgo Matemática",
              desc: "Position sizing, stops dinámicos ATR y take-profits escalonados.",
              icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22C55E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <polyline points="9 12 11 14 15 10" />
                </svg>
              ),
            },
            {
              bg: "#1A2A3A", iconColor: "#3B82F6",
              title: "Asistente IA Determinista",
              desc: "Responde solo con datos reales del activo. Jamás improvisa.",
              icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="3" width="20" height="14" rx="2" /><path d="M8 21h8" /><path d="M12 17v4" />
                  <path d="M7 8h3" /><path d="M7 12h3" /><path d="M14 8h3" /><path d="M14 12h3" />
                </svg>
              ),
            },
          ].map(({ bg, title, desc, icon }) => (
            <div
              key={title}
              className="flex items-start gap-4"
              style={{ backgroundColor: "#252850", borderRadius: 12, padding: "16px 20px" }}
            >
              <div
                className="flex items-center justify-center rounded-lg flex-shrink-0"
                style={{ width: 40, height: 40, backgroundColor: bg }}
              >
                {icon}
              </div>
              <div>
                <p style={{ color: "#FFFFFF", fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{title}</p>
                <p style={{ color: "#A0A4B8", fontSize: 13, lineHeight: 1.5 }}>{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Copyright */}
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

          {/* Header */}
          <div style={{ marginBottom: 32 }}>
            <h2 style={{ color: "#FFFFFF", fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Iniciar Sesión</h2>
            <p style={{ color: "#A0A4B8", fontSize: 14 }}>Ingresa tus credenciales para acceder a la plataforma</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 20 }}>

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
                  className="hc-input"
                  style={{ paddingLeft: 42 }}
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
                  id="password" type={showPassword ? "text" : "password"} placeholder="••••••••"
                  value={password} onChange={(e) => setPassword(e.target.value)} required
                  className="hc-input"
                  style={{ paddingLeft: 42, paddingRight: 44 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: "absolute", right: 14, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", padding: 0, lineHeight: 0 }}
                >
                  {showPassword ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A0A4B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A0A4B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Forgot */}
            <div className="flex justify-end" style={{ marginTop: -8 }}>
              <button type="button" style={{ color: "#6366F1", fontSize: 13, background: "none", border: "none", cursor: "pointer", padding: 0 }}>
                ¿Olvidaste tu contraseña?
              </button>
            </div>

            {/* Error */}
            {error && (
              <div style={{ backgroundColor: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 8, padding: "10px 14px", color: "#F87171", fontSize: 13 }}>
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit" disabled={loading}
              className="flex items-center justify-center gap-2"
              style={{
                height: 50, backgroundColor: loading ? "#2A2D52" : "#6366F1",
                border: "none", borderRadius: 8, color: "#FFFFFF",
                fontSize: 15, fontWeight: 600, cursor: loading ? "not-allowed" : "pointer",
                transition: "background-color 0.15s", width: "100%",
              }}
            >
              {loading ? (
                <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                  <polyline points="10 17 15 12 10 7" /><line x1="15" y1="12" x2="3" y2="12" />
                </svg>
              )}
              {loading ? "Ingresando..." : "Iniciar Sesión"}
            </button>

            {/* Divider */}
            <div className="flex items-center gap-3">
              <div style={{ flex: 1, height: 1, backgroundColor: "#2A2D52" }} />
              <span style={{ color: "#A0A4B8", fontSize: 12, whiteSpace: "nowrap" }}>o continúa con</span>
              <div style={{ flex: 1, height: 1, backgroundColor: "#2A2D52" }} />
            </div>

            {/* Social */}
            <div className="flex gap-3">
              {[
                {
                  label: "Google",
                  icon: (
                    <svg width="16" height="16" viewBox="0 0 24 24">
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                    </svg>
                  ),
                },
                {
                  label: "GitHub",
                  icon: (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#FFFFFF">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                  ),
                },
              ].map(({ label, icon }) => (
                <button
                  key={label} type="button"
                  className="flex flex-1 items-center justify-center gap-2"
                  style={{ height: 48, backgroundColor: "#2A2D52", border: "1px solid #2A2D52", borderRadius: 8, color: "#FFFFFF", fontSize: 14, fontWeight: 500, cursor: "pointer" }}
                >
                  {icon}
                  {label}
                </button>
              ))}
            </div>

            {/* Register link */}
            <p className="text-center" style={{ color: "#A0A4B8", fontSize: 14 }}>
              ¿No tienes cuenta?{" "}
              <Link href="/register" style={{ color: "#6366F1", fontWeight: 600, textDecoration: "none" }}>
                Regístrate aquí
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
