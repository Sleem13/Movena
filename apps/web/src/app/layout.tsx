import type { Metadata } from "next";
import { Preferences } from "../components/Preferences";
import "./globals.css";
export const metadata: Metadata = {
  referrer: 'no-referrer',
  title: "Movena — Move forward",
  description: "Your daily recovery, connected to your care team.",
  icons: { icon: "/movena-mark.png" },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Preferences>{children}</Preferences>
      </body>
    </html>
  );
}
