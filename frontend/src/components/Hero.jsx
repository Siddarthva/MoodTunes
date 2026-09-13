import React from 'react';
import { motion } from 'framer-motion';

export default function Hero() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
  };

  const wordVariants = {
    hidden: {
      opacity: 0,
      y: 30,
      scale: 0.94,
      filter: 'blur(12px)',
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      filter: 'blur(0px)',
      transition: {
        duration: 0.8,
        ease: [0.16, 1, 0.3, 1],
      },
    },
  };

  return (
    <section className="pt-20 pb-16 text-center max-w-5xl mx-auto px-4">
      {/* Primary Kinetic Typography Display */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="flex flex-col items-center justify-center font-extrabold text-[clamp(56px,12vw,160px)] leading-[0.84] tracking-[-0.05em] uppercase text-gradient mb-8 select-none"
      >
        <motion.span variants={wordVariants}>MUSIC</motion.span>
        <motion.span variants={wordVariants}>THAT</motion.span>
        <motion.span variants={wordVariants}>FEELS</motion.span>
        <motion.span variants={wordVariants}>YOU.</motion.span>
      </motion.div>

      {/* Minimal Supporting Copy */}
      <motion.p
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.7 }}
        className="text-neutral-400 font-light text-base md:text-lg tracking-wide max-w-sm mx-auto"
      >
        Capture a moment. Find its soundtrack.
      </motion.p>
    </section>
  );
}
