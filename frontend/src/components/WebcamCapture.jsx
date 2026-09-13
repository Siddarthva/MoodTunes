import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: "user"
};

export default function WebcamCapture({ onCapture, isAnalyzing }) {
  const webcamRef = useRef(null);
  const [cameraError, setCameraError] = useState(null);

  const captureFrame = useCallback(() => {
    if (!webcamRef.current) return;
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    fetch(imageSrc)
      .then(res => res.blob())
      .then(blob => {
        onCapture(blob);
      });
  }, [webcamRef, onCapture]);

  const handleUserMediaError = useCallback(() => {
    setCameraError("Camera access is required to read your expression.");
  }, []);

  return (
    <div className="relative max-w-2xl mx-auto my-12 px-4">
      {/* Editorial Open Camera Container - No cards, no borders */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98, filter: 'blur(10px)' }}
        animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        className="relative bg-[#0a0a0a] overflow-hidden shadow-2xl"
      >
        {/* Minimal Corner Brackets */}
        <div className="absolute top-4 left-4 w-3 h-3 border-t border-l border-neutral-400 z-20 pointer-events-none opacity-60" />
        <div className="absolute top-4 right-4 w-3 h-3 border-t border-r border-neutral-400 z-20 pointer-events-none opacity-60" />
        <div className="absolute bottom-4 left-4 w-3 h-3 border-b border-l border-neutral-400 z-20 pointer-events-none opacity-60" />
        <div className="absolute bottom-4 right-4 w-3 h-3 border-b border-r border-neutral-400 z-20 pointer-events-none opacity-60" />

        {/* Subtle Monochrome Scanline on analysis */}
        {isAnalyzing && (
          <div className="absolute inset-0 scanline animate-scanline z-10 pointer-events-none opacity-50" />
        )}

        {cameraError ? (
          <div className="h-[360px] flex items-center justify-center p-6 text-center text-neutral-400 font-mono text-xs tracking-wider uppercase">
            {cameraError}
          </div>
        ) : (
          <div className="relative aspect-[4/3] bg-[#070707] flex items-center justify-center">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.88}
              videoConstraints={videoConstraints}
              onUserMediaError={handleUserMediaError}
              className={`w-full h-full object-cover filter grayscale contrast-105 transition-all duration-700 ${isAnalyzing ? 'brightness-75 blur-[1px]' : ''}`}
            />
          </div>
        )}
      </motion.div>

      {/* Minimal Editorial Action Link */}
      <div className="mt-8 text-center">
        <button
          onClick={captureFrame}
          disabled={isAnalyzing || !!cameraError}
          className="group inline-flex items-center gap-3 text-xs font-mono uppercase tracking-[0.25em] text-neutral-300 hover:text-white transition-colors py-2 disabled:opacity-30 disabled:pointer-events-none"
        >
          <span>{isAnalyzing ? 'ANALYZING' : 'DETECT MY MOOD'}</span>
          <span className="group-hover:translate-x-1 transition-transform duration-300">→</span>
        </button>
      </div>
    </div>
  );
}
