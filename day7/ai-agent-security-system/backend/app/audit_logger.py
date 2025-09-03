import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib
import hmac
import os
import sqlite3
import aiosqlite

class AuditLogger:
    def __init__(self):
        self.db_path = "audit_log.db"
        self.signing_key = os.environ.get('AUDIT_SIGNING_KEY', 'default-signing-key').encode()
        self.entries_cache = []
    
    async def initialize(self):
        """Initialize audit database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audit_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    agent_id TEXT,
                    timestamp TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    hash_chain TEXT
                )
            """)
            await db.commit()
        print("✅ Audit Logger initialized")
    
    def _calculate_signature(self, event_data: str) -> str:
        """Calculate HMAC signature for audit entry"""
        return hmac.new(
            self.signing_key,
            event_data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _calculate_hash(self, event_type: str, timestamp: str, event_data: str) -> str:
        """Calculate hash for blockchain-like integrity"""
        combined = f"{event_type}:{timestamp}:{event_data}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def log_event(self, event: Dict[str, Any]):
        """Log security event with cryptographic verification"""
        timestamp = datetime.utcnow().isoformat()
        event_type = event.get("type", "unknown")
        agent_id = event.get("agent_id", "system")
        
        # Prepare event data
        event_data = json.dumps(event, sort_keys=True)
        signature = self._calculate_signature(event_data)
        event_hash = self._calculate_hash(event_type, timestamp, event_data)
        
        # Get previous hash for chain
        previous_hash = await self._get_last_hash()
        hash_chain = hashlib.sha256(f"{previous_hash}:{event_hash}".encode()).hexdigest()
        
        # Store in database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO audit_entries 
                (event_type, agent_id, timestamp, event_data, signature, hash_chain)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_type, agent_id, timestamp, event_data, signature, hash_chain))
            await db.commit()
        
        # Update cache
        self.entries_cache.append({
            "event_type": event_type,
            "agent_id": agent_id,
            "timestamp": timestamp,
            "event_data": json.loads(event_data),
            "signature": signature,
            "verified": True
        })
        
        # Keep cache size manageable
        if len(self.entries_cache) > 1000:
            self.entries_cache = self.entries_cache[-500:]
    
    async def _get_last_hash(self) -> str:
        """Get the hash of the last audit entry for chaining"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT hash_chain FROM audit_entries ORDER BY id DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else "genesis"
    
    async def get_entries(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Retrieve audit entries with verification"""
        entries = []
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT event_type, agent_id, timestamp, event_data, signature
                FROM audit_entries
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset)) as cursor:
                async for row in cursor:
                    event_type, agent_id, timestamp, event_data, signature = row
                    
                    # Verify signature
                    expected_signature = self._calculate_signature(event_data)
                    is_verified = hmac.compare_digest(signature, expected_signature)
                    
                    entries.append({
                        "event_type": event_type,
                        "agent_id": agent_id,
                        "timestamp": timestamp,
                        "event_data": json.loads(event_data),
                        "verified": is_verified
                    })
        
        return entries
    
    async def get_security_summary(self) -> Dict:
        """Get security event summary"""
        summary = {
            "total_events": 0,
            "failed_auths": 0,
            "security_violations": 0,
            "last_24h_events": 0
        }
        
        cutoff_time = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Total events
            async with db.execute("SELECT COUNT(*) FROM audit_entries") as cursor:
                result = await cursor.fetchone()
                summary["total_events"] = result[0] if result else 0
            
            # Failed authentications
            async with db.execute("""
                SELECT COUNT(*) FROM audit_entries 
                WHERE event_type = 'auth_failure'
            """) as cursor:
                result = await cursor.fetchone()
                summary["failed_auths"] = result[0] if result else 0
            
            # Recent events
            async with db.execute("""
                SELECT COUNT(*) FROM audit_entries 
                WHERE timestamp > ?
            """, (cutoff_time,)) as cursor:
                result = await cursor.fetchone()
                summary["last_24h_events"] = result[0] if result else 0
        
        return summary
