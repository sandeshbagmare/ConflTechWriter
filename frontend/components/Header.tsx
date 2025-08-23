'use client'

import { motion } from 'framer-motion'
import { Brain, Sparkles, Github } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-3"
          >
            <div className="relative">
              <Brain className="h-8 w-8 text-blue-600" />
              <Sparkles className="h-4 w-4 text-yellow-500 absolute -top-1 -right-1" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Article Generator</h1>
              <p className="text-xs text-gray-500">Fact-backed technical content</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4"
          >
            <span className="text-sm text-gray-600 hidden md:block">
              Multi-Agent AI System
            </span>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-500">Live</span>
            </div>
          </motion.div>
        </div>
      </div>
    </header>
  )
}
