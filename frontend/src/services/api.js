import { DEMO_RESPONSE } from '../data/demoData';
import { API_BASE_URL } from './config';

const IS_DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

export async function analyzeMoodImage(imageBlob, intent = 'match_me') {
  if (IS_DEMO_MODE) {
    // Artificial delay for smooth UX sequence in demo mode
    await new Promise((resolve) => setTimeout(resolve, 1800));
    return DEMO_RESPONSE;
  }

  const formData = new FormData();
  formData.append('image', imageBlob, 'mood_capture.jpg');
  formData.append('intent', intent);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    let errorMsg = data?.error?.message || 'Failed to analyze expression. Please try again.';
    let errorCode = data?.error?.code || 'UNKNOWN_ERROR';
    
    // Gracefully handle FastAPI 422 Validation Errors
    if (response.status === 422 && data.detail) {
      console.error("FastAPI Validation Error Details:", data.detail);
      errorMsg = "We couldn't read that frame. Please try again.";
      errorCode = "VALIDATION_ERROR";
    }

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

export async function getMoodContent(dominantEmotion, profile, energy, valence, intent) {
  const payload = {
    dominant_emotion: dominantEmotion,
    emotional_profile: profile,
    energy: energy,
    valence: valence,
    intent: intent
  };
  
  const response = await fetch(`${API_BASE_URL}/api/content/mood`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Failed to fetch mood content');
  }

  return await response.json();
}

export async function getPostScanContent(dominantEmotion, profile, energy, valence, intent) {
  const payload = {
    dominant_emotion: dominantEmotion,
    emotional_profile: profile,
    energy: energy,
    valence: valence,
    intent: intent
  };
  
  const response = await fetch(`${API_BASE_URL}/api/content/post-scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Failed to fetch post-scan content');
  }

  return await response.json();
}

export async function interpretMood(emotion, profile) {
  const payload = {
    emotion,
    emotional_profile: profile
  };

  const response = await fetch(`${API_BASE_URL}/api/mood/interpret`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Failed to interpret mood spectrum');
  }

  return await response.json();
}

