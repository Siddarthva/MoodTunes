import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MoodProvider } from './context/MoodContext';
import Layout from './components/Layout';
import Discover from './pages/Discover';
import Talk from './pages/Talk';
import HowItWorks from './pages/HowItWorks';
import MusicAndEmotion from './pages/MusicAndEmotion';
import Session from './pages/Session';

export default function App() {
  return (
    <MoodProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Discover />} />
            <Route path="talk" element={<Talk />} />
            <Route path="how-it-works" element={<HowItWorks />} />
            <Route path="music-and-emotion" element={<MusicAndEmotion />} />
            <Route path="session" element={<Session />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </MoodProvider>
  );
}
