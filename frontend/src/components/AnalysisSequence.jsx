import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ANALYSIS_STEPS = [
  "ANALYZING",
  "FACE DETECTED",
  "READING EXPRESSION",
  "MOOD IDENTIFIED",
  "BUILDING SOUNDTRACK"
];

export default function AnalysisSequence({ isAnalyzing }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState("");
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (!isAnalyzing) {
      setCurrentStepIndex(0);
      setDisplayedText("");
      setCharIndex(0);
      return;
    }

    const currentTarget = ANALYSIS_STEPS[currentStepIndex];

    if (charIndex < currentTarget.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + currentTarget[charIndex]);
        setCharIndex(prev => prev + 1);
      }, 30);
      return () => clearTimeout(timeout);
    } else {
      const holdTimeout = setTimeout(() => {
        if (currentStepIndex < ANALYSIS_STEPS.length - 1) {
          setCurrentStepIndex(prev => prev + 1);
          setDisplayedText("");
          setCharIndex(0);
        }
      }, 650);
      return () => clearTimeout(holdTimeout);
    }
  }, [isAnalyzing, currentStepIndex, charIndex]);

  if (!isAnalyzing) return null;

  return (
    <div className="my-10 text-center">
      <AnimatePresence mode="wait">
        <motion.p
          key={displayedText}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="font-mono text-xs tracking-[0.25em] text-neutral-300 uppercase"
        >
          {displayedText}<span className="animate-pulse">▌</span>
        </motion.p>
      </AnimatePresence>
    </div>
  );
}
