import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OpenTA - Your AI Teaching Assistant',
  description: 'Get instant answers to course questions with citations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
