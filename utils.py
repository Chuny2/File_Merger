import os
import heapq
import tempfile
from PyQt6.QtCore import QObject

def external_sort_deduplicate(input_files, output_file, progress_callback=None, active_check=None, chunk_size=64 * 1024 * 1024):
    """
    Deduplicates and merges multiple text files using External Sort-Merge algorithm.
    This ensures minimal RAM usage (approx. chunk_size) even for massive files.
    """
    temp_files = []
    
    try:
        # Step 1: Split and Sort Phase
        total_size = sum(os.path.getsize(f) for f in input_files)
        processed_size = 0
        
        for input_path in input_files:
            if active_check and not active_check():
                return False
                
            with open(input_path, 'rb') as f:
                while True:
                    if active_check and not active_check():
                        return False
                        
                    lines = f.readlines(chunk_size)
                    if not lines:
                        break
                        
                    # Normalize lines (ensure they end with \n) before sorting for consistent deduplication
                    lines = [line.rstrip(b'\r\n') + b'\n' for line in lines]
                    
                    # Sort lines in memory
                    lines.sort()
                    
                    # Store sorted run in a temporary file
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
                    # Remove duplicates in-memory for this chunk to reduce disk usage
                    last_line = None
                    for line in lines:
                        if line != last_line:
                            tmp.write(line)
                            last_line = line
                    
                    tmp.close()
                    temp_files.append(tmp.name)
                    
                    processed_size += sum(len(line) for line in lines)
                    if progress_callback:
                        # Report up to 50% for this phase
                        progress = int((processed_size * 50) / total_size) if total_size > 0 else 50
                        progress_callback(min(progress, 50))
        
        # Step 2: Merge Phase
        if active_check and not active_check():
            return False
            
        # Open all temp files
        opened_temps = [open(name, 'rb') for name in temp_files]
        try:
            # Use heapq.merge to lazily merge all sorted files
            merged_iter = heapq.merge(*opened_temps)
            
            with open(output_file, 'wb') as out_f:
                last_written_line = None
                for line in merged_iter:
                    if active_check and not active_check():
                        return False
                        
                    if line != last_written_line:
                        out_f.write(line)
                        last_written_line = line
                    
                    # We can't easily track exact progress here without more complexity,
                    # so we just move from 50% to 100%.
                    # Simplified progress reporting for merge phase.
        finally:
            for f in opened_temps:
                f.close()
                
        if progress_callback:
            progress_callback(100)
            
        return True
        
    finally:
        # Cleanup temporary files
        for name in temp_files:
            try:
                if os.path.exists(name):
                    os.remove(name)
            except:
                pass
