'use client';

import React, { useState } from 'react';
import { LandingNavbar } from '@/components/landing/LandingNavbar';
import { HeroSection } from '@/components/landing/HeroSection';
import { FeaturesGrid } from '@/components/landing/FeaturesGrid';
import { ProcessArchitecture } from '@/components/landing/ProcessArchitecture';
import { BenchmarkComparison } from '@/components/landing/BenchmarkComparison';
import { LandingFooter } from '@/components/landing/LandingFooter';
import { SignInModal } from '@/components/landing/SignInModal';
import { UserRole } from '@/types/auth';

export default function LandingPage() {
  const [signInOpen, setSignInOpen] = useState<boolean>(false);
  const [initialRole, setInitialRole] = useState<UserRole>('plant_engineer');

  const handleOpenSignIn = (role: UserRole = 'plant_engineer') => {
    setInitialRole(role);
    setSignInOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-sky-500 selection:text-white">
      {/* Sticky Navigation Bar */}
      <LandingNavbar onOpenSignIn={() => handleOpenSignIn('plant_engineer')} />

      {/* Main Page Content */}
      <main className="flex-1">
        {/* Hero Section */}
        <HeroSection onOpenSignIn={() => handleOpenSignIn('plant_engineer')} />

        {/* Feature Subsystems */}
        <FeaturesGrid />

        {/* 3:2 Staging Physics & Process Architecture */}
        <ProcessArchitecture />

        {/* Benchmark Literature Comparison */}
        <BenchmarkComparison />
      </main>

      {/* Footer */}
      <LandingFooter />

      {/* Interactive Sign-In Modal */}
      <SignInModal
        isOpen={signInOpen}
        onClose={() => setSignInOpen(false)}
        initialRole={initialRole}
      />
    </div>
  );
}
