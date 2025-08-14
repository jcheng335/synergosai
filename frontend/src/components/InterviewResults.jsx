import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  BarChart3, 
  TrendingUp, 
  Award, 
  FileText, 
  MessageSquare,
  Star,
  CheckCircle,
  AlertCircle,
  Plus,
  Download,
  Share
} from 'lucide-react'

const API_BASE_URL = '/api'

const InterviewResults = ({ interview, onNewInterview }) => {
  const [finalEvaluation, setFinalEvaluation] = useState(null)
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchInterviewResults()
  }, [interview.id])

  const fetchInterviewResults = async () => {
    try {
      setLoading(true)
      
      // In a real implementation, this would fetch the final evaluation
      // For now, we'll simulate the data
      const mockEvaluation = {
        overall_score: 78,
        category_scores: {
          technical_competency: 82,
          communication_skills: 85,
          cultural_fit: 75,
          problem_solving: 80,
          leadership_potential: 70
        },
        strengths: [
          "Strong technical background with relevant experience",
          "Excellent communication and articulation skills",
          "Demonstrated problem-solving abilities",
          "Good understanding of industry best practices"
        ],
        areas_for_development: [
          "Could provide more specific examples in behavioral responses",
          "Leadership experience could be more extensive"
        ],
        recommendation: "hire",
        key_insights: [
          "Candidate shows strong technical competency aligned with job requirements",
          "Communication style would fit well with team culture",
          "Previous experience directly applicable to role responsibilities"
        ],
        next_steps: [
          "Schedule technical interview with team lead",
          "Check references from previous employers"
        ],
        summary: "Strong candidate with excellent technical skills and communication abilities. Recommended for next round of interviews with some areas for further exploration."
      }

      setFinalEvaluation(mockEvaluation)
      setResponses(interview.responses || [])
      
    } catch (error) {
      setError('Failed to load interview results')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBackground = (score) => {
    if (score >= 80) return 'bg-green-100'
    if (score >= 60) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  const getRecommendationBadge = (recommendation) => {
    const variants = {
      strong_hire: { variant: 'default', color: 'bg-green-600', text: 'Strong Hire' },
      hire: { variant: 'default', color: 'bg-blue-600', text: 'Hire' },
      maybe: { variant: 'secondary', color: 'bg-yellow-600', text: 'Maybe' },
      no_hire: { variant: 'destructive', color: 'bg-red-600', text: 'No Hire' }
    }
    
    const config = variants[recommendation] || variants.maybe
    return (
      <Badge className={`${config.color} text-white`}>
        {config.text}
      </Badge>
    )
  }

  const renderOverviewSection = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Overall Score</p>
              <p className={`text-3xl font-bold ${getScoreColor(finalEvaluation.overall_score)}`}>
                {finalEvaluation.overall_score}
              </p>
            </div>
            <Award className={`h-8 w-8 ${getScoreColor(finalEvaluation.overall_score)}`} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recommendation</p>
              <div className="mt-2">
                {getRecommendationBadge(finalEvaluation.recommendation)}
              </div>
            </div>
            <TrendingUp className="h-8 w-8 text-blue-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Questions Asked</p>
              <p className="text-3xl font-bold text-gray-900">
                {interview.questions?.filter(q => q.is_asked).length || 0}
              </p>
            </div>
            <MessageSquare className="h-8 w-8 text-purple-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Duration</p>
              <p className="text-3xl font-bold text-gray-900">
                {interview.started_at && interview.completed_at 
                  ? Math.round((new Date(interview.completed_at) - new Date(interview.started_at)) / (1000 * 60))
                  : 0}m
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-orange-600" />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderScoreBreakdown = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <span>Score Breakdown</span>
        </CardTitle>
        <CardDescription>
          Detailed evaluation across different competency areas
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {Object.entries(finalEvaluation.category_scores).map(([category, score]) => (
            <div key={category} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium capitalize text-gray-700">
                  {category.replace('_', ' ')}
                </span>
                <span className={`text-sm font-bold ${getScoreColor(score)}`}>
                  {score}/100
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${
                    score >= 80 ? 'bg-green-600' : 
                    score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                  }`}
                  style={{ width: `${score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const renderInsightsSection = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-green-700">
            <CheckCircle className="h-5 w-5" />
            <span>Strengths</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {finalEvaluation.strengths.map((strength, index) => (
              <li key={index} className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-orange-700">
            <AlertCircle className="h-5 w-5" />
            <span>Areas for Development</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {finalEvaluation.areas_for_development.map((area, index) => (
              <li key={index} className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-orange-600 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-gray-700">{area}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )

  const renderResponsesSection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <MessageSquare className="h-5 w-5 text-purple-600" />
          <span>Interview Responses</span>
        </CardTitle>
        <CardDescription>
          Summary of candidate responses with STAR analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {responses.map((response, index) => (
            <div key={response.id} className="border-l-4 border-blue-200 pl-4">
              <div className="mb-3">
                <h4 className="font-semibold text-gray-900 mb-1">
                  Question {index + 1}
                </h4>
                <p className="text-sm text-gray-600 mb-2">{response.question_text}</p>
              </div>

              {response.summary_points && response.summary_points.length > 0 && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Key Points:</h5>
                  <ul className="list-disc list-inside space-y-1">
                    {response.summary_points.map((point, idx) => (
                      <li key={idx} className="text-sm text-gray-600">{point}</li>
                    ))}
                  </ul>
                </div>
              )}

              {response.star_analysis && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">STAR Analysis:</h5>
                  <div className="flex space-x-2">
                    {Object.entries(response.star_analysis).map(([component, data]) => (
                      <Badge 
                        key={component}
                        variant={data.present ? 'default' : 'secondary'}
                        className={`text-xs ${
                          data.present ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}
                      >
                        <Star className="h-3 w-3 mr-1" />
                        {component.charAt(0).toUpperCase()}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {response.evaluation_score && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Response Score:</span>
                  <Badge variant="outline">
                    {Math.round(response.evaluation_score * 10)}/10
                  </Badge>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const renderSummarySection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="h-5 w-5 text-gray-600" />
          <span>Executive Summary</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Overall Assessment</h4>
            <p className="text-gray-700 leading-relaxed">{finalEvaluation.summary}</p>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Key Insights</h4>
            <ul className="space-y-2">
              {finalEvaluation.key_insights.map((insight, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-gray-700">{insight}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Recommended Next Steps</h4>
            <ul className="space-y-2">
              {finalEvaluation.next_steps.map((step, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-gray-700">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Loading interview results...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">{error}</p>
                <Button onClick={fetchInterviewResults} variant="outline">
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Interview Results</h2>
              <p className="text-gray-600">
                Comprehensive evaluation and analysis of {interview.candidate_name}'s interview performance
              </p>
            </div>
            
            <div className="flex space-x-3">
              <Button variant="outline" className="flex items-center space-x-2">
                <Download className="h-4 w-4" />
                <span>Export Report</span>
              </Button>
              <Button variant="outline" className="flex items-center space-x-2">
                <Share className="h-4 w-4" />
                <span>Share</span>
              </Button>
              <Button onClick={onNewInterview} className="flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>New Interview</span>
              </Button>
            </div>
          </div>
        </div>

        {finalEvaluation && (
          <div className="space-y-8">
            {renderOverviewSection()}
            
            <Tabs defaultValue="scores" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="scores">Scores</TabsTrigger>
                <TabsTrigger value="insights">Insights</TabsTrigger>
                <TabsTrigger value="responses">Responses</TabsTrigger>
                <TabsTrigger value="summary">Summary</TabsTrigger>
              </TabsList>
              
              <TabsContent value="scores" className="mt-6">
                {renderScoreBreakdown()}
              </TabsContent>
              
              <TabsContent value="insights" className="mt-6">
                {renderInsightsSection()}
              </TabsContent>
              
              <TabsContent value="responses" className="mt-6">
                {renderResponsesSection()}
              </TabsContent>
              
              <TabsContent value="summary" className="mt-6">
                {renderSummarySection()}
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  )
}

export default InterviewResults

