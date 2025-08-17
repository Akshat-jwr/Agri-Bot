#!/usr/bin/env python3
"""
Test script for Agricultural RAG System
Demonstrates the complete functionality without server dependencies
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tools.rag_core.rag_orchestrator import rag_orchestrator

async def test_rag_system():
    """Test the RAG system with various agricultural queries"""
    
    test_queries = [
        "What fertilizer should I use for wheat?",
        "How much rain do I need for rice farming?", 
        "What's the best time to sell my cotton crop?",
        "Which crop variety gives highest yield in Punjab?",
        "What government schemes are available for farmers?"
    ]
    
    print("🌾 Testing Agricultural Intelligence RAG System")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 40)
        
        try:
            result = await rag_orchestrator.process_farmer_query(query)
            
            if result['success']:
                print(f"✅ Classification: {result['classification'].primary_category}")
                print(f"✅ Confidence: {result['confidence_score']:.2f}")
                print(f"✅ Tools Used: {', '.join(result['tools_used'])}")
                print(f"✅ Processing Time: {result['processing_time']:.2f}s")
                print(f"✅ Main Answer: {result['response']['main_answer'][:100]}...")
                
                if result['response']['agricultural_recommendations']:
                    print(f"✅ Recommendations: {len(result['response']['agricultural_recommendations'])} items")
                    for rec in result['response']['agricultural_recommendations'][:2]:
                        print(f"   • {rec}")
                        
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n🎉 RAG System Test Complete!")
    print("\n📊 Performance Summary:")
    metrics = rag_orchestrator.get_performance_metrics()
    print(f"   • Total Queries: {metrics['total_queries']}")
    print(f"   • Successful: {metrics['successful_queries']}")
    print(f"   • Success Rate: {metrics['successful_queries']/max(metrics['total_queries'], 1)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_rag_system())
