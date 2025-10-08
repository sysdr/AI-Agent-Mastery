import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.models import ExpertiseLevel, ValidationResult, KnowledgeBase, AuditLog
from app.validation.source_validator import SourceValidator
from app.knowledge.knowledge_manager import KnowledgeManager
from config.settings import settings
import structlog

logger = structlog.get_logger()

@dataclass
class ValidationStep:
    step_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence_impact: float
    processing_time: float

class ExpertAgent:
    def __init__(self, domain: str, db: Session):
        self.domain = domain
        self.db = db
        self.source_validator = SourceValidator()
        self.knowledge_manager = KnowledgeManager(db)
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def process_query(self, query: str, required_confidence: float = 0.7) -> Dict[str, Any]:
        query_id = str(uuid.uuid4())
        start_time = time.time()
        validation_steps = []
        
        try:
            # Step 1: Domain expertise check
            expertise_result = await self._check_domain_expertise(query)
            validation_steps.append(ValidationStep(
                "domain_check",
                {"query": query, "domain": self.domain},
                expertise_result,
                0.1,
                0.2
            ))
            
            if expertise_result["has_expertise"]:
                # Step 2: Knowledge retrieval
                knowledge_result = await self._retrieve_knowledge(query)
                validation_steps.append(ValidationStep(
                    "knowledge_retrieval",
                    {"query": query},
                    knowledge_result,
                    0.3,
                    0.5
                ))
                
                # Step 3: Source validation
                source_result = await self._validate_sources(query, knowledge_result["sources"])
                validation_steps.append(ValidationStep(
                    "source_validation",
                    {"sources": knowledge_result["sources"]},
                    source_result,
                    0.4,
                    1.2
                ))
                
                # Step 4: Generate response
                response_result = await self._generate_expert_response(query, knowledge_result, source_result)
                validation_steps.append(ValidationStep(
                    "response_generation",
                    {"query": query, "knowledge": knowledge_result, "sources": source_result},
                    response_result,
                    0.2,
                    0.8
                ))
                
                # Calculate final confidence
                confidence_score = self._calculate_confidence(validation_steps)
                
                # Generate explanation
                explanation = self._generate_explanation(validation_steps, confidence_score)
                
                processing_time = time.time() - start_time
                
                # Log audit trail
                await self._log_audit_trail(query_id, query, response_result["response"], 
                                          confidence_score, validation_steps, processing_time)
                
                return {
                    "query_id": query_id,
                    "response": response_result["response"],
                    "confidence_score": confidence_score,
                    "expertise_level": self._determine_expertise_level(confidence_score),
                    "sources_validated": source_result["validated_sources"],
                    "explanation": explanation,
                    "escalation_required": confidence_score < required_confidence,
                    "processing_time": processing_time,
                    "audit_trail": [step.__dict__ for step in validation_steps]
                }
            else:
                return {
                    "query_id": query_id,
                    "response": "I don't have sufficient expertise in this domain to provide a reliable answer.",
                    "confidence_score": 0.0,
                    "expertise_level": ExpertiseLevel.NOVICE,
                    "sources_validated": [],
                    "explanation": f"Query outside domain expertise: {self.domain}",
                    "escalation_required": True,
                    "processing_time": time.time() - start_time,
                    "audit_trail": [step.__dict__ for step in validation_steps]
                }
                
        except Exception as e:
            logger.error("Error processing query", error=str(e), query_id=query_id)
            return self._error_response(query_id, str(e), time.time() - start_time, query)
    
    async def _check_domain_expertise(self, query: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze if this query falls within the domain of {self.domain}.
        Query: {query}
        
        Respond with JSON:
        {{
            "has_expertise": boolean,
            "relevance_score": float (0-1),
            "domain_match": string,
            "reasoning": string
        }}
        """
        
        response = await self.model.generate_content_async(prompt)
        try:
            import json
            return json.loads(response.text)
        except:
            return {"has_expertise": False, "relevance_score": 0.0, "domain_match": "unknown", "reasoning": "Parse error"}
    
    async def _retrieve_knowledge(self, query: str) -> Dict[str, Any]:
        # Search knowledge base
        knowledge_entries = self.knowledge_manager.search_knowledge(query, self.domain)
        
        return {
            "entries": knowledge_entries,
            "sources": [entry.sources for entry in knowledge_entries if entry.sources],
            "confidence_scores": [entry.confidence_score for entry in knowledge_entries]
        }
    
    async def _validate_sources(self, query: str, sources: List[Any]) -> Dict[str, Any]:
        validated_sources = []
        validation_scores = []
        
        for source_list in sources[:settings.max_sources_to_check]:
            if isinstance(source_list, list):
                for source in source_list:
                    validation_result = await self.source_validator.validate_source(source, query)
                    validated_sources.append(source)
                    validation_scores.append(validation_result["confidence"])
        
        avg_validation_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0
        
        return {
            "validated_sources": validated_sources,
            "validation_scores": validation_scores,
            "average_validation": avg_validation_score
        }
    
    async def _generate_expert_response(self, query: str, knowledge: Dict, sources: Dict) -> Dict[str, Any]:
        prompt = f"""
        As an expert in {self.domain}, answer this query based on the provided knowledge and validated sources.
        
        Query: {query}
        Knowledge entries: {len(knowledge['entries'])}
        Validated sources: {len(sources['validated_sources'])}
        
        Provide a comprehensive, accurate response that:
        1. Directly answers the query
        2. Cites relevant sources
        3. Indicates confidence level
        4. Mentions any limitations or gaps
        
        Response should be professional and authoritative.
        """
        
        response = await self.model.generate_content_async(prompt)
        
        return {
            "response": response.text,
            "sources_cited": sources["validated_sources"]
        }
    
    def _calculate_confidence(self, validation_steps: List[ValidationStep]) -> float:
        total_impact = sum(step.confidence_impact for step in validation_steps)
        weighted_confidence = sum(step.confidence_impact * 
                                (1.0 if "error" not in step.output_data else 0.3) 
                                for step in validation_steps)
        
        return min(weighted_confidence / total_impact if total_impact > 0 else 0.0, 1.0)
    
    def _determine_expertise_level(self, confidence_score: float) -> ExpertiseLevel:
        if confidence_score >= 0.9:
            return ExpertiseLevel.SPECIALIST
        elif confidence_score >= 0.8:
            return ExpertiseLevel.EXPERT
        elif confidence_score >= 0.6:
            return ExpertiseLevel.INTERMEDIATE
        else:
            return ExpertiseLevel.NOVICE
    
    def _generate_explanation(self, validation_steps: List[ValidationStep], confidence_score: float) -> str:
        explanations = []
        
        for step in validation_steps:
            if step.step_type == "domain_check":
                explanations.append(f"Domain relevance: {step.output_data.get('relevance_score', 0):.2f}")
            elif step.step_type == "knowledge_retrieval":
                explanations.append(f"Knowledge entries found: {len(step.output_data.get('entries', []))}")
            elif step.step_type == "source_validation":
                explanations.append(f"Sources validated: {len(step.output_data.get('validated_sources', []))}")
            elif step.step_type == "response_generation":
                explanations.append("Expert response generated based on validated knowledge")
        
        explanations.append(f"Overall confidence: {confidence_score:.2f}")
        
        return "; ".join(explanations)
    
    async def _log_audit_trail(self, query_id: str, query: str, response: str, 
                             confidence: float, steps: List[ValidationStep], processing_time: float):
        audit_log = AuditLog(
            query_id=query_id,
            agent_id=f"{self.domain}_agent",
            query_text=query,
            response_text=response,
            confidence_score=confidence,
            sources_consulted=[],
            validation_steps=[step.__dict__ for step in steps],
            expertise_level=self._determine_expertise_level(confidence).value,
            processing_time=processing_time
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def _error_response(self, query_id: str, error: str, processing_time: float, query: str = "") -> Dict[str, Any]:
        # Log audit trail even for errors
        try:
            audit_log = AuditLog(
                query_id=query_id,
                agent_id=f"{self.domain}_agent",
                query_text=query,
                response_text="Error occurred during processing",
                confidence_score=0.0,
                sources_consulted=[],
                validation_steps=[],
                expertise_level=ExpertiseLevel.NOVICE.value,
                processing_time=processing_time
            )
            self.db.add(audit_log)
            self.db.commit()
        except Exception as e:
            logger.error("Failed to log error audit trail", error=str(e))
        
        return {
            "query_id": query_id,
            "response": "An error occurred while processing your query. Please try again.",
            "confidence_score": 0.0,
            "expertise_level": ExpertiseLevel.NOVICE,
            "sources_validated": [],
            "explanation": f"Error: {error}",
            "escalation_required": True,
            "processing_time": processing_time,
            "audit_trail": []
        }
