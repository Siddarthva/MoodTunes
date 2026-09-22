import { API_BASE_URL } from './config';

export async function sendTalkMessage(message, conversationHistory, emotionProfile, userIntent = "comfort") {
  const payload = {
    message,
    conversation: conversationHistory,
    emotion_profile: emotionProfile,
    user_intent: userIntent
  };

  const response = await fetch(`${API_BASE_URL}/api/talk`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    let errorMsg = data?.message || 'Failed to connect. Please try again.';
    
    // Gracefully handle FastAPI 422 Validation Errors
    if (response.status === 422 && data.detail) {
      console.error("FastAPI Validation Error Details:", data.detail);
      errorMsg = "There was an issue processing your message.";
    }

    throw new Error(errorMsg);
  }

  return data;
}
