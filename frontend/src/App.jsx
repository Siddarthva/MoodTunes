import React, { useState, useEffect } from 'react';
import Hero from './components/Hero';
import WebcamCapture from './components/WebcamCapture';
import AnalysisSequence from './components/AnalysisSequence';
import MoodReveal from './components/MoodReveal';
import Recommendations from './components/Recommendations';
import MusicPlayer from './components/MusicPlayer';
import { useMoodAnalysis } from './hooks/useMoodAnalysis';
import { checkBackendHealth } from './services/api';

export default function App() {
  const { state, result, error, analyze, reset, isAnalyzing } = useMoodAnalysis();
  const [activeTrack, setActiveTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [backendOffline, setBackendOffline] = useState(false);

  // Silent backend connectivity check on mount
  useEffect(() => {
    checkBackendHealth().then((health) => {
      setBackendOffline(!health.online);
    });
  }, []);

  const handleCapture = (blob) => {
    analyze(blob);
  };

  const handleReset = () => {
    reset();
    setActiveTrack(null);
    setIsPlaying(false);
  };

  const handleSelectTrack = (track) => {
    if (activeTrack && activeTrack.id === track.id) {
      setIsPlaying(!isPlaying);
    } else {
      setActiveTrack(track);
      setIsPlaying(true);
    }
  };

  const errorMessage = (err) => {
    if (!err) return null;
    switch (err.code) {
      case 'NO_FACE_DETECTED':
        return "No face detected. Centre yourself in frame and try again.";
      case 'MODEL_NOT_READY':
        return "Emotion model isn't ready. Restart the backend and try again.";
      case 'CORRUPT_IMAGE':
        return "Image could not be read. Try again.";
      case 'MUSIC_PROVIDER_ERROR':
      case 'MUSIC_PROVIDER_TIMEOUT':
        return "Couldn't load recommendations right now. Try again.";
      default:
        return err.message || "Something went wrong. Try again.";
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#f2f2f2] pb-32 selection:bg-neutral-800 selection:text-white film-grain">
      {/* Editorial Navigation Bar */}
      <header className="max-w-6xl mx-auto px-6 py-8 flex justify-between items-center">
        <span className="font-bold text-sm tracking-widest uppercase text-neutral-300">
          MOODTUNES
        </span>
        <div className="flex items-center gap-4">
          {backendOffline && (
            <span className="text-[10px] font-mono text-neutral-600 uppercase tracking-widest">
              backend unavailable
            </span>
          )}
          {import.meta.env.VITE_DEMO_MODE === 'true' && (
            <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest border-b border-neutral-800 pb-0.5">
              DEMO MODE
            </span>
          )}
        </div>
      </header>

      {/* Cinematic Vertical Sequence */}
      <main className="relative z-10">
        <Hero />

        <WebcamCapture
          onCapture={handleCapture}
          isAnalyzing={isAnalyzing}
          analysisState={state}
          onReset={handleReset}
        />

        <AnalysisSequence isAnalyzing={isAnalyzing} />

        {/* Controlled Error Display */}
        {state === 'error' && error && (
          <div className="max-w-md mx-auto my-8 text-center font-mono">
            <p className="text-xs uppercase tracking-widest text-neutral-400 mb-4">
              {errorMessage(error)}
            </p>
            <button
              onClick={handleReset}
              className="text-xs text-neutral-500 hover:text-white uppercase tracking-widest underline transition-colors"
            >
              Try Again →
            </button>
          </div>
        )}

        {/* Mood Reveal & Recommendations */}
        {state === 'success' && result && (
          <>
            <MoodReveal result={result} />
            <Recommendations
              tracks={result.recommendations}
              activeTrack={activeTrack}
              isPlaying={isPlaying}
              onSelectTrack={handleSelectTrack}
            />
            {/* Scan again link */}
            <div className="text-center my-16">
              <button
                onClick={handleReset}
                className="text-xs font-mono uppercase tracking-[0.25em] text-neutral-600 hover:text-neutral-300 transition-colors"
              >
                Scan again →
              </button>
            </div>
          </>
        )}
      </main>

      {/* Persistent Bottom Music Player */}
      <MusicPlayer
        activeTrack={activeTrack}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
      />
    </div>
  );
}
