import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { 
  Search, 
  Calendar, 
  User, 
  Briefcase, 
  Clock,
  CheckCircle,
  Play,
  Eye,
  RefreshCw
} from 'lucide-react'

const InterviewList = ({ interviews, onSelectInterview, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const filteredInterviews = interviews.filter(interview => {
    const matchesSearch = 
      interview.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      interview.position_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      interview.interviewer_name.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || interview.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  const getStatusBadge = (status) => {
    const variants = {
      preparation: { variant: 'secondary', text: 'Preparing' },
      active: { variant: 'destructive', text: 'Active' },
      completed: { variant: 'default', text: 'Completed' }
    }
    
    const config = variants[status] || variants.preparation
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'active':
        return <Play className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not started'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getProgressPercentage = (interview) => {
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

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5 text-blue-600" />
              <span>Recent Interviews</span>
            </CardTitle>
            <CardDescription>
              Manage and review your interview sessions
            </CardDescription>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={onRefresh}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search interviews..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="preparation">Preparing</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          {/* Interview List */}
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredInterviews.length > 0 ? (
              filteredInterviews.map((interview) => (
                <div
                  key={interview.id}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => onSelectInterview(interview)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2">
                        {getStatusIcon(interview.status)}
                        <h4 className="font-semibold text-gray-900 truncate">
                          {interview.candidate_name}
                        </h4>
                        {getStatusBadge(interview.status)}
                      </div>
                      
                      <div className="space-y-1 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Briefcase className="h-3 w-3" />
                          <span className="truncate">{interview.position_title}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <User className="h-3 w-3" />
                          <span className="truncate">{interview.interviewer_name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(interview.created_at)}</span>
                        </div>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="mt-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs text-gray-500">Progress</span>
                          <span className="text-xs text-gray-500">
                            {getProgressPercentage(interview)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div 
                            className={`h-1.5 rounded-full transition-all duration-300 ${
                              interview.status === 'completed' ? 'bg-green-600' :
                              interview.status === 'active' ? 'bg-blue-600' : 'bg-gray-400'
                            }`}
                            style={{ width: `${getProgressPercentage(interview)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4 flex-shrink-0">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          onSelectInterview(interview)
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Quick Stats */}
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>
                        Documents: {interview.documents?.length || 0}
                      </span>
                      <span>
                        Questions: {interview.questions?.length || 0}
                      </span>
                      <span>
                        Responses: {interview.responses?.length || 0}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">
                  {searchTerm || statusFilter !== 'all' 
                    ? 'No interviews match your search criteria' 
                    : 'No interviews found'
                  }
                </p>
                {(searchTerm || statusFilter !== 'all') && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      setSearchTerm('')
                      setStatusFilter('all')
                    }}
                  >
                    Clear Filters
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* Summary Stats */}
          {interviews.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-lg font-semibold text-gray-900">
                    {interviews.length}
                  </p>
                  <p className="text-xs text-gray-600">Total</p>
                </div>
                <div>
                  <p className="text-lg font-semibold text-blue-600">
                    {interviews.filter(i => i.status === 'active').length}
                  </p>
                  <p className="text-xs text-gray-600">Active</p>
                </div>
                <div>
                  <p className="text-lg font-semibold text-green-600">
                    {interviews.filter(i => i.status === 'completed').length}
                  </p>
                  <p className="text-xs text-gray-600">Completed</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default InterviewList

