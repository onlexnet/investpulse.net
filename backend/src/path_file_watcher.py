"""
Path-based file watcher for ticker files.

This module provides an updated version of the file watcher that uses
pathlib.Path objects instead of raw string paths.
"""

import json
import logging
from pathlib import Path
from typing import Callable

from .path_event_handler import PathFileSystemEventHandler, PathFileSystemEvent


class PathTickerFileHandler(PathFileSystemEventHandler):
    """
    Handles creation of new JSON files in the watched directory using Path objects.
    
    This is an updated version of TickerFileHandler that uses pathlib.Path
    objects instead of string paths for better path manipulation and type safety.
    """
    
    def __init__(self, input_dir: Path, callback: Callable[[Path, str], None]):
        """
        Initialize the file handler.
        
        Args:
            input_dir (Path): The input directory being watched
            callback (Callable[[Path, str], None]): Function to call with (file_path, ticker)
        """
        self.input_dir = input_dir if isinstance(input_dir, Path) else Path(input_dir)
        self.callback = callback

    def on_created(self, event: PathFileSystemEvent) -> None:
        """
        Handle file creation events.
        
        Args:
            event (PathFileSystemEvent): File system event object with Path objects
        """
        # Skip directories and non-JSON files
        if event.is_directory or event.src_path.suffix != '.json':
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
            
            # Call the callback with Path object and ticker
            self.callback(event.src_path, ticker)
            
        except Exception as e:
            logging.error(f"Error processing {event.src_path}: {e}")