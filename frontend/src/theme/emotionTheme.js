// MoodTunes Canonical Emotion Theme Engine
// Translates 7-class emotion probability distribution into weighted CSS variables & recommendation presentation

export const EMOTION_THRESHOLDS = {
  primary: 0.50,
  secondary: 0.15,
  meaningful: 0.05,
  negligible: 0.05
};

export const BASE_EMOTION_PALETTES = {
  angry: {
    primaryRgb: [177, 18, 38],    // #B11226 Deep Crimson
    secondaryRgb: [92, 10, 20],   // #5C0A14 Dark Red
    accentRgb: [255, 51, 79],     // #FF334F Intense Crimson Accent
    hex: '#B11226',
    temperature: 'hot',
    animationIntensity: 0.90
  },
  disgust: {
    primaryRgb: [104, 113, 42],   // #68712A Dark Olive
    secondaryRgb: [48, 53, 16],   // #303510 Muted Olive
    accentRgb: [167, 184, 61],    // #A7B83D Earthy Olive Accent
    hex: '#68712A',
    temperature: 'earthy',
    animationIntensity: 0.45
  },
  fear: {
    primaryRgb: [40, 59, 99],     // #283B63 Deep Navy
    secondaryRgb: [17, 24, 39],   // #111827 Cold Dark Blue
    accentRgb: [96, 125, 183],    // #607DB7 Muted Slate Violet
    hex: '#283B63',
    temperature: 'cold',
    animationIntensity: 0.35
  },
  happy: {
    primaryRgb: [216, 155, 25],   // #D89B19 Warm Gold
    secondaryRgb: [118, 80, 11],  // #76500B Amber
    accentRgb: [255, 215, 90],    // #FFD75A Bright Gold Accent
    hex: '#D89B19',
    temperature: 'warm',
    animationIntensity: 0.75
  },
  sad: {
    primaryRgb: [49, 90, 145],    // #315A91 Muted Steel Blue
    secondaryRgb: [23, 38, 61],   // #17263D Deep Slate
    accentRgb: [98, 139, 196],    // #628BC4 Light Steel Accent
    hex: '#315A91',
    temperature: 'cold',
    animationIntensity: 0.20
  },
  surprise: {
    primaryRgb: [180, 90, 158],   // #B45A9E Electric Magenta/Violet
    secondaryRgb: [84, 38, 75],   // #54264B Deep Violet
    accentRgb: [227, 139, 203],   // #E38BCB Electric Accent
    hex: '#B45A9E',
    temperature: 'electric',
    animationIntensity: 0.85
  },
  neutral: {
    primaryRgb: [119, 119, 119], // #777777 Muted Graphite
    secondaryRgb: [51, 51, 51],   // #333333 Charcoal
    accentRgb: [181, 181, 181],   // #B5B5B5 Silver Accent
    hex: '#777777',
    temperature: 'neutral',
    animationIntensity: 0.25
  }
};

const DEFAULT_NEUTRAL_THEME = {
  primary: 'rgb(119, 119, 119)',
  secondary: 'rgb(51, 51, 51)',
  accent: 'rgb(181, 181, 181)',
  background: '#080808',
  gradient: 'radial-gradient(circle at 50% -10%, rgba(119, 119, 119, 0.12), rgba(8, 8, 8, 0.98) 70%)',
  glow: 'rgba(119, 119, 119, 0.15)',
  textAccent: '#B5B5B5',
  animationSpeed: '1s',
  intensity: 0.25
};

/**
 * Derives a dynamic recommendation header based on the emotion spectrum mixture
 * @param {Object} probabilities - Object mapping emotion names to values (0-1 or 0-100)
 * @returns {string} Contextual recommendation heading
 */
export function getRecommendationHeading(probabilities) {
  if (!probabilities || typeof probabilities !== 'object') {
    return "Five tracks for where you are.";
  }

  const entries = Object.entries(probabilities)
    .map(([k, v]) => ({ name: k.toLowerCase(), val: (parseFloat(v) || 0) > 1.0 ? parseFloat(v)/100.0 : parseFloat(v) }))
    .sort((a, b) => b.val - a.val);

  if (entries.length === 0) return "Five tracks for where you are.";

  const dom = entries[0];
  const sec = entries.length > 1 && entries[1].val >= EMOTION_THRESHOLDS.secondary ? entries[1] : null;

  const key = sec ? `${dom.name}_${sec.name}` : dom.name;

  const HEADINGS = {
    // 2-Emotion Mixtures
    'sad_neutral': "Five tracks for a quieter moment.",
    'neutral_sad': "Five tracks for a quieter moment.",
    'angry_sad': "Five tracks carrying a little weight.",
    'sad_angry': "Five tracks carrying a little weight.",
    'happy_surprise': "Five tracks for the unexpected energy.",
    'surprise_happy': "Five tracks for the unexpected energy.",
    'fear_sad': "Five tracks to slow the room down.",
    'sad_fear': "Five tracks to slow the room down.",
    'happy_neutral': "Five tracks for the good kind of calm.",
    'neutral_happy': "Five tracks for the good kind of calm.",
    'angry_surprise': "Five tracks for the volatile energy.",
    'surprise_angry': "Five tracks for the volatile energy.",
    'fear_neutral': "Five tracks for a steady, grounded rhythm.",
    'neutral_fear': "Five tracks for a steady, grounded rhythm.",
    'fear_surprise': "Five tracks for the mysterious atmosphere.",
    'happy_fear': "Five tracks balancing hope and quiet questions.",
    'happy_angry': "Five tracks for confident, powerful energy.",
    'disgust_angry': "Five tracks cutting through the noise.",
    'disgust_sad': "Five tracks for an honest, quiet focus.",

    // Single-Emotion Defaults
    'happy': "Five tracks for the lifted moment.",
    'sad': "Five tracks for where you are.",
    'angry': "Five tracks for the intensity.",
    'fear': "Five tracks to anchor the room.",
    'surprise': "Five tracks for the unexpected.",
    'disgust': "Five tracks for a resilient focus.",
    'neutral': "Five tracks for a balanced state."
  };

  return HEADINGS[key] || HEADINGS[dom.name] || "Five tracks for where you are.";
}

/**
 * Computes a weighted visual theme from a 7-class emotion probability dictionary.
 * @param {Object} probabilities - Object mapping emotion names (e.g. happy, sad) to values (0-1 or 0-100)
 * @returns {Object} Theme CSS properties and metadata
 */
export function computeEmotionTheme(probabilities) {
  if (!probabilities || typeof probabilities !== 'object') {
    return DEFAULT_NEUTRAL_THEME;
  }

  // Normalize entries: ensure probabilities are on a 0..1 scale
  const entries = Object.entries(probabilities)
    .map(([key, val]) => {
      const num = parseFloat(val) || 0;
      return {
        name: key.toLowerCase(),
        val: num > 1.0 ? num / 100.0 : num
      };
    })
    .filter(e => BASE_EMOTION_PALETTES[e.name]);

  if (entries.length === 0) return DEFAULT_NEUTRAL_THEME;

  // Sort descending
  entries.sort((a, b) => b.val - a.val);

  // Filter out tiny contributions < 5% (0.05) to keep color mixing focused
  const activeEmotions = entries.filter(e => e.val >= EMOTION_THRESHOLDS.meaningful);

  const pool = activeEmotions.length > 0 ? activeEmotions : [entries[0]];
  const totalWeight = pool.reduce((sum, item) => sum + item.val, 0);

  if (totalWeight <= 0) return DEFAULT_NEUTRAL_THEME;

  // Weighted color mixing
  let pR = 0, pG = 0, pB = 0;
  let sR = 0, sG = 0, sB = 0;
  let aR = 0, aG = 0, aB = 0;
  let weightedIntensity = 0;
  let comfortWarmth = 0; // Warm-neutral balancing factor

  pool.forEach(item => {
    const weight = item.val / totalWeight;
    const palette = BASE_EMOTION_PALETTES[item.name];

    pR += palette.primaryRgb[0] * weight;
    pG += palette.primaryRgb[1] * weight;
    pB += palette.primaryRgb[2] * weight;

    sR += palette.secondaryRgb[0] * weight;
    sG += palette.secondaryRgb[1] * weight;
    sB += palette.secondaryRgb[2] * weight;

    aR += palette.accentRgb[0] * weight;
    aG += palette.accentRgb[1] * weight;
    aB += palette.accentRgb[2] * weight;

    weightedIntensity += palette.animationIntensity * weight;

    // Apply Comfort Layer adjustments based on valence intensity
    if (item.name === 'sad' || item.name === 'fear') {
      comfortWarmth += 0.20 * weight; // Soft warm-neutral tint (prevent depressing dark blue)
    } else if (item.name === 'angry') {
      comfortWarmth += 0.15 * weight; // Burgundy/amber softening (prevent aggressive flashing red)
    }
  });

  // Blend in subtle comfort layer warmth (RGB 230, 210, 180 - subtle warm-neutral amber)
  if (comfortWarmth > 0) {
    const cR = 230, cG = 210, cB = 180;
    const factor = Math.min(0.25, comfortWarmth);
    pR = pR * (1 - factor) + cR * factor;
    pG = pG * (1 - factor) + cG * factor;
    pB = pB * (1 - factor) + cB * factor;
    
    aR = aR * (1 - factor) + cR * factor;
    aG = aG * (1 - factor) + cG * factor;
    aB = aB * (1 - factor) + cB * factor;
  }

  const dominant = pool[0];
  const secondary = pool[1] || pool[0];

  const primaryStr = `rgb(${Math.round(pR)}, ${Math.round(pG)}, ${Math.round(pB)})`;
  const secondaryStr = `rgb(${Math.round(sR)}, ${Math.round(sG)}, ${Math.round(sB)})`;
  const accentStr = `rgb(${Math.round(aR)}, ${Math.round(aG)}, ${Math.round(aB)})`;

  // Radial gradient blending primary & secondary RGB over dark base with comfort layer
  const opacityPrimary = Math.min(0.32, 0.14 + dominant.val * 0.22);
  const opacitySecondary = Math.min(0.18, 0.07 + secondary.val * 0.14);

  const gradient = `radial-gradient(circle at 50% -15%, rgba(${Math.round(pR)}, ${Math.round(pG)}, ${Math.round(pB)}, ${opacityPrimary.toFixed(2)}), rgba(${Math.round(sR)}, ${Math.round(sG)}, ${Math.round(sB)}, ${opacitySecondary.toFixed(2)}) 55%, rgba(8, 8, 8, 0.98) 85%)`;

  const glow = `rgba(${Math.round(pR)}, ${Math.round(pG)}, ${Math.round(pB)}, ${(0.14 + weightedIntensity * 0.22).toFixed(2)})`;

  // Animation speed modifier based on energy/intensity (comfort layer slows down heavy states)
  const animSpeedSec = Math.max(0.6, (1.4 - weightedIntensity * 0.7)).toFixed(2) + 's';

  return {
    primary: primaryStr,
    secondary: secondaryStr,
    accent: accentStr,
    background: '#080808',
    gradient,
    glow,
    textAccent: accentStr,
    animationSpeed: animSpeedSec,
    intensity: parseFloat(weightedIntensity.toFixed(2)),
    dominantEmotion: dominant.name,
    secondaryEmotion: secondary.name
  };
}

/**
 * Applies the calculated emotion theme to document.documentElement CSS variables
 * @param {Object} probabilities - Object mapping emotion names to values
 */
export function applyEmotionThemeToDocument(probabilities) {
  if (typeof document === 'undefined') return;

  const theme = computeEmotionTheme(probabilities);
  const root = document.documentElement;

  root.style.setProperty('--mood-primary', theme.primary);
  root.style.setProperty('--mood-secondary', theme.secondary);
  root.style.setProperty('--mood-accent', theme.accent);
  root.style.setProperty('--mood-background', theme.background);
  root.style.setProperty('--mood-gradient', theme.gradient);
  root.style.setProperty('--mood-glow', theme.glow);
  root.style.setProperty('--mood-text-accent', theme.textAccent);
  root.style.setProperty('--mood-animation-speed', theme.animationSpeed);
  root.style.setProperty('--mood-intensity', theme.intensity);

  return theme;
}

/**
 * Resets document.documentElement CSS variables to standard neutral theme
 */
export function resetEmotionThemeOnDocument() {
  if (typeof document === 'undefined') return;
  return applyEmotionThemeToDocument({ neutral: 1.0 });
}
