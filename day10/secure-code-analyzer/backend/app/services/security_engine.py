"""
Security Analysis Engine - Core vulnerability detection
"""

import ast
import re
import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class SecurityFinding:
    rule_id: str
    severity: SeverityLevel
    message: str
    file_path: str
    line_number: int
    column: int
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None

class SecurityEngine:
    """Advanced security analysis engine using AST parsing"""
    
    def __init__(self):
        self.vulnerability_patterns = self._load_patterns()
        self.analyzed_cache = {}
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load security vulnerability patterns"""
        return {
            "sql_injection": {
                "pattern": r"execute\s*\(\s*.*\+.*\)",
                "severity": SeverityLevel.HIGH,
                "cwe": "CWE-89",
                "message": "Potential SQL injection vulnerability"
            },
            "xss": {
                "pattern": r"innerHTML\s*=\s*.*\+",
                "severity": SeverityLevel.MEDIUM,
                "cwe": "CWE-79", 
                "message": "Potential XSS vulnerability"
            },
            "path_traversal": {
                "pattern": r"open\s*\(\s*.*\.\./",
                "severity": SeverityLevel.HIGH,
                "cwe": "CWE-22",
                "message": "Potential path traversal vulnerability"
            },
            "hardcoded_secret": {
                "pattern": r"(password|secret|key|token)\s*=\s*['\"][^'\"]{8,}['\"]",
                "severity": SeverityLevel.CRITICAL,
                "cwe": "CWE-798",
                "message": "Hardcoded credentials detected"
            }
        }
    
    async def analyze_code(self, code: str, file_path: str = "") -> List[SecurityFinding]:
        """Analyze code for security vulnerabilities"""
        findings = []
        
        # Create hash for caching
        code_hash = hashlib.md5(code.encode()).hexdigest()
        if code_hash in self.analyzed_cache:
            return self.analyzed_cache[code_hash]
        
        try:
            # AST-based analysis for Python files
            if file_path.endswith('.py'):
                findings.extend(self._analyze_python_ast(code, file_path))
            
            # Pattern-based analysis for all files
            findings.extend(self._analyze_patterns(code, file_path))
            
            # Cache results
            self.analyzed_cache[code_hash] = findings
            
        except Exception as e:
            # Fallback to pattern analysis only
            findings = self._analyze_patterns(code, file_path)
        
        return findings
    
    def _analyze_python_ast(self, code: str, file_path: str) -> List[SecurityFinding]:
        """Advanced AST-based analysis for Python code"""
        findings = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # SQL injection detection
                if isinstance(node, ast.Call):
                    findings.extend(self._check_sql_injection(node, file_path, code))
                
                # Hardcoded secrets
                if isinstance(node, ast.Assign):
                    findings.extend(self._check_hardcoded_secrets(node, file_path, code))
                
                # Unsafe eval/exec usage
                if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                    if node.func.id in ['eval', 'exec']:
                        findings.append(self._create_finding(
                            "unsafe_eval", SeverityLevel.HIGH, node.lineno, 0,
                            "Unsafe use of eval/exec", file_path, code
                        ))
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return findings
    
    def _check_sql_injection(self, node: ast.Call, file_path: str, code: str) -> List[SecurityFinding]:
        """Check for SQL injection patterns in AST"""
        findings = []
        
        if hasattr(node.func, 'attr') and node.func.attr in ['execute', 'executemany']:
            for arg in node.args:
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                    findings.append(self._create_finding(
                        "sql_injection", SeverityLevel.HIGH, node.lineno, node.col_offset,
                        "SQL query constructed using string concatenation", 
                        file_path, code
                    ))
        
        return findings
    
    def _check_hardcoded_secrets(self, node: ast.Assign, file_path: str, code: str) -> List[SecurityFinding]:
        """Check for hardcoded secrets in assignments"""
        findings = []
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(secret in var_name for secret in ['password', 'secret', 'key', 'token']):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if len(node.value.value) > 8:  # Likely a real secret
                            findings.append(self._create_finding(
                                "hardcoded_secret", SeverityLevel.CRITICAL, 
                                node.lineno, node.col_offset,
                                f"Hardcoded credential in variable '{target.id}'",
                                file_path, code
                            ))
        
        return findings
    
    def _analyze_patterns(self, code: str, file_path: str) -> List[SecurityFinding]:
        """Pattern-based vulnerability detection"""
        findings = []
        lines = code.split('\n')
        
        for pattern_name, pattern_info in self.vulnerability_patterns.items():
            pattern = re.compile(pattern_info["pattern"], re.IGNORECASE)
            
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    findings.append(self._create_finding(
                        pattern_name, pattern_info["severity"],
                        line_num, match.start(),
                        pattern_info["message"], file_path, code
                    ))
        
        return findings
    
    def _create_finding(self, rule_id: str, severity: SeverityLevel, line: int, 
                       column: int, message: str, file_path: str, code: str) -> SecurityFinding:
        """Create a security finding object"""
        lines = code.split('\n')
        code_snippet = lines[line-1] if line <= len(lines) else ""
        
        return SecurityFinding(
            rule_id=rule_id,
            severity=severity,
            message=message,
            file_path=file_path,
            line_number=line,
            column=column,
            code_snippet=code_snippet.strip(),
            recommendation=self._get_recommendation(rule_id),
            cwe_id=self.vulnerability_patterns.get(rule_id, {}).get("cwe")
        )
    
    def _get_recommendation(self, rule_id: str) -> str:
        """Get security recommendation for a rule"""
        recommendations = {
            "sql_injection": "Use parameterized queries or prepared statements",
            "xss": "Sanitize user input and use safe DOM manipulation methods",
            "path_traversal": "Validate and sanitize file paths, use allowlists",
            "hardcoded_secret": "Use environment variables or secure credential storage",
            "unsafe_eval": "Avoid eval/exec or validate input thoroughly"
        }
        return recommendations.get(rule_id, "Review and remediate security issue")
