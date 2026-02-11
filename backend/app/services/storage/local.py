import shutil
import logging
from pathlib import Path
from typing import List, Optional, Union
from uuid import UUID
from fastapi import UploadFile

from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)

class LocalStorageManager:
    """
    Manages the ephemeral file system for AetherDocs.
    
    Structure:
    /tmp/aether_docs/
        └── {session_uuid}/
            ├── uploads/      # Raw user files (PDFs, MP4s)
            ├── processed/    # Transcripts (JSON), Extracted Images
            └── artifacts/    # The Final "Common Book" (PDF)
    """

    def __init__(self):
        # Base path usually /tmp/aether_workspace
        self.base_root = Path(settings.TEMP_DIR)
        self.base_root.mkdir(parents=True, exist_ok=True)

    def _get_session_dir(self, session_id: UUID) -> Path:
        return self.base_root / str(session_id)

    def initialize_session(self, session_id: UUID) -> Path:
        """
        Creates the isolated directory structure for a new session.
        """
        session_dir = self._get_session_dir(session_id)
        
        # Create sub-directories
        (session_dir / "uploads").mkdir(parents=True, exist_ok=True)
        (session_dir / "processed").mkdir(parents=True, exist_ok=True)
        (session_dir / "artifacts").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[{session_id}] Workspace initialized at {session_dir}")
        return session_dir

    async def save_upload(self, session_id: UUID, file: UploadFile) -> Path:
        """
        Stream-writes an uploaded file to the session's upload directory.
        """
        session_dir = self._get_session_dir(session_id)
        if not session_dir.exists():
            # Auto-heal if session dir missing (rare race condition)
            self.initialize_session(session_id)

        target_path = session_dir / "uploads" / file.filename

        try:
            # Ensure we start from the beginning
            await file.seek(0)
            
            with open(target_path, "wb") as buffer:
                # Read in chunks to avoid memory spikes with large videos
                while content := await file.read(1024 * 1024):  # 1MB chunks
                    buffer.write(content)
            
            # Verify file integrity
            file_size = target_path.stat().st_size
            if file_size == 0:
                target_path.unlink() # Delete 0-byte file
                logger.warning(f"[{session_id}] Uploaded file {file.filename} was empty.")
                raise ValueError(f"File {file.filename} is empty (0 bytes).")
            
            logger.info(f"[{session_id}] File saved: {file.filename} ({round(file_size / (1024 * 1024), 2)} MB)")
            return target_path
            
        except Exception as e:
            logger.error(f"[{session_id}] Failed to save upload {file.filename}: {e}")
            if "empty" in str(e):
                raise e # Propagate ValueError
            raise IOError(f"Could not save file {file.filename}")

    def get_path(self, session_id: UUID, filename: str, folder: str = "uploads") -> Optional[Path]:
        """
        Retreives the absolute path of a file if it exists.
        Protection against directory traversal is implicit via pathlib.
        """
        target = self._get_session_dir(session_id) / folder / filename
        return target if target.exists() else None

    def list_files(self, session_id: UUID, folder: str = "uploads") -> List[Path]:
        """
        Lists all files in a specific subfolder.
        """
        target_dir = self._get_session_dir(session_id) / folder
        if not target_dir.exists():
            return []
        return list(target_dir.iterdir())

    def nuke_session(self, session_id: UUID) -> bool:
        """
        THE KILL SWITCH.
        Recursively deletes the session directory from the disk.
        """
        target_dir = self._get_session_dir(session_id)
        
        if not target_dir.exists():
            logger.warning(f"[{session_id}] Clean up requested but directory not found.")
            return False

        try:
            shutil.rmtree(target_dir)
            logger.info(f"[{session_id}] 💥 Workspace wiped successfully.")
            return True
        except Exception as e:
            logger.critical(f"[{session_id}] FAILED TO WIPE DATA: {e}")
            # In a real security context, you might raise an alert here
            return False