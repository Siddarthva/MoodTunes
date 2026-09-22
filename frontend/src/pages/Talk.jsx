import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useMoodContext } from '../context/MoodContext';
import { sendTalkMessage } from '../services/talkService';
import VoiceControl from '../components/VoiceControl';
import WebcamCapture from '../components/WebcamCapture';
import { Volume2, VolumeX, RefreshCw } from 'lucide-react';

export default function Talk() {
  const { analysisState, result, analyze, isAnalyzing, reset } = useMoodContext();
  
  const [conversation, setConversation] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [inputMode, setInputMode] = useState(() => (result?.emotional_profile ? 'chat' : 'choose')); // 'choose', 'camera', 'chat'
  const [useCurrentMood, setUseCurrentMood] = useState(true);
  const messagesEndRef = useRef(null);

  // Sync mode if scan completed elsewhere
  useEffect(() => {
    if (result?.emotional_profile && inputMode !== 'chat') {
      setInputMode('chat');
    }
  }, [result]);


  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  // Handle TTS
  const speakText = (text) => {
    if (!voiceEnabled || !window.speechSynthesis) return;
    
    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    // Find a nice english voice if possible
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.lang.includes('en') && v.name.includes('Google')) || voices[0];
    if (voice) utterance.voice = voice;
    
    utterance.rate = 0.95; // slightly slower, calmer
    utterance.pitch = 1;
    
    window.speechSynthesis.speak(utterance);
  };

  const handleCapture = async (blob) => {
    await analyze(blob);
    setInputMode('chat');
  };

  const handleSendMessage = async (text) => {
    const userMessage = { role: 'user', content: text };
    setConversation(prev => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      // Use existing profile if available and user hasn't toggled mood off
      const profile = (useCurrentMood && result?.emotional_profile) ? result.emotional_profile : null;
      
      const response = await sendTalkMessage(text, conversation, profile);

      
      const assistantMessage = { role: 'assistant', content: response.message, should_suggest_music: response.should_suggest_music };
      setConversation(prev => [...prev, assistantMessage]);
      
      if (voiceEnabled) {
        speakText(response.message);
      }
      
    } catch (error) {
      console.error(error);
      setConversation(prev => [...prev, { role: 'assistant', content: error.message }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearSession = () => {
    setConversation([]);
    setInputMode('choose');
    reset();
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  };

  // Render Initial Choice Screen
  if (inputMode === 'choose') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
        <div className="text-center mb-16 max-w-2xl mx-auto">
          <p className="text-xs uppercase tracking-[0.3em] text-neutral-500 mb-6 font-mono">Talk</p>
          <h1 className="text-4xl md:text-6xl font-light tracking-tight mb-6">
            You don't have to <span className="italic text-neutral-400">have it figured out.</span>
          </h1>
          <p className="text-neutral-500 tracking-wide text-lg max-w-xl mx-auto">
            How should I meet you today?
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-6 w-full max-w-xl px-4">
          <button 
            onClick={() => setInputMode('camera')}
            className="flex-1 py-6 border border-neutral-800 hover:border-neutral-500 bg-[#0a0a0a] transition-all group"
          >
            <span className="block text-sm uppercase tracking-widest font-mono text-neutral-400 group-hover:text-white mb-2">Use My Mood</span>
            <span className="block text-xs text-neutral-600 px-4">Let the camera read your emotional signal first</span>
          </button>
          
          <button 
            onClick={() => setInputMode('chat')}
            className="flex-1 py-6 border border-neutral-800 hover:border-neutral-500 bg-[#0a0a0a] transition-all group"
          >
            <span className="block text-sm uppercase tracking-widest font-mono text-neutral-400 group-hover:text-white mb-2">Just Let Me Talk</span>
            <span className="block text-xs text-neutral-600 px-4">Jump straight into the conversation</span>
          </button>
        </div>
      </div>
    );
  }

  // Render Camera Flow
  if (inputMode === 'camera' && analysisState !== 'success') {
    return (
      <div className="flex flex-col items-center animate-fade-in pt-12">
        <p className="text-xs uppercase tracking-[0.3em] text-neutral-500 mb-8 font-mono">Setting the context</p>
        <WebcamCapture 
          onCapture={handleCapture}
          isAnalyzing={isAnalyzing}
          analysisState={analysisState}
        />
        <button 
          onClick={() => setInputMode('chat')}
          className="mt-8 text-xs text-neutral-500 hover:text-white transition-colors tracking-widest uppercase font-mono"
        >
          Skip this step
        </button>
      </div>
    );
  }

  // Render Conversation Flow
  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-w-4xl mx-auto pt-8 animate-fade-in relative">
      
      {/* Header controls */}
      <div className="flex flex-wrap justify-between items-center mb-8 px-4 gap-4 border-b border-white/[0.06] pb-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={clearSession}
            className="text-neutral-500 hover:text-white transition-colors flex items-center gap-2 text-xs uppercase tracking-widest font-mono"
          >
            <RefreshCw size={14} /> Reset
          </button>

          {result?.emotion?.dominant && (
            <div className="flex items-center gap-2 bg-white/[0.03] px-3 py-1 rounded-full border border-white/[0.08]">
              <span className="text-[10px] font-mono uppercase tracking-widest text-neutral-400">
                Session: Expression leaning <span style={{ color: 'var(--mood-accent, #ffffff)' }}>{result.emotion.dominant}</span>
              </span>
              <button
                onClick={() => setUseCurrentMood(!useCurrentMood)}
                className={`text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded transition-all ${
                  useCurrentMood ? 'bg-white/10 text-white' : 'text-neutral-500 hover:text-neutral-300'
                }`}
                title="Toggle whether emotional signal is included in conversation"
              >
                {useCurrentMood ? 'Mood On' : 'Mood Off'}
              </button>
            </div>
          )}
        </div>
        
        <button 
          onClick={() => setVoiceEnabled(!voiceEnabled)}
          className={`transition-colors flex items-center gap-2 text-xs uppercase tracking-widest font-mono ${voiceEnabled ? 'text-white' : 'text-neutral-600'}`}
        >
          {voiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          {voiceEnabled ? 'Voice On' : 'Voice Off'}
        </button>
      </div>


      {/* Conversation History */}
      <div className="flex-1 overflow-y-auto px-4 pb-8 space-y-12 hide-scrollbar">
        {conversation.length === 0 && (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <p className="text-2xl font-light text-[#f2f2f2] mb-4">I'm listening.</p>
              <p className="text-neutral-500 tracking-wide">Say what's on your mind. We'll take it from there.</p>
            </div>
          </div>
        )}
        
        {conversation.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-blur-reveal`}>
            {msg.role === 'user' ? (
              <div className="max-w-[80%] text-right">
                <p className="text-lg md:text-xl font-light text-neutral-400 leading-relaxed">{msg.content}</p>
              </div>
            ) : (
              <div className="max-w-[85%] border-l-2 border-neutral-800 pl-6 py-2">
                <p className="text-xl md:text-3xl font-light text-[#f2f2f2] leading-tight tracking-tight">{msg.content}</p>
                {msg.should_suggest_music && (
                  <div className="mt-6">
                    <Link to="/" className="inline-block px-4 py-2 bg-[#1a1a1a] text-xs font-mono tracking-widest uppercase hover:bg-white hover:text-black transition-colors">
                      Listen to music
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        
        {isProcessing && (
          <div className="border-l-2 border-neutral-800 pl-6 py-2 animate-pulse">
            <p className="text-xl md:text-3xl font-light text-neutral-700 leading-tight">...</p>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="pt-4 pb-8 px-4 bg-gradient-to-t from-[#080808] via-[#080808] to-transparent shrink-0">
        <VoiceControl onSend={handleSendMessage} isProcessing={isProcessing} />
      </div>
      
    </div>
  );
}
