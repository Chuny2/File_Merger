
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
            total_size = sum(os.path.getsize(f) for f in self.sources)
            processed_size = 0
            last_progress = -1
            
            for src in self.sources:
                if not self._active:
                    break
                
                # Use a hidden temp file in the same directory for safety
                target = src + ".tmp"
                
                seen_lines = set()
                try:
                    with open(src, 'rb') as infile, open(target, 'wb') as outfile:
                        for line in infile:
                            if not self._active:
                                break
                            
                            stripped_line = line.rstrip(b'\r\n')
                            if stripped_line not in seen_lines:
                                outfile.write(stripped_line + b'\n')
                                seen_lines.add(stripped_line)
                            
                            processed_size += len(line)
                            progress = int((processed_size * 100) / total_size) if total_size > 0 else 100
                            if progress != last_progress:
                                self.progress.emit(progress)
                                last_progress = progress
                    
                    if self._active:
                        # Success: Swap temp file for original
                        os.remove(src)
                        os.rename(target, src)
                    else:
                        # Cancelled: Remove partial temp file
                        if os.path.exists(target):
                            os.remove(target)
                except Exception as file_error:
                    if os.path.exists(target):
                        os.remove(target)
                    raise file_error
            
            if self._active:
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, "Deduplication cancelled by user.")
                
        except Exception as e:
            self.finished.emit(False, str(e))
