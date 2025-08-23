'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle, Clock, RefreshCw, Brain, Search, FileText, Sparkles, X } from 'lucide-react'

interface JobStatusProps {
  job: {
    job_id: string
    status: string
    topic: string
    progress_percentage?: number
    current_step?: string
    error_message?: string
  }
  onJobCompleted: (article: any) => void
  onJobFailed: (error: string) => void
  onNewArticle: () => void
}

export default function JobStatus({ job, onJobCompleted, onJobFailed, onNewArticle }: JobStatusProps) {
  const [currentProgress, setCurrentProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('Initializing...')
  const [logs, setLogs] = useState<string[]>([])

  useEffect(() => {
    let eventSource: EventSource | null = null
    let pollInterval: NodeJS.Timeout | null = null

    const connectEventSource = () => {
      try {
        eventSource = new EventSource(`${process.env.NEXT_PUBLIC_API_URL}/v1/jobs/${job.job_id}/events`)
        
        eventSource.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.status === 'completed') {
            fetchFinalArticle()
          } else if (data.status === 'failed') {
            onJobFailed(data.error || 'Job failed')
          }
        }

        eventSource.onerror = () => {
          eventSource?.close()
          startPolling()
        }
      } catch (error) {
        startPolling()
      }
    }

    const startPolling = () => {
      pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/jobs/${job.job_id}`)
          const data = await response.json()
          
          setCurrentProgress(data.progress_percentage || 0)
          setCurrentStep(data.current_step || data.status)
          
          if (data.status === 'completed') {
            clearInterval(pollInterval!)
            fetchFinalArticle()
          } else if (data.status === 'failed') {
            clearInterval(pollInterval!)
            onJobFailed(data.error_message || 'Job failed')
          }
        } catch (error) {
          console.error('Error polling job status:', error)
        }
      }, 2000)
    }

    const fetchFinalArticle = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/jobs/${job.job_id}/artifacts`)
        const data = await response.json()
        onJobCompleted(data.article)
      } catch (error) {
        onJobFailed('Failed to fetch completed article')
      }
    }

    // Start with EventSource, fallback to polling
    connectEventSource()

    return () => {
      eventSource?.close()
      if (pollInterval) clearInterval(pollInterval)
    }
  }, [job.job_id, onJobCompleted, onJobFailed])

  const stepDetails = {
    'queued': { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100', desc: 'Waiting in queue...' },
    'research_planning': { icon: Brain, color: 'text-blue-600', bg: 'bg-blue-100', desc: 'Planning research strategy' },
    'information_gathering': { icon: Search, color: 'text-purple-600', bg: 'bg-purple-100', desc: 'Searching for sources' },
    'content_analysis': { icon: FileText, color: 'text-green-600', bg: 'bg-green-100', desc: 'Analyzing content' },
    'content_writing': { icon: FileText, color: 'text-indigo-600', bg: 'bg-indigo-100', desc: 'Writing article' },
    'quality_assurance': { icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-100', desc: 'Quality checks' },
    'visualization': { icon: Sparkles, color: 'text-pink-600', bg: 'bg-pink-100', desc: 'Creating visuals' },
    'finalization': { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', desc: 'Finalizing article' },
    'running': { icon: RefreshCw, color: 'text-blue-600', bg: 'bg-blue-100', desc: 'Processing...' },
    'refining': { icon: Sparkles, color: 'text-purple-600', bg: 'bg-purple-100', desc: 'Refining content' },
  }

  const currentStepKey = currentStep.toLowerCase().replace(/\s+/g, '_') as keyof typeof stepDetails
  const stepInfo = stepDetails[currentStepKey] || stepDetails.running

  const StepIcon = stepInfo.icon

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Generating Article</h2>
            <p className="text-blue-100 text-lg truncate">{job.topic}</p>
          </div>
          <button
            onClick={onNewArticle}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            title="Cancel and start new"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Progress Section */}
      <div className="p-6">
        {/* Current Step */}
        <div className="flex items-center space-x-4 mb-6">
          <div className={`p-3 rounded-full ${stepInfo.bg}`}>
            <StepIcon className={`h-6 w-6 ${stepInfo.color} ${stepInfo.icon === RefreshCw ? 'animate-spin' : ''}`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{stepInfo.desc}</h3>
            <p className="text-gray-600">Our AI agents are working on your article</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{currentProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <motion.div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${currentProgress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Agent Workflow Visualization */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { name: 'Research', icon: Brain, step: 'research_planning' },
            { name: 'Search', icon: Search, step: 'information_gathering' },
            { name: 'Write', icon: FileText, step: 'content_writing' },
            { name: 'Verify', icon: CheckCircle, step: 'quality_assurance' },
          ].map((agent, index) => {
            const isActive = currentStepKey === agent.step
            const isCompleted = ['research_planning', 'information_gathering', 'content_writing'].indexOf(agent.step) < 
                              ['research_planning', 'information_gathering', 'content_writing'].indexOf(currentStepKey)
            
            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-4 rounded-lg border-2 transition-all ${
                  isActive 
                    ? 'border-blue-500 bg-blue-50 scale-105' 
                    : isCompleted 
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <agent.icon className={`h-6 w-6 mx-auto mb-2 ${
                  isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-400'
                }`} />
                <p className={`text-sm font-medium text-center ${
                  isActive ? 'text-blue-900' : isCompleted ? 'text-green-900' : 'text-gray-600'
                }`}>
                  {agent.name}
                </p>
              </motion.div>
            )
          })}
        </div>

        {/* Estimated Time */}
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <Clock className="h-5 w-5 text-gray-500 mx-auto mb-2" />
          <p className="text-sm text-gray-600">
            Estimated completion: 3-5 minutes
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Time varies based on topic complexity and source availability
          </p>
        </div>

        {/* Fun Facts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="mt-6 p-4 bg-blue-50 rounded-lg"
        >
          <h4 className="font-medium text-blue-900 mb-2">Did you know?</h4>
          <p className="text-sm text-blue-800">
            Our AI agents can process hundreds of sources in minutes, equivalent to days of human research work.
          </p>
        </motion.div>
      </div>
    </div>
  )
}
