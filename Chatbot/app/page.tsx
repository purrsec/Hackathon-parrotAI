'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';

export interface ToolCall {
  id: string;
  name: string;
  arguments: any;
  result: any;
}

export interface FlightCommand {
  id: string;
  action: string;
  parameters: any;
  description: string;
  status?: 'pending' | 'executing' | 'success' | 'error';
  result?: any;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
  toolCalls?: ToolCall[];
  reasoning?: string | null;
  flightPlan?: FlightCommand[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Bonjour ! Je suis votre assistant pour contrôler le drone. Comment puis-je vous aider ? Par exemple, vous pouvez me demander : "Va voir si la centrale de Fessenheim a été touchée"',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [executingFlightPlan, setExecutingFlightPlan] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    console.log('\n👤 ========== CLIENT: Message utilisateur ==========');
    console.log('📝 Contenu:', userMessage.content);

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const messagesToSend = [...messages, userMessage].map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));
      
      console.log('📤 Envoi au serveur:', messagesToSend.length, 'messages');
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messagesToSend,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erreur serveur:', response.status, errorText);
        throw new Error('Erreur lors de la communication avec le serveur');
      }

      const data = await response.json();
      
      console.log('📥 Réponse serveur reçue:');
      console.log('   - Message:', data.message?.content?.substring(0, 100) + '...');
      console.log('   - Tool calls:', data.toolCalls?.length || 0);
      console.log('   - Réflexion:', data.reasoning || '(aucune)');
      console.log('   - Plan de vol:', data.flightPlan?.length || 0, 'commandes');
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message.content,
        timestamp: new Date(),
        toolCalls: data.toolCalls || undefined,
        reasoning: data.reasoning || undefined,
        flightPlan: data.flightPlan || undefined,
      };

      let messageIndex: number;
      setMessages((prev) => {
        const updated = [...prev, assistantMessage];
        messageIndex = updated.length - 1; // Index du nouveau message
        return updated;
      });

      // Exécuter automatiquement le plan de vol s'il existe
      if (data.flightPlan && data.flightPlan.length > 0) {
        console.log('🚀 Démarrage de l\'exécution automatique du plan de vol...');
        // Attendre un peu pour que l'UI se mette à jour
        setTimeout(() => {
          executeFlightPlan(messageIndex!, data.flightPlan);
        }, 1000);
      }
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Erreur : ${error.message || 'Une erreur est survenue'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const executeFlightPlan = async (messageIndex: number, flightPlan: FlightCommand[]) => {
    if (executingFlightPlan !== null) {
      return; // Déjà en cours d'exécution
    }

    setExecutingFlightPlan(messageIndex);

    // Délai initial avant de commencer l'exécution
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Mettre à jour le message avec les statuts
    setMessages((prev) => {
      const updated = [...prev];
      if (updated[messageIndex] && updated[messageIndex].flightPlan) {
        updated[messageIndex] = {
          ...updated[messageIndex],
          flightPlan: updated[messageIndex].flightPlan!.map(cmd => ({
            ...cmd,
            status: 'pending' as const,
          })),
        };
      }
      return updated;
    });

    // Nettoyer l'URL pour enlever les guillemets éventuels
    let DRONE_API_URL = (process.env.NEXT_PUBLIC_DRONE_API_URL || 'http://localhost:8000').trim();
    DRONE_API_URL = DRONE_API_URL.replace(/^["']|["']$/g, ''); // Enlever les guillemets au début et à la fin
    
    console.log('URL du serveur Python:', DRONE_API_URL);

    // Exécuter chaque commande séquentiellement
    for (let i = 0; i < flightPlan.length; i++) {
      const cmd = flightPlan[i];

      // Mettre à jour le statut à "executing"
      setMessages((prev) => {
        const updated = [...prev];
        if (updated[messageIndex] && updated[messageIndex].flightPlan) {
          updated[messageIndex] = {
            ...updated[messageIndex],
            flightPlan: updated[messageIndex].flightPlan!.map((c, idx) =>
              idx === i ? { ...c, status: 'executing' as const } : c
            ),
          };
        }
        return updated;
      });

      try {
        // Envoyer la commande au serveur Python
        console.log(`Envoi de la commande ${i + 1}/${flightPlan.length}:`, {
          id: cmd.id,
          action: cmd.action,
          parameters: cmd.parameters,
          url: `${DRONE_API_URL}/cmd`,
        });

        const response = await fetch(`${DRONE_API_URL}/cmd`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            id: cmd.id,
            action: cmd.action,
            parameters: cmd.parameters,
          }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Erreur HTTP ${response.status}:`, errorText);
          throw new Error(`Erreur HTTP ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        console.log(`Réponse reçue pour ${cmd.action}:`, result);

        // Mettre à jour le statut à "success"
        setMessages((prev) => {
          const updated = [...prev];
          if (updated[messageIndex] && updated[messageIndex].flightPlan) {
            updated[messageIndex] = {
              ...updated[messageIndex],
              flightPlan: updated[messageIndex].flightPlan!.map((c, idx) =>
                idx === i
                  ? { ...c, status: 'success' as const, result: result }
                  : c
              ),
            };
          }
          return updated;
        });

        // Attendre un peu avant la prochaine commande (2 secondes entre chaque commande)
        await new Promise((resolve) => setTimeout(resolve, 2000));
      } catch (error: any) {
        console.error(`Erreur lors de l'exécution de ${cmd.action}:`, error);
        // Mettre à jour le statut à "error"
        setMessages((prev) => {
          const updated = [...prev];
          if (updated[messageIndex] && updated[messageIndex].flightPlan) {
            updated[messageIndex] = {
              ...updated[messageIndex],
              flightPlan: updated[messageIndex].flightPlan!.map((c, idx) =>
                idx === i
                  ? { 
                      ...c, 
                      status: 'error' as const, 
                      result: { 
                        error: error.message || 'Erreur inconnue',
                        details: error.toString(),
                      } 
                    }
                  : c
              ),
            };
          }
          return updated;
        });
        // Continuer avec la prochaine commande au lieu d'arrêter
        // break; // Arrêter l'exécution en cas d'erreur
      }
    }

    setExecutingFlightPlan(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">EDTH - Contrôleur Drone</h1>
          <p className="text-sm text-gray-600 mt-1">
            Interface conversationnelle pour missions autonomes de drones
          </p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message}
              messageIndex={index}
              isExecuting={executingFlightPlan === index}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-lg shadow-sm px-4 py-3 max-w-md">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}

