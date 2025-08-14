import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Settings as SettingsIcon, 
  Key, 
  Save, 
  Eye, 
  EyeOff, 
  CheckCircle,
  AlertCircle,
  Brain,
  Cloud
} from 'lucide-react'

const API_BASE_URL = 'http://localhost:5001/api'

const Settings = ({ onClose }) => {
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    aws_access_key: '',
    aws_secret_key: '',
    aws_region: 'us-east-1',
    ai_provider: 'openai' // 'openai' or 'aws_nova'
  })
  
  const [showKeys, setShowKeys] = useState({
    openai: false,
    aws_access_key: false,
    aws_secret_key: false
  })
  
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)

  useEffect(() => {
    // Load saved API keys from localStorage
    const savedKeys = localStorage.getItem('synergos_api_keys')
    if (savedKeys) {
      try {
        const parsed = JSON.parse(savedKeys)
        setApiKeys(prev => ({ ...prev, ...parsed }))
      } catch (e) {
        console.error('Failed to load API keys:', e)
      }
    }
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSaved(false)
    
    try {
      // Save to localStorage
      localStorage.setItem('synergos_api_keys', JSON.stringify(apiKeys))
      
      // Send to backend
      const response = await fetch(`${API_BASE_URL}/settings/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiKeys)
      })
      
      if (response.ok) {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      } else {
        throw new Error('Failed to save API keys')
      }
    } catch (error) {
      setError('Failed to save settings. They will be saved locally.')
      // Even if backend fails, we've saved to localStorage
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  const testConnection = async (provider) => {
    setTesting(true)
    setTestResult(null)
    
    try {
      const response = await fetch(`${API_BASE_URL}/settings/test-ai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider,
          ...apiKeys
        })
      })
      
      const result = await response.json()
      setTestResult(result)
    } catch (error) {
      setTestResult({ success: false, message: 'Connection test failed' })
    } finally {
      setTesting(false)
    }
  }

  const toggleShowKey = (key) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <Card className="border-0">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <SettingsIcon className="h-6 w-6 text-blue-600" />
                <div>
                  <CardTitle>API Settings</CardTitle>
                  <CardDescription>Configure AI service API keys for enhanced functionality</CardDescription>
                </div>
              </div>
              <Button variant="ghost" onClick={onClose}>✕</Button>
            </div>
          </CardHeader>
          
          <CardContent className="pt-6">
            <Tabs defaultValue="openai">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="openai" className="flex items-center space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>OpenAI</span>
                </TabsTrigger>
                <TabsTrigger value="aws" className="flex items-center space-x-2">
                  <Cloud className="h-4 w-4" />
                  <span>AWS Bedrock Nova</span>
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="openai" className="space-y-4">
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    OpenAI API key is required for advanced AI analysis and STAR-based follow-up question generation.
                    Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" className="underline">OpenAI Platform</a>
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-2">
                  <Label htmlFor="openai-key">OpenAI API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="openai-key"
                      type={showKeys.openai ? "text" : "password"}
                      placeholder="sk-..."
                      value={apiKeys.openai}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, openai: e.target.value }))}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => toggleShowKey('openai')}
                    >
                      {showKeys.openai ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => testConnection('openai')}
                    disabled={!apiKeys.openai || testing}
                  >
                    {testing ? 'Testing...' : 'Test Connection'}
                  </Button>
                  
                  <Button
                    variant={apiKeys.ai_provider === 'openai' ? 'default' : 'outline'}
                    onClick={() => setApiKeys(prev => ({ ...prev, ai_provider: 'openai' }))}
                  >
                    {apiKeys.ai_provider === 'openai' && <CheckCircle className="h-4 w-4 mr-2" />}
                    Use OpenAI
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="aws" className="space-y-4">
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    AWS Bedrock Nova provides enterprise-grade AI capabilities. Configure your AWS credentials to use Claude or other foundation models.
                    Learn more about <a href="https://aws.amazon.com/bedrock/" target="_blank" className="underline">AWS Bedrock</a>
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="aws-access">AWS Access Key ID</Label>
                    <div className="flex space-x-2">
                      <Input
                        id="aws-access"
                        type={showKeys.aws_access_key ? "text" : "password"}
                        placeholder="AKIA..."
                        value={apiKeys.aws_access_key}
                        onChange={(e) => setApiKeys(prev => ({ ...prev, aws_access_key: e.target.value }))}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => toggleShowKey('aws_access_key')}
                      >
                        {showKeys.aws_access_key ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="aws-secret">AWS Secret Access Key</Label>
                    <div className="flex space-x-2">
                      <Input
                        id="aws-secret"
                        type={showKeys.aws_secret_key ? "text" : "password"}
                        placeholder="Enter your AWS secret key"
                        value={apiKeys.aws_secret_key}
                        onChange={(e) => setApiKeys(prev => ({ ...prev, aws_secret_key: e.target.value }))}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => toggleShowKey('aws_secret_key')}
                      >
                        {showKeys.aws_secret_key ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="aws-region">AWS Region</Label>
                    <select
                      id="aws-region"
                      className="w-full px-3 py-2 border rounded-md"
                      value={apiKeys.aws_region}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, aws_region: e.target.value }))}
                    >
                      <option value="us-east-1">US East (N. Virginia)</option>
                      <option value="us-west-2">US West (Oregon)</option>
                      <option value="eu-west-1">EU (Ireland)</option>
                      <option value="eu-central-1">EU (Frankfurt)</option>
                      <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                      <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => testConnection('aws_nova')}
                    disabled={!apiKeys.aws_access_key || !apiKeys.aws_secret_key || testing}
                  >
                    {testing ? 'Testing...' : 'Test Connection'}
                  </Button>
                  
                  <Button
                    variant={apiKeys.ai_provider === 'aws_nova' ? 'default' : 'outline'}
                    onClick={() => setApiKeys(prev => ({ ...prev, ai_provider: 'aws_nova' }))}
                  >
                    {apiKeys.ai_provider === 'aws_nova' && <CheckCircle className="h-4 w-4 mr-2" />}
                    Use AWS Nova
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
            
            {testResult && (
              <Alert className={`mt-4 ${testResult.success ? 'border-green-500' : 'border-red-500'}`}>
                {testResult.success ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-600" />
                )}
                <AlertDescription>{testResult.message}</AlertDescription>
              </Alert>
            )}
            
            {error && (
              <Alert variant="destructive" className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="flex justify-between items-center pt-6 border-t">
              <div className="text-sm text-gray-500">
                API keys are stored locally and sent securely to the backend
              </div>
              
              <div className="flex space-x-2">
                <Button variant="outline" onClick={onClose}>
                  Cancel
                </Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? (
                    'Saving...'
                  ) : saved ? (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Saved
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Settings
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Settings