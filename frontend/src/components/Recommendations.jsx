import React, { useEffect, useState } from 'react';
import { Play, Pause, Heart, SkipForward } from 'lucide-react';
import { useMoodContext } from '../context/MoodContext';
import { getRecommendationHeading } from '../theme/emotionTheme';

export default function Recommendations({ tracks }) {
  const { 
    result,
    activeTrack, 
    setActiveTrack, 
    isPlaying, 
    setIsPlaying,
    likedTracks,
    likeTrack,
    skippedTracks,
    skipTrack
  } = useMoodContext();

  const [visibleItems, setVisibleItems] = useState([]);

  const recommendationHeading = getRecommendationHeading(result?.emotion?.probabilities);

  // Staggered fade in effect
  useEffect(() => {
    if (!tracks || tracks.length === 0) return;
    
    setVisibleItems([]);
    const timeouts = [];
    
    tracks.slice(0, 5).forEach((_, i) => {
      const timeout = setTimeout(() => {
        setVisibleItems(prev => [...prev, i]);
      }, 300 * i);
      timeouts.push(timeout);
    });
    
    return () => timeouts.forEach(clearTimeout);
  }, [tracks]);

  if (!tracks || tracks.length === 0) return null;

  // Filter out skipped tracks
  const visibleTracks = tracks.filter(t => !skippedTracks.includes(t.id)).slice(0, 5);

  const handlePlayToggle = (track) => {
    if (activeTrack?.id === track.id) {
      setIsPlaying(!isPlaying);
    } else {
      setActiveTrack(track);
      setIsPlaying(true);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto flex flex-col gap-12 pt-8 relative z-10">
      {/* Editorial Header */}
      <div className="text-center mb-8 animate-fade-in-slow">
        <h2 className="text-3xl md:text-5xl font-light tracking-tight text-white mb-4">
          {recommendationHeading}
        </h2>
        <p className="text-neutral-400 font-light text-lg">
          Not just songs that match the expression. Songs that fit the shape of the moment.
        </p>
      </div>

      {/* Editorial List */}
      <div className="w-full border-t border-neutral-900">
        {visibleTracks.map((track, index) => {
          const isActive = activeTrack?.id === track.id;
          const isLiked = likedTracks.includes(track.id);
          const isVisible = visibleItems.includes(index);
          const whyFits = track.source_metadata?.why_this_fits || "Fits the shape of the moment.";

          return (
            <div 
              key={track.id}
              className={`group flex flex-col lg:flex-row lg:items-center justify-between py-8 border-b border-neutral-900/80 transition-all duration-700 hover:bg-white/[0.01] ${isActive ? 'bg-white/[0.03]' : ''} ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
              style={{
                borderColor: isActive ? 'var(--mood-primary, #ffffff)' : undefined,
                boxShadow: isActive ? '0 0 25px var(--mood-glow, rgba(255,255,255,0.05))' : undefined
              }}
            >
              {/* Left Side: Number, Artwork, Title/Artist */}
              <div className="flex items-start lg:items-center gap-6 flex-1 min-w-0 mb-6 lg:mb-0">
                <span className="font-mono text-xs text-neutral-600 w-6 hidden md:block mt-2 lg:mt-0">
                  {String(index + 1).padStart(2, '0')}
                </span>
                
                <div className="relative w-20 h-20 md:w-24 md:h-24 bg-neutral-900 overflow-hidden flex-shrink-0">
                  {track.artworkUrl ? (
                    <img 
                      src={track.artworkUrl.replace('100x100', '300x300')} 
                      alt={track.title} 
                      className={`w-full h-full object-cover transition-transform duration-1000 ${isActive ? 'scale-105' : 'group-hover:scale-110'} grayscale group-hover:grayscale-0`}
                    />
                  ) : (
                    <div className="w-full h-full bg-neutral-800"></div>
                  )}
                  {isActive && (
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                      <div className="flex gap-1 items-end h-4">
                        <div className="w-1 bg-white animate-[bounce_1s_infinite] h-4"></div>
                        <div className="w-1 bg-white animate-[bounce_1s_infinite_100ms] h-2"></div>
                        <div className="w-1 bg-white animate-[bounce_1s_infinite_200ms] h-3"></div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-2 flex-1 min-w-0">
                  <h4 className={`text-xl md:text-3xl font-light tracking-tight truncate ${isActive ? 'text-white' : 'text-neutral-200 group-hover:text-white transition-colors duration-500'}`}>
                    {track.title}
                  </h4>
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-sm md:text-base text-neutral-400 tracking-wide truncate">
                      {track.artist}
                    </span>
                    <span className="text-neutral-800">•</span>
                    <span className="text-xs text-neutral-600 font-mono uppercase tracking-widest">
                      {track.source}
                    </span>
                  </div>
                </div>
              </div>

              {/* Right Side: Reason, Actions */}
              <div className="flex flex-col lg:flex-row items-start lg:items-center gap-6 lg:gap-12 pl-0 md:pl-12 lg:pl-4">
                <div className="w-full lg:w-48 xl:w-64">
                  <p className="text-[10px] uppercase font-mono tracking-[0.2em] text-neutral-600 mb-1">Why this fits</p>
                  <p className="text-xs font-mono text-neutral-400 tracking-wide leading-relaxed">
                    {whyFits}
                  </p>
                </div>

                <div className="flex items-center gap-4 text-neutral-500 w-full lg:w-auto justify-end lg:justify-start pt-4 lg:pt-0 border-t lg:border-t-0 border-neutral-900 lg:border-none">
                  <button 
                    onClick={() => likeTrack(track.id)}
                    className={`p-2 transition-colors duration-300 ${isLiked ? 'text-white' : 'hover:text-white'}`}
                    aria-label="Like track"
                  >
                    <Heart size={20} className={isLiked ? 'fill-white' : ''} />
                  </button>
                  <button 
                    onClick={() => skipTrack(track.id)}
                    className="p-2 hover:text-white transition-colors duration-300"
                    title="Skip and replace"
                    aria-label="Skip track"
                  >
                    <SkipForward size={20} />
                  </button>
                  <button 
                    onClick={() => handlePlayToggle(track)}
                    disabled={!track.previewUrl}
                    aria-label={isActive && isPlaying ? "Pause track" : "Play track"}
                    className={`ml-2 p-4 rounded-full border transition-all duration-300 ${isActive ? 'border-white text-black bg-white scale-105' : 'border-neutral-700 hover:border-white hover:text-white text-neutral-400 group-hover:border-neutral-500'} disabled:opacity-30 disabled:hover:border-neutral-700 disabled:hover:text-neutral-400 disabled:scale-100`}
                  >
                    {isActive && isPlaying ? <Pause size={20} /> : <Play size={20} className={!isActive && !isPlaying ? 'ml-0.5' : ''} />}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
