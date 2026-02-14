import "./globals.css";
import Providers from "../components/providers";

export const metadata = {
  title: "InvestiPet",
  description: "Gamified investing and financial literacy",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <main className="app-shell">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
