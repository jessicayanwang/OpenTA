'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Logo from '@/components/Logo'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to login page
    router.push('/login')
  }, [router])

  return (
    <div className="min-h-screen bg-[#f7f7f5] flex items-center justify-center">
      <div className="text-center">
        <div className="mb-4 animate-pulse">
          <Logo size="xl" showText={false} />
        </div>
        <p className="text-gray-600">Loading OpenTA...</p>
      </div>
    </div>
  )
}
