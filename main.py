

import sys
from PyQt6.QtWidgets import QApplication
from main_window import FileMergerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileMergerApp()
    window.show()
    sys.exit(app.exec())