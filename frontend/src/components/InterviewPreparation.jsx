import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Brain, 
  MessageSquare, 
  CheckCircle, 
  Play, 
  Eye, 
  Lightbulb,
  Target,
  Users,
  Clock
} from 'lucide-react'

const API_BASE_URL = '/api'

const InterviewPreparation = ({ interview, onStartInterview, onRefresh }) => {
  const [questions, setQuestions] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [startingInterview, setStartingInterview] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchQuestions()
  }, [interview.id])

  const fetchQuestions = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/interviews/${interview.id}/questions`)
      
      if (response.ok) {
        const data = await response.json()
        setQuestions(data.questions)
        
        // Get analysis from documents
        const resumeDoc = interview.documents.find(d => d.document_type === 'resume')
        if (resumeDoc && resumeDoc.analysis_result) {
          setAnalysis(resumeDoc.analysis_result)
        }
      } else {
        setError('Failed to load questions')
      }
    } catch (error) {
      setError('Failed to load questions')
    } finally {
      setLoading(false)
    }
  }

  const startInterview = async () => {
    try {
      setStartingInterview(true)
      const response = await fetch(`${API_BASE_URL}/interviews/${interview.id}/start`, {
        method: 'POST'
      })
      
      if (response.ok) {
        onRefresh()
        onStartInterview()
      } else {
        setError('Failed to start interview')
      }
    } catch (error) {
      setError('Failed to start interview')
    } finally {
      setStartingInterview(false)
    }
  }

  const generatedQuestions = questions.filter(q => q.is_generated)
  const commonQuestions = questions.filter(q => !q.is_generated)

  const getCategoryColor = (category) => {
    const colors = {
      behavioral: 'bg-blue-100 text-blue-800',
      technical: 'bg-green-100 text-green-800',
      situational: 'bg-purple-100 text-purple-800',
      cultural: 'bg-orange-100 text-orange-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const renderQuestionCard = (question, index) => (
    <Card key={question.id} className="mb-4">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-500">Q{index + 1}</span>
            <Badge className={getCategoryColor(question.category)}>
              {question.category}
            </Badge>
            {question.is_generated && (
              <Badge variant="outline" className="text-xs">
                <Brain className="h-3 w-3 mr-1" />
                AI Generated
              </Badge>
            )}
          </div>
        </div>
        
        <p className="text-gray-900 leading-relaxed">{question.text}</p>
        
        {question.rationale && (
          <div className="mt-3 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-start space-x-2">
              <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-blue-800">{question.rationale}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  const renderAnalysisSection = () => {
    if (!analysis) return null

    return (
      <div className="space-y-6">
        {/* Candidate Profile */}
        {analysis.candidate_profile && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span>Candidate Profile</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysis.candidate_profile.key_skills && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Key Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.candidate_profile.key_skills.map((skill, index) => (
                      <Badge key={index} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {analysis.candidate_profile.experience_years && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Experience</h4>
                  <p className="text-gray-600">{analysis.candidate_profile.experience_years}</p>
                </div>
              )}
              
              {analysis.candidate_profile.strengths && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Strengths</h4>
                  <ul className="list-disc list-inside text-gray-600 space-y-1">
                    {analysis.candidate_profile.strengths.map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Match Analysis */}
        {analysis.match_analysis && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-green-600" />
                <span>Job Match Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysis.match_analysis.skill_match_percentage && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-gray-900">Skill Match</span>
                    <span className="text-lg font-bold text-green-600">
                      {analysis.match_analysis.skill_match_percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${analysis.match_analysis.skill_match_percentage}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {analysis.match_analysis.gaps_to_explore && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Areas to Explore</h4>
                  <ul className="list-disc list-inside text-gray-600 space-y-1">
                    {analysis.match_analysis.gaps_to_explore.map((gap, index) => (
                      <li key={index}>{gap}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Loading interview preparation...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Interview Preparation</h2>
          <p className="text-gray-600">
            Review the AI-generated questions and candidate analysis before starting the interview.
          </p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Questions Section */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="generated" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="generated" className="flex items-center space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>AI Generated ({generatedQuestions.length})</span>
                </TabsTrigger>
                <TabsTrigger value="common" className="flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4" />
                  <span>Common Questions ({commonQuestions.length})</span>
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="generated" className="mt-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <Brain className="h-5 w-5 text-blue-600" />
                    <h3 className="text-lg font-semibold">Tailored Questions</h3>
                    <Badge variant="outline">Based on resume & job analysis</Badge>
                  </div>
                  
                  {generatedQuestions.length > 0 ? (
                    generatedQuestions.map((question, index) => renderQuestionCard(question, index))
                  ) : (
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center py-8">
                          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-gray-600">No AI-generated questions available.</p>
                          <p className="text-sm text-gray-500 mt-2">
                            Make sure documents have been analyzed.
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="common" className="mt-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <MessageSquare className="h-5 w-5 text-green-600" />
                    <h3 className="text-lg font-semibold">Standard HR Questions</h3>
                    <Badge variant="outline">Common interview questions</Badge>
                  </div>
                  
                  {commonQuestions.length > 0 ? (
                    commonQuestions.map((question, index) => renderQuestionCard(question, index))
                  ) : (
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center py-8">
                          <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-gray-600">No common questions loaded.</p>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Analysis & Controls */}
          <div className="space-y-6">
            {/* Start Interview Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Play className="h-5 w-5 text-green-600" />
                  <span>Ready to Start?</span>
                </CardTitle>
                <CardDescription>
                  Begin the live interview session with real-time transcription and AI assistance.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-sm text-gray-600">
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span>Questions prepared</span>
                    </div>
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span>Documents analyzed</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span>Ready for live session</span>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={startInterview}
                    disabled={startingInterview}
                    className="w-full"
                    size="lg"
                  >
                    {startingInterview ? (
                      <>
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        Starting Interview...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Start Interview
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Section */}
            {renderAnalysisSection()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default InterviewPreparation

