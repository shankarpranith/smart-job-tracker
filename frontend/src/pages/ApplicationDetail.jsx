import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getApplication, getResumeUploadUrl, getResumeDownloadUrl } from '../api/applications';
import { uploadFileToS3 } from '../api/client';

const ALLOWED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

export default function ApplicationDetail() {
  const { id } = useParams();
  const [app, setApp] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  function loadApplication() {
    return getApplication(id)
      .then(setApp)
      .catch(() => setError('Application not found'));
  }

  useEffect(() => {
    loadApplication();
  }, [id]);

  async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setUploadError('Only PDF, DOC, and DOCX files are allowed.');
      return;
    }

    setUploading(true);
    setUploadError('');
    try {
      const { upload_url } = await getResumeUploadUrl(id, file.type);
      await uploadFileToS3(upload_url, file);
      await loadApplication(); // refresh so resume_s3_key shows up
    } catch (err) {
      setUploadError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
      e.target.value = ''; // reset the file input
    }
  }

  async function handleDownload() {
    try {
      const { download_url } = await getResumeDownloadUrl(id);
      window.open(download_url, '_blank');
    } catch (err) {
      alert('Failed to get download link');
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!app) return <p>Loading...</p>;

  return (
    <div className="application-detail">
      <Link to="/">← Back to Dashboard</Link>
      <h1>{app.job_title} at {app.company}</h1>
      <p><strong>Status:</strong> {app.status}</p>
      {app.location && <p><strong>Location:</strong> {app.location}</p>}
      {app.salary && <p><strong>Salary:</strong> {app.salary}</p>}
      {app.applied_date && <p><strong>Applied:</strong> {app.applied_date}</p>}
      {app.follow_up_date && <p><strong>Follow-up:</strong> {app.follow_up_date}</p>}
      {app.job_url && (
        <p><strong>Job URL:</strong> <a href={app.job_url} target="_blank" rel="noreferrer">{app.job_url}</a></p>
      )}
      {app.job_description && (
        <div><strong>Job Description:</strong><p>{app.job_description}</p></div>
      )}
      {app.notes && <div><strong>Notes:</strong><p>{app.notes}</p></div>}

      <section className="resume-section">
        <h2>Resume</h2>
        {app.resume_s3_key ? (
          <div>
            <p>A resume has been uploaded.</p>
            <button onClick={handleDownload}>Download / View Resume</button>
          </div>
        ) : (
          <p>No resume uploaded yet.</p>
        )}

        <label>
          {app.resume_s3_key ? 'Replace resume' : 'Upload resume'}
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileSelect}
            disabled={uploading}
          />
        </label>
        {uploading && <p>Uploading...</p>}
        {uploadError && <p className="error">{uploadError}</p>}
      </section>

      <Link to={`/applications/${id}/edit`}>Edit</Link>
    </div>
  );
}