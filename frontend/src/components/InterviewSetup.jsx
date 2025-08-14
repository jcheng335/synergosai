import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Users, Briefcase, Mail, User } from 'lucide-react'

const InterviewSetup = ({ onCreateInterview, loading }) => {
  const [formData, setFormData] = useState({
    interviewer_name: '',
    interviewer_email: '',
    candidate_name: '',
    candidate_email: '',
    position_title: '',
  })
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.interviewer_name.trim()) {
      newErrors.interviewer_name = 'Interviewer name is required'
    }
    
    if (!formData.interviewer_email.trim()) {
      newErrors.interviewer_email = 'Interviewer email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.interviewer_email)) {
      newErrors.interviewer_email = 'Please enter a valid email address'
    }
    
    if (!formData.candidate_name.trim()) {
      newErrors.candidate_name = 'Candidate name is required'
    }
    
    if (!formData.position_title.trim()) {
      newErrors.position_title = 'Position title is required'
    }
    
    if (formData.candidate_email && !/\S+@\S+\.\S+/.test(formData.candidate_email)) {
      newErrors.candidate_email = 'Please enter a valid email address'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitError('')
    
    if (!validateForm()) {
      return
    }
    
    try {
      await onCreateInterview(formData)
    } catch (error) {
      setSubmitError(error.message || 'Failed to create interview. Please try again.')
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-6 w-6 text-blue-600" />
              <span>Create New Interview</span>
            </CardTitle>
            <CardDescription>
              Set up a new interview session by providing the interviewer and candidate details.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Interviewer Information */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2 mb-3">
                  <User className="h-5 w-5 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Interviewer Information</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="interviewer_name">Full Name *</Label>
                    <Input
                      id="interviewer_name"
                      type="text"
                      placeholder="Enter interviewer's full name"
                      value={formData.interviewer_name}
                      onChange={(e) => handleInputChange('interviewer_name', e.target.value)}
                      className={errors.interviewer_name ? 'border-red-500' : ''}
                    />
                    {errors.interviewer_name && (
                      <p className="text-sm text-red-600">{errors.interviewer_name}</p>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="interviewer_email">Email Address *</Label>
                    <Input
                      id="interviewer_email"
                      type="email"
                      placeholder="interviewer@company.com"
                      value={formData.interviewer_email}
                      onChange={(e) => handleInputChange('interviewer_email', e.target.value)}
                      className={errors.interviewer_email ? 'border-red-500' : ''}
                    />
                    {errors.interviewer_email && (
                      <p className="text-sm text-red-600">{errors.interviewer_email}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Candidate Information */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2 mb-3">
                  <Users className="h-5 w-5 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Candidate Information</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="candidate_name">Full Name *</Label>
                    <Input
                      id="candidate_name"
                      type="text"
                      placeholder="Enter candidate's full name"
                      value={formData.candidate_name}
                      onChange={(e) => handleInputChange('candidate_name', e.target.value)}
                      className={errors.candidate_name ? 'border-red-500' : ''}
                    />
                    {errors.candidate_name && (
                      <p className="text-sm text-red-600">{errors.candidate_name}</p>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="candidate_email">Email Address</Label>
                    <Input
                      id="candidate_email"
                      type="email"
                      placeholder="candidate@email.com (optional)"
                      value={formData.candidate_email}
                      onChange={(e) => handleInputChange('candidate_email', e.target.value)}
                      className={errors.candidate_email ? 'border-red-500' : ''}
                    />
                    {errors.candidate_email && (
                      <p className="text-sm text-red-600">{errors.candidate_email}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Position Information */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2 mb-3">
                  <Briefcase className="h-5 w-5 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Position Information</h3>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="position_title">Position Title *</Label>
                  <Input
                    id="position_title"
                    type="text"
                    placeholder="e.g., Senior Software Engineer, Marketing Manager"
                    value={formData.position_title}
                    onChange={(e) => handleInputChange('position_title', e.target.value)}
                    className={errors.position_title ? 'border-red-500' : ''}
                  />
                  {errors.position_title && (
                    <p className="text-sm text-red-600">{errors.position_title}</p>
                  )}
                </div>
              </div>

              {submitError && (
                <Alert variant="destructive">
                  <AlertDescription>{submitError}</AlertDescription>
                </Alert>
              )}

              <div className="flex justify-end space-x-3 pt-4">
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => window.history.back()}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="min-w-[120px]"
                >
                  {loading ? 'Creating...' : 'Create Interview'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Information Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">What happens next?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                <p><strong>Document Upload:</strong> Upload the candidate's resume, job listing, and any company-specific interview questions.</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                <p><strong>AI Analysis:</strong> Our AI will analyze the documents and generate tailored interview questions.</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                <p><strong>Interview Preparation:</strong> Review generated questions and prepare for the interview session.</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                <p><strong>Live Interview:</strong> Conduct the interview with real-time transcription and AI assistance.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default InterviewSetup

