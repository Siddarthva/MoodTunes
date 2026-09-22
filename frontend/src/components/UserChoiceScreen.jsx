import React from 'react';
import { Music, MessageSquare } from 'lucide-react';

export default function UserChoiceScreen({ onSelectChoice, selectedChoice }) {
  return (
    <div className="w-full max-w-4xl mx-auto pt-4 pb-16 animate-fade-in-slow text-center relative z-10">
      <div className="mb-12">
        <h2 className="text-3xl md:text-5xl font-light tracking-tight text-white mb-4">
          What would you like to do with this moment?
        </h2>
        <p className="text-neutral-400 font-light text-lg">
          You can find a soundtrack, or simply talk.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4">
        {/* Choice 1: Music Soundtrack */}
        <button
          onClick={() => onSelectChoice('music')}
          className={`group relative p-8 md:p-10 rounded-2xl border text-left transition-all duration-500 flex flex-col justify-between min-h-[240px] ${
            selectedChoice === 'music'
              ? 'border-white bg-white/[0.06] shadow-[0_0_40px_var(--mood-glow,rgba(255,255,255,0.15))]'
              : 'border-white/[0.08] bg-white/[0.02] hover:border-white/30 hover:bg-white/[0.04]'
          }`}
        >
          <div className="flex items-center justify-between mb-8">
            <div className="p-4 rounded-xl bg-white/[0.05] text-white group-hover:scale-110 transition-transform duration-500">
              <Music size={28} style={{ color: 'var(--mood-accent, #ffffff)' }} />
            </div>
            <span className="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-500">Path 01</span>
          </div>

          <div>
            <h3 className="text-2xl font-light text-white mb-2 group-hover:translate-x-1 transition-transform duration-300">
              Find my soundtrack
            </h3>
            <p className="text-sm font-light text-neutral-400 leading-relaxed">
              Turn this emotional spectrum into a personalized music session.
            </p>
          </div>

          <div 
            className="mt-6 h-0.5 w-12 rounded-full transition-all duration-500 group-hover:w-full"
            style={{ backgroundColor: 'var(--mood-accent, #ffffff)' }}
          ></div>
        </button>

        {/* Choice 2: Talk Experience */}
        <button
          onClick={() => onSelectChoice('talk')}
          className={`group relative p-8 md:p-10 rounded-2xl border text-left transition-all duration-500 flex flex-col justify-between min-h-[240px] ${
            selectedChoice === 'talk'
              ? 'border-white bg-white/[0.06] shadow-[0_0_40px_var(--mood-glow,rgba(255,255,255,0.15))]'
              : 'border-white/[0.08] bg-white/[0.02] hover:border-white/30 hover:bg-white/[0.04]'
          }`}
        >
          <div className="flex items-center justify-between mb-8">
            <div className="p-4 rounded-xl bg-white/[0.05] text-white group-hover:scale-110 transition-transform duration-500">
              <MessageSquare size={28} style={{ color: 'var(--mood-accent, #ffffff)' }} />
            </div>
            <span className="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-500">Path 02</span>
          </div>

          <div>
            <h3 className="text-2xl font-light text-white mb-2 group-hover:translate-x-1 transition-transform duration-300">
              Talk about it
            </h3>
            <p className="text-sm font-light text-neutral-400 leading-relaxed">
              Take the moment somewhere quieter and talk with MoodTunes.
            </p>
          </div>

          <div 
            className="mt-6 h-0.5 w-12 rounded-full transition-all duration-500 group-hover:w-full"
            style={{ backgroundColor: 'var(--mood-accent, #ffffff)' }}
          ></div>
        </button>
      </div>
    </div>
  );
}
