import { DEMO_RESPONSE } from '../data/demoData';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';
const IS_DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

export async function analyzeMoodImage(imageBlob) {
  if (IS_DEMO_MODE) {
    // Artificial delay for smooth UX sequence in demo mode
    await new Promise((resolve) => setTimeout(resolve, 1800));
    return DEMO_RESPONSE;
  }

  const formData = new FormData();
  formData.append('image', imageBlob, 'mood_capture.jpg');

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    const errorMsg = data?.error?.message || 'Failed to analyze expression. Please try again.';
    const errorCode = data?.error?.code || 'UNKNOWN_ERROR';
    const err = new Error(errorMsg);
    err.code = errorCode;
    throw err;
  }

  return data;
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: true, ...data };
  } catch (e) {
    return { online: false };
  }
}
