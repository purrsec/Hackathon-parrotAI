"""
Script de test pour le Message Gateway FastAPI.

Envoie des messages en langage naturel via REST ou WebSocket.
"""

import requests
import json
import time
from typing import Literal

API_URL = "http://localhost:8000"


def test_rest_api():
    """Test l'envoi de messages via REST API."""
    print("=" * 80)
    print("Test REST API - POST /message")
    print("=" * 80)
    
    messages = [
        "va inspecter la tour Eiffel",
        "décolle à 10 mètres",
        "reviens à la maison",
        "atterris",
    ]
    
    for i, msg_text in enumerate(messages, 1):
        message = {
            "id": f"test-msg-{i}",
            "message": msg_text,
            "source": "api",
            "user_id": "test-user-123",
            "metadata": {
                "test": True,
                "timestamp": time.time()
            }
        }
        
        print(f"\n📤 Envoi du message {i}:")
        print(f"   {msg_text}")
        
        try:
            response = requests.post(
                f"{API_URL}/message",
                json=message,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Réponse:")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print(f"   Timestamp: {result['timestamp']}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        time.sleep(0.5)


def test_health():
    """Test le health check."""
    print("\n" + "=" * 80)
    print("Test Health Check - GET /health")
    print("=" * 80)
    
    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        
        health = response.json()
        print(f"✅ Service Health:")
        print(f"   Status: {health['status']}")
        print(f"   Uptime: {health['uptime_seconds']:.2f}s")
        print(f"   Olympe Available: {health['olympe_available']}")
        print(f"   Drone Connected: {health['drone_connected']}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_history():
    """Test la récupération de l'historique."""
    print("\n" + "=" * 80)
    print("Test History - GET /history")
    print("=" * 80)
    
    try:
        response = requests.get(f"{API_URL}/history")
        response.raise_for_status()
        
        history = response.json()
        print(f"✅ Message History:")
        print(f"   Total: {history['total']}")
        print(f"   Messages récents: {len(history['messages'])}")
        
        if history['messages']:
            print(f"\n   Derniers messages:")
            for msg in history['messages'][-3:]:
                print(f"   - [{msg['source']}] {msg['message'][:50]}...")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_websocket():
    """Test WebSocket (nécessite websockets installé)."""
    print("\n" + "=" * 80)
    print("Test WebSocket - ws://localhost:8000/ws")
    print("=" * 80)
    
    try:
        import asyncio
        import websockets
        
        async def ws_test():
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Recevoir le welcome
                welcome = await websocket.recv()
                print(f"✅ Connecté!")
                print(f"   Welcome: {json.loads(welcome)['message']}")
                
                # Envoyer un message
                test_msg = {
                    "id": "ws-test-1",
                    "message": "test websocket: va inspecter le pont",
                    "source": "api",
                    "user_id": "ws-tester"
                }
                
                print(f"\n📤 Envoi via WebSocket:")
                print(f"   {test_msg['message']}")
                
                await websocket.send(json.dumps(test_msg))
                
                # Recevoir la réponse
                response = await websocket.recv()
                result = json.loads(response)
                
                print(f"✅ Réponse WebSocket:")
                print(f"   Status: {result['status']}")
                print(f"   Message: {result['message']}")
        
        asyncio.run(ws_test())
        
    except ImportError:
        print("⚠️  Module 'websockets' non installé")
        print("   Installation: pip install websockets")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    """Lance tous les tests."""
    print("\n" + "=" * 80)
    print("🧪 Test Suite - Message Gateway FastAPI")
    print("=" * 80)
    print("\nAssurez-vous que le serveur tourne:")
    print("  uvicorn fastapi_entrypoint:app --reload")
    print("\n")
    
    input("Appuyez sur Enter pour continuer...")
    
    try:
        # Tests REST
        test_rest_api()
        test_health()
        test_history()
        
        # Test WebSocket
        print("\n")
        if input("Tester WebSocket? (y/n): ").lower() == 'y':
            test_websocket()
        
        print("\n" + "=" * 80)
        print("✅ Tests terminés!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus")
    except Exception as e:
        print(f"\n\n❌ Erreur globale: {e}")


if __name__ == "__main__":
    main()

