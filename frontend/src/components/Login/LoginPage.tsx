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

    const [successMessage, setSuccessMessage] = useState<string | null>(null)

    // Form States
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [name, setName] = useState('')

    // Helper for password validation matching backend regex
    const validatePassword = (pwd: string) => {
        const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[ !#$%^&*(),.?":{}|<>]).{8,}$/
        return pattern.test(pwd)
    }

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        setError(null)
        setSuccessMessage(null)
        try {
            const response = await fetch('https://lawyer-agent-api-214571216460.us-central1.run.app/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, hashed_password: password }),
            })
            const data = await response.json()

            if (response.ok && data.status === 'success') {
                localStorage.setItem('user_id', data.user_id)
                navigate('/chat')
            } else {
                setError('Error al iniciar sesión, verifica el usuario y la contraseña, e intenta de nuevo')
            }
        } catch (err) {
            setError('Error de conexión con el servidor')
        } finally {
            setIsLoading(false)
        }
    }

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()

        // Frontend Validation
        if (!validatePassword(password)) {
            setError('La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.')
            return
        }

        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch('https://lawyer-agent-api-214571216460.us-central1.run.app/create_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, hashed_password: password }),
            })
            const data = await response.json()

            if (response.ok && data.user_id) {
                // User requested: Show success message and ask to login
                setSuccessMessage('Registro exitoso. Por favor inicia sesión.')
                setMode('login')
                // Clear password for security/UX flow? Maybe keep email.
                setPassword('')
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
        setSuccessMessage(null)
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

            {/* Branding Block: Moved outside login-content to prevent shifting */}
            <div className="login-branding">
                <p className="login-welcome-text">BIENVENIDO A</p>
                <h1 className="login-title">
                    LIA
                </h1>
                <p className="login-subtitle">
                    Asistente Legal de Investigación Avanzada
                </p>
            </div>

            <div className="login-content">
                {/* Interaction Area */}
                <div className="login-card">

                    {/* Landing Mode: Buttons */}
                    {mode === 'landing' && (
                        <div className="action-buttons animate-fade-in">
                            <h2 className="section-title">Comenzar</h2>

                            <button
                                onClick={() => setMode('login')}
                                className="btn btn-primary group"
                            >
                                <User className="w-5 h-5" />
                                <span>Entrar a mi Cuenta</span>
                                <ArrowRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                            </button>

                            <button
                                onClick={() => setMode('register')}
                                className="btn btn-outline"
                            >
                                <Mail className="w-5 h-5" />
                                <span>Registrarse</span>
                            </button>
                        </div>
                    )}

                    {/* Login Form */}
                    {mode === 'login' && (
                        <form onSubmit={handleLogin} className="flex flex-col gap-4 animate-fade-in">
                            <div className="form-title-row">
                                <button
                                    type="button"
                                    onClick={() => { setMode('landing'); resetForm(); }}
                                    className="back-btn"
                                >
                                    <ArrowLeft className="w-4 h-4 mr-1" /> Volver
                                </button>
                                <h2 className="form-header">Iniciar Sesión</h2>
                            </div>

                            {successMessage && (
                                <div className="success-msg">
                                    {successMessage}
                                </div>
                            )}

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
                            <div className="form-title-row">
                                <button
                                    type="button"
                                    onClick={() => { setMode('landing'); resetForm(); }}
                                    className="back-btn"
                                >
                                    <ArrowLeft className="w-4 h-4 mr-1" /> Volver
                                </button>
                                <h2 className="form-header">Crear Cuenta</h2>
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

                {/* Right Side: Branding (Swapped) */}
                {/* Right Side: Branding (Swapped) */}

            </div>
        </div>
    )
}
