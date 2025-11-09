"""
Path-based event handler wrapper for watchdog events.

This module provides a wrapper around watchdog's FileSystemEventHandler
that converts src_path and dest_path from bytes|str to pathlib.Path objects.
"""

import os
from pathlib import Path
from typing import Callable, Optional
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from dataclasses import dataclass, field


@dataclass(unsafe_hash=True)
class PathFileSystemEvent:
    """
    Immutable type that represents a file system event with Path objects.
    
    This is similar to FileSystemEvent but uses pathlib.Path for paths
    instead of bytes | str.
    """
    
    src_path: Path
    dest_path: Optional[Path] = None
    event_type: str = field(default="", init=False)
    is_directory: bool = field(default=False, init=False)
    is_synthetic: bool = field(default=False)
    
    @classmethod
    def from_watchdog_event(cls, event: FileSystemEvent) -> 'PathFileSystemEvent':
        """
        Convert a watchdog FileSystemEvent to PathFileSystemEvent.
        
        Args:
            event (FileSystemEvent): Original watchdog event
            
        Returns:
            PathFileSystemEvent: Event with Path objects
        """
        # Convert src_path to Path using os.fsdecode to handle bytes/str properly
        src_path = Path(os.fsdecode(event.src_path))
        
        # Convert dest_path to Path if it exists
        dest_path = None
        if hasattr(event, 'dest_path') and event.dest_path:
            dest_path = Path(os.fsdecode(event.dest_path))
        
        # Create new event with Path objects
        path_event = cls(
            src_path=src_path,
            dest_path=dest_path,
            is_synthetic=getattr(event, 'is_synthetic', False)
        )
        
        # Set the derived fields from original event
        path_event.event_type = event.event_type
        path_event.is_directory = event.is_directory
        
        return path_event


class PathFileSystemEventHandler:
    """
    Base path-based file system event handler.
    
    This class wraps the watchdog FileSystemEventHandler and converts
    all events to use pathlib.Path objects instead of str/bytes.
    """
    
    def dispatch(self, event: PathFileSystemEvent) -> None:
        """
        Dispatches events to the appropriate methods.
        
        Args:
            event (PathFileSystemEvent): The event with Path objects
        """
        self.on_any_event(event)
        method_name = f"on_{event.event_type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(event)
    
    def on_any_event(self, event: PathFileSystemEvent) -> None:
        """
        Catch-all event handler.
        
        Args:
            event (PathFileSystemEvent): The event object with Path objects
        """
        pass
    
    def on_moved(self, event: PathFileSystemEvent) -> None:
        """
        Called when a file or a directory is moved or renamed.
        
        Args:
            event (PathFileSystemEvent): Event representing file/directory movement
        """
        pass
    
    def on_created(self, event: PathFileSystemEvent) -> None:
        """
        Called when a file or directory is created.
        
        Args:
            event (PathFileSystemEvent): Event representing file/directory creation
        """
        pass
    
    def on_deleted(self, event: PathFileSystemEvent) -> None:
        """
        Called when a file or directory is deleted.
        
        Args:
            event (PathFileSystemEvent): Event representing file/directory deletion
        """
        pass
    
    def on_modified(self, event: PathFileSystemEvent) -> None:
        """
        Called when a file or directory is modified.
        
        Args:
            event (PathFileSystemEvent): Event representing file/directory modification
        """
        pass
    
    def on_closed(self, event: PathFileSystemEvent) -> None:
        """
        Called when a file opened for writing is closed.
        
        Args:
            event (PathFileSystemEvent): Event representing file closing
        """
        pass
    
    def on_opened(self, event: PathFileSystemEvent) -> None:
        """
        Called when a file is opened.
        
        Args:
            event (PathFileSystemEvent): Event representing file opening
        """
        pass


class PathEventHandlerAdapter(FileSystemEventHandler):
    """
    Adapter that wraps a PathFileSystemEventHandler to work with watchdog.
    
    This class receives watchdog events, converts them to Path-based events,
    and forwards them to a PathFileSystemEventHandler.
    """
    
    def __init__(self, path_handler: PathFileSystemEventHandler):
        """
        Initialize the adapter.
        
        Args:
            path_handler (PathFileSystemEventHandler): Handler that uses Path objects
        """
        super().__init__()
        self.path_handler = path_handler
    
    def dispatch(self, event: FileSystemEvent) -> None:
        """
        Convert watchdog event to Path event and dispatch.
        
        Args:
            event (FileSystemEvent): Original watchdog event
        """
        path_event = PathFileSystemEvent.from_watchdog_event(event)
        self.path_handler.dispatch(path_event)