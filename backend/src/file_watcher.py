
import os
import json
import time
import logging
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TickerFileHandler(FileSystemEventHandler):
    """
    Handles creation of new JSON files in the watched directory.
    Extracts ticker from JSON files and calls the provided callback
    with the file path and ticker symbol.
    """
    def __init__(self, input_dir: str, callback: Callable[[str, str], None]):
        """
        Initialize the file handler.
        
        Args:
            input_dir (str): The input directory being watched
            callback (Callable[[str, str], None]): Function to call with (file_path, ticker)
        """
        self.input_dir = input_dir
        self.callback = callback

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
            
            logging.info(f"New ticker file detected: {event.src_path} for ticker {ticker}")
            
            # Call the callback with file path and ticker
            self.callback(event.src_path, ticker)
            
        except Exception as e:
            logging.error(f"Error processing {event.src_path}: {e}")


def watch_input_folder(folder: str, callback: Callable[[str, str], None]) -> None:
    """
    Watches the specified folder for new JSON files and processes tickers.
    
    Args:
        folder (str): Directory path to watch for new files
        callback (Callable[[str, str], None]): Function to call with (file_path, ticker)
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
