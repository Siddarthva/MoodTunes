import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function MusicPlayer({ activeTrack, isPlaying, setIsPlaying }) {
  const audioRef = useRef(null);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (!audioRef.current) return;
    if (activeTrack && activeTrack.previewUrl) {
      audioRef.current.src = activeTrack.previewUrl;
      audioRef.current.play()
        .then(() => setIsPlaying(true))
        .catch(() => setIsPlaying(false));
    } else {
      setIsPlaying(false);
    }
  }, [activeTrack]);

  const togglePlay = () => {
    if (!audioRef.current || !activeTrack?.previewUrl) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setProgress(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const formatTime = (secs) => {
    if (isNaN(secs)) return '0:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (!activeTrack) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 30 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="fixed bottom-0 left-0 right-0 z-50 bg-[#070707]/95 border-t border-neutral-900 px-6 py-4 backdrop-blur-md"
      >
        <audio
          ref={audioRef}
          onTimeUpdate={handleTimeUpdate}
          onEnded={() => setIsPlaying(false)}
        />

        <div className="max-w-5xl mx-auto flex items-center justify-between gap-6">
          {/* Left: Metadata */}
          <div className="flex items-center gap-4 min-w-0">
            {activeTrack.artworkUrl && (
              <div className="w-10 h-10 bg-neutral-900 overflow-hidden flex-shrink-0">
                <img
                  src={activeTrack.artworkUrl}
                  alt={activeTrack.title}
                  className="w-full h-full object-cover filter grayscale"
                />
              </div>
            )}
            <div className="min-w-0">
              <p className="text-xs font-bold text-white truncate">{activeTrack.title}</p>
              <p className="text-[10px] text-neutral-500 font-mono truncate">{activeTrack.artist}</p>
            </div>
          </div>

          {/* Center: Play/Pause & Scrubber */}
          <div className="flex flex-col items-center flex-grow max-w-md">
            <button
              onClick={togglePlay}
              disabled={!activeTrack.previewUrl}
              className="w-8 h-8 flex items-center justify-center rounded-full text-white hover:text-neutral-300 transition-transform active:scale-95 disabled:opacity-30 font-mono text-xs"
            >
              {isPlaying ? '❚❚' : '▶'}
            </button>

            <div className="w-full flex items-center gap-3 mt-1 text-[10px] font-mono text-neutral-600">
              <span>{formatTime(progress)}</span>
              <div className="flex-grow h-[2px] bg-neutral-900 overflow-hidden">
                <div
                  className="h-full bg-neutral-300 transition-all duration-100"
                  style={{ width: `${duration ? (progress / duration) * 100 : 0}%` }}
                />
              </div>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Right: Source Metadata */}
          <div className="hidden sm:block font-mono text-[10px] text-neutral-600 uppercase tracking-widest">
            {activeTrack.source}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
