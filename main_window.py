import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QCheckBox)
from PyQt6.QtCore import Qt
from merge_thread import MergeThread
from animated_progress_bar import AnimatedProgressBar
from custom_list_widget import CustomListWidget

class FileMergerApp(QMainWindow):
    # Class constant for message box styling (avoid recreating it each time)
    MESSAGE_BOX_STYLE = """
        QMessageBox {
            background-color: #34495e;
            color: #ecf0f1;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Merger")
        self.setGeometry(100, 100, 800, 600)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                background-color: #34495e;
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2574a9;
            }
            QListWidget {
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #2c3e50;
                padding: 10px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:alternate {
                background-color: #2c3e50;
            }
            QProgressBar {
                border: none;
                background-color: #34495e;
                height: 10px;
                text-align: center;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
            }
            QCheckBox {
                color: #ecf0f1;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3498db;
                border-radius: 3px;
                background-color: #2c3e50;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #2980b9;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        title_label = QLabel("File Merger")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        layout.addWidget(title_label)

        self.file_list = CustomListWidget()
        layout.addWidget(self.file_list)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_files)
        button_layout.addWidget(self.remove_button)

        self.merge_button = QPushButton("Merge Files")
        self.merge_button.clicked.connect(self.merge_files)
        button_layout.addWidget(self.merge_button)

        # Add checkbox for deleting source files after merge
        self.delete_sources_checkbox = QCheckBox("Delete source files after merging")
        self.delete_sources_checkbox.setToolTip("Check this to delete the original files after successful merge")
        layout.addWidget(self.delete_sources_checkbox)

        self.progress_label = QLabel("Progress:")
        layout.addWidget(self.progress_label)

        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().endswith('.txt')]
        self.add_files(files)

    def add_files(self, files):
        for file in files:
            item = QListWidgetItem(os.path.basename(file))
            item.setToolTip(file)
            self.file_list.addItem(item)
        self.status_label.setText(f"{len(files)} file(s) added successfully.")

    def remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def merge_files(self):
        if self.file_list.count() == 0:
            self.show_message("Error", "No files to merge.", QMessageBox.Icon.Warning)
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Save Combined File", "", "Text File (*.txt)")
        if not output_file:
            return

        # Collect file paths efficiently
        file_paths = [self.file_list.item(i).toolTip() for i in range(self.file_list.count())]
        delete_sources = self.delete_sources_checkbox.isChecked()
        self.merge_thread = MergeThread(file_paths, output_file, delete_sources)
        self.merge_thread.progress.connect(self.update_progress)
        self.merge_thread.finished.connect(self.merge_finished)
        self.merge_thread.start()

        self.merge_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.delete_sources_checkbox.setEnabled(False)
        self.status_label.setText("Merging files...")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def merge_finished(self, success, error_message):
        self.merge_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        self.delete_sources_checkbox.setEnabled(True)

        if success:
            self.show_message("Success", "Content merged successfully.", QMessageBox.Icon.Information)
            self.status_label.setText("Merging completed successfully.")
            # Clear the file list if delete sources was checked and merge was successful
            # Check checkbox state only once and cache it
            should_clear_list = self.delete_sources_checkbox.isChecked()
            if should_clear_list:
                self.file_list.clear()
        else:
            self.show_message("Error", f"An error occurred while merging the files: {error_message}", QMessageBox.Icon.Critical)
            self.status_label.setText("Error while merging files.")

        self.progress_bar.setValue(0)

    def show_message(self, title, message, icon):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet(self.MESSAGE_BOX_STYLE)
        msg_box.exec()