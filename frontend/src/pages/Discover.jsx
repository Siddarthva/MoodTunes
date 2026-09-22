import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import IntentSelector from '../components/IntentSelector';
import WebcamCapture from '../components/WebcamCapture';
import MoodReveal from '../components/MoodReveal';
import UserChoiceScreen from '../components/UserChoiceScreen';
import Recommendations from '../components/Recommendations';
import LoadingMessages from '../components/LoadingMessages';
import EditorialQuote from '../components/EditorialQuote';
import MusicEmotionEditorial from '../components/MusicEmotionEditorial';
import TalkAnchor from '../components/TalkAnchor';
import { useMoodContext } from '../context/MoodContext';
import { API_BASE_URL } from '../services/config';

export default function Discover() {
  const navigate = useNavigate();
  const { 
    analysisState, 
    error,
    result, 
    analyze, 
    isAnalyzing, 
    reset,
    selectedChoice,
    setSelectedChoice
  } = useMoodContext();

  const [content, setContent] = useState(null);

  useEffect(() => {
    // Fetch dynamic content on mount
    const fetchContent = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/content/home`);
        if (res.ok) {
          const data = await res.json();
          setContent(data);
        }
      } catch (err) {
        console.error("Failed to fetch home content", err);
      }
    };
    fetchContent();
  }, []);

  const handleCapture = (blob) => {
    analyze(blob);
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
    <div className="flex flex-col items-center pb-24">
      {analysisState === 'idle' && (
        <>
          <div className="animate-blur-reveal text-center mt-20 mb-16 max-w-2xl mx-auto px-4">
            <h1 className="text-4xl md:text-6xl font-light tracking-tight mb-6">
              {content ? (
                <>
                  <span className="text-white">Mood, </span>
                  <span className="italic text-neutral-400">translated into music.</span>
                </>
              ) : (
                <>
                  Find the sound that meets you <span className="italic text-neutral-400">where you are.</span>
                </>
              )}
            </h1>
            <p className="text-neutral-500 tracking-wide text-lg max-w-xl mx-auto">
              {content ? content.subheadline : "MoodTunes reads the emotional pattern in your expression and shapes a music direction around it."}
            </p>
          </div>
          
          <div className="max-w-xl text-center mb-16 animate-fade-in-slow text-sm uppercase tracking-widest font-mono text-neutral-600">
            {content ? content.micro_statement : "An intelligent approach to what you hear."}
          </div>
        </>
      )}

      {/* Main Analysis Flow */}
      {(analysisState === 'idle' || analysisState === 'capturing' || analysisState === 'analyzing') && (
        <div className="w-full flex flex-col items-center">
          <IntentSelector />
          
          <WebcamCapture
            onCapture={handleCapture}
            isAnalyzing={isAnalyzing}
            analysisState={analysisState}
          />
          
          {isAnalyzing && <LoadingMessages />}
        </div>
      )}

      {/* Analysis Error */}
      {analysisState === 'error' && (
        <div className="text-center mt-12 animate-fade-in">
          <p className="text-[#f2f2f2] font-light text-xl mb-8">{errorMessage(error)}</p>
          <button
            onClick={reset}
            className="px-8 py-3 border border-neutral-800 hover:border-neutral-500 transition-colors uppercase tracking-[0.2em] text-xs font-mono text-neutral-400 hover:text-white"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Analysis Results Sequence */}
      {analysisState === 'success' && result && (
        <div className="w-full flex flex-col items-center">
          {/* 1. Seven-Class Emotional Spectrum & Groq Reflection */}
          <MoodReveal result={result} />
          
          {/* 2. User Choice Screen (Find Soundtrack OR Talk) */}
          <UserChoiceScreen 
            selectedChoice={selectedChoice}
            onSelectChoice={(choice) => {
              setSelectedChoice(choice);
              if (choice === 'talk') {
                navigate('/talk');
              }
            }} 
          />

          {/* 3. Selected Experience: Music Path */}
          {selectedChoice === 'music' && (
            <div className="w-full flex flex-col items-center animate-fade-in-slow pt-12">
              <Recommendations tracks={result.recommendations} />
              <EditorialQuote result={result} />
              <MusicEmotionEditorial />
            </div>
          )}

          <div className="flex justify-center mt-16">
            <button
              onClick={reset}
              className="px-8 py-3 border border-neutral-800 hover:border-neutral-500 transition-colors uppercase tracking-[0.2em] text-xs font-mono text-neutral-400 hover:text-white"
            >
              Start New Scan
            </button>
          </div>
        </div>
      )}


      {/* Editorial Content Blocks for the Homepage (Only shown when idle) */}
      {analysisState === 'idle' && content && (
        <div className="w-full max-w-4xl mx-auto mt-32 px-4 flex flex-col gap-24 animate-fade-in-slow">
          <div className="border-t border-neutral-900 pt-16 flex flex-col md:flex-row gap-8 justify-between items-start">
            <div className="flex-1">
              <p className="text-xs uppercase tracking-widest font-mono text-neutral-500 mb-4">Emotional Complexity</p>
              <h2 className="text-2xl font-light text-[#f2f2f2] leading-relaxed">
                {content.mood_fact}
              </h2>
            </div>
            <div className="flex-1">
              <p className="text-xs uppercase tracking-widest font-mono text-neutral-500 mb-4">Aural Perception</p>
              <h2 className="text-2xl font-light text-[#f2f2f2] leading-relaxed">
                {content.music_fact}
              </h2>
            </div>
          </div>
          
          <div className="border border-neutral-900 p-12 text-center bg-[#0a0a0a]">
            <p className="text-sm uppercase tracking-widest font-mono text-neutral-500 mb-4">Talk Experience</p>
            <h3 className="text-3xl font-light mb-6 text-white">{content.talk_teaser}</h3>
            <Link to="/talk" className="inline-block px-8 py-3 bg-[#f2f2f2] text-black hover:bg-white uppercase tracking-[0.2em] text-xs font-mono transition-colors">
              Talk to MoodTunes
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
