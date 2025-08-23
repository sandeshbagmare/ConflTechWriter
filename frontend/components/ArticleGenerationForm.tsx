'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Zap, Settings, HelpCircle } from 'lucide-react'

interface ArticleGenerationFormProps {
  onJobCreated: (job: any) => void
}

export default function ArticleGenerationForm({ onJobCreated }: ArticleGenerationFormProps) {
  const [topic, setTopic] = useState('')
  const [depth, setDepth] = useState<'beginner' | 'intermediate' | 'expert'>('intermediate')
  const [maxLength, setMaxLength] = useState(5000)
  const [includeVisuals, setIncludeVisuals] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return

    setIsSubmitting(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          desired_depth: depth,
          max_length: maxLength,
          include_visuals: includeVisuals,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create job')
      }

      const jobData = await response.json()
      onJobCreated({
        job_id: jobData.job_id,
        status: jobData.status,
        topic: topic.trim(),
      })
    } catch (error) {
      console.error('Error creating job:', error)
      alert('Failed to create article. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const exampleTopics = [
    "Introduction to Vector Databases for RAG Systems",
    "Microservices vs Monoliths: A Comprehensive Comparison",
    "Understanding Kubernetes Pod Networking",
    "Redis Clustering Strategies for High Availability",
    "Modern Authentication Patterns in Web Applications"
  ]

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Generate Technical Article</h2>
        <p className="text-blue-100">Describe your topic and our AI agents will research and write a comprehensive article</p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Topic Input */}
        <div>
          <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
            Article Topic *
          </label>
          <textarea
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Comprehensive guide to implementing microservices with Docker and Kubernetes"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
            rows={3}
            required
            disabled={isSubmitting}
          />
          <p className="text-xs text-gray-500 mt-1">
            Be specific about what you want to learn or explain. The AI will create a structured research plan.
          </p>
        </div>

        {/* Example Topics */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Example Topics:</p>
          <div className="space-y-2">
            {exampleTopics.slice(0, 3).map((example, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setTopic(example)}
                className="text-left text-sm text-blue-600 hover:text-blue-800 hover:underline block"
                disabled={isSubmitting}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Target Audience */}
        <div>
          <label htmlFor="depth" className="block text-sm font-medium text-gray-700 mb-2">
            Target Audience
          </label>
          <select
            id="depth"
            value={depth}
            onChange={(e) => setDepth(e.target.value as any)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isSubmitting}
          >
            <option value="beginner">Beginner - New to the topic, needs fundamentals</option>
            <option value="intermediate">Intermediate - Has basic knowledge, wants implementation details</option>
            <option value="expert">Expert - Experienced, wants advanced concepts and best practices</option>
          </select>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-gray-600 hover:text-gray-900"
            disabled={isSubmitting}
          >
            <Settings className="h-4 w-4 mr-1" />
            Advanced Options
          </button>

          {showAdvanced && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg"
            >
              <div>
                <label htmlFor="maxLength" className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum Length: {maxLength.toLocaleString()} words
                </label>
                <input
                  type="range"
                  id="maxLength"
                  min="1000"
                  max="15000"
                  step="500"
                  value={maxLength}
                  onChange={(e) => setMaxLength(parseInt(e.target.value))}
                  className="w-full"
                  disabled={isSubmitting}
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1,000</span>
                  <span>15,000</span>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includeVisuals"
                  checked={includeVisuals}
                  onChange={(e) => setIncludeVisuals(e.target.checked)}
                  className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  disabled={isSubmitting}
                />
                <label htmlFor="includeVisuals" className="ml-2 text-sm text-gray-700">
                  Include diagrams and visual aids
                </label>
              </div>
            </motion.div>
          )}
        </div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={!topic.trim() || isSubmitting}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center space-x-2"
          whileHover={{ scale: isSubmitting ? 1 : 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Starting AI Agents...</span>
            </>
          ) : (
            <>
              <Zap className="h-5 w-5" />
              <span>Generate Article</span>
            </>
          )}
        </motion.button>

        {/* Info */}
        <div className="flex items-start space-x-2 text-sm text-gray-600 bg-blue-50 p-4 rounded-lg">
          <HelpCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900">How it works:</p>
            <ul className="mt-1 space-y-1 text-blue-800">
              <li>• AI agents research your topic using real-time web search</li>
              <li>• Every fact is verified and linked to credible sources</li>
              <li>• Multiple quality checks ensure accuracy and readability</li>
              <li>• Processing typically takes 3-5 minutes</li>
            </ul>
          </div>
        </div>
      </form>
    </div>
  )
}
