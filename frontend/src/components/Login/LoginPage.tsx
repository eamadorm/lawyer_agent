import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Lock, Mail, ArrowRight, ArrowLeft } from 'lucide-react'
import loginBg from '../../assets/login_bg.png'
import './LoginPage.css'

type AuthMode = 'landing' | 'login' | 'register'

export const LoginPage = () => {
    const navigate = useNavigate()
    const [mode, setMode] = useState<AuthMode>('landing')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Form States
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [name, setName] = useState('')

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, hashed_password: password }),
            })
            const data = await response.json()

            if (response.ok && data.status === 'success') {
                localStorage.setItem('user_id', data.user_id)
                navigate('/chat')
            } else {
                setError(data.message || 'Error al iniciar sesión')
            }
        } catch (err) {
            setError('Error de conexión con el servidor')
        } finally {
            setIsLoading(false)
        }
    }

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch('http://localhost:8000/create_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, hashed_password: password }),
            })
            const data = await response.json()

            if (response.ok && data.user_id) {
                localStorage.setItem('user_id', data.user_id)
                navigate('/chat')
            } else {
                setError(data.message || 'Error al registrar usuario')
            }
        } catch (err) {
            setError('Error de conexión con el servidor')
        } finally {
            setIsLoading(false)
        }
    }

    const resetForm = () => {
        setError(null)
        setEmail('')
        setPassword('')
        setName('')
    }

    return (
        <div className="login-container">
            <img
                src={loginBg}
                alt="Background"
                className="login-bg-image"
            />
            <div className="login-overlay" />

            <div className="login-content">

                {/* Left Side: Branding */}
                <div className="login-branding">
                    <h1 className="login-title">
                        Bienvenido <br />
                        <span className="highlight">a ALIA</span>
                    </h1>
                    <p className="login-subtitle">
                        Tu asistente legal inteligente.<br />
                        Justicia, precisión y tecnología a tu alcance.
                    </p>
                </div>

                {/* Right Side: Interaction Area */}
                <div className="login-card">

                    {/* Landing Mode: Buttons */}
                    {mode === 'landing' && (
                        <div className="action-buttons animate-fade-in">
                            <h2 className="section-title">Comenzar</h2>

                            <button
                                onClick={() => setMode('login')}
                                className="btn btn-primary group"
                            >
                                <User className="w-6 h-6" />
                                <span>Entrar a mi Cuenta</span>
                                <ArrowRight className="w-5 h-5 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                            </button>

                            <button
                                onClick={() => setMode('register')}
                                className="btn btn-outline"
                            >
                                <Mail className="w-6 h-6" />
                                <span>Registrarse</span>
                            </button>
                        </div>
                    )}

                    {/* Login Form */}
                    {mode === 'login' && (
                        <form onSubmit={handleLogin} className="flex flex-col gap-4 animate-fade-in">
                            <div className="flex items-center justify-between mb-2">
                                <button
                                    type="button"
                                    onClick={() => { setMode('landing'); resetForm(); }}
                                    className="back-btn"
                                >
                                    <ArrowLeft className="w-4 h-4 mr-1" /> Volver
                                </button>
                                <h2 className="text-2xl font-bold text-white m-0">Iniciar Sesión</h2>
                            </div>

                            {error && (
                                <div className="error-msg">
                                    {error}
                                </div>
                            )}

                            <div className="form-group">
                                <label className="form-label">Correo Electrónico</label>
                                <div className="input-wrapper">
                                    <Mail className="input-icon" />
                                    <input
                                        type="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="form-input"
                                        placeholder="nombre@ejemplo.com"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Contraseña</label>
                                <div className="input-wrapper">
                                    <Lock className="input-icon" />
                                    <input
                                        type="password"
                                        required
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="form-input"
                                        placeholder="••••••••"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="btn btn-primary mt-4"
                            >
                                {isLoading ? 'Entrando...' : 'Entrar'}
                            </button>
                        </form>
                    )}

                    {/* Register Form */}
                    {mode === 'register' && (
                        <form onSubmit={handleRegister} className="flex flex-col gap-4 animate-fade-in">
                            <div className="flex items-center justify-between mb-2">
                                <button
                                    type="button"
                                    onClick={() => { setMode('landing'); resetForm(); }}
                                    className="back-btn"
                                >
                                    <ArrowLeft className="w-4 h-4 mr-1" /> Volver
                                </button>
                                <h2 className="text-2xl font-bold text-white m-0">Crear Cuenta</h2>
                            </div>

                            {error && (
                                <div className="error-msg">
                                    {error}
                                </div>
                            )}

                            <div className="form-group">
                                <label className="form-label">Nombre Completo</label>
                                <div className="input-wrapper">
                                    <User className="input-icon" />
                                    <input
                                        type="text"
                                        required
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="form-input"
                                        placeholder="Juan Pérez"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Correo Electrónico</label>
                                <div className="input-wrapper">
                                    <Mail className="input-icon" />
                                    <input
                                        type="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="form-input"
                                        placeholder="nombre@ejemplo.com"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Contraseña</label>
                                <div className="input-wrapper">
                                    <Lock className="input-icon" />
                                    <input
                                        type="password"
                                        required
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="form-input"
                                        placeholder="••••••••"
                                    />
                                </div>
                                <p className="text-xs text-slate-500 mt-1 m-0">
                                    Mínimo 8 caracteres, mayúscula, minúscula, número y símbolo.
                                </p>
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="btn btn-primary mt-4"
                            >
                                {isLoading ? 'Registrando...' : 'Registrarse'}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    )
}
