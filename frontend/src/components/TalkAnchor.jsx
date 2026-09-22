import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMoodContext } from '../context/MoodContext';

export default function TalkAnchor() {
  const navigate = useNavigate();
  const { result } = useMoodContext();

  const handleNavigate = () => {
    // The MoodContext is global, so /talk will naturally have access to `result`
    navigate('/talk');
  };

  return (
    <div className="w-full py-32 px-4 flex flex-col items-center animate-fade-in-slow text-center">
      <p className="text-xs font-mono uppercase tracking-[0.3em] text-neutral-500 mb-6">
        Still got something on your mind?
      </p>
      
      <h2 className="text-4xl md:text-6xl font-light tracking-tight text-white mb-8">
        The music is one way to talk about it.
      </h2>
      
      <p className="text-lg text-neutral-400 font-light max-w-xl mb-12">
        Talk to MoodTunes about whatever is on your mind. You can bring the current mood context with you, or simply start talking.
      </p>
      
      <button 
        onClick={handleNavigate}
        className="group relative px-12 py-4 bg-transparent border-none cursor-pointer flex flex-col items-center gap-3"
      >
        <span className="uppercase tracking-[0.3em] text-sm font-mono text-white transition-colors group-hover:text-amber-500/90 z-10">
          Talk to MoodTunes
        </span>
        
        <div className="w-full h-px bg-neutral-800 relative overflow-hidden">
          <div className="absolute inset-0 bg-amber-500/80 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-out"></div>
        </div>
        
        <span className="text-xs text-neutral-600 font-mono transition-colors group-hover:text-neutral-400">
          Continue to the conversation
        </span>
      </button>
    </div>
  );
}
