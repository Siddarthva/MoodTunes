export const DEMO_RESPONSE = {
  success: true,
  emotion: {
    dominant: "happy",
    confidence: 89.4,
    probabilities: {
      angry: 1.1,
      disgust: 0.3,
      fear: 0.5,
      happy: 89.4,
      sad: 1.8,
      surprise: 2.7,
      neutral: 4.2
    }
  },
  emotional_profile: {
    dominant_emotion: "happy",
    energy: 78.5,
    valence: 82.3,
    tempo: "high",
    weighted_genres: [
      { genre: "Pop", weight: 92.1 },
      { genre: "Dance", weight: 92.1 },
      { genre: "Feel Good", weight: 89.4 },
      { genre: "Electronic", weight: 2.7 }
    ]
  },
  recommendations: [
    {
      id: "demo_1",
      title: "Monochrome Horizon",
      artist: "Acoustic Noir",
      album: "Editorial Echoes",
      genre: "Indie Pop",
      artworkUrl: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400",
      previewUrl: "https://file-examples.com/storage/fe9471131166dd653df32d3/2017/11/file_example_MP3_700KB.mp3",
      source: "Demo Library",
      sourceUrl: "https://jamendo.com",
      matchScore: 96.5
    },
    {
      id: "demo_2",
      title: "Velvet Static",
      artist: "Subtle Frequency",
      album: "Resonance",
      genre: "Electronic",
      artworkUrl: "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=400",
      previewUrl: "https://file-examples.com/storage/fe9471131166dd653df32d3/2017/11/file_example_MP3_700KB.mp3",
      source: "Demo Library",
      sourceUrl: "https://jamendo.com",
      matchScore: 92.0
    },
    {
      id: "demo_3",
      title: "Silver Lining",
      artist: "Lunar Tide",
      album: "Midnight Sessions",
      genre: "Feel Good",
      artworkUrl: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400",
      previewUrl: null,
      source: "Demo Library",
      sourceUrl: "https://jamendo.com",
      matchScore: 88.4
    },
    {
      id: "demo_4",
      title: "Pulse of Light",
      artist: "Moderna",
      album: "Kinetics",
      genre: "Dance",
      artworkUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400",
      previewUrl: null,
      source: "Demo Library",
      sourceUrl: "https://jamendo.com",
      matchScore: 84.1
    },
    {
      id: "demo_5",
      title: "Reflections in B Flat",
      artist: "Soloist Duo",
      album: "Minimalist",
      genre: "Ambient Pop",
      artworkUrl: "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=400",
      previewUrl: null,
      source: "Demo Library",
      sourceUrl: "https://jamendo.com",
      matchScore: 81.0
    }
  ]
};
