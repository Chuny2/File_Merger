import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt
from merge_thread import MergeThread
from deduplication_thread import DeduplicationThread
from animated_progress_bar import AnimatedProgressBar
from custom_list_widget import CustomListWidget

class FileMergerApp(QMainWindow):
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
        self.setGeometry(100, 100, 900, 700)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                background-color: #34495e;
                color: #ecf0f1;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2574a9;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QPushButton#primaryButton {
                background-color: #2ecc71;
                font-size: 15px;
                padding: 12px 24px;
            }
            QPushButton#primaryButton:hover {
                background-color: #27ae60;
            }
            QPushButton#stopButton {
                background-color: #e74c3c;
            }
            QPushButton#stopButton:hover {
                background-color: #c0392b;
            }
            QPushButton#dangerButton {
                background-color: #d35400;
            }
            QPushButton#dangerButton:hover {
                background-color: #e67e22;
            }
            QListWidget {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                background-color: #2c3e50;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #34495e;
                color: #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #3498db;
                background-color: #2c3e50;
                height: 14px;
                text-align: center;
                border-radius: 7px;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 6px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #ecf0f1;
                margin-bottom: 5px;
            }
            QLabel#infoLabel {
                color: #bdc3c7;
                font-size: 11px;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        main_widget.setLayout(main_layout)

        # --- Header ---
        header_layout = QVBoxLayout()
        title_label = QLabel("File Merger Pro")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Combine and clean your text files with ease")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #bdc3c7; font-style: italic;")
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # --- Section 1: Source Files ---
        source_group = QGroupBox("Source Files")
        source_layout = QVBoxLayout()
        source_group.setLayout(source_layout)

        self.file_list = CustomListWidget()
        source_layout.addWidget(self.file_list)

        file_actions_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Files")
        self.add_button.clicked.connect(self.select_files)
        file_actions_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.remove_selected)
        file_actions_layout.addWidget(self.remove_button)

        file_actions_layout.addStretch()

        self.file_info_label = QLabel("0 files loaded")
        self.file_info_label.setObjectName("infoLabel")
        file_actions_layout.addWidget(self.file_info_label)
        
        source_layout.addLayout(file_actions_layout)
        main_layout.addWidget(source_group)

        # --- Section 2: Tools & Options ---
        options_row_layout = QHBoxLayout()
        
        # Tools Group
        tools_group = QGroupBox("Processing Tools")
        tools_layout = QVBoxLayout()
        tools_group.setLayout(tools_layout)
        
        self.dedup_selected_button = QPushButton("Deduplicate Selected Files")
        self.dedup_selected_button.setObjectName("dangerButton")
        self.dedup_selected_button.setEnabled(False)
        self.dedup_selected_button.setToolTip("Removes duplicate lines from each selected file individually (overwrites originals)")
        self.dedup_selected_button.clicked.connect(self.deduplicate_selected)
        tools_layout.addWidget(self.dedup_selected_button)
        
        options_row_layout.addWidget(tools_group)

        # Options Group
        merge_options_group = QGroupBox("Merge Settings")
        merge_options_layout = QVBoxLayout()
        merge_options_group.setLayout(merge_options_layout)

        self.cleanup_checkbox = QCheckBox("Delete source files after successful merge")
        merge_options_layout.addWidget(self.cleanup_checkbox)

        self.dedup_checkbox = QCheckBox("Apply global deduplication to merged result")
        merge_options_layout.addWidget(self.dedup_checkbox)
        
        options_row_layout.addWidget(merge_options_group)
        main_layout.addLayout(options_row_layout)

        # --- Section 3: Execution ---
        execution_layout = QVBoxLayout()
        
        self.merge_button = QPushButton("RUN MERGE PROCESS")
        self.merge_button.setObjectName("primaryButton")
        self.merge_button.setEnabled(False)
        self.merge_button.clicked.connect(self.merge_files)
        execution_layout.addWidget(self.merge_button)

        progress_layout = QHBoxLayout()
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        self.cancel_button = QPushButton("STOP")
        self.cancel_button.setObjectName("stopButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.stop_merging)
        self.cancel_button.setFixedWidth(80)
        progress_layout.addWidget(self.cancel_button)
        
        execution_layout.addLayout(progress_layout)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-style: italic; color: #bdc3c7; height: 20px;")
        execution_layout.addWidget(self.status_label)
        
        main_layout.addLayout(execution_layout)

        self.file_list.itemSelectionChanged.connect(self.update_button_states)
        self.active_worker = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls() 
                 if u.toLocalFile().lower().endswith('.txt')]
        self.import_files(files)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Text Files", "", "Text Files (*.txt)")
        if files:
            self.import_files(files)

    def deduplicate_selected(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        reply = QMessageBox.question(self, 'Confirm Deduplication',
                                   f"This will remove duplicate lines from {len(selected_items)} file(s) and overwrite the originals. This action cannot be undone.\n\nDo you want to proceed?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return

        sources = [item.toolTip() for item in selected_items]
        
        self.active_worker = DeduplicationThread(sources)
        self.active_worker.progress.connect(self.update_progress)
        self.active_worker.finished.connect(self.on_process_complete)
        self.active_worker.start()

        self.set_ui_processing_state(True)
        self.status_label.setText("Deduplicating selected files...")

    def import_files(self, files):
        if not files:
            return
            
        self.file_list.setUpdatesEnabled(False)
        added_count = 0
        try:
            existing_files = {self.file_list.item(i).toolTip() for i in range(self.file_list.count())}
            for file in files:
                if file in existing_files:
                    continue
                item = QListWidgetItem(os.path.basename(file))
                item.setToolTip(file)
                self.file_list.addItem(item)
                added_count += 1
        finally:
            self.file_list.setUpdatesEnabled(True)
            
        if added_count > 0:
            self.status_label.setText(f"{added_count} file(s) added.")
        
        self.update_button_states()

    def remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self.update_button_states()

    def update_button_states(self):
        count = self.file_list.count()
        selected_count = len(self.file_list.selectedItems())
        is_merging = self.cancel_button.isEnabled()

        self.merge_button.setEnabled(count > 0 and not is_merging)
        self.remove_button.setEnabled(selected_count > 0 and not is_merging)
        self.dedup_selected_button.setEnabled(selected_count > 0 and not is_merging)
        self.add_button.setEnabled(not is_merging)
        self.cleanup_checkbox.setEnabled(not is_merging)
        self.dedup_checkbox.setEnabled(not is_merging)
        
        self.file_info_label.setText(f"{count} files loaded | {selected_count} selected")

    def merge_files(self):
        if self.file_list.count() == 0:
            return

        if self.cleanup_checkbox.isChecked():
            reply = QMessageBox.question(self, 'Confirm Cleanup',
                                       "You have selected 'Delete source files after merging'. Original files will be REMOVED after a successful merge.\n\nAre you sure?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        output_file, _ = QFileDialog.getSaveFileName(self, "Save Combined File", "", "Text File (*.txt)")
        if not output_file:
            return

        sources = [self.file_list.item(i).toolTip() for i in range(self.file_list.count())]
        cleanup = self.cleanup_checkbox.isChecked()
        dedup = self.dedup_checkbox.isChecked()
        
        self.active_worker = MergeThread(sources, output_file, cleanup, dedup)
        self.active_worker.progress.connect(self.update_progress)
        self.active_worker.finished.connect(self.on_process_complete)
        self.active_worker.start()

        self.set_ui_processing_state(True)
        self.status_label.setText("Merging files...")

    def set_ui_processing_state(self, processing):
        self.cancel_button.setEnabled(processing)
        if not processing:
            self.update_button_states()

    def stop_merging(self):
        if self.active_worker and self.active_worker.isRunning():
            self.cancel_button.setEnabled(False)
            self.status_label.setText("Stopping...")
            self.active_worker.stop()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_process_complete(self, success, error_message):
        self.set_ui_processing_state(False)
        
        action = "Processing"
        if isinstance(self.active_worker, MergeThread):
            action = "Merging"
        elif isinstance(self.active_worker, DeduplicationThread):
            action = "Deduplication"

        if success:
            self.progress_bar.setValue(100)
            self.show_message("Success", f"{action} completed successfully.", QMessageBox.Icon.Information)
            self.status_label.setText(f"{action} completed successfully.")
            
            if action == "Merging" and self.cleanup_checkbox.isChecked():
                self.file_list.clear()
                self.update_button_states()
        else:
            if "cancelled" in error_message.lower():
                self.status_label.setText(f"{action} cancelled.")
            else:
                self.show_message("Error", f"An error occurred: {error_message}", QMessageBox.Icon.Critical)
                self.status_label.setText("An error occurred.")
            self.progress_bar.setValue(0)

    def closeEvent(self, event):
        if self.active_worker and self.active_worker.isRunning():
            reply = QMessageBox.question(self, 'Confirm Exit',
                                       "An operation is currently in progress. Do you want to stop and exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                       QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.active_worker.stop()
                self.active_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def show_message(self, title, message, icon):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet(self.MESSAGE_BOX_STYLE)
        msg_box.exec()