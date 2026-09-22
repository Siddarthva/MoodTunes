import React from 'react';

export default function HowItWorks() {
  const steps = [
    { title: "Camera", desc: "A secure, client-side feed captures your expression in real time." },
    { title: "Face detection", desc: "Haar cascade detects and isolates the primary face for analysis." },
    { title: "Emotion model", desc: "A FER2013-trained CNN outputs a raw probability distribution." },
    { title: "Seven-emotion profile", desc: "Scores across 7 emotions are mapped into energy and valence coordinates." },
    { title: "Music intelligence", desc: "Groq analyzes the profile and user intent to build a search strategy." },
    { title: "Real music search", desc: "The API fetches real track candidates from iTunes." },
    { title: "Recommendation ranking", desc: "Tracks are deterministically scored, deduplicated, and diversified by artist." }
  ];

  return (
    <div className="w-full max-w-3xl mx-auto py-24 animate-fade-in-slow">
      <h3 className="text-xs font-mono tracking-[0.3em] uppercase text-neutral-500 mb-24">
        How It Works
      </h3>
      
      <div className="flex flex-col gap-12">
        {steps.map((step, idx) => (
          <div key={idx} className="flex gap-8 group">
            <span className="font-mono text-xs text-neutral-600 mt-1 w-8">
              {String(idx + 1).padStart(2, '0')}
            </span>
            <div className="flex-1 pb-12 border-b border-neutral-900 group-last:border-0">
              <h2 className="text-2xl md:text-3xl font-light text-white mb-3 tracking-tight">
                {step.title}
              </h2>
              <p className="text-neutral-500 text-sm tracking-wide">
                {step.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
