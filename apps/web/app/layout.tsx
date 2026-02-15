import "./globals.css";
import Providers from "../components/providers";

export const metadata = {
  title: "InvestiPet",
  description: "Gamified investing and financial literacy",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-cream text-ink dark:bg-ink dark:text-cream transition-colors duration-300">
        <Providers>
          <main className="app-shell min-h-screen">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
