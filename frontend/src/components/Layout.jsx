import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';
import MusicPlayer from './MusicPlayer';
import { checkBackendHealth } from '../services/api';

export default function Layout() {
  const [backendOffline, setBackendOffline] = useState(false);

  useEffect(() => {
    checkBackendHealth().then((health) => {
      setBackendOffline(!health.online);
    });
  }, []);

  return (
    <div className="min-h-screen flex flex-col relative z-10 selection:bg-neutral-800 selection:text-white">
      {/* Dynamic Multi-Layered Emotional Atmosphere & Vignette */}
      <div className="ambient-mood-backdrop" />
      <div className="ambient-vignette" />

      {/* Floating Spatial Glass Navigation Bar */}
      <header className="sticky top-0 z-30 w-full glass-nav px-8 py-5 transition-all duration-700">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:justify-between md:items-center gap-6">
          <div className="flex items-center gap-6">
            <span className="font-bold text-sm tracking-[0.35em] uppercase text-neutral-200">
              MOODTUNES
            </span>
            {backendOffline && (
              <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest border border-neutral-800/60 px-2 py-0.5 rounded-full">
                Backend Offline
              </span>
            )}
            {import.meta.env.VITE_DEMO_MODE === 'true' && (
              <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest border border-neutral-800/60 px-2 py-0.5 rounded-full">
                Demo Mode
              </span>
            )}
          </div>
          
          <Navigation />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-8 pb-40 relative z-10">
        <Outlet />
      </main>

      {/* Persistent Bottom Music Player */}
      <MusicPlayer />
    </div>
  );
}
