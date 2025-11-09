'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to login page
    router.push('/login')
  }, [router])

  return (
    <div className="min-h-screen bg-[#f7f7f5] flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold shadow-lg mx-auto mb-4 animate-pulse">
          O
        </div>
        <p className="text-gray-600">Loading OpenTA...</p>
      </div>
    </div>
  )
}
