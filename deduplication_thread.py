
import os
import shutil
from PyQt6.QtCore import QThread, pyqtSignal

class DeduplicationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, sources):
        super().__init__()
        self.sources = sources
        self._active = True

    def stop(self):
        self._active = False

    def run(self):
        try:
            from utils import external_sort_deduplicate
            
            for src in self.sources:
                if not self._active:
                    break
                
                # Use a hidden temp file in the same directory for safety
                target = src + ".tmp"
                
                success = external_sort_deduplicate(
                    [src], 
                    target, 
                    progress_callback=self.progress.emit,
                    active_check=lambda: self._active
                )
                
                if success and self._active:
                    # Success: Swap temp file for original
                    os.remove(src)
                    os.rename(target, src)
                else:
                    # Cancelled or Error: Remove partial temp file
                    if os.path.exists(target):
                        os.remove(target)
                    if not self._active:
                        break
                    else:
                        raise Exception(f"An error occurred during deduplication of {src}.")
            
            if self._active:
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, "Deduplication cancelled by user.")
                
        except Exception as e:
            self.finished.emit(False, str(e))
