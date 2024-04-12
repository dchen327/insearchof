import { Inter } from "next/font/google";
import "./globals.css";
import "@fortawesome/fontawesome-svg-core/styles.css";
// Prevent fontawesome from adding its CSS since we did it manually above:
import { config } from "@fortawesome/fontawesome-svg-core";
import { Navbar } from "./components/navbar";
config.autoAddCss = false; /* eslint-disable import/first */
import "bulma/css/bulma.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "In Search Of",
  description: "College Campus Marketplace",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
