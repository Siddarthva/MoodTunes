import React from 'react';

export default function MusicAndEmotion() {
  return (
    <div className="w-full max-w-4xl mx-auto py-24 animate-fade-in-slow">
      <div className="mb-32">
        <h3 className="text-xs font-mono tracking-[0.3em] uppercase text-neutral-500 mb-8">
          Music & Emotion
        </h3>
        <h1 className="text-5xl md:text-7xl font-light tracking-tight leading-tight mb-8">
          Why can the same song feel <br className="hidden md:block" />
          <span className="italic text-neutral-400">completely different</span> to two people?
        </h1>
      </div>

      <div className="space-y-40">
        <section className="group">
          <div className="flex flex-col md:flex-row gap-8 md:gap-24">
            <h2 className="text-sm font-mono tracking-widest text-neutral-500 w-16">
              01<br />TEMPO
            </h2>
            <div className="flex-1 max-w-xl">
              <p className="text-3xl md:text-4xl font-light leading-snug mb-6 text-white group-hover:text-neutral-300 transition-colors">
                The pace of a song can change how its energy is perceived.
              </p>
              <p className="text-neutral-500 leading-relaxed text-sm">
                Tempo can influence perceived arousal and energy, but it does not deterministically cause a specific emotion. A fast song might be experienced as joyful, chaotic, or anxious depending on the listener's current state and expectations.
              </p>
              <div className="h-[1px] w-full bg-neutral-900 mt-12 group-hover:bg-neutral-800 transition-colors"></div>
            </div>
          </div>
        </section>

        <section className="group">
          <div className="flex flex-col md:flex-row gap-8 md:gap-24">
            <h2 className="text-sm font-mono tracking-widest text-neutral-500 w-16">
              02<br />MEMORY
            </h2>
            <div className="flex-1 max-w-xl">
              <p className="text-3xl md:text-4xl font-light leading-snug mb-6 text-white group-hover:text-neutral-300 transition-colors">
                A familiar melody can carry a completely personal history.
              </p>
              <p className="text-neutral-500 leading-relaxed text-sm">
                Individual memories and associations substantially alter the emotional response to a song. Music that is statistically classified as "happy" may evoke profound sadness if tied to a difficult memory, making musical experience inherently personal.
              </p>
              <div className="h-[1px] w-full bg-neutral-900 mt-12 group-hover:bg-neutral-800 transition-colors"></div>
            </div>
          </div>
        </section>

        <section className="group">
          <div className="flex flex-col md:flex-row gap-8 md:gap-24">
            <h2 className="text-sm font-mono tracking-widest text-neutral-500 w-16">
              03<br />HARMONY
            </h2>
            <div className="flex-1 max-w-xl">
              <p className="text-3xl md:text-4xl font-light leading-snug mb-6 text-white group-hover:text-neutral-300 transition-colors">
                Tension and resolution shape anticipation and release.
              </p>
              <p className="text-neutral-500 leading-relaxed text-sm">
                Harmonic structures build tonal expectations. The way a song delays or fulfills these expectations contributes heavily to its emotional weight, but cultural background dictates how these harmonic languages are understood.
              </p>
              <div className="h-[1px] w-full bg-neutral-900 mt-12 group-hover:bg-neutral-800 transition-colors"></div>
            </div>
          </div>
        </section>

        <section className="group">
          <div className="flex flex-col md:flex-row gap-8 md:gap-24">
            <h2 className="text-sm font-mono tracking-widest text-neutral-500 w-16">
              04<br />CONTEXT
            </h2>
            <div className="flex-1 max-w-xl">
              <p className="text-3xl md:text-4xl font-light leading-snug mb-6 text-white group-hover:text-neutral-300 transition-colors">
                The same song can feel different depending on where you are, what happened today, and what you need right now.
              </p>
              <p className="text-neutral-500 leading-relaxed text-sm">
                A recommendation system should respond to the listener's current signal and active intent, rather than assuming a universal emotional truth. Music does not force an emotion; it interacts with your state.
              </p>
            </div>
          </div>
        </section>
      </div>

      <div className="mt-40 pt-16 border-t border-neutral-900 text-center font-mono text-xs tracking-[0.2em] uppercase text-neutral-500 leading-loose">
        <p>Your State</p>
        <p>+</p>
        <p>The Music</p>
        <p>+</p>
        <p>Your Intent</p>
        <p className="text-white my-4">↓</p>
        <p className="text-white">A Different Listening Experience</p>
      </div>
    </div>
  );
}
