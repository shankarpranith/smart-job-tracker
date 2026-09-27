import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  LineChart, Line, ResponsiveContainer,
} from 'recharts';
import { getStats } from '../api/applications';

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setError('Failed to load statistics'));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!stats) return <p>Loading statistics...</p>;

  if (stats.total_applications === 0) {
    return (
      <div className="analytics-page">
        <Link to="/">← Back to Dashboard</Link>
        <h1>Analytics</h1>
        <p>No applications yet. Add some to see your stats here.</p>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <Link to="/">← Back to Dashboard</Link>
      <h1>Analytics</h1>

      <div className="stats-summary">
        <div className="stat-card">
          <span className="stat-value">{stats.total_applications}</span>
          <span className="stat-label">Total Applications</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.response_rate}%</span>
          <span className="stat-label">Response Rate</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.interview_rate}%</span>
          <span className="stat-label">Interview Rate</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.offer_rate}%</span>
          <span className="stat-label">Offer Rate</span>
        </div>
      </div>

      <section>
        <h2>Applications by Status</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stats.status_breakdown}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="status" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#4f46e5" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h2>Applications Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={stats.applications_over_time}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#4f46e5" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h2>Outcomes</h2>
        <ul>
          <li>Interviews: {stats.interviews}</li>
          <li>Offers: {stats.offers}</li>
          <li>Rejections: {stats.rejections}</li>
        </ul>
      </section>
    </div>
  );
}