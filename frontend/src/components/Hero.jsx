import React from 'react';

export default function Hero({ analysisState }) {
  if (analysisState !== 'idle') return null;

  return (
    <div className="animate-blur-reveal text-center mt-20 mb-16 max-w-2xl mx-auto">
      <h1 className="text-4xl md:text-6xl font-light tracking-tight mb-6">
        Find the sound that meets you <span className="italic text-neutral-400">where you are.</span>
      </h1>
      <p className="text-neutral-500 tracking-wide text-lg max-w-xl mx-auto">
        MoodTunes reads the emotional pattern in your expression and shapes a music direction around it.
      </p>
    </div>
  );
}
