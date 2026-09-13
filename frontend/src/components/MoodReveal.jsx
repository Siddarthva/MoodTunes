import React from 'react';
import { motion } from 'framer-motion';

export default function MoodReveal({ result }) {
  if (!result || !result.emotion || !result.emotional_profile) return null;

  const { emotion, emotional_profile } = result;

  // Define the ordered emotions for the profile breakdown
  const profileItems = [
    { label: "Happy", value: emotion.probabilities.happy },
    { label: "Sad", value: emotion.probabilities.sad },
    { label: "Surprise", value: emotion.probabilities.surprise },
    { label: "Fear", value: emotion.probabilities.fear },
    { label: "Angry", value: emotion.probabilities.angry },
    { label: "Neutral", value: emotion.probabilities.neutral },
    { label: "Disgust", value: emotion.probabilities.disgust }
  ].sort((a, b) => b.value - a.value);

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, filter: 'blur(20px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
      className="max-w-4xl mx-auto my-20 text-center px-4"
    >
      <p className="text-[11px] font-mono uppercase tracking-[0.3em] text-neutral-500 mb-4">
        YOUR MOOD
      </p>

      {/* Dramatic Oversized Emotion Heading */}
      <h2 className="text-[clamp(80px,18vw,260px)] font-extrabold uppercase tracking-[-0.05em] leading-[0.8] text-gradient mb-3 select-none">
        {emotion.dominant}
      </h2>

      {/* Dominant Confidence */}
      <p className="text-[11px] font-mono text-neutral-600 tracking-widest mb-16">
        {emotion.confidence.toFixed(1)}% confidence
      </p>

      {/* Subtle Emotional Profile Breakdown */}
      <div className="max-w-md mx-auto mb-16">
        <p className="text-[10px] font-mono uppercase tracking-[0.2em] text-neutral-500 mb-6 text-left border-b border-neutral-900 pb-2">
          EMOTIONAL PROFILE
        </p>
        <div className="flex flex-col gap-3 font-mono text-xs">
          {profileItems.map((item) => (
            <div key={item.label} className="flex items-center">
              <span className="w-24 text-left text-neutral-400">{item.label}</span>
              <div className="flex-1 flex items-center">
                <span className="text-neutral-700 tracking-tighter">
                  {'━'.repeat(Math.ceil((item.value / 100) * 20))}
                </span>
              </div>
              <span className="w-16 text-right text-neutral-500">
                {item.value.toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Clean Tonal Metrics (Weighted) */}
      <div className="grid grid-cols-3 gap-8 max-w-md mx-auto pt-6 border-t border-neutral-900 font-mono">
        <div>
          <span className="block text-[10px] text-neutral-500 uppercase tracking-[0.2em] mb-1">Energy</span>
          <span className="text-xl text-neutral-200 font-medium">{emotional_profile.energy}</span>
        </div>
        <div>
          <span className="block text-[10px] text-neutral-500 uppercase tracking-[0.2em] mb-1">Valence</span>
          <span className="text-xl text-neutral-200 font-medium">{emotional_profile.valence}</span>
        </div>
        <div>
          <span className="block text-[10px] text-neutral-500 uppercase tracking-[0.2em] mb-1">Tempo</span>
          <span className="text-xl text-neutral-200 font-medium uppercase">{emotional_profile.tempo}</span>
        </div>
      </div>
    </motion.div>
  );
}
