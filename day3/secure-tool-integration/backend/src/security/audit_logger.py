"""
Security Audit Logging System
"""
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
import sqlite3
import structlog
from pathlib import Path

logger = structlog.get_logger()

class AuditLogger:
    def __init__(self):
        self.db_path = "logs/audit.db"
        self.connection = None
        
    async def initialize(self):
        """Initialize audit logging database"""
        Path("logs").mkdir(exist_ok=True)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        await self._create_tables()
        logger.info("Audit logger initialized")
        
    async def _create_tables(self):
        """Create audit log tables"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                parameters TEXT,
                result TEXT,
                security_level TEXT,
                ip_address TEXT,
                correlation_id TEXT
            )
        """)
        self.connection.commit()
        
    async def log_action(self, agent_id: str, action: str, resource: str, 
                        parameters: Dict = None, result: str = "success",
                        security_level: str = "info", correlation_id: str = None):
        """Log security-relevant action"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO audit_logs 
                (timestamp, agent_id, action, resource, parameters, result, security_level, correlation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, agent_id, action, resource,
                json.dumps(parameters or {}), result, security_level, correlation_id
            ))
            self.connection.commit()
            
            # Also log to structured logger
            logger.info(
                "Security action logged",
                agent_id=agent_id,
                action=action,
                resource=resource,
                result=result,
                security_level=security_level
            )
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))
            
    async def log_security_incident(self, agent_id: str, incident_type: str, 
                                  details: Dict, severity: str = "high"):
        """Log security incident"""
        await self.log_action(
            agent_id=agent_id,
            action="security_incident",
            resource=incident_type,
            parameters=details,
            result="incident",
            security_level=severity
        )
        
    async def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent audit logs"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM audit_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        logs = []
        for row in cursor.fetchall():
            log_dict = dict(zip(columns, row))
            if log_dict['parameters']:
                log_dict['parameters'] = json.loads(log_dict['parameters'])
            logs.append(log_dict)
            
        return logs
        
    async def search_logs(self, agent_id: str = None, action: str = None, 
                         security_level: str = None) -> List[Dict]:
        """Search audit logs with filters"""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if action:
            query += " AND action = ?"
            params.append(action)
        if security_level:
            query += " AND security_level = ?"
            params.append(security_level)
            
        query += " ORDER BY timestamp DESC"
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
