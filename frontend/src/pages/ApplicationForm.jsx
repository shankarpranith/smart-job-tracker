import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  createApplication,
  updateApplication,
  getApplication,
} from '../api/applications';

const STATUS_OPTIONS = [
  'Saved',
  'Applied',
  'Online Assessment',
  'Interview',
  'Offer',
  'Rejected',
  'Accepted',
  'Withdrawn',
];

const EMPTY_FORM = {
  company: '',
  job_title: '',
  job_url: '',
  location: '',
  salary: '',
  status: 'Saved',
  applied_date: '',
  follow_up_date: '',
  job_description: '',
  notes: '',
};

export default function ApplicationForm() {
  const { id } = useParams(); // undefined when adding, set when editing
  const isEditing = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(isEditing);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isEditing) return;
    getApplication(id)
      .then((data) => {
        setForm({
          company: data.company || '',
          job_title: data.job_title || '',
          job_url: data.job_url || '',
          location: data.location || '',
          salary: data.salary || '',
          status: data.status || 'Saved',
          applied_date: data.applied_date || '',
          follow_up_date: data.follow_up_date || '',
          job_description: data.job_description || '',
          notes: data.notes || '',
        });
      })
      .catch(() => setError('Failed to load application'))
      .finally(() => setLoading(false));
  }, [id, isEditing]);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError('');

    // Don't send empty strings for optional date fields —
    // the backend expects either a valid date or the field omitted.
    const payload = { ...form };
    if (!payload.applied_date) delete payload.applied_date;
    if (!payload.follow_up_date) delete payload.follow_up_date;

    try {
      if (isEditing) {
        await updateApplication(id, payload);
      } else {
        await createApplication(payload);
      }
      navigate('/');
    } catch (err) {
      setError('Failed to save application');
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p>Loading...</p>;

  return (
    <div className="application-form">
      <h1>{isEditing ? 'Edit Application' : 'Add Application'}</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Company *
          <input name="company" value={form.company} onChange={handleChange} required />
        </label>
        <label>
          Job Title *
          <input name="job_title" value={form.job_title} onChange={handleChange} required />
        </label>
        <label>
          Job URL
          <input name="job_url" value={form.job_url} onChange={handleChange} />
        </label>
        <label>
          Location
          <input name="location" value={form.location} onChange={handleChange} />
        </label>
        <label>
          Salary
          <input name="salary" value={form.salary} onChange={handleChange} />
        </label>
        <label>
          Status
          <select name="status" value={form.status} onChange={handleChange}>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>
        <label>
          Applied Date
          <input
            type="date"
            name="applied_date"
            value={form.applied_date}
            onChange={handleChange}
          />
        </label>
        <label>
          Follow-up Date
          <input
            type="date"
            name="follow_up_date"
            value={form.follow_up_date}
            onChange={handleChange}
          />
        </label>
        <label>
          Job Description
          <textarea
            name="job_description"
            value={form.job_description}
            onChange={handleChange}
            rows={4}
          />
        </label>
        <label>
          Notes
          <textarea name="notes" value={form.notes} onChange={handleChange} rows={3} />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={saving}>
          {saving ? 'Saving...' : isEditing ? 'Save Changes' : 'Add Application'}
        </button>
      </form>
    </div>
  );
}