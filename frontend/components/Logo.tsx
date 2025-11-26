interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showText?: boolean
  label?: string
  className?: string
}

export default function Logo({ size = 'md', showText = true, label = 'OpenTA', className = '' }: LogoProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  }

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl'
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Logo Icon - Academic Book with "O" */}
      <div className={`${sizeClasses[size]} flex-shrink-0 bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl flex items-center justify-center shadow-sm relative overflow-hidden`}>
        {/* Letter O */}
        <span className="text-white font-bold relative z-10" style={{ fontSize: size === 'sm' ? '1rem' : size === 'md' ? '1.25rem' : size === 'lg' ? '1.5rem' : '2rem' }}>
          O
        </span>
      </div>
      
      {/* Logo Text */}
      {showText && (
        <span className={`font-normal ${textSizeClasses[size]} text-gray-900 tracking-tight flex-shrink-0`}>
          {label}
        </span>
      )}
    </div>
  )
}
