'use client';

import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';
import { SCIENTIFIC_GLOSSARY } from '@/utils/constants';

interface EngineeringTooltipProps {
  term: keyof typeof SCIENTIFIC_GLOSSARY | string;
  customText?: string;
  children?: React.ReactNode;
}

export function EngineeringTooltip({ term, customText, children }: EngineeringTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const text = customText || SCIENTIFIC_GLOSSARY[term] || term;

  return (
    <span className="relative inline-flex items-center gap-1">
      {children}
      <button
        type="button"
        className="text-slate-400 hover:text-sky-600 transition-colors p-0.5 rounded focus:outline-none"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={`Definition for ${term}`}
      >
        <HelpCircle className="w-3.5 h-3.5" />
      </button>

      {isOpen && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64 p-2.5 text-xs text-slate-700 bg-white rounded-lg shadow-lg border border-slate-200 pointer-events-none transition-all">
          <span className="font-semibold text-sky-700 block mb-1">{term}</span>
          <span className="leading-relaxed block">{text}</span>
          <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-white" />
        </span>
      )}
    </span>
  );
}
