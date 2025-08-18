import { 
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Input,
  ScrollArea,
  Avatar,
  AvatarImage,
  AvatarFallback,
  Badge,
  Separator,
  Progress,
  Loader
} from '../../components/ui'

export default function ComponentTest() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-foreground mb-4">
            🌾 Agricultural UI Components
          </h1>
          <p className="text-muted-foreground">
            Complete UI component library for our agricultural intelligence platform
          </p>
        </div>

        {/* Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
            <CardDescription>Different button variants and sizes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button variant="default">Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="link">Link</Button>
            </div>
            <Separator className="my-4" />
            <div className="flex flex-wrap gap-4">
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
              <Button size="icon">🌱</Button>
            </div>
          </CardContent>
        </Card>

        {/* Input and Form Elements */}
        <Card>
          <CardHeader>
            <CardTitle>Form Elements</CardTitle>
            <CardDescription>Input fields and form components</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input placeholder="Enter your farming question..." />
            <Input type="email" placeholder="your-email@farm.com" />
            <div className="flex items-center space-x-4">
              <Badge variant="default">Wheat</Badge>
              <Badge variant="secondary">Rice</Badge>
              <Badge variant="outline">Corn</Badge>
              <Badge variant="destructive">Pest Alert</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Progress and Loading */}
        <Card>
          <CardHeader>
            <CardTitle>Progress Indicators</CardTitle>
            <CardDescription>Progress bars and loading states</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Crop Analysis Progress</span>
                <span>65%</span>
              </div>
              <Progress value={65} className="w-full" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Weather Data Loading</span>
                <span>30%</span>
              </div>
              <Progress value={30} className="w-full" />
            </div>
            <div className="flex items-center space-x-4">
              <Loader size="sm" variant="primary" />
              <span className="text-sm">Loading small...</span>
              <Loader size="md" variant="default" />
              <span className="text-sm">Loading medium...</span>
              <Loader size="lg" variant="muted" />
              <span className="text-sm">Loading large...</span>
            </div>
          </CardContent>
        </Card>

        {/* Avatar and User Elements */}
        <Card>
          <CardHeader>
            <CardTitle>User Interface</CardTitle>
            <CardDescription>Avatars and user-related components</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" alt="Farmer" />
                <AvatarFallback>FM</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">Farmer Singh</p>
                <p className="text-xs text-muted-foreground">Punjab, India</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Scrollable Content */}
        <Card>
          <CardHeader>
            <CardTitle>Scrollable Chat History</CardTitle>
            <CardDescription>Example of scrollable content area</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-32 w-full rounded border p-4">
              <div className="space-y-3">
                {Array.from({ length: 20 }, (_, i) => (
                  <div key={i} className="text-sm">
                    <strong>Q{i + 1}:</strong> How do I improve my wheat yield this season?
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Complete Example Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>🤖</span>
              <span>AI Agricultural Assistant</span>
              <Badge variant="secondary">Online</Badge>
            </CardTitle>
            <CardDescription>
              Complete example showing all components working together
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <Avatar>
                <AvatarFallback>AI</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <p className="text-sm">
                  Based on your location and current weather conditions, 
                  I recommend the following steps for your wheat crop...
                </p>
              </div>
            </div>
            <Separator />
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Analysis Complete</span>
                <span>100%</span>
              </div>
              <Progress value={100} className="w-full" />
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline">Ask Follow-up</Button>
            <Button>Get Full Report</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
