import './globals.css'
import React from 'react'

export const metadata = { title: 'LeadGen Agentic RAG' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <main className="mx-auto max-w-3xl p-6">{children}</main>
      </body>
    </html>
  )
}
