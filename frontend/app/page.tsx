'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Brain, FileText, Search, CheckCircle, AlertCircle, Clock, ExternalLink } from 'lucide-react'
import ArticleGenerationForm from '../components/ArticleGenerationForm'
import ArticleDisplay from '../components/ArticleDisplay'
import JobStatus from '../components/JobStatus'
import Header from '../components/Header'

interface Job {
  job_id: string
  status: 'queued' | 'running' | 'refining' | 'completed' | 'failed'
  topic: string
  progress_percentage?: number
  current_step?: string
  error_message?: string
}

export default function HomePage() {
  const [currentJob, setCurrentJob] = useState<Job | null>(null)
  const [completedArticle, setCompletedArticle] = useState<any>(null)
  const [showDemo, setShowDemo] = useState(false)

  const handleJobCreated = (job: Job) => {
    setCurrentJob(job)
    setCompletedArticle(null)
  }

  const handleJobCompleted = (article: any) => {
    setCompletedArticle(article)
    setCurrentJob(null)
  }

  const handleJobFailed = (error: string) => {
    console.error('Job failed:', error)
    setCurrentJob(null)
  }

  const handleNewArticle = () => {
    setCurrentJob(null)
    setCompletedArticle(null)
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {!currentJob && !completedArticle && (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="max-w-4xl mx-auto"
            >
              {/* Hero Section */}
              <div className="text-center mb-12">
                <motion.div
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.1 }}
                  className="mb-6"
                >
                  <Brain className="h-16 w-16 mx-auto text-blue-600 mb-4" />
                  <h1 className="text-5xl font-bold gradient-text mb-4">
                    AI Article Generator
                  </h1>
                  <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    Create comprehensive, fact-backed technical articles with transparent citations. 
                    Our multi-agent AI system researches, analyzes, and writes professional content with verifiable sources.
                  </p>
                </motion.div>

                {/* Feature highlights */}
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
                >
                  <div className="glass-effect rounded-lg p-6">
                    <Search className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                    <h3 className="font-semibold mb-2">Real-time Research</h3>
                    <p className="text-sm text-gray-600">Live web search for current, accurate information</p>
                  </div>
                  <div className="glass-effect rounded-lg p-6">
                    <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-3" />
                    <h3 className="font-semibold mb-2">Fact-Checked Content</h3>
                    <p className="text-sm text-gray-600">Every claim verified and linked to sources</p>
                  </div>
                  <div className="glass-effect rounded-lg p-6">
                    <FileText className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                    <h3 className="font-semibold mb-2">Professional Quality</h3>
                    <p className="text-sm text-gray-600">Human-level writing with visual aids</p>
                  </div>
                </motion.div>
              </div>

              {/* Article Generation Form */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <ArticleGenerationForm onJobCreated={handleJobCreated} />
              </motion.div>

              {/* Demo Section */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.7 }}
                className="mt-12 text-center"
              >
                <button
                  onClick={() => setShowDemo(!showDemo)}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  {showDemo ? 'Hide' : 'See'} How It Works
                </button>
                
                <AnimatePresence>
                  {showDemo && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
                    >
                      {[
                        { icon: Brain, title: 'Chief Researcher', desc: 'Plans research strategy' },
                        { icon: Search, title: 'Search Agents', desc: 'Find credible sources' },
                        { icon: FileText, title: 'Writer Agent', desc: 'Synthesizes content' },
                        { icon: CheckCircle, title: 'QA Trinity', desc: 'Fact-checks & refines' },
                      ].map((step, index) => (
                        <motion.div
                          key={step.title}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="bg-white rounded-lg p-4 shadow-sm border"
                        >
                          <step.icon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                          <h4 className="font-medium text-sm mb-1">{step.title}</h4>
                          <p className="text-xs text-gray-600">{step.desc}</p>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </motion.div>
          )}

          {currentJob && (
            <motion.div
              key="status"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.5 }}
              className="max-w-4xl mx-auto"
            >
              <JobStatus
                job={currentJob}
                onJobCompleted={handleJobCompleted}
                onJobFailed={handleJobFailed}
                onNewArticle={handleNewArticle}
              />
            </motion.div>
          )}

          {completedArticle && (
            <motion.div
              key="article"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.5 }}
              className="max-w-6xl mx-auto"
            >
              <ArticleDisplay
                article={completedArticle}
                onNewArticle={handleNewArticle}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-gray-600 text-sm">
              Powered by advanced AI agents • Built for professional content creation
            </p>
            <div className="flex justify-center items-center mt-4 space-x-6 text-xs text-gray-500">
              <span>Multi-Agent Architecture</span>
              <span>•</span>
              <span>Real-Time Fact Checking</span>
              <span>•</span>
              <span>Transparent Citations</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
