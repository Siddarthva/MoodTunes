import React, { useState, useEffect } from 'react';

const STEPS = [
  "Reading expression",
  "Building emotional profile",
  "Finding the right musical direction",
  "Searching real music",
  "Curating your five"
];

export default function AnalysisSequence({ isAnalyzing }) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isAnalyzing) {
      setCurrentStep(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < STEPS.length - 1) return prev + 1;
        return prev; // hold at last step
      });
    }, 1200);

    return () => clearInterval(interval);
  }, [isAnalyzing]);

  if (!isAnalyzing) return null;

  return (
    <div className="w-full max-w-md mx-auto my-16 animate-fade-in-slow">
      <div className="flex flex-col gap-4 font-mono text-xs tracking-[0.2em] uppercase text-neutral-600">
        {STEPS.map((step, idx) => (
          <div 
            key={idx}
            className={`flex items-center gap-4 transition-all duration-700 ${
              idx === currentStep ? 'text-white' : idx < currentStep ? 'text-neutral-500' : 'text-neutral-800'
            }`}
          >
            <span className="w-6 text-right">0{idx + 1}</span>
            <span className="w-2 h-2 rounded-full border border-current" style={{ backgroundColor: idx <= currentStep ? 'currentColor' : 'transparent' }}></span>
            <span>{step}</span>
            {idx === currentStep && <span className="animate-pulse">▌</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
