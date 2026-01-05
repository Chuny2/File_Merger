import os
from PyQt6.QtCore import QThread, pyqtSignal

class MergeThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, sources, target, cleanup=False):
        super().__init__()
        self.sources = sources
        self.target = target
        self.cleanup = cleanup
        self._active = True

    def stop(self):
        self._active = False

    def run(self):
        try:
            target_abs = os.path.abspath(self.target)
            sources_abs = [os.path.abspath(p) for p in self.sources]
            
            if target_abs in sources_abs:
                raise ValueError("Target file cannot be one of the source files.")

            total_size = sum(os.path.getsize(f) for f in self.sources)
            processed_size = 0
            last_progress = -1
            
            with open(self.target, 'wb') as outfile:
                for src in self.sources:
                    if not self._active:
                        break
                        
                    with open(src, 'rb') as infile:
                        while self._active:
                            chunk = infile.read(1024 * 1024)
                            if not chunk:
                                break
                            outfile.write(chunk)
                            
                            processed_size += len(chunk)
                            
                            progress = int((processed_size * 100) / total_size) if total_size > 0 else 100

                            if progress != last_progress:
                                self.progress.emit(progress)
                                last_progress = progress
                        


            if not self._active:
                if os.path.exists(self.target):
                    try:
                        os.remove(self.target)
                    except:
                        pass
                self.finished.emit(False, "Merging cancelled by user.")
                return
            
            if self.cleanup:
                for src in self.sources:
                    try:
                        os.remove(src)
                    except OSError as e:
                        print(f"Warning: Could not delete {src}: {e}")
            
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))