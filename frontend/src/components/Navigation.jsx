import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Navigation() {
  const links = [
    { path: '/', label: 'Discover' },
    { path: '/talk', label: 'Talk' },
    { path: '/how-it-works', label: 'How It Works' },
    { path: '/music-and-emotion', label: 'Music & Emotion' },
    { path: '/session', label: 'Session' }
  ];

  return (
    <nav className="flex items-center gap-8 py-1">
      {links.map((link) => (
        <NavLink
          key={link.path}
          to={link.path}
          className={({ isActive }) =>
            `relative text-xs font-mono tracking-[0.2em] uppercase transition-all duration-500 py-1 ${
              isActive ? 'text-white' : 'text-neutral-500 hover:text-neutral-300'
            }`
          }
        >
          {({ isActive }) => (
            <>
              {link.label}
              {isActive && (
                <span 
                  className="absolute bottom-0 left-0 w-full h-[1.5px] rounded-full transition-all duration-700" 
                  style={{ 
                    backgroundColor: 'var(--mood-accent, #ffffff)',
                    boxShadow: '0 0 10px var(--mood-glow, rgba(255,255,255,0.3))' 
                  }}
                />
              )}
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
