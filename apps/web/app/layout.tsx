import "./globals.css";
import Providers from "./providers";
export const metadata = { title: "RAKSHA | Financial Safety Layer", description: "Demo financial fraud prevention interface" };
export default function RootLayout({ children }: { children: React.ReactNode }) { return <html lang="en"><body><Providers>{children}</Providers></body></html>; }
