import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { analyzeMoodImage } from '../services/api';
import { applyEmotionThemeToDocument, resetEmotionThemeOnDocument } from '../theme/emotionTheme';

const MoodContext = createContext(null);

export function MoodProvider({ children }) {
  // Analysis State
  const [analysisState, setAnalysisState] = useState('idle'); // idle | capturing | analyzing | success | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  // User Input
  const [intent, setIntent] = useState('match_me');
  
  // Music Player State
  const [activeTrack, setActiveTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // Session History
  const [likedTracks, setLikedTracks] = useState([]);
  const [skippedTracks, setSkippedTracks] = useState([]);

  // Dynamic Theme Engine Effect: Apply weighted 7-class emotion theme to document root
  useEffect(() => {
    if (result && result.emotion && result.emotion.probabilities) {
      applyEmotionThemeToDocument(result.emotion.probabilities);
    } else {
      resetEmotionThemeOnDocument();
    }
  }, [result]);

  const analyze = useCallback(async (imageBlob, selectedIntent = intent) => {
    if (analysisState === 'analyzing' || analysisState === 'capturing') return;

    setAnalysisState('analyzing');
    setError(null);

    try {
      const data = await analyzeMoodImage(imageBlob, selectedIntent);
      setResult(data);
      setAnalysisState('success');
    } catch (err) {
      setError(err);
      setAnalysisState('error');
    }
  }, [analysisState, intent]);

  // User Selected Experience Path ('music' | 'talk' | null)
  const [selectedChoice, setSelectedChoice] = useState(null);

  const reset = useCallback(() => {
    setAnalysisState('idle');
    setResult(null);
    setError(null);
    setActiveTrack(null);
    setIsPlaying(false);
    setSelectedChoice(null);
    resetEmotionThemeOnDocument();
  }, []);

  const likeTrack = useCallback((trackId) => {
    if (!likedTracks.includes(trackId)) {
      setLikedTracks(prev => [...prev, trackId]);
    }
  }, [likedTracks]);

  const skipTrack = useCallback((trackId) => {
    if (!skippedTracks.includes(trackId)) {
      setSkippedTracks(prev => [...prev, trackId]);
    }
  }, [skippedTracks]);

  const value = {
    analysisState,
    setAnalysisState,
    result,
    setResult,
    error,
    analyze,
    reset,
    isAnalyzing: analysisState === 'analyzing' || analysisState === 'capturing',
    
    intent,
    setIntent,

    selectedChoice,
    setSelectedChoice,
    
    activeTrack,
    setActiveTrack,
    isPlaying,
    setIsPlaying,
    
    likedTracks,
    likeTrack,
    skippedTracks,
    skipTrack
  };


  return (
    <MoodContext.Provider value={value}>
      {children}
    </MoodContext.Provider>
  );
}

export function useMoodContext() {
  const context = useContext(MoodContext);
  if (!context) {
    throw new Error('useMoodContext must be used within a MoodProvider');
  }
  return context;
}
