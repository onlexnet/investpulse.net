
import os
import json
import time
import shutil
import logging
from datetime import datetime
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .processing_state import ProcessingState, ProcessingStatus


class TickerFileHandler(FileSystemEventHandler):
    """
    Handles creation of new JSON files in the watched directory.
    Extracts ticker from JSON files, moves them to processing directory,
    creates state files, and calls the provided callback with ProcessingState.
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
        
        # Create processing directory if it doesn't exist
        os.makedirs(self.processing_dir, exist_ok=True)

    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event object
        """
        if event.is_directory or not str(event.src_path).endswith('.json'):
            return
            
        # Convert src_path to string to ensure compatibility
        file_path = str(event.src_path)
        
        try:
            # Read and validate the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            ticker = data.get('ticker')
            if not ticker:
                logging.warning(f"No ticker found in {file_path}")
                return
            
            logging.info(f"New ticker file detected: {file_path} for ticker {ticker}")
            
            # Create initial processing state
            processing_state = ProcessingState(
                ticker=ticker,
                original_file_path=file_path,
                status=ProcessingStatus.DISCOVERED
            )
            
            # Move file to processing directory
            filename = os.path.basename(file_path)
            processing_file_path = os.path.join(self.processing_dir, filename)
            shutil.move(file_path, processing_file_path)
            
            # Update state with new paths
            processing_state.processing_file_path = processing_file_path
            processing_state.status = ProcessingStatus.MOVED_TO_PROCESSING
            processing_state.updated_at = datetime.now()
            
            # Create state file path
            base_name = os.path.splitext(filename)[0]  # Remove .json extension
            state_filename = f"{base_name}.state.json"
            state_file_path = os.path.join(self.processing_dir, state_filename)
            processing_state.state_file_path = state_file_path
            
            # Save state to file
            with open(state_file_path, 'w') as f:
                json.dump(processing_state.to_dict(), f, indent=2)
            
            # Call the callback with ProcessingState
            self.callback(processing_state)
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")


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
