import React, { useRef, useEffect } from 'react';
import { Play, Pause, Volume2, SkipBack, SkipForward } from 'lucide-react';
import { useMoodContext } from '../context/MoodContext';

export default function MusicPlayer() {
  const { activeTrack, isPlaying, setIsPlaying, result } = useMoodContext();
  const audioRef = useRef(null);

  useEffect(() => {
    if (!audioRef.current) return;
    if (isPlaying && activeTrack?.previewUrl) {
      audioRef.current.play().catch(e => {
        console.error("Playback failed:", e);
        setIsPlaying(false);
      });
    } else {
      audioRef.current.pause();
    }
  }, [isPlaying, activeTrack, setIsPlaying]);

  const togglePlay = () => {
    if (activeTrack) {
      setIsPlaying(!isPlaying);
    }
  };

  const tracks = result?.recommendations || [];
  const currentIndex = tracks.findIndex(t => t.id === activeTrack?.id);

  if (!activeTrack) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 w-[calc(100%-3rem)] max-w-5xl glass-player rounded-2xl z-50 animate-fade-in-slow overflow-hidden">
      <audio 
        ref={audioRef} 
        src={activeTrack.previewUrl}
        onEnded={() => setIsPlaying(false)}
      />
      {/* Top Thin Progress Line inheriting mood accent */}
      <div 
        className="h-[2px] w-full transition-all duration-500" 
        style={{ 
          backgroundColor: isPlaying ? 'var(--mood-accent, #ffffff)' : 'rgba(255,255,255,0.1)',
          boxShadow: isPlaying ? '0 0 10px var(--mood-glow, rgba(255,255,255,0.4))' : undefined 
        }} 
      />
      <div className="px-6 h-20 flex flex-col md:flex-row items-center justify-between">
        
        {/* Left: Track Info & Artwork */}
        <div className="flex flex-row items-center gap-4 w-full md:w-1/3 min-w-0">
          <div 
            className="w-12 h-12 bg-neutral-900 rounded-lg overflow-hidden flex-shrink-0 transition-transform duration-500"
            style={{ boxShadow: isPlaying ? '0 0 15px var(--mood-glow, rgba(255,255,255,0.2))' : undefined }}
          >
            {activeTrack.artworkUrl ? (
              <img src={activeTrack.artworkUrl} alt={activeTrack.title} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full bg-neutral-800 flex items-center justify-center font-mono text-xs text-neutral-500">♫</div>
            )}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium text-white tracking-wide truncate">
              {activeTrack.title}
            </span>
            <span className="text-xs font-mono text-neutral-400 tracking-wider truncate">
              {activeTrack.artist}
            </span>
          </div>
        </div>

        {/* Center: Controls */}
        <div className="flex items-center gap-8 justify-center w-full md:w-1/3 my-2 md:my-0">
          <button className="text-neutral-500 hover:text-white transition-colors">
            <SkipBack size={18} />
          </button>
          
          <button 
            onClick={togglePlay}
            aria-label={isPlaying ? "Pause track" : "Play track"}
            className="w-10 h-10 flex items-center justify-center rounded-full text-black hover:scale-105 transition-all duration-300"
            style={{ 
              backgroundColor: 'var(--mood-primary, #ffffff)',
              boxShadow: '0 0 20px var(--mood-glow, rgba(255,255,255,0.3))' 
            }}
          >
            {isPlaying ? <Pause size={18} /> : <Play size={18} className="ml-0.5" />}
          </button>
          
          <button className="text-neutral-500 hover:text-white transition-colors">
            <SkipForward size={18} />
          </button>
        </div>

        {/* Right: Source Metadata */}
        <div className="hidden md:flex flex-row items-center justify-end gap-6 w-full md:w-1/3">
           <span className="text-[9px] font-mono text-neutral-400 uppercase tracking-widest border border-white/10 px-2.5 py-1 rounded-full bg-white/[0.02]">
             {activeTrack.source} Preview
           </span>
        </div>
      </div>
    </div>
  );
}
