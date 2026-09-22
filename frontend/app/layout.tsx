import type { Metadata } from "next"
import localFont from "next/font/local"

import "./globals.css"

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
})

export const metadata: Metadata = {
  title: "ForgeIQ",
  description: "Observed manufacturing telemetry",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} bg-zinc-50 font-sans text-zinc-900 antialiased`}>
        {children}
      </body>
    </html>
  )
}
