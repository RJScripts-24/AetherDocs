import os
import shutil
from uuid import uuid4
from app.core.config import settings

class LocalStorage:
    def create_temp_dir(self):
        dir_path = os.path.join(settings.TMP_DIR, str(uuid4()))
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def cleanup(self, path):
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
