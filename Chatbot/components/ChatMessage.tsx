import { Message } from '@/app/page';

interface ChatMessageProps {
  message: Message;
  messageIndex: number;
  isExecuting?: boolean;
}

export default function ChatMessage({
  message,
  messageIndex,
  isExecuting = false,
}: ChatMessageProps) {
  const isUser = message.role === 'user';
  const time = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
      })
    : '';

  const hasToolCalls = message.toolCalls && message.toolCalls.length > 0;
  const hasReasoning = message.reasoning && message.reasoning.trim().length > 0;
  const hasFlightPlan = message.flightPlan && message.flightPlan.length > 0;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-2xl rounded-lg px-4 py-3 shadow-sm ${
          isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-white text-gray-900 border border-gray-200'
        }`}
      >
        {/* Message de réflexion (si présent) */}
        {hasReasoning && !isUser && (
          <div className="mb-3 pb-3 border-b border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">
                Réflexion
              </span>
            </div>
            <p className="text-sm text-gray-600 italic whitespace-pre-wrap break-words">
              {message.reasoning}
            </p>
          </div>
        )}

        {/* Tool calls (si présents) */}
        {hasToolCalls && !isUser && (
          <div className="mb-3 pb-3 border-b border-gray-200 space-y-3">
            <div className="flex items-center gap-2 mb-2">
              <svg
                className="w-4 h-4 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span className="text-xs font-semibold text-purple-600 uppercase tracking-wide">
                Outils utilisés ({message.toolCalls!.length})
              </span>
            </div>
            {message.toolCalls!.map((toolCall, index) => (
              <div
                key={toolCall.id || index}
                className="bg-gray-50 rounded-lg p-3 border border-gray-200"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-mono font-semibold text-gray-800">
                      {toolCall.name}
                    </span>
                  </div>
                  {toolCall.result?.error ? (
                    <span className="text-xs text-red-600 font-semibold">Erreur</span>
                  ) : (
                    <span className="text-xs text-green-600 font-semibold">✓ Succès</span>
                  )}
                </div>
                
                {/* Arguments */}
                <div className="mb-2">
                  <span className="text-xs text-gray-500 font-medium">Paramètres :</span>
                  <pre className="text-xs mt-1 p-2 bg-white rounded border border-gray-200 overflow-x-auto text-gray-700">
                    {JSON.stringify(toolCall.arguments, null, 2)}
                  </pre>
                </div>

                {/* Résultat */}
                <div>
                  <span className="text-xs text-gray-500 font-medium">Résultat :</span>
                  <pre className="text-xs mt-1 p-2 bg-white rounded border border-gray-200 overflow-x-auto text-gray-700">
                    {JSON.stringify(toolCall.result, null, 2)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Plan de vol (si présent) */}
        {hasFlightPlan && !isUser && (
          <div className="mb-3 pb-3 border-b border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <svg
                className="w-4 h-4 text-orange-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
              <span className="text-xs font-semibold text-orange-600 uppercase tracking-wide">
                Plan de vol ({message.flightPlan!.length} commandes)
              </span>
            </div>
            <div className="space-y-2">
              {message.flightPlan!.map((cmd, index) => (
                <div
                  key={cmd.id}
                  className="bg-orange-50 rounded-lg p-3 border border-orange-200"
                >
                  <div className="flex items-start justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-orange-700 bg-orange-200 px-2 py-0.5 rounded">
                        {index + 1}
                      </span>
                      <span className="text-sm font-mono font-semibold text-gray-800">
                        {cmd.action}
                      </span>
                    </div>
                    {cmd.status === 'executing' && (
                      <span className="text-xs text-blue-600 font-medium animate-pulse">
                        ⏳ En cours...
                      </span>
                    )}
                    {cmd.status === 'success' && (
                      <span className="text-xs text-green-600 font-medium">
                        ✓ Succès
                      </span>
                    )}
                    {cmd.status === 'error' && (
                      <span className="text-xs text-red-600 font-medium">
                        ✗ Erreur
                      </span>
                    )}
                    {(!cmd.status || cmd.status === 'pending') && (
                      <span className="text-xs text-orange-600 font-medium">En attente</span>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mb-2">{cmd.description}</p>
                  {cmd.status === 'error' && cmd.result?.error && (
                    <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
                      <strong>Erreur :</strong> {cmd.result.error}
                      {cmd.result.details && (
                        <div className="mt-1 text-red-600 text-xs">{cmd.result.details}</div>
                      )}
                    </div>
                  )}
                  <details className="text-xs">
                    <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
                      Voir les paramètres
                    </summary>
                    <pre className="mt-2 p-2 bg-white rounded border border-gray-200 overflow-x-auto text-gray-700">
                      {JSON.stringify(cmd.parameters, null, 2)}
                    </pre>
                  </details>
                  {cmd.status === 'success' && cmd.result && (
                    <details className="text-xs mt-2">
                      <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
                        Voir la réponse
                      </summary>
                      <pre className="mt-2 p-2 bg-green-50 rounded border border-green-200 overflow-x-auto text-gray-700">
                        {JSON.stringify(cmd.result, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-800">
                <strong>🚀 Exécution automatique :</strong> Le plan de vol est en cours d'exécution commande par commande.
                {isExecuting && <span className="ml-2 animate-pulse">⏳ En cours...</span>}
              </p>
            </div>
          </div>
        )}

        {/* Contenu principal du message */}
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        
        {time && (
          <p
            className={`text-xs mt-2 ${
              isUser ? 'text-indigo-200' : 'text-gray-500'
            }`}
          >
            {time}
          </p>
        )}
      </div>
    </div>
  );
}

