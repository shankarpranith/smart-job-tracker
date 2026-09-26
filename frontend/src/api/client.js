import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

// This function is set once, from AuthContext, so the API client
// can always get a fresh token without importing AuthContext directly
// (avoids a circular import between AuthContext and this file).
let tokenProvider = null;

export function setTokenProvider(fn) {
  tokenProvider = fn;
}

const apiClient = axios.create({
  baseURL: API_URL,
});

// Runs before every request — attaches a fresh, auto-refreshed token.
apiClient.interceptors.request.use(async (config) => {
  if (tokenProvider) {
    const token = await tokenProvider();
    // NOTE: no "Bearer " prefix — API Gateway's native Cognito
    // authorizer expects the raw token (see Phase 6 debugging notes).
    config.headers.Authorization = token;
  }
  return config;
});

export default apiClient;

// A separate, plain axios instance (NOT apiClient) for uploading directly
// to S3 via presigned URLs. It must NOT carry our Cognito Authorization
// header — S3 authenticates the request via the presigned URL's own
// signature, and an unexpected extra header would break that signature.
export async function uploadFileToS3(uploadUrl, file) {
  await axios.put(uploadUrl, file, {
    headers: { 'Content-Type': file.type },
  });
}