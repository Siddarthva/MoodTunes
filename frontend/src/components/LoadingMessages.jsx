import React, { useState, useEffect } from 'react';

const MESSAGES = [
  "Reading the shape of the moment...",
  "Finding the right musical direction...",
  "Searching beyond the obvious...",
  "Curating a few possibilities...",
  "Choosing what belongs together..."
];

export default function LoadingMessages() {
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false); // trigger fade out
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % MESSAGES.length);
        setFade(true); // trigger fade in
      }, 500); // Wait for fade out to complete
    }, 3000); // Change message every 3 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center justify-center mt-12 h-16">
      <p 
        className={`text-neutral-500 font-mono tracking-widest uppercase text-xs transition-opacity duration-500 ${fade ? 'opacity-100' : 'opacity-0'}`}
      >
        {MESSAGES[index]}
      </p>
    </div>
  );
}
