import pytest
import asyncio
from app.services.security_engine import SecurityEngine, SeverityLevel

@pytest.fixture
def security_engine():
    return SecurityEngine()

class TestSecurityEngine:
    
    def test_sql_injection_detection(self, security_engine):
        vulnerable_code = '''
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()
'''
        
        findings = asyncio.run(security_engine.analyze_code(vulnerable_code, "test.py"))
        
        # Should detect SQL injection
        sql_findings = [f for f in findings if f.rule_id == "sql_injection"]
        assert len(sql_findings) > 0
        assert sql_findings[0].severity == SeverityLevel.HIGH
    
    def test_hardcoded_secret_detection(self, security_engine):
        vulnerable_code = '''
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "supersecretpassword123"
'''
        
        findings = asyncio.run(security_engine.analyze_code(vulnerable_code, "test.py"))
        
        # Should detect hardcoded secrets
        secret_findings = [f for f in findings if f.rule_id == "hardcoded_secret"]
        assert len(secret_findings) > 0
        assert secret_findings[0].severity == SeverityLevel.CRITICAL
    
    def test_clean_code(self, security_engine):
        clean_code = '''
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    query = "SELECT * FROM users WHERE id = ?"
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    return cursor.fetchone()
'''
        
        findings = asyncio.run(security_engine.analyze_code(clean_code, "test.py"))
        
        # Should not detect SQL injection in parameterized query
        sql_findings = [f for f in findings if f.rule_id == "sql_injection"]
        assert len(sql_findings) == 0
