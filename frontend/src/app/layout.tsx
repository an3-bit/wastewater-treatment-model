import type { Metadata } from 'next';
import './globals.css';
import { APP_CONFIG } from '@/utils/constants';

export const metadata: Metadata = {
  title: `${APP_CONFIG.NAME} | ${APP_CONFIG.SUBTITLE}`,
  description:
    'AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse — Research Framework',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full bg-slate-50">
      <body className="min-h-full flex flex-col text-slate-900 bg-slate-50 antialiased">
        {children}
      </body>
    </html>
  );
}
