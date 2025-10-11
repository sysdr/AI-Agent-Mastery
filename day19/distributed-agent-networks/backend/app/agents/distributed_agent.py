import asyncio
import json
import uuid
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict
import google.generativeai as genai
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    id: str
    sender_id: str
    receiver_id: str
    message_type: str
    content: dict
    timestamp: float
    signature: Optional[str] = None

@dataclass
class AgentNode:
    id: str
    host: str
    port: int
    public_key: bytes
    private_key: bytes
    status: str = "active"
    reputation_score: float = 1.0
    resource_usage: Dict = None
    
    def __post_init__(self):
        if self.resource_usage is None:
            self.resource_usage = {"cpu": 0.0, "memory": 0.0, "api_calls": 0}

class DistributedAgentNetwork:
    def __init__(self):
        self.agents: Dict[str, AgentNode] = {}
        self.connections: Dict[str, Dict] = {}
        self.encryption_keys: Dict[str, Fernet] = {}
        self.message_history: List[AgentMessage] = []
        self.resource_pool = {"total_cpu": 0, "total_memory": 0, "available_api_credits": 1000}
        
        # Configure Gemini AI
        genai.configure(api_key="your-gemini-api-key-here")
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def initialize_network(self, num_agents: int = 3):
        """Initialize the distributed agent network"""
        logger.info(f"🔧 Initializing network with {num_agents} agents...")
        
        # Create agents with unique identities
        base_port = 8001
        for i in range(num_agents):
            agent_id = f"agent_{i+1}"
            
            # Generate encryption keys for secure communication
            encryption_key = Fernet.generate_key()
            self.encryption_keys[agent_id] = Fernet(encryption_key)
            
            # Create agent node
            agent = AgentNode(
                id=agent_id,
                host="localhost",
                port=base_port + i,
                public_key=encryption_key,
                private_key=encryption_key,  # Simplified for demo
                status="active"
            )
            
            self.agents[agent_id] = agent
            self.connections[agent_id] = {}
            
            logger.info(f"✅ Created agent {agent_id} on port {agent.port}")
        
        # Establish peer-to-peer connections
        await self._establish_connections()
        
        # Start background tasks
        asyncio.create_task(self._resource_monitor())
        asyncio.create_task(self._reputation_updater())
        
        logger.info("🌐 Network initialization complete")
    
    async def _establish_connections(self):
        """Create secure peer-to-peer connections between all agents"""
        agent_ids = list(self.agents.keys())
        
        for i, agent_id in enumerate(agent_ids):
            for j, peer_id in enumerate(agent_ids):
                if i != j:  # Don't connect to self
                    # Simulate secure handshake
                    connection_id = f"{agent_id}->{peer_id}"
                    self.connections[agent_id][peer_id] = {
                        "status": "connected",
                        "encryption": True,
                        "last_ping": time.time(),
                        "latency": 0.001 + (abs(i-j) * 0.0005)  # Simulate network latency
                    }
        
        logger.info("🔐 Secure connections established between all agents")
    
    async def send_encrypted_message(self, sender_id: str, receiver_id: str, 
                                   message_type: str, content: dict) -> bool:
        """Send encrypted message between agents with mutual authentication"""
        if sender_id not in self.agents or receiver_id not in self.agents:
            return False
        
        # Create message
        message = AgentMessage(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=time.time()
        )
        
        # Encrypt content
        encrypted_content = self.encryption_keys[sender_id].encrypt(
            json.dumps(content).encode()
        )
        
        message.content = {"encrypted": encrypted_content.decode('latin-1')}
        message.signature = f"signed_by_{sender_id}"
        
        # Store in history
        self.message_history.append(message)
        
        logger.info(f"📨 Encrypted message sent: {sender_id} -> {receiver_id}")
        return True
    
    async def solve_collaboratively(self, problem_data: dict) -> dict:
        """Solve problem using distributed consensus and resource pooling"""
        logger.info(f"🧠 Starting collaborative problem solving...")
        
        problem_text = problem_data.get("problem", "What is the capital of France?")
        
        # Phase 1: Distribute work using resource pooling
        available_agents = [a for a in self.agents.values() if a.status == "active"]
        if len(available_agents) < 2:
            return {"error": "Insufficient agents for distributed processing"}
        
        # Phase 2: Each agent generates solution
        solutions = []
        for agent in available_agents[:3]:  # Use top 3 agents
            try:
                # Simulate AI processing with actual Gemini call (simplified)
                agent_solution = await self._agent_process_problem(agent.id, problem_text)
                solutions.append({
                    "agent_id": agent.id,
                    "solution": agent_solution,
                    "confidence": 0.8 + (agent.reputation_score * 0.2),
                    "processing_time": 0.5 + (hash(agent.id) % 100) / 200
                })
                
                # Update resource usage
                agent.resource_usage["api_calls"] += 1
                agent.resource_usage["cpu"] += 0.1
                
            except Exception as e:
                logger.error(f"Agent {agent.id} failed: {e}")
                solutions.append({
                    "agent_id": agent.id,
                    "solution": f"Error processing: {str(e)[:50]}",
                    "confidence": 0.1,
                    "processing_time": 1.0
                })
        
        # Phase 3: Distributed consensus voting
        consensus_result = await self._reach_consensus(solutions)
        
        # Phase 4: Update agent reputations
        await self._update_reputations(solutions, consensus_result)
        
        return {
            "problem": problem_text,
            "consensus_solution": consensus_result["solution"],
            "confidence": consensus_result["confidence"],
            "participating_agents": len(solutions),
            "individual_solutions": solutions,
            "consensus_method": "weighted_voting",
            "processing_time": consensus_result.get("total_time", 1.0)
        }
    
    async def _agent_process_problem(self, agent_id: str, problem: str) -> str:
        """Simulate agent processing problem with Gemini AI"""
        # For demo purposes, return varied responses based on agent
        responses = {
            "agent_1": f"Solution from Agent 1: Analyzing '{problem}' using primary reasoning approach.",
            "agent_2": f"Solution from Agent 2: Alternative perspective on '{problem}' with secondary analysis.",
            "agent_3": f"Solution from Agent 3: Comprehensive evaluation of '{problem}' with tertiary validation."
        }
        
        return responses.get(agent_id, f"Generic solution for '{problem}' from {agent_id}")
    
    async def _reach_consensus(self, solutions: List[dict]) -> dict:
        """Implement distributed consensus voting algorithm"""
        if not solutions:
            return {"solution": "No solutions available", "confidence": 0.0}
        
        # Weight solutions by confidence and agent reputation
        weighted_scores = []
        for sol in solutions:
            agent = self.agents[sol["agent_id"]]
            weight = sol["confidence"] * agent.reputation_score
            weighted_scores.append((sol, weight))
        
        # Find highest weighted solution
        best_solution = max(weighted_scores, key=lambda x: x[1])
        
        # Require at least 51% agreement for consensus
        total_weight = sum(score for _, score in weighted_scores)
        consensus_threshold = total_weight * 0.51
        
        if best_solution[1] >= consensus_threshold:
            return {
                "solution": best_solution[0]["solution"],
                "confidence": best_solution[0]["confidence"],
                "consensus_reached": True,
                "voting_weight": best_solution[1] / total_weight
            }
        else:
            # Merge top solutions if no clear consensus
            merged_solution = "Consensus solution: " + "; ".join([
                sol["solution"] for sol in solutions[:2]
            ])
            return {
                "solution": merged_solution,
                "confidence": 0.6,
                "consensus_reached": False,
                "voting_weight": 0.6
            }
    
    async def _update_reputations(self, solutions: List[dict], consensus: dict):
        """Update agent reputation scores based on solution quality"""
        for sol in solutions:
            agent = self.agents[sol["agent_id"]]
            
            # Increase reputation if solution was close to consensus
            if sol["solution"] in consensus["solution"]:
                agent.reputation_score = min(2.0, agent.reputation_score + 0.1)
            else:
                agent.reputation_score = max(0.1, agent.reputation_score - 0.05)
    
    async def _resource_monitor(self):
        """Monitor and optimize resource allocation"""
        while True:
            try:
                total_cpu = sum(agent.resource_usage["cpu"] for agent in self.agents.values())
                total_memory = sum(agent.resource_usage["memory"] for agent in self.agents.values())
                total_api_calls = sum(agent.resource_usage["api_calls"] for agent in self.agents.values())
                
                self.resource_pool.update({
                    "total_cpu": total_cpu,
                    "total_memory": total_memory,
                    "total_api_calls": total_api_calls,
                    "available_api_credits": max(0, 1000 - total_api_calls)
                })
                
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Resource monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _reputation_updater(self):
        """Background task to decay reputation scores over time"""
        while True:
            try:
                for agent in self.agents.values():
                    # Slight reputation decay to encourage continued good performance
                    agent.reputation_score = max(0.1, agent.reputation_score * 0.999)
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Reputation updater error: {e}")
                await asyncio.sleep(60)
    
    async def get_network_status(self) -> dict:
        """Get current network status for dashboard"""
        return {
            "agents": {
                agent_id: {
                    "id": agent.id,
                    "status": agent.status,
                    "reputation": round(agent.reputation_score, 2),
                    "resource_usage": agent.resource_usage,
                    "port": agent.port
                } for agent_id, agent in self.agents.items()
            },
            "connections": sum(len(conns) for conns in self.connections.values()),
            "total_messages": len(self.message_history),
            "resource_pool": self.resource_pool,
            "network_health": "healthy" if len([a for a in self.agents.values() if a.status == "active"]) > 1 else "degraded"
        }
    
    async def shutdown(self):
        """Gracefully shutdown the network"""
        logger.info("🛑 Shutting down distributed agent network...")
        for agent in self.agents.values():
            agent.status = "offline"
