import React from 'react';
import { useMoodContext } from '../context/MoodContext';

export default function Session() {
  const { result, likedTracks, skippedTracks, intent } = useMoodContext();

  if (!result) {
    return (
      <div className="w-full max-w-3xl mx-auto py-24 text-center animate-fade-in-slow">
        <h3 className="text-xs font-mono tracking-[0.3em] uppercase text-neutral-500 mb-8">
          Session Data
        </h3>
        <p className="text-neutral-400">No active session. Run an analysis to view session data.</p>
      </div>
    );
  }

  const { emotional_profile, music_direction, recommendations } = result;

  return (
    <div className="w-full max-w-4xl mx-auto py-24 animate-fade-in-slow">
      <h3 className="text-xs font-mono tracking-[0.3em] uppercase text-neutral-500 mb-16">
        Session Activity
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
        {/* Left Column: Emotion & Direction */}
        <div className="flex flex-col gap-12">
          
          <section>
            <h4 className="text-[10px] font-mono tracking-widest uppercase text-neutral-600 mb-6 border-b border-neutral-900 pb-2">
              Emotional Profile
            </h4>
            <div className="flex flex-col gap-2 text-sm text-neutral-300">
              <div className="flex justify-between">
                <span className="text-neutral-500">Dominant</span>
                <span className="uppercase">{emotional_profile.dominant_emotion}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Energy</span>
                <span>{emotional_profile.energy}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Valence</span>
                <span>{emotional_profile.valence}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Tempo</span>
                <span className="uppercase">{emotional_profile.tempo}</span>
              </div>
            </div>
          </section>

          <section>
            <h4 className="text-[10px] font-mono tracking-widest uppercase text-neutral-600 mb-6 border-b border-neutral-900 pb-2">
              Music Direction ({intent.replace(/_/g, ' ')})
            </h4>
            {music_direction ? (
              <div className="flex flex-col gap-4 text-sm text-neutral-300">
                <div>
                  <span className="block text-neutral-500 mb-1">Genres</span>
                  <p>{(music_direction.preferred_genres || music_direction.genres)?.join(', ') || 'Auto'}</p>
                </div>
                <div>
                  <span className="block text-neutral-500 mb-1">Subgenres</span>
                  <p>{(music_direction.preferred_subgenres || music_direction.subgenres)?.join(', ') || 'None'}</p>
                </div>
                <div>
                  <span className="block text-neutral-500 mb-1">Descriptors</span>
                  <p>{music_direction.descriptors?.join(', ') || 'None'}</p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-neutral-500">Standard mapping applied.</p>
            )}
          </section>

        </div>

        {/* Right Column: Tracks */}
        <div className="flex flex-col gap-12">
          
          <section>
            <h4 className="text-[10px] font-mono tracking-widest uppercase text-neutral-600 mb-6 border-b border-neutral-900 pb-2">
              Tracks Explored
            </h4>
            <div className="text-3xl font-light text-white">
              {recommendations.length}
            </div>
          </section>

          <section>
            <h4 className="text-[10px] font-mono tracking-widest uppercase text-neutral-600 mb-6 border-b border-neutral-900 pb-2">
              Liked Tracks ({likedTracks.length})
            </h4>
            {likedTracks.length === 0 ? (
              <p className="text-sm text-neutral-500">No tracks liked yet.</p>
            ) : (
              <ul className="flex flex-col gap-3 text-sm">
                {likedTracks.map(id => {
                  const t = recommendations.find(r => r.id === id);
                  return t ? (
                    <li key={id} className="text-white truncate">
                      {t.title} <span className="text-neutral-500">by {t.artist}</span>
                    </li>
                  ) : null;
                })}
              </ul>
            )}
          </section>

          <section>
            <h4 className="text-[10px] font-mono tracking-widest uppercase text-neutral-600 mb-6 border-b border-neutral-900 pb-2">
              Skipped Tracks ({skippedTracks.length})
            </h4>
            {skippedTracks.length === 0 ? (
              <p className="text-sm text-neutral-500">No tracks skipped.</p>
            ) : (
              <ul className="flex flex-col gap-3 text-sm">
                {skippedTracks.map(id => {
                  const t = recommendations.find(r => r.id === id);
                  return t ? (
                    <li key={id} className="text-neutral-400 line-through truncate">
                      {t.title} <span className="text-neutral-600">by {t.artist}</span>
                    </li>
                  ) : null;
                })}
              </ul>
            )}
          </section>

        </div>
      </div>
    </div>
  );
}
