import { NextRequest, NextResponse } from 'next/server';
import { toolDefinitions } from '@/lib/tools/definitions';
import { executeTool } from '@/lib/tools/executor';
import { generateFlightPlan } from '@/lib/tools/flightPlanGenerator';

// Configuration des providers AI
// Par défaut: Azure OpenAI (si USE_AZURE_OPENAI n'est pas défini ou vaut 'true')
// Pour utiliser MistralAI, définir USE_AZURE_OPENAI=false
const USE_AZURE_OPENAI = process.env.USE_AZURE_OPENAI !== 'false';
const USE_MISTRAL = !USE_AZURE_OPENAI;

// Azure OpenAI
const AZURE_OPENAI_ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT || '';
const AZURE_OPENAI_API_KEY = process.env.AZURE_OPENAI_API_KEY || '';

// MistralAI
const MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions';
const MISTRAL_API_KEY = process.env.MISTRAL_API_KEY || '';

// Fonction helper pour appeler l'API (Azure OpenAI ou MistralAI)
async function callAIAPI(messages: any[], tools: any[], toolChoice: string = 'auto') {
  const provider = USE_AZURE_OPENAI ? 'Azure OpenAI' : 'MistralAI';
  console.log(`\n🌐 Appel API ${provider}`);
  console.log(`   - Tool choice: ${toolChoice}`);
  console.log(`   - Nombre de messages: ${messages.length}`);
  console.log(`   - Nombre de tools: ${tools.length}`);
  
  if (USE_AZURE_OPENAI) {
    // Azure OpenAI
    if (!AZURE_OPENAI_ENDPOINT) {
      throw new Error('AZURE_OPENAI_ENDPOINT not configured. Please set it in your .env.local file');
    }
    if (!AZURE_OPENAI_API_KEY) {
      throw new Error('AZURE_OPENAI_API_KEY not configured. Please set it in your .env.local file');
    }

    const headers: any = {
      'Content-Type': 'application/json',
      'api-key': AZURE_OPENAI_API_KEY,
    };

    const body: any = {
      messages: messages,
      // Note: Certains modèles Azure OpenAI ne supportent que temperature=1 (par défaut)
      // On ne spécifie pas temperature pour utiliser la valeur par défaut
    };

    // Azure OpenAI utilise "functions" au lieu de "tools" pour les anciennes versions
    // Mais les nouvelles versions supportent "tools"
    if (tools && tools.length > 0) {
      body.tools = tools;
      // Azure OpenAI utilise "auto" ou "none" ou un objet spécifique pour tool_choice
      if (toolChoice === 'auto') {
        body.tool_choice = 'auto';
      } else if (toolChoice === 'none') {
        body.tool_choice = 'none';
      } else {
        body.tool_choice = toolChoice;
      }
    }

    console.log('   📤 Requête HTTP:');
    console.log('      URL:', AZURE_OPENAI_ENDPOINT);
    console.log('      Headers:', { 'Content-Type': headers['Content-Type'], 'api-key': '***' });
    console.log('      Body (preview):', JSON.stringify(body).substring(0, 500) + '...');
    
    const response = await fetch(AZURE_OPENAI_ENDPOINT, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('   ❌ Erreur API:', response.status, errorData);
      throw new Error(`Azure OpenAI API error: ${response.status} - ${errorData}`);
    }

    const responseData = await response.json();
    console.log('   📥 Réponse API reçue (preview):', JSON.stringify(responseData).substring(0, 500) + '...');
    
    return responseData;
  } else {
    // MistralAI
    if (!MISTRAL_API_KEY) {
      throw new Error('MISTRAL_API_KEY not configured');
    }

    const body: any = {
      model: 'mistral-large-latest',
      messages: messages,
    };

    if (tools && tools.length > 0) {
      body.tools = tools;
      body.tool_choice = toolChoice;
    }

    console.log('   📤 Requête HTTP:');
    console.log('      URL:', MISTRAL_API_URL);
    console.log('      Headers:', { 'Content-Type': 'application/json', 'Authorization': 'Bearer ***' });
    console.log('      Body (preview):', JSON.stringify(body).substring(0, 500) + '...');
    
    const response = await fetch(MISTRAL_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${MISTRAL_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('   ❌ Erreur API:', response.status, errorData);
      throw new Error(`MistralAI API error: ${response.status} - ${errorData}`);
    }

    const responseData = await response.json();
    console.log('   📥 Réponse API reçue (preview):', JSON.stringify(responseData).substring(0, 500) + '...');
    
    return responseData;
  }
}

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      );
    }

    // Vérifier la configuration
    if (USE_AZURE_OPENAI) {
      if (!AZURE_OPENAI_ENDPOINT) {
        return NextResponse.json(
          { error: 'AZURE_OPENAI_ENDPOINT not configured. Please create a .env.local file with AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY' },
          { status: 500 }
        );
      }
      if (!AZURE_OPENAI_API_KEY) {
        return NextResponse.json(
          { error: 'AZURE_OPENAI_API_KEY not configured. Please create a .env.local file with AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY' },
          { status: 500 }
        );
      }
    }

    if (USE_MISTRAL && !MISTRAL_API_KEY) {
      return NextResponse.json(
        { error: 'MISTRAL_API_KEY not configured. Please create a .env.local file with MISTRAL_API_KEY' },
        { status: 500 }
      );
    }

    // Préparer les messages pour l'API
    const apiMessages = messages.map((msg: any) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Ajouter un prompt système pour guider l'assistant
    const systemPrompt = {
      role: 'system',
      content: `Tu es un assistant expert pour contrôler un drone. Quand l'utilisateur demande une mission (inspection, reconnaissance, etc.), tu DOIS automatiquement :

1. Récupérer les coordonnées GPS de tous les sites mentionnés avec getCoordonnees
2. Récupérer l'état initial du drone avec getEtatInitial (point de départ, altitude, vitesse)
3. Vérifier les zones interdites avec getZoneInterdite
4. Pour CHAQUE site, générer un plan de mission avec planMissionRecon (rayon par défaut: 200m, altitude: celle de getEtatInitial)

IMPORTANT : Tu dois être PROACTIF et appeler TOUS ces outils automatiquement sans demander confirmation. Ne demande JAMAIS "voulez-vous que je fasse X ?" - fais-le directement.

Si l'utilisateur demande d'inspecter plusieurs sites, génère un plan pour CHAQUE site.`,
    };

    console.log('\n🤖 ========== DÉBUT ÉCHANGE IA ==========');
    console.log('📤 Provider:', USE_AZURE_OPENAI ? 'Azure OpenAI' : 'MistralAI');
    console.log('📝 Messages utilisateur:', JSON.stringify(apiMessages, null, 2));
    console.log('🔧 System Prompt:', systemPrompt.content.substring(0, 200) + '...');
    console.log('🛠️  Tools disponibles:', toolDefinitions.map(t => t.function.name).join(', '));

    // Appel initial à l'API avec les outils
    console.log('\n📡 Appel initial à l\'IA...');
    let data = await callAIAPI([systemPrompt, ...apiMessages], toolDefinitions, 'auto');
    const assistantMessage = data.choices[0]?.message;
    
    console.log('📥 Réponse IA reçue:');
    console.log('   - Contenu:', assistantMessage?.content || '(vide)');
    console.log('   - Tool calls:', assistantMessage?.tool_calls?.length || 0);
    if (assistantMessage?.tool_calls) {
      assistantMessage.tool_calls.forEach((tc: any, idx: number) => {
        console.log(`   - Tool ${idx + 1}: ${tc.function.name}`);
        console.log(`     Arguments:`, JSON.stringify(tc.function.arguments, null, 2));
      });
    }
    
    // Stocker les tool calls et résultats pour la réponse finale
    let toolCallsForResponse: any[] = [];
    let reasoningMessage: string | null = null;
    
    // Permettre plusieurs tours de tool calls (max 5 pour éviter les boucles infinies)
    let maxIterations = 5;
    let iteration = 0;
    
    while (iteration < maxIterations) {
      const currentMessage = iteration === 0 ? assistantMessage : data.choices[0]?.message;
      
      console.log(`\n🔄 Tour ${iteration + 1}/${maxIterations}`);
      
      // Si MistralAI veut utiliser un outil
      if (currentMessage?.tool_calls && currentMessage.tool_calls.length > 0) {
        console.log(`\n🔧 ${currentMessage.tool_calls.length} outil(s) à exécuter:`);
        const toolCalls = currentMessage.tool_calls;
        const toolResults: any[] = [];
        if (iteration === 0) {
          reasoningMessage = currentMessage.content || null;
        }

        // Exécuter tous les outils demandés
        for (const toolCall of toolCalls) {
          try {
            const args = typeof toolCall.function.arguments === 'string' 
              ? JSON.parse(toolCall.function.arguments)
              : toolCall.function.arguments;
            
            console.log(`\n⚙️  Exécution: ${toolCall.function.name}`);
            console.log(`   Paramètres:`, JSON.stringify(args, null, 2));
            
            const result = await executeTool(toolCall.function.name, args);
            
            console.log(`   ✅ Résultat:`, JSON.stringify(result, null, 2));
            
            // Stocker pour la réponse finale
            toolCallsForResponse.push({
              id: toolCall.id,
              name: toolCall.function.name,
              arguments: args,
              result: result,
            });
            
            // Stocker pour l'envoi à MistralAI
            toolResults.push({
              type: 'tool',
              tool_call_id: toolCall.id,
              tool_name: toolCall.function.name,
              result: result,
            });
          } catch (error: any) {
            const args = typeof toolCall.function.arguments === 'string' 
              ? JSON.parse(toolCall.function.arguments)
              : toolCall.function.arguments;
            
            console.log(`   ❌ Erreur:`, error.message);
            
            // Stocker pour la réponse finale
            toolCallsForResponse.push({
              id: toolCall.id,
              name: toolCall.function.name,
              arguments: args,
              result: { error: error.message },
            });
            
            // Stocker pour l'envoi à MistralAI
            toolResults.push({
              type: 'tool',
              tool_call_id: toolCall.id,
              tool_name: toolCall.function.name,
              result: { error: error.message },
            });
          }
        }

        // Ajouter le message de l'assistant avec les tool calls
        apiMessages.push({
          role: 'assistant',
          content: currentMessage.content || null,
          tool_calls: toolCalls.map((tc: any) => ({
            id: tc.id,
            type: 'function',
            function: {
              name: tc.function.name,
              arguments: typeof tc.function.arguments === 'string' 
                ? tc.function.arguments 
                : JSON.stringify(tc.function.arguments),
            },
          })),
        } as any);

        // Ajouter les résultats des outils
        for (const toolResult of toolResults) {
          apiMessages.push({
            role: 'tool',
            content: JSON.stringify(toolResult.result),
            tool_call_id: toolResult.tool_call_id,
          } as any);
        }

        // Vérifier si on a besoin de plus d'informations
        const hasCoords = toolCallsForResponse.some(tc => tc.name === 'getCoordonnees');
        const hasEtat = toolCallsForResponse.some(tc => tc.name === 'getEtatInitial');
        const hasZones = toolCallsForResponse.some(tc => tc.name === 'getZoneInterdite');
        const coordsResults = toolCallsForResponse.filter(tc => tc.name === 'getCoordonnees' && !tc.result.error);
        const hasMissionPlans = toolCallsForResponse.some(tc => tc.name === 'planMissionRecon');

        console.log('\n📊 État actuel:');
        console.log('   - Coordonnées récupérées:', hasCoords);
        console.log('   - État initial récupéré:', hasEtat);
        console.log('   - Zones interdites récupérées:', hasZones);
        console.log('   - Plans de mission générés:', hasMissionPlans);
        console.log('   - Nombre de sites:', coordsResults.length);

        // Si on a des coordonnées mais pas de plan de mission, continuer
        const needsMoreTools = hasCoords && hasEtat && !hasMissionPlans && coordsResults.length > 0;

        if (needsMoreTools && iteration < maxIterations - 1) {
          // Continuer avec un autre tour de tool calls
          iteration++;
          const continuePrompt = {
            role: 'system',
            content: `Tu as récupéré les coordonnées et l'état initial. Tu DOIS maintenant générer un plan de mission (planMissionRecon) pour CHAQUE site dont tu as les coordonnées. Utilise un rayon de 200m par défaut et l'altitude de croisière récupérée.`,
          };

          console.log('\n🔄 Continuation - Demande de plans de mission...');
          console.log('📤 Messages envoyés à l\'IA:', apiMessages.length + 2, 'messages');
          
          data = await callAIAPI([systemPrompt, ...apiMessages, continuePrompt], toolDefinitions, 'auto');
          
          console.log('📥 Nouvelle réponse IA:');
          const newMessage = data.choices[0]?.message;
          console.log('   - Contenu:', newMessage?.content || '(vide)');
          console.log('   - Tool calls:', newMessage?.tool_calls?.length || 0);
          
          continue; // Continuer la boucle
        } else {
          // On a assez d'informations, générer la réponse finale
          break;
        }
      } else {
        // Pas de tool calls, on peut arrêter
        break;
      }
    }

    // Ajouter un message système pour guider la réponse finale
    const finalSystemPrompt = {
      role: 'system',
      content: 'Tu es un assistant pour contrôler un drone. Après avoir utilisé des outils, tu dois toujours fournir une réponse claire et détaillée à l\'utilisateur expliquant ce qui a été fait. Un plan de vol sera généré automatiquement à partir des données récupérées.',
    };

    console.log('\n💬 Génération de la réponse finale...');
    console.log('📤 Contexte complet:', apiMessages.length + 2, 'messages');
    console.log('   - Tool calls effectués:', toolCallsForResponse.length);
    console.log('   - Réflexion IA:', reasoningMessage || '(aucune)');

    // Rappel à l'API avec les résultats des outils pour la réponse finale
    data = await callAIAPI([systemPrompt, ...apiMessages, finalSystemPrompt], toolDefinitions, 'none');
    
    const finalMessage = data.choices[0]?.message;
    console.log('📥 Réponse finale IA:');
    console.log('   - Contenu:', finalMessage?.content || '(vide)');

    // Générer le plan de vol si des tool calls ont été effectués
    let flightPlan = null;
    if (toolCallsForResponse.length > 0) {
      // Vérifier si on a les outils nécessaires pour générer un plan
      const hasCoords = toolCallsForResponse.some(tc => tc.name === 'getCoordonnees' && !tc.result.error);
      const hasEtat = toolCallsForResponse.some(tc => tc.name === 'getEtatInitial' && !tc.result.error);
      
      console.log('\n✈️  Génération du plan de vol...');
      console.log('   - Coordonnées disponibles:', hasCoords);
      console.log('   - État initial disponible:', hasEtat);
      
      // Générer le plan de vol si on a au moins des coordonnées et l'état initial
      if (hasCoords && hasEtat) {
        flightPlan = generateFlightPlan(toolCallsForResponse);
        console.log('   ✅ Plan de vol généré:', flightPlan.length, 'commandes');
        flightPlan.forEach((cmd, idx) => {
          console.log(`      ${idx + 1}. ${cmd.action} - ${cmd.description}`);
        });
      } else {
        console.log('   ⚠️  Plan de vol non généré (données insuffisantes)');
      }
    }

    // Construire la réponse avec les détails des tool calls
    const responseData: any = {
      message: {
        role: 'assistant',
        content: finalMessage?.content || (flightPlan ? 'Plan de vol généré. Veuillez valider avant exécution.' : 'Aucune réponse générée'),
      },
    };

    // Si des tool calls ont été effectués, les inclure dans la réponse
    if (toolCallsForResponse.length > 0) {
      responseData.toolCalls = toolCallsForResponse;
      responseData.reasoning = reasoningMessage;
      if (flightPlan) {
        responseData.flightPlan = flightPlan;
      }
    }

    console.log('\n📤 Réponse finale envoyée au client:');
    console.log('   - Message:', responseData.message.content.substring(0, 100) + '...');
    console.log('   - Tool calls:', responseData.toolCalls?.length || 0);
    console.log('   - Plan de vol:', responseData.flightPlan?.length || 0, 'commandes');
    console.log('🤖 ========== FIN ÉCHANGE IA ==========\n');

    return NextResponse.json(responseData);
  } catch (error: any) {
    console.error('Error in chat API:', error);
    return NextResponse.json(
      { error: error.message || 'Erreur lors du traitement de la requête' },
      { status: 500 }
    );
  }
}

