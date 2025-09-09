
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
    Calls the provided callback with the ticker symbol if found.
    """
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
        try:
            with open(event.src_path, 'r') as f:
                data = json.load(f)
            ticker = data.get('ticker')
            if ticker:
                self.callback(ticker)
        except Exception as e:
            logging.error(f"Error reading {event.src_path}: {e}")

def watch_input_folder(folder: str, callback: Callable[[str], None]) -> None:
    """
    Watches the specified folder for new JSON files and processes tickers.
    """
    event_handler = TickerFileHandler(callback)
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
