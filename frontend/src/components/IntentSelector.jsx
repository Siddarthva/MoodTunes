import React from 'react';
import { useMoodContext } from '../context/MoodContext';

const INTENT_OPTIONS = [
  { id: 'match_me', label: 'Match me' },
  { id: 'lift_my_mood', label: 'Lift my mood' },
  { id: 'help_me_relax', label: 'Help me relax' },
  { id: 'help_me_focus', label: 'Help me focus' },
  { id: 'give_me_energy', label: 'Give me energy' },
  { id: 'surprise_me', label: 'Surprise me' }
];

export default function IntentSelector() {
  const { intent, setIntent, analysisState } = useMoodContext();
  const isDisabled = analysisState === 'analyzing' || analysisState === 'capturing';

  return (
    <div className="w-full max-w-xl mx-auto my-16 text-center animate-fade-in-slow">
      <h3 className="text-sm font-mono tracking-[0.2em] uppercase text-neutral-500 mb-8">
        What do you want from the music?
      </h3>
      <div className="flex flex-wrap justify-center gap-6">
        {INTENT_OPTIONS.map((opt) => (
          <button
            key={opt.id}
            onClick={() => setIntent(opt.id)}
            disabled={isDisabled}
            className={`text-sm tracking-wide transition-all duration-500 pb-1 border-b ${
              intent === opt.id
                ? 'text-white border-white'
                : 'text-neutral-500 border-transparent hover:text-neutral-300'
            } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
