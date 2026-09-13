import { useState, useCallback } from 'react';
import { analyzeMoodImage } from '../services/api';

export function useMoodAnalysis() {
  const [state, setState] = useState('idle'); // idle | capturing | analyzing | success | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (imageBlob) => {
    if (state === 'analyzing' || state === 'capturing') return;

    setState('analyzing');
    setError(null);

    try {
      const data = await analyzeMoodImage(imageBlob);
      setResult(data);
      setState('success');
    } catch (err) {
      setError(err);
      setState('error');
    }
  }, [state]);

  const reset = useCallback(() => {
    setState('idle');
    setResult(null);
    setError(null);
  }, []);

  return {
    state,
    setState,
    result,
    error,
    analyze,
    reset,
    isAnalyzing: state === 'analyzing' || state === 'capturing',
  };
}
