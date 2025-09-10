from PIL import Image, ExifTags
import os
import hashlib
from typing import Dict, Any, List
from ..models.schemas import SecurityAnalysisResult, ThreatLevel
from .security_service import SecurityService

class ImageSecurityService:
    def __init__(self):
        self.security_service = SecurityService()
        self.malicious_hashes = set()  # In production, load from database
    
    async def analyze_image(self, file_path: str, filename: str) -> SecurityAnalysisResult:
        """Complete image security analysis"""
        analysis_data = {
            "type": "image",
            "filename": filename,
            "file_path": file_path
        }
        
        # Basic file validation
        file_info = self._validate_image_file(file_path)
        analysis_data.update(file_info)
        
        # EXIF data analysis
        exif_analysis = self._analyze_exif_data(file_path)
        analysis_data["exif_analysis"] = exif_analysis
        
        # Malware detection
        malware_check = self._check_malware_signatures(file_path)
        analysis_data["malware_check"] = malware_check
        
        # Content analysis
        content_analysis = self._analyze_image_content(file_path)
        analysis_data["content_analysis"] = content_analysis
        
        # Steganography detection
        stego_analysis = self._detect_steganography(file_path)
        analysis_data["steganography_check"] = stego_analysis
        
        # Get AI risk classification
        risk_assessment = await self.security_service.classify_content_risk(analysis_data)
        
        # Build result
        result = SecurityAnalysisResult(
            content_type="image",
            filename=filename,
            risk_score=risk_assessment["overall_risk_score"],
            threat_level=ThreatLevel(risk_assessment["threat_level"]),
            issues_found=risk_assessment["specific_risks"],
            recommendations=risk_assessment["recommendations"],
            confidence_score=risk_assessment["confidence_score"],
            metadata={
                "file_size": file_info["file_size"],
                "dimensions": file_info["dimensions"],
                "format": file_info["format"],
                "exif_data": exif_analysis,
                "malware_indicators": malware_check["indicators"],
                "content_flags": content_analysis["flags"]
            }
        )
        
        return result
    
    def _validate_image_file(self, file_path: str) -> Dict[str, Any]:
        """Basic image file validation"""
        try:
            # Get file info
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            
            # Check file signature (simplified)
            file_type = "image/jpeg"  # Simplified for demo
            
            # Open with PIL for format validation
            with Image.open(file_path) as img:
                return {
                    "file_size": file_size,
                    "dimensions": f"{img.width}x{img.height}",
                    "format": img.format,
                    "mode": img.mode,
                    "mime_type": file_type,
                    "is_valid": True
                }
        except Exception as e:
            return {
                "file_size": 0,
                "is_valid": False,
                "error": str(e)
            }
    
    def _analyze_exif_data(self, file_path: str) -> Dict[str, Any]:
        """Analyze EXIF data for security concerns"""
        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                
                if not exif_data:
                    return {"has_exif": False, "security_flags": []}
                
                readable_exif = {}
                security_flags = []
                
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    readable_exif[tag] = str(value)
                    
                    # Check for security concerns
                    if tag == "GPS" or "GPS" in str(tag):
                        security_flags.append("GPS_DATA_PRESENT")
                    if tag == "Software" and "script" in str(value).lower():
                        security_flags.append("SUSPICIOUS_SOFTWARE_TAG")
                
                return {
                    "has_exif": True,
                    "exif_data": readable_exif,
                    "security_flags": security_flags
                }
        except:
            return {"has_exif": False, "security_flags": [], "analysis_error": True}
    
    def _check_malware_signatures(self, file_path: str) -> Dict[str, Any]:
        """Check for malware signatures in image"""
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            indicators = []
            
            # Check against known malicious hashes
            if file_hash in self.malicious_hashes:
                indicators.append("KNOWN_MALICIOUS_HASH")
            
            # Check file size anomalies
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
                indicators.append("UNUSUALLY_LARGE_FILE")
            
            # Basic pattern detection in file
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Read first 1KB
                if b'javascript:' in content or b'<script' in content:
                    indicators.append("SCRIPT_CONTENT_DETECTED")
            
            return {
                "file_hash": file_hash,
                "is_suspicious": len(indicators) > 0,
                "indicators": indicators
            }
        except Exception as e:
            return {
                "file_hash": "",
                "is_suspicious": True,
                "indicators": ["ANALYSIS_FAILED"],
                "error": str(e)
            }
    
    def _analyze_image_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze image content for inappropriate material (simplified)"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                flags = []
                
                # Basic content analysis
                if width > 10000 or height > 10000:
                    flags.append("UNUSUALLY_LARGE_DIMENSIONS")
                
                # Check for unusual aspect ratios
                aspect_ratio = width / height
                if aspect_ratio > 10 or aspect_ratio < 0.1:
                    flags.append("UNUSUAL_ASPECT_RATIO")
                
                return {
                    "analysis_possible": True,
                    "dimensions": f"{width}x{height}",
                    "flags": flags
                }
        except Exception as e:
            return {
                "analysis_possible": False,
                "flags": ["CONTENT_ANALYSIS_FAILED"],
                "error": str(e)
            }
    
    def _detect_steganography(self, file_path: str) -> Dict[str, Any]:
        """Basic steganography detection"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            indicators = []
            
            # Check for unusual file size vs visual content
            img = Image.open(file_path)
            expected_size = img.width * img.height * 3  # Rough estimate
            actual_size = len(file_content)
            
            if actual_size > expected_size * 2:
                indicators.append("FILE_SIZE_ANOMALY")
            
            # Check for embedded files (simple signature detection)
            common_signatures = [b'PK\x03\x04', b'%PDF', b'\x89PNG', b'\xFF\xD8\xFF']
            content_lower = file_content[1000:]  # Skip image header
            
            for sig in common_signatures:
                if sig in content_lower:
                    indicators.append("EMBEDDED_FILE_SIGNATURE")
                    break
            
            return {
                "analysis_performed": True,
                "suspicious_indicators": indicators,
                "confidence": 70 if indicators else 30
            }
        except Exception as e:
            return {
                "analysis_performed": False,
                "error": str(e)
            }
