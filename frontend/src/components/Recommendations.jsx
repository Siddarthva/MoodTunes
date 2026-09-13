import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Recommendations({ tracks, activeTrack, isPlaying, onSelectTrack }) {
  const [hoveredTrack, setHoveredTrack] = useState(null);

  if (!tracks || tracks.length === 0) return null;

  return (
    <div className="max-w-4xl mx-auto my-24 px-4">
      <p className="text-[11px] font-mono uppercase tracking-[0.3em] text-neutral-500 mb-10 text-center">
        YOUR SOUNDTRACK
      </p>

      <div className="relative">
        {tracks.map((track, idx) => {
          const isCurrent = activeTrack && activeTrack.id === track.id;
          const numStr = (idx + 1).toString().padStart(2, '0');
          const isHovered = hoveredTrack && hoveredTrack.id === track.id;

          return (
            <div
              key={track.id}
              onMouseEnter={() => setHoveredTrack(track)}
              onMouseLeave={() => setHoveredTrack(null)}
              onClick={() => onSelectTrack(track)}
              className="group relative flex items-center justify-between py-6 border-b border-neutral-900 cursor-pointer transition-colors duration-300"
            >
              {/* Left Column: Number + Title + Artist */}
              <div className="flex items-center gap-6 md:gap-10 min-w-0 z-10">
                <span className="font-mono text-xs text-neutral-600 group-hover:text-neutral-300 transition-colors">
                  {numStr}
                </span>

                <div className="min-w-0">
                  <h4 className={`text-xl md:text-2xl font-bold tracking-tight transition-all duration-300 group-hover:translate-x-2 ${isCurrent ? 'text-white' : 'text-neutral-300 group-hover:text-white'}`}>
                    {track.title}
                  </h4>
                  <p className="text-xs text-neutral-500 font-light mt-1">
                    {track.artist} &bull; <span className="font-mono text-[10px] uppercase text-neutral-600">{track.album}</span>
                  </p>
                </div>
              </div>

              {/* Right Column: Subtle Minimal Play Trigger */}
              <div className="flex items-center gap-8 z-10 flex-shrink-0">
                <div className="text-right hidden sm:block font-mono text-[10px] text-neutral-600 uppercase tracking-widest">
                  {track.matchScore}% MATCH
                </div>

                <button
                  disabled={!track.previewUrl}
                  className="w-10 h-10 flex items-center justify-center rounded-full border border-neutral-800 text-neutral-400 group-hover:border-white group-hover:text-white transition-all duration-300 disabled:opacity-20"
                >
                  <span className="font-mono text-xs">
                    {isCurrent && isPlaying ? '❚❚' : '▶'}
                  </span>
                </button>
              </div>

              {/* Hover Artwork Reveal Effect */}
              <AnimatePresence>
                {isHovered && track.artworkUrl && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.94, filter: 'blur(8px)' }}
                    animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, scale: 0.94, filter: 'blur(8px)' }}
                    transition={{ duration: 0.3 }}
                    className="absolute right-24 top-1/2 -translate-y-1/2 w-20 h-20 bg-neutral-900 overflow-hidden pointer-events-none hidden md:block z-20 shadow-2xl"
                  >
                    <img
                      src={track.artworkUrl}
                      alt={track.title}
                      className="w-full h-full object-cover filter grayscale contrast-110"
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
