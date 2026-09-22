import React, { useEffect, useState } from 'react';
import { getPostScanContent } from '../services/api';

export default function EditorialQuote({ result }) {
  const [content, setContent] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchContent = async () => {
      try {
        const data = await getPostScanContent(
          result.emotion.dominant,
          result.emotional_profile,
          result.emotional_profile.energy,
          result.emotional_profile.valence,
          result.user_intent
        );
        if (isMounted) setContent(data);
      } catch (e) {
        console.error("Failed to fetch post scan content:", e);
      }
    };
    
    if (result) {
      fetchContent();
    }
    
    return () => { isMounted = false; };
  }, [result]);

  if (!content) {
    return (
      <div className="w-full max-w-4xl mx-auto py-24 px-4 animate-pulse">
        <div className="h-16 w-3/4 bg-neutral-900 rounded mb-8"></div>
        <div className="h-6 w-1/2 bg-neutral-900 rounded"></div>
      </div>
    );
  }

  const headlineText = content.headline || content.quote || "A moment in sound.";
  const reflectionText = content.reflection || "The sound meets you right where you are.";

  return (
    <div className="w-full max-w-4xl mx-auto py-24 px-4 animate-fade-in-slow text-center relative z-10">
      <div className="flex justify-center mb-8">
        <div className="h-12 w-px bg-neutral-800"></div>
      </div>
      
      <p className="text-xs uppercase tracking-widest font-mono text-neutral-500 mb-8">
        MoodTunes Reflection
      </p>
      
      <h3 
        className="text-4xl md:text-5xl lg:text-6xl font-light leading-tight mb-8"
        style={{ color: 'var(--mood-text-accent, #ffffff)' }}
      >
        "{headlineText}"
      </h3>
      
      <p className="text-lg md:text-xl font-light text-neutral-400 leading-relaxed max-w-2xl mx-auto mb-6">
        {reflectionText}
      </p>

      {content.music_intro && (
        <p className="text-sm font-mono text-neutral-500 uppercase tracking-widest">
          {content.music_intro}
        </p>
      )}
      
      <div className="flex justify-center mt-12">
        <div className="h-12 w-px bg-neutral-800"></div>
      </div>
    </div>
  );
}
