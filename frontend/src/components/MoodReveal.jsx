import React, { useEffect, useState } from 'react';
import { interpretMood } from '../services/api';
import { BASE_EMOTION_PALETTES } from '../theme/emotionTheme';

export default function MoodReveal({ result }) {
  if (!result || !result.emotion || !result.emotional_profile) return null;

  const { emotion, emotional_profile } = result;

  // 1. Extract emotion probabilities
  const probMap = emotion.probabilities || {};
  const allEmotions = Object.entries(probMap).map(([name, val]) => ({
    name: name.toUpperCase(),
    val: parseFloat(val).toFixed(1)
  })).sort((a, b) => b.val - a.val);

  // 2. Determine dominant emotion & confidence
  const dominant = allEmotions[0] || { name: 'NEUTRAL', val: '0.0' };
  
  // 3. Calculate secondary mood support text
  const secondaryEmotions = allEmotions.filter(e => e.val > 5.0 && e.name !== dominant.name);
  let supportText = "";
  if (secondaryEmotions.length > 0) {
    const names = secondaryEmotions.map(e => `${e.name} (${e.val}%)`);
    supportText = `with traces of ${names.join(' and ')}`;
  }

  const getEmotionColorHex = (name) => {
    const key = (name || '').toLowerCase();
    return BASE_EMOTION_PALETTES[key]?.hex || '#B5B5B5';
  };
  
  // 4. Fetch Groq Interpretation
  const [interpretation, setInterpretation] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    const fetchInterpretation = async () => {
      try {
        const content = await interpretMood(emotion, emotional_profile);
        if (isMounted) setInterpretation(content);
      } catch (e) {
        console.error("Failed to fetch mood interpretation:", e);
      }
    };
    
    if (dominant && emotional_profile) {
      fetchInterpretation();
    }
    
    return () => { isMounted = false; };
  }, [dominant?.name, emotional_profile]);


  // Original emotion ordering: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral
  const spectrumOrder = ['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL'];
  const spectrumData = spectrumOrder.map(name => {
    const found = allEmotions.find(e => e.name === name);
    return found || { name, val: '0.0' };
  });

  return (
    <div className="w-full max-w-5xl mx-auto pt-6 pb-20 animate-fade-in-slow relative z-10">
      {/* 1. Cinematic Borderless Mood Title & Confidence */}
      <div className="text-center mb-20">
        <p className="text-[10px] font-mono uppercase tracking-[0.45em] text-neutral-500 mb-6">
          Detected Emotional Spectrum
        </p>
        <h1 
          className="text-7xl md:text-9xl lg:text-[10.5rem] font-bold tracking-tighter leading-none mb-4 uppercase transition-all duration-1000"
          style={{ 
            color: 'var(--mood-primary, #ffffff)',
            textShadow: '0 0 50px var(--mood-glow, rgba(255,255,255,0.15))'
          }}
        >
          {dominant.name}
          <span className="text-xl md:text-3xl text-neutral-500 font-light ml-3 md:ml-6 tracking-normal align-top">
            {dominant.val}%
          </span>
        </h1>
        {supportText && (
          <p className="text-lg md:text-2xl font-light text-neutral-400 tracking-tight lowercase">
            {supportText}
          </p>
        )}
      </div>

      {/* 2. Continuous 6px Horizontal Spectrum Ribbon */}
      <div className="w-full max-w-4xl mx-auto mb-20">
        <p className="text-[9px] uppercase tracking-[0.35em] text-neutral-500 mb-4 text-center font-mono">
          Seven-Class Distribution Ribbon
        </p>
        <div className="flex w-full h-1.5 bg-neutral-900/90 rounded-full overflow-hidden mb-5 p-[0.5px]">
          {spectrumData.map((emo) => {
            const width = parseFloat(emo.val);
            if (width < 0.1) return null;
            const isDominant = emo.name === dominant.name;
            return (
              <div 
                key={`bar-${emo.name}`}
                className="h-full transition-all duration-1000 ease-out"
                style={{ 
                  width: `${width}%`, 
                  backgroundColor: getEmotionColorHex(emo.name),
                  opacity: width < 10 ? 0.45 : 0.95,
                  boxShadow: isDominant ? '0 0 12px var(--mood-glow, rgba(255,255,255,0.3))' : undefined
                }}
                title={`${emo.name}: ${emo.val}%`}
              ></div>
            );
          })}
        </div>
        <div className="flex justify-between w-full px-1">
          {spectrumData.map((emo) => {
            const isDominant = emo.name === dominant.name;
            const width = parseFloat(emo.val);
            if (width < 4 && !isDominant) return null;
            return (
              <div key={`label-${emo.name}`} className={`flex flex-col items-center transition-opacity duration-1000 ${isDominant ? 'opacity-100 font-semibold' : 'opacity-40'}`}>
                <span className="text-[9px] font-mono tracking-widest" style={{ color: getEmotionColorHex(emo.name) }}>{emo.name}</span>
                <span className="text-[8px] font-mono text-neutral-500">{emo.val}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Single Editorial Information Row (Borderless with Hairline Dividers) */}
      <div className="max-w-4xl mx-auto grid grid-cols-3 font-mono text-center border-t border-b border-white/[0.06] py-8 mb-20">
        <div className="border-r border-white/[0.06] px-4">
          <span className="block text-[9px] uppercase tracking-[0.25em] text-neutral-500 mb-1">Energy</span>
          <span className="text-xl md:text-2xl text-neutral-200 font-light">{parseFloat(emotional_profile.energy).toFixed(1)}</span>
        </div>
        <div className="border-r border-white/[0.06] px-4">
          <span className="block text-[9px] uppercase tracking-[0.25em] text-neutral-500 mb-1">Valence</span>
          <span className="text-xl md:text-2xl text-neutral-200 font-light">{parseFloat(emotional_profile.valence).toFixed(1)}</span>
        </div>
        <div className="px-4">
          <span className="block text-[9px] uppercase tracking-[0.25em] text-neutral-500 mb-1">Tempo</span>
          <span className="text-xl md:text-2xl text-neutral-200 font-light uppercase">{emotional_profile.tempo}</span>
        </div>
      </div>

      {/* 4. Short Groq Interpretation & Contextual Reflection */}
      <div className="max-w-3xl mx-auto text-center">
        {interpretation ? (
          <div className="animate-fade-in-slow">
            <h3 className="text-3xl md:text-4xl font-light text-[#f2f2f2] leading-tight mb-4">
              "{interpretation.headline || 'A moment in focus'}"
            </h3>
            <p className="text-lg font-light text-neutral-400 leading-relaxed mb-6">
              {interpretation.reflection}
            </p>
            {interpretation.spectrum_summary && (
              <p className="text-xs font-mono uppercase tracking-[0.25em] text-neutral-500">
                {interpretation.spectrum_summary}
              </p>
            )}
          </div>
        ) : (
          <div className="animate-pulse flex flex-col items-center gap-6">
            <div className="h-10 w-3/4 bg-neutral-900/60 rounded"></div>
            <div className="h-6 w-1/2 bg-neutral-900/60 rounded"></div>
          </div>
        )}
      </div>
    </div>
  );
}

