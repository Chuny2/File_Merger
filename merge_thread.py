import os
from PyQt6.QtCore import QThread, pyqtSignal

class MergeThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, file_paths, output_file, delete_sources=False):
        super().__init__()
        self.file_paths = file_paths
        self.output_file = output_file
        self.delete_sources = delete_sources

    def run(self):
        try:
            total_files = len(self.file_paths)
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                for i, file_path in enumerate(self.file_paths):
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as infile:
                        # Stream file content in chunks to avoid memory issues with large files
                        while True:
                            chunk = infile.read(8192)  # Read 8KB chunks
                            if not chunk:
                                break
                            outfile.write(chunk)
                        # Add separator between files (except for the last one)
                        if i < total_files - 1:
                            outfile.write('\n')
                    # Pre-calculate progress percentage
                    progress_percent = int((i + 1) * 100 / total_files)
                    self.progress.emit(progress_percent)
            
            # Delete source files if requested (only after successful merge)
            if self.delete_sources:
                deleted_count = 0
                for file_path in self.file_paths:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except OSError as e:
                        # Log the error but don't fail the entire operation
                        print(f"Warning: Could not delete {file_path}: {e}")
                
                # Optional: Could emit a signal about deletion results
                # self.deletion_complete.emit(deleted_count, len(self.file_paths))
            
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))