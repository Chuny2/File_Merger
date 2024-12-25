from PyQt6.QtCore import QThread, pyqtSignal

class MergeThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, file_paths, output_file):
        super().__init__()
        self.file_paths = file_paths
        self.output_file = output_file

    def run(self):
        try:
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                for i, file_path in enumerate(self.file_paths):
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n')
                    self.progress.emit(int((i + 1) / len(self.file_paths) * 100))
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))