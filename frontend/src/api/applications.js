import apiClient from './client';

export async function listApplications() {
  const res = await apiClient.get('/applications');
  return res.data;
}

export async function getApplication(id) {
  const res = await apiClient.get(`/applications/${id}`);
  return res.data;
}

export async function createApplication(data) {
  const res = await apiClient.post('/applications', data);
  return res.data;
}

export async function updateApplication(id, data) {
  const res = await apiClient.put(`/applications/${id}`, data);
  return res.data;
}

export async function deleteApplication(id) {
  await apiClient.delete(`/applications/${id}`);
}

export async function getResumeUploadUrl(id, contentType) {
  const res = await apiClient.post(`/applications/${id}/resume-upload-url`, {
    content_type: contentType,
  });
  return res.data; // { upload_url, s3_key }
}

export async function getResumeDownloadUrl(id) {
  const res = await apiClient.get(`/applications/${id}/resume-download-url`);
  return res.data; // { download_url }
}