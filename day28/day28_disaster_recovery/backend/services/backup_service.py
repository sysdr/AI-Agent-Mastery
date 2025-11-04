import asyncio
import hashlib
import json
from datetime import datetime
from cryptography.fernet import Fernet
from typing import Dict, List, Optional
import aiofiles
import os
from backend.models.schemas import BackupMetadata, ComplianceTag, RegionEnum
from backend.config.settings import settings

class BackupService:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.backups: Dict[str, List[BackupMetadata]] = {
            region.value: [] for region in RegionEnum
        }
        
    async def create_snapshot(self, region: RegionEnum, data: Dict) -> BackupMetadata:
        """Create an encrypted backup snapshot"""
        # Serialize data
        data_json = json.dumps(data).encode()
        
        # Encrypt
        encrypted_data = self.cipher.encrypt(data_json)
        
        # Calculate hash
        hash_sha256 = hashlib.sha256(encrypted_data).hexdigest()
        
        # Create backup ID
        backup_id = f"backup_{region.value}_{datetime.utcnow().isoformat()}"
        
        # Compliance tags
        compliance_tags = ComplianceTag(
            data_classification="PII",
            retention_days=2555,
            encryption_required=True,
            allowed_regions=self._get_allowed_regions(region)
        )
        
        # Create metadata
        metadata = BackupMetadata(
            backup_id=backup_id,
            timestamp=datetime.utcnow(),
            region=region,
            size_bytes=len(encrypted_data),
            encrypted=True,
            compliance_tags=compliance_tags,
            hash_sha256=hash_sha256
        )
        
        # Save to disk
        backup_path = f"data/backups/{backup_id}.enc"
        async with aiofiles.open(backup_path, 'wb') as f:
            await f.write(encrypted_data)
        
        # Save metadata
        metadata_path = f"data/backups/{backup_id}_metadata.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(metadata.model_dump_json())
        
        self.backups[region.value].append(metadata)
        return metadata
    
    def _get_allowed_regions(self, region: RegionEnum) -> List[str]:
        """Get allowed regions based on sovereignty rules"""
        sovereignty_map = {
            RegionEnum.US_EAST: ["us-east", "us-west"],
            RegionEnum.EU_WEST: ["eu-west", "eu-central"],
            RegionEnum.AP_SOUTH: ["ap-south", "ap-southeast"]
        }
        return sovereignty_map.get(region, [region.value])
    
    async def continuous_backup(self, region: RegionEnum):
        """Run continuous backup loop"""
        while True:
            try:
                # Simulate agent state
                agent_data = {
                    "conversations": [
                        {"id": f"conv_{i}", "messages": f"Message data {i}"}
                        for i in range(10)
                    ],
                    "state": "active",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                metadata = await self.create_snapshot(region, agent_data)
                print(f"✓ Backup created: {metadata.backup_id} ({metadata.size_bytes} bytes)")
                
                await asyncio.sleep(settings.BACKUP_INTERVAL_SECONDS)
            except Exception as e:
                print(f"✗ Backup error: {str(e)}")
                await asyncio.sleep(5)
    
    async def restore_from_backup(self, backup_id: str) -> Dict:
        """Restore data from encrypted backup"""
        backup_path = f"data/backups/{backup_id}.enc"
        
        async with aiofiles.open(backup_path, 'rb') as f:
            encrypted_data = await f.read()
        
        # Decrypt
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        # Parse
        data = json.loads(decrypted_data.decode())
        return data
    
    def get_latest_backup(self, region: RegionEnum) -> Optional[BackupMetadata]:
        """Get the most recent backup for a region"""
        region_backups = self.backups.get(region.value, [])
        return region_backups[-1] if region_backups else None

backup_service = BackupService()
