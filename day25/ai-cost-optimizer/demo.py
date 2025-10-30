#!/usr/bin/env python3
"""
AI Cost Optimizer - Demo Script
Demonstrates cost tracking, performance monitoring, and forecasting capabilities
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class CostOptimizerDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.agent_id = "demo-agent"
    
    async def demo_cost_tracking(self) -> Dict[str, Any]:
        """Demonstrate cost tracking with sample AI requests"""
        print("🔍 Demonstrating Cost Tracking...")
        
        # Sample prompts for testing
        test_prompts = [
            "Explain machine learning in simple terms",
            "Write a Python function to calculate fibonacci numbers",
            "What are the benefits of renewable energy?",
            "Describe the process of photosynthesis",
            "How do neural networks work?"
        ]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for i, prompt in enumerate(test_prompts, 1):
                print(f"  📝 Making AI request {i}/5...")
                
                try:
                    # Make tracked AI request
                    async with session.post(
                        f"{self.base_url}/api/cost/request",
                        json={
                            "agent_id": self.agent_id,
                            "prompt": prompt,
                            "model_name": "gemini-pro"
                        }
                    ) as response:
                        result = await response.json()
                        results.append(result)
                        
                        if result.get('success'):
                            metrics = result.get('metrics', {})
                            print(f"    ✅ Cost: ${metrics.get('cost_usd', 0):.6f}")
                            print(f"    📊 Tokens: {metrics.get('tokens_used', 0)}")
                            print(f"    ⏱️  Time: {metrics.get('response_time_ms', 0)}ms")
                        else:
                            print(f"    ❌ Request failed: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    # Add mock result for demo continuity
                    results.append({
                        'success': True,
                        'response': f"Mock response for: {prompt[:50]}...",
                        'metrics': {
                            'cost_usd': 0.001 + (i * 0.0002),
                            'tokens_used': 120 + (i * 15),
                            'response_time_ms': 1000 + (i * 100),
                            'model_name': 'gemini-pro'
                        }
                    })
                
                # Small delay between requests
                await asyncio.sleep(1)
        
        return results
    
    async def demo_cost_analytics(self) -> Dict[str, Any]:
        """Demonstrate cost analytics and optimization"""
        print("\n💰 Demonstrating Cost Analytics...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get cost summary
                async with session.get(
                    f"{self.base_url}/api/cost/summary/{self.agent_id}?hours=1"
                ) as response:
                    cost_summary = await response.json()
                    
                    print(f"  📈 Total Cost (1h): ${cost_summary.get('total_cost', 0):.4f}")
                    print(f"  🔢 Total Requests: {cost_summary.get('request_count', 0)}")
                    print(f"  💵 Avg Cost/Request: ${cost_summary.get('average_cost_per_request', 0):.4f}")
                    print(f"  🎯 Cost Trend: {cost_summary.get('cost_trend', 'unknown')}")
                    
            except Exception as e:
                print(f"  ❌ Error fetching cost summary: {e}")
                cost_summary = {
                    'total_cost': 0.0123,
                    'request_count': 5,
                    'average_cost_per_request': 0.00246,
                    'cost_trend': 'stable'
                }
                print(f"  📈 Total Cost (1h): ${cost_summary['total_cost']:.4f} (mock)")
            
            try:
                # Get optimization opportunities
                async with session.get(
                    f"{self.base_url}/api/cost/optimization/{self.agent_id}"
                ) as response:
                    optimizations = await response.json()
                    
                    if optimizations:
                        print(f"  🎯 Found {len(optimizations)} optimization opportunities:")
                        for opt in optimizations:
                            print(f"    • {opt.get('rule_name', 'Unknown')} - Savings: ${opt.get('estimated_savings', 0):.4f}")
                    else:
                        print("  ✅ No optimization opportunities found")
                        
            except Exception as e:
                print(f"  ❌ Error fetching optimizations: {e}")
                print("  ✅ No optimization opportunities found (mock)")
        
        return cost_summary
    
    async def demo_performance_monitoring(self) -> Dict[str, Any]:
        """Demonstrate performance monitoring"""
        print("\n⚡ Demonstrating Performance Monitoring...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get performance summary
                async with session.get(
                    f"{self.base_url}/api/performance/summary/{self.agent_id}?minutes=60"
                ) as response:
                    perf_summary = await response.json()
                    
                    if perf_summary.get('status') != 'no_data':
                        print(f"  🖥️  CPU Usage: {perf_summary.get('avg_cpu_usage', 0):.1f}%")
                        print(f"  💾 Memory Usage: {perf_summary.get('avg_memory_usage', 0):.1f}%")
                        print(f"  ⏱️  Avg Response Time: {perf_summary.get('avg_response_time', 0):.1f}ms")
                        print(f"  📊 Performance Score: {perf_summary.get('performance_score', 0)}/100")
                        print(f"  🔄 Status: {perf_summary.get('status', 'unknown')}")
                    else:
                        print("  📊 No performance data available yet")
                        
            except Exception as e:
                print(f"  ❌ Error fetching performance data: {e}")
                perf_summary = {
                    'avg_cpu_usage': 45.2,
                    'avg_memory_usage': 62.8,
                    'avg_response_time': 1234,
                    'performance_score': 87,
                    'status': 'healthy'
                }
                print(f"  🖥️  CPU Usage: {perf_summary['avg_cpu_usage']:.1f}% (mock)")
                print(f"  💾 Memory Usage: {perf_summary['avg_memory_usage']:.1f}% (mock)")
                print(f"  ⏱️  Avg Response Time: {perf_summary['avg_response_time']:.1f}ms (mock)")
                print(f"  📊 Performance Score: {perf_summary['performance_score']}/100 (mock)")
        
        return perf_summary
    
    async def demo_forecasting(self) -> Dict[str, Any]:
        """Demonstrate cost forecasting"""
        print("\n🔮 Demonstrating Cost Forecasting...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get cost forecast
                async with session.get(
                    f"{self.base_url}/api/forecast/costs/{self.agent_id}?forecast_hours=24"
                ) as response:
                    forecast = await response.json()
                    
                    if forecast.get('status') != 'insufficient_data':
                        print(f"  📊 Current Hourly Rate: ${forecast.get('current_hourly_rate', 0):.4f}")
                        print(f"  🎯 Forecasted Total (24h): ${forecast.get('forecasted_total_cost', 0):.4f}")
                        print(f"  📈 Trend: {forecast.get('trend', 'unknown')}")
                        
                        risk = forecast.get('risk_assessment', {})
                        print(f"  ⚠️  Risk Level: {risk.get('risk_level', 'unknown')}")
                        print(f"  💡 {risk.get('message', 'No message')}")
                        
                        recommendations = forecast.get('recommendations', [])
                        if recommendations:
                            print("  📝 Recommendations:")
                            for rec in recommendations[:3]:  # Show first 3
                                print(f"    • {rec}")
                    else:
                        print("  📊 Insufficient data for forecasting")
                        
            except Exception as e:
                print(f"  ❌ Error fetching forecast: {e}")
                # Mock forecast data
                print("  📊 Current Hourly Rate: $0.0082 (mock)")
                print("  🎯 Forecasted Total (24h): $0.1968 (mock)")
                print("  📈 Trend: stable (mock)")
                print("  ⚠️  Risk Level: low (mock)")
                print("  💡 Forecasted costs within acceptable range (mock)")
        
        return forecast
    
    async def run_complete_demo(self):
        """Run complete demonstration"""
        print("🚀 AI Agent Cost Optimization Platform Demo")
        print("=" * 50)
        
        try:
            # Check if backend is running
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    health = await response.json()
                    if health.get('status') == 'healthy':
                        print("✅ Backend is healthy and ready")
                    else:
                        print("⚠️  Backend health check warning")
        except:
            print("⚠️  Backend not available - using mock data")
        
        # Run demo steps
        await self.demo_cost_tracking()
        await asyncio.sleep(2)
        
        await self.demo_cost_analytics()
        await asyncio.sleep(1)
        
        await self.demo_performance_monitoring()
        await asyncio.sleep(1)
        
        await self.demo_forecasting()
        
        print("\n🎉 Demo completed!")
        print("\n📱 Visit http://localhost:3000 for the web dashboard")
        print("🔧 API Documentation: http://localhost:8000/docs")

async def main():
    """Run the demo"""
    demo = CostOptimizerDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
