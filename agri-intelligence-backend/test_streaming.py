#!/usr/bin/env python3
"""
Test the streaming chat endpoint
"""
import requests
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import create_access_token

def test_streaming_endpoint():
    """Test the streaming chat endpoint"""
    
    # Create a demo token
    token = create_access_token({"sub": "demo@farmer.com"})
    
    # Prepare the request
    url = "http://localhost:8000/api/v1/streaming/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    session_id = os.environ.get("TEST_SESSION_ID", "demo_session_123")
    query = os.environ.get("TEST_QUERY", "Mere chawal ke khet me keede lag gaye hai kya karu?")
    data = {"session_id": session_id, "content": query}
    
    print("🌊 Testing streaming chat endpoint...")
    print(f"📤 Message: {data['content']}")
    print("=" * 60)
    
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        if response.status_code == 200:
            print("✅ Connection established, receiving stream...")
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            
                            # Pretty print different event types
                            event_type = event_data.get('type', 'unknown')
                            
                            if event_type == 'status':
                                print(f"📊 {event_data.get('message', '')} ({event_data.get('progress', 0)}%)")
                            
                            elif event_type == 'phase':
                                print(f"🔄 {event_data.get('title', '')}")
                            
                            elif event_type == 'phase_complete':
                                print(f"✅ {event_data.get('result', 'Phase complete')} ({event_data.get('progress', 0)}%)")
                            
                            elif event_type == 'sources_found':
                                sources = event_data.get('sources', [])
                                print(f"📚 Found {len(sources)} sources")
                                for source in sources[:2]:  # Show first 2
                                    print(f"   - {source.get('title', '')} ({source.get('confidence', 0):.0%})")
                            
                            elif event_type == 'reasoning_step':
                                print(f"🧠 Step {event_data.get('index', 0)}: {event_data.get('step', '')}")
                            
                            elif event_type == 'web_search_query':
                                print(f"🔍 Searching: {event_data.get('query', '')}")
                            
                            elif event_type == 'thinking':
                                phase = event_data.get('phase')
                                title = event_data.get('title','')
                                if phase == 'google_search':
                                    results = event_data.get('results', [])
                                    print(f"🔎 Web results ({len(results)} shown): " + ", ".join(r.get('title','')[:40] for r in results[:3]))
                                elif phase == 'tool_execution':
                                    print(f"🧪 Tools: {event_data.get('apis', [])}")
                                elif phase == 'context_fusion':
                                    print(f"🌀 Fusing keys: {event_data.get('keys', [])[:8]}")
                                elif phase == 'draft_generation':
                                    print("✍️ Generating draft...")
                                elif phase == 'draft_preview':
                                    draft = event_data.get('draft','')
                                    print(f"📝 Draft: {draft[:120]}{'...' if len(draft)>120 else ''}")
                                else:
                                    print(f"🤔 {title} ({phase})")
                            elif event_type == 'final_start':
                                print("✅ Streaming verified answer...")
                            elif event_type == 'response_chunk':
                                chunk = event_data.get('chunk', '')
                                if chunk:
                                    print(f"💬 {chunk[:140]}..." if len(chunk) > 140 else f"💬 {chunk}")
                            
                            elif event_type == 'fact_check_result':
                                print(f"✅ Fact-check: {event_data.get('status', '')} ({event_data.get('confidence', 0):.0%})")
                            
                            elif event_type == 'completion':
                                print(f"🎉 {event_data.get('message', 'Completed!')}")
                                break
                            
                            elif event_type == 'error':
                                print(f"❌ Error: {event_data.get('message', '')}")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Could not parse JSON: {line_str}")
            
            print("\n🎯 Streaming test completed!")
            
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streaming_endpoint()
