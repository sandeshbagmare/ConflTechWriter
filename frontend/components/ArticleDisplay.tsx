'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Eye, ExternalLink, Clock, User, BookOpen, Share2, Copy, Check } from 'lucide-react'

interface ArticleDisplayProps {
  article: {
    title: string
    content: string
    metadata: {
      word_count: number
      reading_time: number
      audience: string
      author?: string
      created_at: string
    }
    sources: Array<{
      id: string
      title: string
      url: string
      domain: string
      excerpt: string
      relevance_score: number
    }>
    citations: Array<{
      text: string
      source_id: string
      page?: number
    }>
  }
  onNewArticle: () => void
}

export default function ArticleDisplay({ article, onNewArticle }: ArticleDisplayProps) {
  const [showSources, setShowSources] = useState(false)
  const [copiedText, setCopiedText] = useState('')

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(''), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const downloadArticle = () => {
    const blob = new Blob([
      `# ${article.title}\n\n`,
      `*Generated on ${new Date(article.metadata.created_at).toLocaleDateString()}*\n`,
      `*Target Audience: ${article.metadata.audience}*\n`,
      `*Reading Time: ${article.metadata.reading_time} minutes*\n\n`,
      '---\n\n',
      article.content,
      '\n\n## Sources\n\n',
      ...article.sources.map((source, index) => 
        `${index + 1}. [${source.title}](${source.url}) - ${source.domain}\n`
      )
    ], { type: 'text/markdown' })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${article.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const shareArticle = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: article.title,
          text: `Check out this AI-generated article: ${article.title}`,
          url: window.location.href
        })
      } catch (error) {
        console.error('Error sharing:', error)
      }
    } else {
      copyToClipboard(window.location.href, 'URL')
    }
  }

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-blue-600 p-6 text-white">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-3 leading-tight">{article.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-emerald-100">
              <div className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                <span>{article.metadata.word_count} words</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{article.metadata.reading_time} min read</span>
              </div>
              <div className="flex items-center gap-1">
                <User className="h-4 w-4" />
                <span>{article.metadata.audience}</span>
              </div>
              <div className="flex items-center gap-1">
                <BookOpen className="h-4 w-4" />
                <span>{article.sources.length} sources</span>
              </div>
            </div>
          </div>
          <button
            onClick={onNewArticle}
            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            New Article
          </button>
        </div>
      </div>

      <div className="flex">
        {/* Main Content */}
        <div className="flex-1 p-8">
          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 mb-8">
            <button
              onClick={downloadArticle}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <button
              onClick={shareArticle}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Share2 className="h-4 w-4" />
              Share
            </button>
            <button
              onClick={() => copyToClipboard(article.content, 'Article')}
              className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {copiedText === 'Article' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copiedText === 'Article' ? 'Copied!' : 'Copy Text'}
            </button>
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Eye className="h-4 w-4" />
              {showSources ? 'Hide' : 'View'} Sources
            </button>
          </div>

          {/* Article Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="prose prose-lg max-w-none"
          >
            <div 
              className="text-gray-800 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: article.content.replace(/\n/g, '<br>') }}
            />
          </motion.div>

          {/* Generated Info */}
          <div className="mt-12 p-6 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">About This Article</h3>
            <p className="text-gray-600 text-sm">
              This article was generated using advanced AI research agents that analyzed {article.sources.length} high-quality sources. 
              The content has been fact-checked, edited, and optimized for your target audience.
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Generated on {new Date(article.metadata.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Sources Sidebar */}
        <motion.div
          initial={{ width: 0, opacity: 0 }}
          animate={{ 
            width: showSources ? 400 : 0, 
            opacity: showSources ? 1 : 0 
          }}
          transition={{ duration: 0.3 }}
          className="border-l border-gray-200 bg-gray-50 overflow-hidden"
        >
          <div className="p-6">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Sources ({article.sources.length})
            </h3>
            
            <div className="space-y-4 max-h-[80vh] overflow-y-auto">
              {article.sources.map((source, index) => (
                <motion.div
                  key={source.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white p-4 rounded-lg shadow-sm border border-gray-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      #{index + 1}
                    </span>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <div className={`w-2 h-2 rounded-full ${
                        source.relevance_score > 0.8 ? 'bg-green-500' :
                        source.relevance_score > 0.6 ? 'bg-yellow-500' : 'bg-gray-400'
                      }`} />
                      {Math.round(source.relevance_score * 100)}%
                    </div>
                  </div>
                  
                  <h4 className="font-medium text-gray-900 text-sm mb-2 line-clamp-2">
                    {source.title}
                  </h4>
                  
                  <p className="text-xs text-gray-600 mb-3 line-clamp-3">
                    {source.excerpt}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{source.domain}</span>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 text-xs flex items-center gap-1"
                    >
                      <ExternalLink className="h-3 w-3" />
                      Visit
                    </a>
                  </div>
                </motion.div>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 text-sm mb-2">Source Quality</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-blue-800">High relevance (80%+)</span>
                  <span className="font-medium text-blue-900">
                    {article.sources.filter(s => s.relevance_score > 0.8).length}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-blue-800">Medium relevance (60-80%)</span>
                  <span className="font-medium text-blue-900">
                    {article.sources.filter(s => s.relevance_score > 0.6 && s.relevance_score <= 0.8).length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
