// src/app/page.tsx
import { AppLayout } from '@/components/layout/AppLayout'
import { ChatContainer } from '@/components/feature/Chat/ChatContainer'
import { DocumentSidebar } from '@/components/feature/Document/DocumentSidebar'

export default function HomePage() {
  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-3.5rem)]">
        <DocumentSidebar />
        <div className="flex-1 p-6">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-foreground">Document Chat</h2>
            <p className="text-muted-foreground">Upload documents and ask questions about their content</p>
          </div>
          <ChatContainer />
        </div>
      </div>
    </AppLayout>
  )
}