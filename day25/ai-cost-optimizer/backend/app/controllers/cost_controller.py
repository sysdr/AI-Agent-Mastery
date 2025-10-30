from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from datetime import datetime
from typing import Dict, Any, List
import google.generativeai as genai
from app.services.cost_optimizer import CostOptimizerService
from app.models.cost_metrics import CostMetric
from config.config import config

router = APIRouter(prefix="/api/cost", tags=["cost"])

class CostController:
    def __init__(self, cost_service: CostOptimizerService):
        self.cost_service = cost_service
        genai.configure(api_key=config.GEMINI_API_KEY)
    
    async def create_ai_request_with_tracking(self, agent_id: str, prompt: str, 
                                            model_name: str = "gemini-pro") -> Dict[str, Any]:
        """Make AI request with cost tracking"""
        start_time = datetime.now()
        
        try:
            # Make Gemini API request
            model = genai.GenerativeModel(model_name)
            response = await model.generate_content_async(prompt)
            
            # Calculate metrics
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Estimate token usage (approximate)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response.text.split()) * 1.3 if response.text else 0
            total_tokens = int(input_tokens + output_tokens)
            
            # Calculate cost (Gemini Pro pricing: $0.0005/1K input tokens, $0.0015/1K output tokens)
            input_cost = (input_tokens / 1000) * 0.0005
            output_cost = (output_tokens / 1000) * 0.0015
            total_cost = input_cost + output_cost
            
            # Record cost metric
            cost_metric = CostMetric(
                agent_id=agent_id,
                request_type="generate_content",
                tokens_used=total_tokens,
                cost_usd=total_cost,
                model_name=model_name,
                success=True,
                response_time_ms=response_time_ms
            )
            
            await self.cost_service.record_cost_metric(cost_metric)
            
            return {
                'success': True,
                'response': response.text if response.text else "No response",
                'metrics': {
                    'tokens_used': total_tokens,
                    'cost_usd': round(total_cost, 6),
                    'response_time_ms': response_time_ms,
                    'model_name': model_name
                }
            }
            
        except Exception as e:
            # Record failed request
            cost_metric = CostMetric(
                agent_id=agent_id,
                request_type="generate_content",
                tokens_used=0,
                cost_usd=0.0,
                model_name=model_name,
                success=False,
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            
            await self.cost_service.record_cost_metric(cost_metric)
            
            return {
                'success': False,
                'error': str(e),
                'metrics': {
                    'tokens_used': 0,
                    'cost_usd': 0.0,
                    'response_time_ms': cost_metric.response_time_ms,
                    'model_name': model_name
                }
            }
