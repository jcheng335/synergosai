import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Brain, Users, FileText, MessageSquare, BarChart3, Mic, Play, CheckCircle, Settings as SettingsIcon } from 'lucide-react'
import InterviewSetup from './components/InterviewSetup.jsx'
import DocumentUpload from './components/DocumentUpload.jsx'
import InterviewPreparation from './components/InterviewPreparation.jsx'
import LiveInterview from './components/LiveInterview.jsx'
import InterviewResults from './components/InterviewResults.jsx'
import InterviewList from './components/InterviewList.jsx'
import Settings from './components/Settings.jsx'
import './App.css'

const API_BASE_URL = 'http://localhost:5001/api'

function App() {
  const [currentView, setCurrentView] = useState('dashboard')
  const [currentInterview, setCurrentInterview] = useState(null)
  const [interviews, setInterviews] = useState([])
  const [loading, setLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    fetchInterviews()
  }, [])

  const fetchInterviews = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/interviews`)
      if (response.ok) {
        const data = await response.json()
        setInterviews(data.interviews)
      }
    } catch (error) {
      console.error('Failed to fetch interviews:', error)
    }
  }

  const createNewInterview = async (interviewData) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/interviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(interviewData),
      })
      
      if (response.ok) {
        const data = await response.json()
        setCurrentInterview(data.interview)
        setCurrentView('documents')
        await fetchInterviews()
        return data.interview
      } else {
        throw new Error('Failed to create interview')
      }
    } catch (error) {
      console.error('Error creating interview:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const selectInterview = (interview) => {
    setCurrentInterview(interview)
    
    // Navigate to appropriate view based on interview status
    switch (interview.status) {
      case 'preparation':
        if (interview.documents.length === 0) {
          setCurrentView('documents')
        } else {
          setCurrentView('preparation')
        }
        break
      case 'active':
        setCurrentView('live')
        break
      case 'completed':
        setCurrentView('results')
        break
      default:
        setCurrentView('documents')
    }
  }

  const getProgressPercentage = (interview) => {
    if (!interview) return 0
    
    switch (interview.status) {
      case 'preparation':
        return interview.documents.length > 0 ? 40 : 20
      case 'active':
        return 70
      case 'completed':
        return 100
      default:
        return 0
    }
  }

  const renderHeader = () => (
    <div className="border-b bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Synergos AI</h1>
                <p className="text-sm text-gray-600">Interview Companion Tool</p>
              </div>
            </div>
          </div>
          
          {currentInterview && (
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {currentInterview.candidate_name}
                </p>
                <p className="text-xs text-gray-600">
                  {currentInterview.position_title}
                </p>
              </div>
              <Badge variant={
                currentInterview.status === 'completed' ? 'default' :
                currentInterview.status === 'active' ? 'destructive' : 'secondary'
              }>
                {currentInterview.status}
              </Badge>
            </div>
          )}
          
          <div className="flex space-x-2">
            <Button 
              variant="outline"
              size="icon"
              onClick={() => setShowSettings(true)}
              title="API Settings"
            >
              <SettingsIcon className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              onClick={() => {
                setCurrentView('dashboard')
                setCurrentInterview(null)
              }}
            >
              Dashboard
            </Button>
          </div>
        </div>
        
        {currentInterview && (
          <div className="mt-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-sm font-medium text-gray-700">Progress:</span>
              <span className="text-sm text-gray-600">
                {getProgressPercentage(currentInterview)}%
              </span>
            </div>
            <Progress value={getProgressPercentage(currentInterview)} className="h-2" />
          </div>
        )}
      </div>
    </div>
  )

  const renderNavigation = () => {
    if (!currentInterview) return null

    const navItems = [
      { key: 'documents', label: 'Documents', icon: FileText, enabled: true },
      { 
        key: 'preparation', 
        label: 'Preparation', 
        icon: Users, 
        enabled: currentInterview.documents.length > 0 
      },
      { 
        key: 'live', 
        label: 'Live Interview', 
        icon: Mic, 
        enabled: currentInterview.status !== 'preparation' || currentInterview.questions?.length > 0 
      },
      { 
        key: 'results', 
        label: 'Results', 
        icon: BarChart3, 
        enabled: currentInterview.status === 'completed' 
      },
    ]

    return (
      <div className="border-b bg-gray-50">
        <div className="container mx-auto px-4">
          <nav className="flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = currentView === item.key
              const isEnabled = item.enabled
              
              return (
                <button
                  key={item.key}
                  onClick={() => isEnabled && setCurrentView(item.key)}
                  disabled={!isEnabled}
                  className={`
                    flex items-center space-x-2 py-4 px-2 border-b-2 text-sm font-medium transition-colors
                    ${isActive 
                      ? 'border-blue-500 text-blue-600' 
                      : isEnabled 
                        ? 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        : 'border-transparent text-gray-300 cursor-not-allowed'
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                  {isActive && <CheckCircle className="h-3 w-3" />}
                </button>
              )
            })}
          </nav>
        </div>
      </div>
    )
  }

  const renderDashboard = () => (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Welcome Section */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-6 w-6 text-blue-600" />
                <span>Welcome to Synergos AI</span>
              </CardTitle>
              <CardDescription>
                Your AI-powered interview companion tool designed to streamline and optimize recruitment processes.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
                  <FileText className="h-8 w-8 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Document Analysis</h3>
                    <p className="text-sm text-gray-600">AI-powered resume and job listing analysis</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
                  <MessageSquare className="h-8 w-8 text-green-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Smart Questions</h3>
                    <p className="text-sm text-gray-600">Tailored interview questions generation</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-4 bg-purple-50 rounded-lg">
                  <Mic className="h-8 w-8 text-purple-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Live Transcription</h3>
                    <p className="text-sm text-gray-600">Real-time speech-to-text with speaker detection</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-4 bg-orange-50 rounded-lg">
                  <BarChart3 className="h-8 w-8 text-orange-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Performance Analytics</h3>
                    <p className="text-sm text-gray-600">STAR method analysis and candidate evaluation</p>
                  </div>
                </div>
              </div>
              
              <Button 
                onClick={() => setCurrentView('setup')} 
                className="w-full md:w-auto"
                size="lg"
              >
                <Play className="h-4 w-4 mr-2" />
                Start New Interview
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Interview Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Interviews</span>
                  <span className="font-semibold">{interviews.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Completed</span>
                  <span className="font-semibold">
                    {interviews.filter(i => i.status === 'completed').length}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">In Progress</span>
                  <span className="font-semibold">
                    {interviews.filter(i => i.status === 'active').length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <InterviewList 
            interviews={interviews}
            onSelectInterview={selectInterview}
            onRefresh={fetchInterviews}
          />
        </div>
      </div>
    </div>
  )

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return renderDashboard()
      case 'setup':
        return (
          <InterviewSetup 
            onCreateInterview={createNewInterview}
            loading={loading}
          />
        )
      case 'documents':
        return (
          <DocumentUpload 
            interview={currentInterview}
            onDocumentsUploaded={() => {
              fetchInterviews()
              setCurrentView('preparation')
            }}
          />
        )
      case 'preparation':
        return (
          <InterviewPreparation 
            interview={currentInterview}
            onStartInterview={() => setCurrentView('live')}
            onRefresh={fetchInterviews}
          />
        )
      case 'live':
        return (
          <LiveInterview 
            interview={currentInterview}
            onCompleteInterview={() => {
              fetchInterviews()
              setCurrentView('results')
            }}
          />
        )
      case 'results':
        return (
          <InterviewResults 
            interview={currentInterview}
            onNewInterview={() => setCurrentView('setup')}
          />
        )
      default:
        return renderDashboard()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {renderHeader()}
      {renderNavigation()}
      <main className="flex-1">
        {renderCurrentView()}
      </main>
      {showSettings && <Settings onClose={() => setShowSettings(false)} />}
    </div>
  )
}

export default App

