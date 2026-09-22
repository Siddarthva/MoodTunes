import React from 'react';

export default function MusicEmotionEditorial() {
  return (
    <div className="w-full max-w-4xl mx-auto py-16 px-4 animate-fade-in-slow">
      <div className="border border-neutral-900 bg-[#0a0a0a] p-12 md:p-16 text-center">
        <p className="text-xs uppercase tracking-[0.2em] font-mono text-neutral-500 mb-6">
          The Science of Sound
        </p>
        <h4 className="text-2xl md:text-3xl font-light text-[#f2f2f2] leading-relaxed mb-8 max-w-3xl mx-auto">
          Music doesn't dictate how a moment feels. It influences it.
        </h4>
        <p className="text-neutral-400 font-light leading-loose max-w-2xl mx-auto mb-6">
          People do not respond identically to the same song. Tempo, energy, familiarity, context, and personal taste all matter. MoodTunes treats your facial expression as one signal rather than a definitive emotional label.
        </p>
        <p className="text-neutral-500 font-mono text-sm tracking-wide">
          The recommendation is an exploration, not a prescription.
        </p>
      </div>
    </div>
  );
}
