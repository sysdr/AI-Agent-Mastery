import asyncio
import time
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VoteProposal:
    id: str
    proposer_id: str
    content: Any
    created_at: float
    votes: Dict[str, bool] = None
    status: str = "pending"  # pending, approved, rejected
    
    def __post_init__(self):
        if self.votes is None:
            self.votes = {}

class ConsensusManager:
    def __init__(self, network_manager):
        self.network = network_manager
        self.proposals: Dict[str, VoteProposal] = {}
        self.voting_history: List[Dict] = []
        self.consensus_threshold = 0.67  # 67% agreement required
        
    async def create_proposal(self, proposer_id: str, content: Any) -> str:
        """Create a new consensus proposal"""
        proposal_id = f"proposal_{int(time.time())}_{proposer_id}"
        
        proposal = VoteProposal(
            id=proposal_id,
            proposer_id=proposer_id,
            content=content,
            created_at=time.time()
        )
        
        self.proposals[proposal_id] = proposal
        
        # Notify all agents about new proposal
        for agent_id in self.network.agents.keys():
            if agent_id != proposer_id:
                await self.network.send_encrypted_message(
                    proposer_id, agent_id, "vote_request", 
                    {"proposal_id": proposal_id, "content": content}
                )
        
        logger.info(f"📋 Created proposal {proposal_id}")
        return proposal_id
    
    async def cast_vote(self, proposal_id: str, voter_id: str, vote: bool) -> bool:
        """Cast vote on a proposal"""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != "pending":
            return False
        
        # Verify voter is valid agent
        if voter_id not in self.network.agents:
            return False
        
        proposal.votes[voter_id] = vote
        logger.info(f"🗳️ Vote cast: {voter_id} -> {vote} for {proposal_id}")
        
        # Check if we have enough votes to reach consensus
        await self._check_consensus(proposal_id)
        return True
    
    async def _check_consensus(self, proposal_id: str):
        """Check if proposal has reached consensus"""
        proposal = self.proposals[proposal_id]
        active_agents = [a for a in self.network.agents.values() if a.status == "active"]
        
        total_votes = len(proposal.votes)
        positive_votes = sum(1 for vote in proposal.votes.values() if vote)
        
        # Need votes from majority of active agents
        if total_votes >= len(active_agents) * 0.5:
            consensus_ratio = positive_votes / total_votes
            
            if consensus_ratio >= self.consensus_threshold:
                proposal.status = "approved"
                logger.info(f"✅ Proposal {proposal_id} approved with {consensus_ratio:.2%} agreement")
            else:
                proposal.status = "rejected" 
                logger.info(f"❌ Proposal {proposal_id} rejected with {consensus_ratio:.2%} agreement")
            
            # Record in history
            self.voting_history.append({
                "proposal_id": proposal_id,
                "status": proposal.status,
                "votes": dict(proposal.votes),
                "consensus_ratio": consensus_ratio,
                "timestamp": time.time()
            })
    
    def get_voting_status(self) -> Dict:
        """Get current voting status for dashboard"""
        return {
            "active_proposals": len([p for p in self.proposals.values() if p.status == "pending"]),
            "total_proposals": len(self.proposals),
            "voting_history": self.voting_history[-10:],  # Last 10 votes
            "consensus_threshold": self.consensus_threshold
        }
