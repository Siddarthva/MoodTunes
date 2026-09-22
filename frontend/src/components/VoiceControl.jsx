import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Volume2, VolumeX } from 'lucide-react';

export default function VoiceControl({ onSend, isProcessing }) {
  const [isListening, setIsListening] = useState(false);
  const [text, setText] = useState('');
  const [hasSupport, setHasSupport] = useState(true);
  const recognitionRef = useRef(null);
  
  useEffect(() => {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        
        if (finalTranscript) {
          setText((prev) => prev + finalTranscript + ' ');
        }
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
    } else {
      setHasSupport(false);
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleSend = () => {
    if (text.trim() && !isProcessing) {
      onSend(text.trim());
      setText('');
      if (isListening) {
        recognitionRef.current?.stop();
        setIsListening(false);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto border border-neutral-800 bg-[#0c0c0c] p-4 relative group transition-colors focus-within:border-neutral-600">
      <div className="flex flex-col gap-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type or speak your mind..."
          className="w-full bg-transparent text-[#f2f2f2] placeholder-neutral-600 resize-none outline-none min-h-[60px] text-lg font-light tracking-wide leading-relaxed"
          disabled={isProcessing}
        />
        
        <div className="flex justify-between items-center pt-2 border-t border-neutral-800/50">
          <div className="flex items-center gap-4">
            {hasSupport && (
              <button
                onClick={toggleListening}
                className={`p-2 transition-colors flex items-center gap-2 ${isListening ? 'text-[#f2f2f2]' : 'text-neutral-500 hover:text-neutral-300'}`}
                title={isListening ? "Stop listening" : "Start speaking"}
                disabled={isProcessing}
              >
                {isListening ? (
                  <>
                    <span className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                    </span>
                    <span className="text-xs uppercase tracking-widest font-mono">Listening</span>
                  </>
                ) : (
                  <Mic size={20} />
                )}
              </button>
            )}
          </div>
          
          <button
            onClick={handleSend}
            disabled={!text.trim() || isProcessing}
            className="px-6 py-2 bg-[#f2f2f2] text-black font-medium tracking-wide uppercase text-xs hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isProcessing ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
