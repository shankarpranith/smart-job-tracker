import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function RegisterPage() {
  const [step, setStep] = useState('register'); // 'register' | 'confirm'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { register, confirmRegistration } = useAuth();
  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(email, password);
      setStep('confirm');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleConfirm(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await confirmRegistration(email, code);
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Confirmation failed');
    } finally {
      setSubmitting(false);
    }
  }

  if (step === 'confirm') {
    return (
      <div className="auth-page">
        <h1>Check Your Email</h1>
        <p>We sent a confirmation code to {email}.</p>
        <form onSubmit={handleConfirm}>
          <label>
            Confirmation Code
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={submitting}>
            {submitting ? 'Confirming...' : 'Confirm'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <h1>Register</h1>
      <form onSubmit={handleRegister}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
          <small>At least 8 characters, with uppercase, lowercase, and a number.</small>
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Registering...' : 'Register'}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log In</Link>
      </p>
    </div>
  );
}