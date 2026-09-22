import React, { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';
import { Camera, AlertCircle } from 'lucide-react';

export default function WebcamCapture({ onCapture, isAnalyzing, analysisState, onReset }) {
  const webcamRef = useRef(null);
  const [hasPermissionError, setHasPermissionError] = useState(false);

  const capture = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        fetch(imageSrc)
          .then(res => res.blob())
          .then(blob => onCapture(blob));
      }
    }
  }, [webcamRef, onCapture]);

  if (analysisState === 'success' || analysisState === 'error') {
    return null;
  }

  return (
    <div className="flex flex-col items-center w-full max-w-2xl mx-auto my-12 relative animate-fade-in-slow">
      {/* Editorial Frame with Thin Brackets */}
      <div className="relative p-1">
        {/* Top Left Bracket */}
        <div className="absolute top-0 left-0 w-8 h-8 border-t border-l pointer-events-none z-10 transition-colors duration-700" style={{ borderColor: isAnalyzing ? 'var(--mood-primary, #f2f2f2)' : '#404040' }}></div>
        {/* Top Right Bracket */}
        <div className="absolute top-0 right-0 w-8 h-8 border-t border-r pointer-events-none z-10 transition-colors duration-700" style={{ borderColor: isAnalyzing ? 'var(--mood-primary, #f2f2f2)' : '#404040' }}></div>
        {/* Bottom Left Bracket */}
        <div className="absolute bottom-0 left-0 w-8 h-8 border-b border-l pointer-events-none z-10 transition-colors duration-700" style={{ borderColor: isAnalyzing ? 'var(--mood-primary, #f2f2f2)' : '#404040' }}></div>
        {/* Bottom Right Bracket */}
        <div className="absolute bottom-0 right-0 w-8 h-8 border-b border-r pointer-events-none z-10 transition-colors duration-700" style={{ borderColor: isAnalyzing ? 'var(--mood-primary, #f2f2f2)' : '#404040' }}></div>
        
        <div className="relative overflow-hidden bg-[#0a0a0a] w-full max-w-[640px] aspect-video flex items-center justify-center">
          
          {hasPermissionError ? (
            <div className="text-center font-mono text-neutral-500 flex flex-col items-center gap-4">
              <AlertCircle size={20} className="opacity-50" />
              <p className="text-xs uppercase tracking-widest">Camera access required</p>
            </div>
          ) : (
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                width: 640,
                height: 480,
                facingMode: "user"
              }}
              onUserMediaError={() => setHasPermissionError(true)}
              className={`w-full h-full object-cover transition-all duration-1000 ${isAnalyzing ? 'grayscale contrast-125 opacity-40' : 'grayscale-0 opacity-100'}`}
            />
          )}

          {/* Monochrome Scanline overlay when analyzing */}
          {isAnalyzing && (
            <div className="absolute inset-0 w-full h-full pointer-events-none overflow-hidden">
              <div className="w-full h-full scanline animate-scanline"></div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-12 h-16 flex items-center justify-center">
        {!isAnalyzing && !hasPermissionError && (
          <button
            onClick={capture}
            className="group flex items-center gap-3 text-neutral-400 hover:text-white transition-colors"
          >
            <Camera size={16} className="transition-transform group-hover:scale-110" />
            <span className="text-xs font-mono uppercase tracking-[0.25em]">Read My Mood</span>
          </button>
        )}
        
        {isAnalyzing && (
          <div className="flex flex-col items-center gap-2">
            <span className="text-xs font-mono uppercase tracking-[0.25em] text-neutral-300">
              Analyzing Signal
            </span>
            <span className="text-neutral-600 animate-pulse">▌</span>
          </div>
        )}
      </div>
    </div>
  );
}
