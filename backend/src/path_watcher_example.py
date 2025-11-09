"""
Example usage of Path-based file watcher.

This example shows how to use the new Path-based event handlers
that work with pathlib.Path objects instead of string paths.
"""

from pathlib import Path
from typing import Callable
from watchdog.observers import Observer

from .path_event_handler import PathEventHandlerAdapter
from .path_file_watcher import PathTickerFileHandler


def watch_input_folder_with_paths(folder: Path, callback: Callable[[Path, str], None]) -> None:
    """
    Watches the specified folder for new JSON files using Path objects.
    
    Args:
        folder (Path): Directory path to watch for new files
        callback (Callable[[Path, str], None]): Function to call with (file_path, ticker)
    """
    # Create the Path-based handler
    path_handler = PathTickerFileHandler(folder, callback)
    
    # Wrap it with the adapter to work with watchdog
    event_handler = PathEventHandlerAdapter(path_handler)
    
    # Set up the observer
    observer = Observer()
    observer.schedule(event_handler, str(folder), recursive=False)
    observer.start()
    
    print(f"Watching folder: {folder}")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def example_callback(file_path: Path, ticker: str) -> None:
    """
    Example callback function that receives a Path object.
    
    Args:
        file_path (Path): Path object pointing to the ticker file
        ticker (str): The ticker symbol extracted from the file
    """
    print(f"Processing ticker {ticker} from file: {file_path}")
    print(f"File name: {file_path.name}")
    print(f"File parent directory: {file_path.parent}")
    print(f"File exists: {file_path.exists()}")
    print(f"File size: {file_path.stat().st_size} bytes")


if __name__ == "__main__":
    # Example usage with Path objects
    input_folder = Path("input/entry")
    watch_input_folder_with_paths(input_folder, example_callback)