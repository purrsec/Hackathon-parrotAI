import ChatInterface from '@/components/ChatInterface'
import { Plane } from 'lucide-react'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl h-screen flex flex-col">
        <header className="border-b border-gray-200 dark:border-gray-800 p-4">
          <h1 className="text-2xl font-bold text-center flex items-center justify-center gap-2">
            <Plane className="w-6 h-6" />
            Parrot AI - Drone Control
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-1">
            Control your drone with natural language commands
          </p>
        </header>
        <ChatInterface />
      </div>
    </main>
  )
}

