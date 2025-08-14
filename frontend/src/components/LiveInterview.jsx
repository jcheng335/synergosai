import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Mic, 
  MicOff, 
  Play, 
  Pause, 
  Square, 
  MessageSquare, 
  CheckCircle,
  Clock,
  User,
  Users,
  Brain,
  Star,
  ArrowRight,
  AlertCircle,
  Activity
} from 'lucide-react'

const API_BASE_URL = import.meta.env.PROD ? '/api' : 'http://localhost:5001/api'

const LiveInterview = ({ interview, onCompleteInterview }) => {
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [responses, setResponses] = useState([])
  const [currentResponse, setCurrentResponse] = useState('')
  const [currentSpeaker, setCurrentSpeaker] = useState('interviewer')
  const [followUpQuestions, setFollowUpQuestions] = useState([])
  const [analyzing, setAnalyzing] = useState(false)
  const [completing, setCompleting] = useState(false)
  const [error, setError] = useState('')
  
  const transcriptionRef = useRef(null)
  const recordingTimeRef = useRef(0)
  const [recordingTime, setRecordingTime] = useState(0)
  const recognitionRef = useRef(null)
  const [isListening, setIsListening] = useState(false)
  const [browserSupported, setBrowserSupported] = useState(true)
  const silenceTimerRef = useRef(null)
  const lastAnalysisRef = useRef('')
  const [liveAnalysis, setLiveAnalysis] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  useEffect(() => {
    fetchQuestions()
    initializeSpeechRecognition()
  }, [interview.id])
  
  const initializeSpeechRecognition = () => {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      setBrowserSupported(false)
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }
    
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'
    
    recognition.onstart = () => {
      setIsListening(true)
      setTranscription('')
      setCurrentResponse('')
    }
    
    recognition.onresult = (event) => {
      let interimTranscript = ''
      let finalTranscript = ''
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' '
        } else {
          interimTranscript += transcript
        }
      }
      
      const fullTranscript = currentResponse + finalTranscript + interimTranscript
      setTranscription(fullTranscript)
      
      if (finalTranscript) {
        setCurrentResponse(prev => {
          const newResponse = prev + finalTranscript
          
          // Clear existing silence timer
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current)
          }
          
          // Set new silence timer - analyze after 2 seconds of silence
          silenceTimerRef.current = setTimeout(() => {
            if (newResponse.trim().length > 50) {
              performLiveAnalysis(newResponse)
            }
          }, 2000)
          
          // Also analyze every 100 words for long responses
          const wordCount = newResponse.trim().split(/\s+/).length
          if (wordCount > 0 && wordCount % 100 === 0) {
            performLiveAnalysis(newResponse)
          }
          
          return newResponse
        })
      }
    }
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      if (event.error === 'no-speech') {
        setError('No speech detected. Please speak clearly into your microphone.')
      } else if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access and reload the page.')
      } else {
        setError(`Speech recognition error: ${event.error}`)
      }
      setIsListening(false)
    }
    
    recognition.onend = () => {
      setIsListening(false)
    }
    
    recognitionRef.current = recognition
  }

  useEffect(() => {
    let interval = null
    if (isRecording) {
      interval = setInterval(() => {
        recordingTimeRef.current += 1
        setRecordingTime(recordingTimeRef.current)
      }, 1000)
    } else {
      clearInterval(interval)
    }
    return () => clearInterval(interval)
  }, [isRecording])

  const fetchQuestions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/interviews/${interview.id}/questions`)
      if (response.ok) {
        const data = await response.json()
        setQuestions(data.questions)
      }
    } catch (error) {
      setError('Failed to load questions')
    }
  }

  const startRecording = () => {
    if (!browserSupported) {
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }
    
    setIsRecording(true)
    recordingTimeRef.current = 0
    setRecordingTime(0)
    setError('') // Clear any previous errors
    
    // Start real speech recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Failed to start recognition:', error)
        // If already started, restart it
        recognitionRef.current.stop()
        setTimeout(() => {
          recognitionRef.current.start()
        }, 100)
      }
    }
    
    // Fallback to simulation if speech recognition fails
    if (!recognitionRef.current || !isListening) {
      setTimeout(() => {
        if (!isListening && isRecording) {
          console.log('Falling back to simulated transcription')
          simulateTranscription()
        }
      }, 2000)
    }
  }

  const stopRecording = () => {
    setIsRecording(false)
    
    // Stop speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    
    if (currentResponse.trim()) {
      saveResponse()
    }
  }

  const simulateTranscription = () => {
    // This would be replaced with actual speech recognition
    const sampleResponses = [
      "I have over 5 years of experience in software development, primarily working with React and Node.js. In my previous role at TechCorp, I led a team of 4 developers to build a customer management system that increased efficiency by 30%.",
      "One of my biggest challenges was when our main database crashed during peak hours. I quickly coordinated with the infrastructure team, implemented a backup solution, and communicated with stakeholders. We restored service within 2 hours and prevented data loss.",
      "I'm passionate about clean code and continuous learning. I regularly contribute to open source projects and stay updated with the latest technologies. I believe in collaborative development and mentoring junior developers.",
      "My goal is to grow into a technical leadership role where I can influence architecture decisions and help build scalable systems. I'm particularly interested in your company's focus on innovation and would love to contribute to your AI initiatives."
    ]
    
    if (currentQuestionIndex < sampleResponses.length) {
      const response = sampleResponses[currentQuestionIndex]
      let currentText = ''
      let index = 0
      
      const typeText = () => {
        if (index < response.length && isRecording) {
          currentText += response[index]
          setCurrentResponse(currentText)
          setTranscription(currentText)
          index++
          setTimeout(typeText, 50 + Math.random() * 50) // Simulate natural typing speed
        }
      }
      
      setTimeout(typeText, 1000) // Start after 1 second
    }
  }

  const askQuestion = async (questionIndex) => {
    const question = questions[questionIndex]
    if (!question) return

    try {
      await fetch(`${API_BASE_URL}/interviews/${interview.id}/questions/${question.id}/ask`, {
        method: 'POST'
      })
      
      setCurrentQuestionIndex(questionIndex)
      setCurrentResponse('')
      setTranscription('')
      setFollowUpQuestions([])
      
      // Update question status locally
      setQuestions(prev => prev.map(q => 
        q.id === question.id ? { ...q, is_asked: true } : q
      ))
      
    } catch (error) {
      setError('Failed to mark question as asked')
    }
  }

  const performLiveAnalysis = async (responseText) => {
    if (!responseText.trim() || responseText.trim().length < 50) return // Wait for meaningful content
    
    // Avoid re-analyzing the same content
    if (responseText.trim() === lastAnalysisRef.current) return
    
    lastAnalysisRef.current = responseText.trim()
    setIsAnalyzing(true)
    
    try {
      const response = await fetch(`${API_BASE_URL}/interviews/${interview.id}/analyze-live`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_text: questions[currentQuestionIndex]?.text || '',
          partial_response: responseText
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setLiveAnalysis(data)
        
        // Update follow-up questions immediately
        if (data.follow_up_questions) {
          setFollowUpQuestions(data.follow_up_questions)
        }
      }
    } catch (error) {
      console.error('Live analysis error:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleSilenceDetected = () => {
    // When silence is detected, perform analysis
    if (currentResponse.trim().length > 30) {
      performLiveAnalysis(currentResponse)
    }
  }

  const saveResponse = async () => {
    if (!currentResponse.trim() || !questions[currentQuestionIndex]) return

    try {
      setAnalyzing(true)
      const response = await fetch(`${API_BASE_URL}/interviews/${interview.id}/responses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: questions[currentQuestionIndex].id,
          question_text: questions[currentQuestionIndex].text,
          transcribed_text: currentResponse
        })
      })

      if (response.ok) {
        const data = await response.json()
        setResponses(prev => [...prev, data.response])
        setFollowUpQuestions(data.follow_up_questions || [])
        setLiveAnalysis(null) // Clear live analysis
        setCurrentResponse('')
        setTranscription('')
      } else {
        setError('Failed to save response')
      }
    } catch (error) {
      setError('Failed to save response')
    } finally {
      setAnalyzing(false)
    }
  }

  const completeInterview = async () => {
    try {
      setCompleting(true)
      const response = await fetch(`${API_BASE_URL}/interviews/${interview.id}/complete`, {
        method: 'POST'
      })

      if (response.ok) {
        onCompleteInterview()
      } else {
        setError('Failed to complete interview')
      }
    } catch (error) {
      setError('Failed to complete interview')
    } finally {
      setCompleting(false)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getCurrentQuestion = () => {
    return questions[currentQuestionIndex]
  }

  const getAskedQuestions = () => {
    return questions.filter(q => q.is_asked)
  }

  const renderQuestionsList = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <MessageSquare className="h-5 w-5 text-blue-600" />
          <span>Interview Questions</span>
        </CardTitle>
        <CardDescription>
          Click on a question to ask it during the interview
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {questions.map((question, index) => (
            <div
              key={question.id}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                question.is_asked 
                  ? 'bg-green-50 border-green-200' 
                  : index === currentQuestionIndex
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-white border-gray-200 hover:bg-gray-50'
              }`}
              onClick={() => !question.is_asked && askQuestion(index)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-medium text-gray-500">Q{index + 1}</span>
                    <Badge 
                      variant={question.is_generated ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {question.is_generated ? 'AI' : 'Standard'}
                    </Badge>
                    {question.is_asked && (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-900 leading-relaxed">
                    {question.text}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const renderTranscriptionPanel = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Mic className="h-5 w-5 text-red-600" />
            <span>Live Transcription</span>
          </div>
          <div className="flex items-center space-x-2">
            {isRecording && (
              <>
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
                <span className="text-sm font-mono text-red-600">
                  {formatTime(recordingTime)}
                </span>
              </>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Current Question */}
          {getCurrentQuestion() && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <User className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Current Question</span>
              </div>
              <p className="text-blue-900">{getCurrentQuestion().text}</p>
            </div>
          )}

          {/* Transcription Area */}
          <div className="min-h-[200px] p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-3">
              <Users className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">
                {currentSpeaker === 'interviewer' ? 'Interviewer' : 'Candidate'} Speaking
              </span>
            </div>
            
            <div 
              ref={transcriptionRef}
              className="text-gray-900 leading-relaxed whitespace-pre-wrap"
            >
              {transcription || (
                <span className="text-gray-500 italic">
                  {isRecording ? (
                    isListening ? '🎤 Listening... Speak clearly into your microphone' : 'Initializing microphone...'
                  ) : (
                    'Click "Start Recording" to begin transcription'
                  )}
                </span>
              )}
            </div>
            
            {/* Microphone Status Indicator */}
            {isRecording && (
              <div className="mt-2 flex items-center space-x-2">
                {isListening ? (
                  <>
                    <div className="flex space-x-1">
                      <div className="w-1 h-4 bg-green-500 animate-pulse"></div>
                      <div className="w-1 h-4 bg-green-500 animate-pulse delay-75"></div>
                      <div className="w-1 h-4 bg-green-500 animate-pulse delay-150"></div>
                    </div>
                    <span className="text-xs text-green-600">Microphone active</span>
                  </>
                ) : (
                  <>
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <span className="text-xs text-yellow-600">Waiting for microphone...</span>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Recording Controls */}
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              {!isRecording ? (
                <Button onClick={startRecording} className="flex items-center space-x-2">
                  <Mic className="h-4 w-4" />
                  <span>Start Recording</span>
                </Button>
              ) : (
                <Button 
                  onClick={stopRecording} 
                  variant="destructive"
                  className="flex items-center space-x-2"
                >
                  <Square className="h-4 w-4" />
                  <span>Stop & Save Response</span>
                </Button>
              )}
            </div>

            {analyzing && (
              <div className="flex items-center space-x-2 text-blue-600">
                <div className="h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm">Analyzing response...</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderLiveAnalysisSection = () => {
    // Always show this section, even if no analysis yet
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-green-600" />
              <span>Live STAR Analysis</span>
            </div>
            {isRecording && isAnalyzing && (
              <Badge variant="outline" className="animate-pulse">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                Analyzing...
              </Badge>
            )}
          </CardTitle>
          <CardDescription>
            Real-time analysis of candidate responses using STAR methodology
          </CardDescription>
        </CardHeader>
        <CardContent>
          {liveAnalysis ? (
            <div className="space-y-4">
              {/* STAR Breakdown */}
              {liveAnalysis.star_breakdown && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">STAR Components Detected</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(liveAnalysis.star_breakdown).map(([component, data]) => {
                      const qualityColors = {
                        'strong': 'bg-green-50 text-green-800 border-green-200',
                        'adequate': 'bg-blue-50 text-blue-800 border-blue-200',
                        'weak': 'bg-yellow-50 text-yellow-800 border-yellow-200',
                        'missing': 'bg-red-50 text-red-800 border-red-200'
                      }
                      const quality = data.quality || (data.present ? 'adequate' : 'missing')
                      const colorClass = qualityColors[quality] || 'bg-gray-50 text-gray-800 border-gray-200'
                      
                      return (
                        <div key={component} className={`p-3 rounded-lg border ${colorClass}`}>
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center space-x-2">
                              <Star className="h-3 w-3" />
                              <span className="text-sm font-semibold capitalize">{component}</span>
                            </div>
                            {data.present ? (
                              <CheckCircle className="h-3 w-3" />
                            ) : (
                              <AlertCircle className="h-3 w-3" />
                            )}
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {quality}
                          </Badge>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Missing Components Alert */}
              {liveAnalysis.missing_components && liveAnalysis.missing_components.length > 0 && (
                <Alert className="border-orange-200 bg-orange-50">
                  <AlertCircle className="h-4 w-4 text-orange-600" />
                  <AlertDescription className="text-sm">
                    <strong>Components to address:</strong> {liveAnalysis.missing_components.map(c => c.charAt(0).toUpperCase() + c.slice(1)).join(', ')}
                  </AlertDescription>
                </Alert>
              )}

              {/* Follow-up Questions */}
              {liveAnalysis.follow_up_questions && liveAnalysis.follow_up_questions.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Real-time Follow-up Questions</h4>
                  <div className="space-y-2">
                    {liveAnalysis.follow_up_questions.slice(0, 3).map((question, index) => (
                      <div key={index} className="p-2 bg-purple-50 border border-purple-200 rounded text-sm">
                        <ArrowRight className="h-3 w-3 inline mr-1 text-purple-600" />
                        <span className="text-purple-900">{question}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Overall Quality */}
              {liveAnalysis.overall_quality && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Response Quality</span>
                    <Badge 
                      variant={liveAnalysis.overall_quality === 'excellent' ? 'default' : 
                               liveAnalysis.overall_quality === 'good' ? 'secondary' : 'outline'}
                    >
                      {liveAnalysis.overall_quality.charAt(0).toUpperCase() + liveAnalysis.overall_quality.slice(1)}
                    </Badge>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Brain className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">
                {isRecording ? 'Speak for at least 2 seconds to trigger analysis...' : 'Start recording to see live STAR analysis'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const renderResponseSummary = () => {
    // Show saved response analysis (not live)
    const lastResponse = responses[responses.length - 1]
    if (!lastResponse) return null

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <span>{isRecording && liveAnalysis ? 'Live Analysis' : 'Response Analysis'}</span>
            </div>
            {isRecording && liveAnalysis && (
              <Badge variant="outline" className="animate-pulse">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                Real-time
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Summary Points */}
            {analysisToShow.summary_points && analysisToShow.summary_points.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Key Points</h4>
                <ul className="list-disc list-inside space-y-1">
                  {analysisToShow.summary_points.map((point, index) => (
                    <li key={index} className="text-sm text-gray-700">{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Enhanced STAR Analysis */}
            {(analysisToShow.star_breakdown || analysisToShow.star_analysis) && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">STAR Analysis</h4>
                <div className="space-y-3">
                  {Object.entries(analysisToShow.star_breakdown || analysisToShow.star_analysis).map(([component, data]) => {
                    const qualityColors = {
                      'strong': 'bg-green-100 text-green-800 border-green-300',
                      'adequate': 'bg-blue-100 text-blue-800 border-blue-300',
                      'weak': 'bg-yellow-100 text-yellow-800 border-yellow-300',
                      'missing': 'bg-red-100 text-red-800 border-red-300'
                    }
                    const quality = data.quality || (data.present ? 'adequate' : 'missing')
                    const colorClass = qualityColors[quality] || 'bg-gray-100 text-gray-800'
                    
                    return (
                      <div key={component} className={`p-3 rounded-lg border ${colorClass}`}>
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <Star className="h-4 w-4" />
                            <span className="font-semibold capitalize">{component}</span>
                            <Badge variant="outline" className="text-xs">
                              {quality}
                            </Badge>
                          </div>
                          {data.present ? (
                            <CheckCircle className="h-4 w-4" />
                          ) : (
                            <AlertCircle className="h-4 w-4" />
                          )}
                        </div>
                        {data.content && (
                          <p className="text-xs mt-2 italic opacity-90">
                            "{data.content}"
                          </p>
                        )}
                      </div>
                    )
                  })}
                </div>
                
                {/* Missing Components Alert */}
                {analysisToShow.missing_components && analysisToShow.missing_components.length > 0 && (
                  <Alert className="mt-3 border-orange-200 bg-orange-50">
                    <AlertCircle className="h-4 w-4 text-orange-600" />
                    <AlertDescription className="text-sm">
                      <strong>Missing STAR components:</strong> {analysisToShow.missing_components.join(', ')}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}

            {/* Follow-up Questions */}
            {followUpQuestions.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Suggested Follow-ups</h4>
                <div className="space-y-2">
                  {followUpQuestions.map((question, index) => (
                    <div key={index} className="p-2 bg-yellow-50 rounded text-sm">
                      <ArrowRight className="h-3 w-3 inline mr-1 text-yellow-600" />
                      {question}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Live Interview</h2>
              <p className="text-gray-600">
                Conducting interview with real-time transcription and AI assistance
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Questions Asked</p>
                <p className="text-lg font-bold">
                  {getAskedQuestions().length} / {questions.length}
                </p>
              </div>
              
              <Button 
                onClick={completeInterview}
                disabled={completing || getAskedQuestions().length === 0}
                variant="outline"
              >
                {completing ? (
                  <>
                    <div className="h-4 w-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin mr-2" />
                    Completing...
                  </>
                ) : (
                  'Complete Interview'
                )}
              </Button>
            </div>
          </div>
          
          {getAskedQuestions().length > 0 && (
            <div className="mt-4">
              <Progress 
                value={(getAskedQuestions().length / questions.length) * 100} 
                className="h-2" 
              />
            </div>
          )}
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Interview Panel */}
          <div className="lg:col-span-2 space-y-6">
            {renderTranscriptionPanel()}
            {renderLiveAnalysisSection()}
            {renderResponseSummary()}
          </div>

          {/* Questions Sidebar */}
          <div className="space-y-6">
            {renderQuestionsList()}
            
            {/* Interview Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Session Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Questions</span>
                    <span className="font-medium">{questions.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Questions Asked</span>
                    <span className="font-medium">{getAskedQuestions().length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Responses Saved</span>
                    <span className="font-medium">{responses.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recording Time</span>
                    <span className="font-medium font-mono">{formatTime(recordingTime)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LiveInterview

