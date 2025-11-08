#!/usr/bin/env python3
"""
Simple Terminal Chat Client - Test client for ParrotAI FastAPI server
Connects via WebSocket to test the natural language message processing.
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Optional

try:
    import websockets
except ImportError:
    print("❌ websockets not installed. Run: pip install websockets")
    sys.exit(1)


class ChatClient:
    """Simple WebSocket chat client for testing ParrotAI API"""
    
    def __init__(self, server_url: str = "ws://localhost:8000/ws"):
        self.server_url = server_url
        self.websocket = None
        self.user_id = f"user-{str(uuid.uuid4())[:8]}"
        self.running = False
        self.pending_mission_id = None  # Track mission waiting for confirmation
        
    async def connect(self) -> bool:
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"✅ Connected to {self.server_url}")
            self.running = True
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def receive_messages(self):
        """Continuously receive messages from server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                self._display_message(data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self.running:
                print(f"❌ Error receiving message: {e}")
    
    async def send_message(self, user_input: str):
        """Send message to server"""
        if not self.websocket:
            print("❌ Not connected to server")
            return
        
        message_id = f"msg-{str(uuid.uuid4())[:8]}"
        
        # Check if this is a confirmation response
        user_lower = user_input.lower().strip()
        is_confirmation = user_lower in ["yes", "y", "oui", "no", "n", "non"]
        
        payload = {
            "id": message_id,
            "message": user_input,
            "source": "api",
            "user_id": self.user_id
        }
        
        # Add confirmation metadata if applicable
        if is_confirmation and self.pending_mission_id:
            payload["is_confirmation"] = True
            payload["confirmation_for"] = self.pending_mission_id
            payload["confirmation_value"] = user_lower in ["yes", "y", "oui"]
        
        try:
            await self.websocket.send(json.dumps(payload))
            print(f"📤 Sent: {user_input}\n")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
    
    def _display_message(self, data: dict):
        """Pretty print received message"""
        msg_type = data.get("type", "unknown")
        
        if msg_type == "welcome":
            print("\n" + "=" * 70)
            print(f"🎉 {data.get('message')}")
            print(f"   API Version: {data.get('api_version')}")
            print(f"   {data.get('note')}")
            print("=" * 70)
            print("\n💬 Type your message (or 'quit' to exit):\n")
        
        elif msg_type == "message_processed":
            print("\n" + "-" * 70)
            status = data.get("status", "unknown")
            status_icon = "✅" if status == "processed" else "⚠️"
            print(f"{status_icon} {data.get('message')}")
            print(f"   Status: {status}")
            print(f"   ID: {data.get('id')}")
            
            mission_dsl = data.get("mission_dsl")
            if mission_dsl:
                # Display the understanding FIRST if available
                understanding = mission_dsl.get("understanding")
                if understanding:
                    print(f"\n   🤖 Understanding: {understanding}")
                    print()
                
                print(f"   📋 Mission DSL Generated:")
                print(f"      - Mission ID: {mission_dsl.get('missionId', 'N/A')}")
                segments = mission_dsl.get('segments', [])
                print(f"      - Segments: {len(segments)}")
                for i, seg in enumerate(segments[:3], 1):  # Show first 3
                    print(f"        {i}. {seg.get('type', 'unknown')}: {seg.get('action', 'N/A')}")
                if len(segments) > 3:
                    print(f"        ... and {len(segments) - 3} more")
            
            print("-" * 70)
        
        elif msg_type == "mission_confirmation":
            # Store the mission ID for confirmation
            self.pending_mission_id = data.get('id')
            
            print("\n" + "=" * 70)
            print(f"🚁 MISSION CONFIRMATION")
            print(f"   Drone ID: {data.get('drone_id')}")
            print(f"   Drone IP: {data.get('drone_ip')}")
            print(f"   Status: {data.get('ready')}")
            print(f"   {data.get('message')}")
            print("=" * 70)
        
        elif msg_type == "mission_confirmed":
            # Clear pending mission after confirmation
            self.pending_mission_id = None
            
            print("\n" + "🎯" * 35)
            print(f"✅ MISSION EXECUTING")
            print(f"   {data.get('message')}")
            print(f"   Mission ID: {data.get('id')}")
            print(f"   Status: {data.get('status')}")
            print("🎯" * 35)
        
        elif msg_type == "mission_cancelled":
            # Clear pending mission after cancellation
            self.pending_mission_id = None
            
            print("\n" + "🚫" * 35)
            print(f"❌ MISSION CANCELLED")
            print(f"   {data.get('message')}")
            print(f"   Mission ID: {data.get('id')}")
            print("🚫" * 35)
        
        elif msg_type == "error":
            print("\n" + "⚠️" * 35)
            print(f"❌ ERROR: {data.get('message')}")
            print("⚠️" * 35)
        
        else:
            print(f"\n📨 [{msg_type}] {json.dumps(data, indent=2)}")
        
        print()
    
    async def input_loop(self):
        """Handle user input in non-blocking way"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Get user input in a non-blocking way
                user_input = await loop.run_in_executor(None, input, "You: ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    self.running = False
                    break
                
                if user_input.strip():
                    await self.send_message(user_input.strip())
                
            except EOFError:
                self.running = False
                break
            except Exception as e:
                print(f"❌ Input error: {e}")
                self.running = False
                break
    
    async def run(self):
        """Main run loop"""
        # Connect to server
        if not await self.connect():
            return
        
        try:
            # Create tasks for receiving and input
            receive_task = asyncio.create_task(self.receive_messages())
            input_task = asyncio.create_task(self.input_loop())
            
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [receive_task, input_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        finally:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
        print("\n🔌 Disconnected")


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("🚁 PARROT AI - TERMINAL CHAT CLIENT")
    print("=" * 70)
    print("Connecting to ws://localhost:8000/ws")
    print("(Make sure FastAPI server is running on port 8000)")
    print("=" * 70 + "\n")
    
    client = ChatClient()
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrupted by user")
        sys.exit(0)

