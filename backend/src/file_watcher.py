
import os
import json
import time
import logging
import shutil
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.processing_state import ProcessingState, ProcessingStatus

class TickerFileHandler(FileSystemEventHandler):
    """
    Handles creation of new JSON files in the watched directory.
    Moves files to processing folder, creates state files, and calls 
    the provided callback with the ProcessingState object.
    """
    def __init__(self, input_dir: str, callback: Callable[[ProcessingState], None]):
        """
        Initialize the file handler.
        
        Args:
            input_dir (str): The input directory being watched
            callback (Callable[[ProcessingState], None]): Function to call with ProcessingState
        """
        self.input_dir = input_dir
        self.processing_dir = os.path.join(input_dir, "processing")
        self.callback = callback
        
        # Ensure processing directory exists
        os.makedirs(self.processing_dir, exist_ok=True)

    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event object
        """
        if event.is_directory or not event.src_path.endswith('.json'):
            return
            
        try:
            # Read and validate the JSON file
            with open(event.src_path, 'r') as f:
                data = json.load(f)
            
            ticker = data.get('ticker')
            if not ticker:
                logging.warning(f"No ticker found in {event.src_path}")
                return
            
            # Create ProcessingState
            processing_state = ProcessingState(
                ticker=ticker,
                original_file_path=event.src_path
            )
            
            # Move file to processing directory
            filename = os.path.basename(event.src_path)
            processing_file_path = os.path.join(self.processing_dir, filename)
            shutil.move(event.src_path, processing_file_path)
            
            processing_state.processing_file_path = processing_file_path
            processing_state.update_status(ProcessingStatus.MOVED_TO_PROCESSING)
            
            # Create state file path (ticker-name.state.json)
            base_name = os.path.splitext(filename)[0]  # Remove .json extension
            state_filename = f"{base_name}.state.json"
            state_file_path = os.path.join(self.processing_dir, state_filename)
            processing_state.state_file_path = state_file_path
            
            # Save initial state
            processing_state.save_to_file()
            
            logging.info(f"Moved {filename} to processing and created state file")
            
            # Call the callback with ProcessingState
            self.callback(processing_state)
            
        except Exception as e:
            logging.error(f"Error processing {event.src_path}: {e}")
            # If we have a processing state, mark it as error
            try:
                if 'processing_state' in locals():
                    processing_state.update_status(ProcessingStatus.ERROR, str(e))
                    processing_state.save_to_file()
            except Exception as save_error:
                logging.error(f"Failed to save error state: {save_error}")

def watch_input_folder(folder: str, callback: Callable[[ProcessingState], None]) -> None:
    """
    Watches the specified folder for new JSON files and processes tickers.
    
    Args:
        folder (str): Directory path to watch for new files
        callback (Callable[[ProcessingState], None]): Function to call with ProcessingState
    """
    event_handler = TickerFileHandler(folder, callback)
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    print(f"Watching folder: {folder}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
