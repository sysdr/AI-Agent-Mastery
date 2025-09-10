import os
from typing import Dict, Any, List
from ..models.schemas import SecurityAnalysisResult, ThreatLevel
from .security_service import SecurityService

class AudioSecurityService:
    def __init__(self):
        self.security_service = SecurityService()
        self.prohibited_content = self._load_prohibited_content()
    
    def _load_prohibited_content(self) -> List[str]:
        """Load prohibited content keywords"""
        return [
            "threat", "violence", "attack", "bomb", "weapon",
            "hate", "discrimination", "harassment", "abuse",
            "illegal", "fraud", "scam", "phishing", "malware"
        ]
    
    async def analyze_audio(self, file_path: str, filename: str) -> SecurityAnalysisResult:
        """Complete audio security analysis"""
        analysis_data = {
            "type": "audio",
            "filename": filename,
            "file_path": file_path
        }
        
        # File validation
        file_info = self._validate_audio_file(file_path)
        analysis_data.update(file_info)
        
        # Audio properties analysis
        audio_properties = self._analyze_audio_properties(file_path)
        analysis_data["audio_properties"] = audio_properties
        
        # Speech recognition and content analysis
        transcript_analysis = self._analyze_speech_content(file_path)
        analysis_data["transcript_analysis"] = transcript_analysis
        
        # Acoustic analysis for anomalies
        acoustic_analysis = self._analyze_acoustic_features(file_path)
        analysis_data["acoustic_analysis"] = acoustic_analysis
        
        # Content moderation
        moderation_analysis = self._moderate_audio_content(transcript_analysis.get("transcript", ""))
        analysis_data["moderation_analysis"] = moderation_analysis
        
        # Get AI risk classification
        risk_assessment = await self.security_service.classify_content_risk(analysis_data)
        
        result = SecurityAnalysisResult(
            content_type="audio",
            filename=filename,
            risk_score=risk_assessment["overall_risk_score"],
            threat_level=ThreatLevel(risk_assessment["threat_level"]),
            issues_found=risk_assessment["specific_risks"],
            recommendations=risk_assessment["recommendations"],
            confidence_score=risk_assessment["confidence_score"],
            metadata={
                "duration": audio_properties.get("duration", 0),
                "sample_rate": audio_properties.get("sample_rate", 0),
                "channels": audio_properties.get("channels", 0),
                "transcript_confidence": transcript_analysis.get("confidence", 0),
                "content_flags": moderation_analysis.get("flags", []),
                "acoustic_anomalies": acoustic_analysis.get("anomalies", [])
            }
        )
        
        return result
    
    def _validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Basic audio file validation (simplified)"""
        try:
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            file_type = "audio/mpeg"  # Simplified for demo
            
            return {
                "file_size": file_size,
                "mime_type": file_type,
                "format": "mp3",
                "is_valid": True,
                "loadable": True
            }
        except Exception as e:
            return {
                "file_size": 0,
                "is_valid": False,
                "loadable": False,
                "error": str(e)
            }
    
    def _analyze_audio_properties(self, file_path: str) -> Dict[str, Any]:
        """Analyze basic audio properties (simplified)"""
        try:
            file_stats = os.stat(file_path)
            return {
                "duration": 30.0,  # Simulated duration
                "sample_rate": 44100,
                "channels": 2,
                "frames": 1323000,
                "format": "MP3",
                "subtype": "MP3"
            }
        except Exception as e:
            return {
                "error": str(e),
                "analysis_failed": True
            }
    
    def _analyze_speech_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze speech content (simplified)"""
        try:
            # Simplified speech analysis for demo
            return {
                "transcript": "[Speech recognition would require additional setup]",
                "confidence": 75,
                "word_count": 0,
                "has_speech": True
            }
        except Exception as e:
            return {
                "transcript": "",
                "confidence": 0,
                "error": str(e),
                "has_speech": False
            }
    
    def _analyze_acoustic_features(self, file_path: str) -> Dict[str, Any]:
        """Analyze acoustic features for anomalies (simplified)"""
        try:
            # Simplified acoustic analysis for demo
            return {
                "anomalies": [],
                "silence_ratio": 0.1,
                "estimated_tempo": 120.0,
                "analysis_successful": True
            }
        except Exception as e:
            return {
                "anomalies": ["ANALYSIS_FAILED"],
                "error": str(e),
                "analysis_successful": False
            }
    
    def _moderate_audio_content(self, transcript: str) -> Dict[str, Any]:
        """Moderate audio content based on transcript"""
        if not transcript:
            return {
                "flags": [],
                "risk_score": 0,
                "prohibited_matches": []
            }
        
        transcript_lower = transcript.lower()
        flags = []
        prohibited_matches = []
        
        # Check for prohibited content
        for prohibited_word in self.prohibited_content:
            if prohibited_word in transcript_lower:
                flags.append(f"PROHIBITED_CONTENT_{prohibited_word.upper()}")
                prohibited_matches.append(prohibited_word)
        
        # Check for excessive profanity (basic)
        profanity_count = transcript_lower.count("damn") + transcript_lower.count("hell")
        if profanity_count > 5:
            flags.append("EXCESSIVE_PROFANITY")
        
        # Calculate risk score
        risk_score = min(len(flags) * 20, 100)
        
        return {
            "flags": flags,
            "risk_score": risk_score,
            "prohibited_matches": prohibited_matches,
            "word_count": len(transcript.split())
        }
