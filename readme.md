# File Merger

**File Merger** is a simple program used to combine multiple text files into one. It is ideal for tasks such as merging combo lists or processing datasets.

---

## Features
- **Drag-and-drop support** for adding files.
- Merge multiple text files into a **single output file**.
- Displays progress with an **animated progress bar**.
- Allows **removing selected files** before merging.
- **User-friendly and responsive interface** with PyQt6.

---

## Requirements
- **Python 3.10 or higher**
- **PyQt6**

---

## Installation
```bash
pip install PyQt6
```

---

## Usage
1. **Run the application:**
```bash
python main.py
```
2. **Drag and drop text files** into the application.
3. Click **Merge Files** to combine the selected files.
4. **Choose a destination** to save the merged file.

---

## File Structure
- **main.py**: Entry point for launching the application.
- **main_window.py**: Main GUI application logic.
- **merge_thread.py**: Handles file merging in a background thread.
- **animated_progress_bar.py**: Custom animated progress bar widget.
- **custom_list_widget.py**: Custom list widget with drag-and-drop support.

---

![App Screenshot](image.png)


