import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { listApplications, deleteApplication } from '../api/applications';

export default function Dashboard() {
  const { currentUser, logout } = useAuth();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadApplications() {
    setLoading(true);
    setError('');
    try {
      const data = await listApplications();
      setApplications(data);
    } catch (err) {
      setError('Failed to load applications');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplications();
  }, []);

  async function handleDelete(id) {
    if (!confirm('Delete this application?')) return;
    try {
      await deleteApplication(id);
      setApplications((prev) => prev.filter((app) => app.application_id !== id));
    } catch (err) {
      alert('Failed to delete application');
    }
  }

  return (
    <div className="dashboard">
      <header>
        <h1>Smart Job Application Tracker</h1>
        <div>
          <span>{currentUser.email}</span>
          <button onClick={logout}>Log Out</button>
        </div>
      </header>

      <div className="dashboard-actions">
        <Link to="/applications/new">+ Add Application</Link>
      </div>

      {loading && <p>Loading applications...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && applications.length === 0 && (
        <p>No applications yet. Add your first one!</p>
      )}

      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Job Title</th>
            <th>Status</th>
            <th>Applied Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.application_id}>
              <td>{app.company}</td>
              <td>{app.job_title}</td>
              <td>{app.status}</td>
              <td>{app.applied_date || '—'}</td>
              <td>
                <Link to={`/applications/${app.application_id}`}>View</Link>
                {' | '}
                <Link to={`/applications/${app.application_id}/edit`}>Edit</Link>
                {' | '}
                <button onClick={() => handleDelete(app.application_id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}