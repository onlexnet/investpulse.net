"""
Integration example: Using Path-based handlers with existing InvestPulse architecture.

This module demonstrates how to integrate the new Path-based event handlers
with the existing ProcessingState and StateManager architecture.
"""

from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer

try:
    # For module import
    from .path_event_handler import PathEventHandlerAdapter
    from .path_file_watcher import PathTickerFileHandler
    from .processing_state import ProcessingState, ProcessingStatus
    from .state_manager import StateManager
except ImportError:
    # For standalone execution
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from path_event_handler import PathEventHandlerAdapter
    from path_file_watcher import PathTickerFileHandler
    from processing_state import ProcessingState, ProcessingStatus
    from state_manager import StateManager


class PathInvestPulseHandler(PathTickerFileHandler):
    """
    InvestPulse-specific handler using Path objects.
    
    This handler integrates with the existing ProcessingState and StateManager
    architecture while providing the benefits of Path objects.
    """
    
    def __init__(self, input_dir: Path, state_manager: StateManager):
        """
        Initialize the InvestPulse Path handler.
        
        Args:
            input_dir (Path): Directory to watch for ticker files
            state_manager (StateManager): Manager for processing states
        """
        self.state_manager = state_manager
        super().__init__(input_dir, self._process_ticker_with_paths)
    
    def _process_ticker_with_paths(self, file_path: Path, ticker: str) -> None:
        """
        Process ticker file using Path objects.
        
        Args:
            file_path (Path): Path to the ticker file
            ticker (str): Ticker symbol extracted from file
        """
        try:
            # Check if we already have a state for this ticker
            existing_state = self.state_manager.find_state_by_ticker(ticker)
            
            if existing_state:
                print(f"State already exists for {ticker}, skipping...")
                return
            
            # Create new processing state with Path-based file paths
            processing_state = ProcessingState(
                ticker=ticker,
                original_file_path=str(file_path),  # Convert to str for compatibility
                status=ProcessingStatus.DISCOVERED
            )
            
            print(f"Created new processing state for {ticker}")
            print(f"Original file: {file_path}")
            print(f"File size: {file_path.stat().st_size} bytes")
            print(f"Parent directory: {file_path.parent}")
            
            # Save the initial state
            self.state_manager.save_state(processing_state)
            
            # Demonstrate Path benefits for processing directory setup
            processing_dir = file_path.parent.parent / "processing"
            processing_dir.mkdir(exist_ok=True)
            
            # Easy path construction for processing file
            processing_file_path = processing_dir / file_path.name
            
            print(f"Will move to: {processing_file_path}")
            
            # You could continue with the processing workflow here...
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


def start_path_based_monitoring(config: Dict[str, Any]) -> None:
    """
    Start file monitoring using Path-based handlers.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
    """
    # Convert string paths to Path objects
    input_dir = Path(config.get('input_dir', 'input/entry'))
    state_dir = Path(config.get('state_dir', 'input/processing'))
    
    # Ensure directories exist
    input_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    
    # Create state manager
    state_manager = StateManager(str(state_dir))  # StateManager still expects string
    
    # Create Path-based handler
    path_handler = PathInvestPulseHandler(input_dir, state_manager)
    
    # Wrap with adapter for watchdog compatibility
    event_handler = PathEventHandlerAdapter(path_handler)
    
    # Set up observer
    observer = Observer()
    observer.schedule(event_handler, str(input_dir), recursive=False)
    observer.start()
    
    print(f"Path-based monitoring started for: {input_dir}")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Monitoring stopped.")
    
    observer.join()


def demonstrate_path_benefits() -> None:
    """
    Demonstrate the benefits of using Path objects in the InvestPulse context.
    """
    # Sample ticker file path
    ticker_file = Path("input/entry/aapl.json")
    
    print("=== Path Object Benefits for InvestPulse ===")
    
    # 1. Easy path construction for related files
    print("\n1. Related file path construction:")
    state_file = ticker_file.with_suffix('.state.json')
    processing_file = ticker_file.parent.parent / "processing" / ticker_file.name
    backup_file = ticker_file.parent / "backup" / f"backup_{ticker_file.name}"
    
    print(f"Original:    {ticker_file}")
    print(f"State file:  {state_file}")
    print(f"Processing:  {processing_file}")
    print(f"Backup:      {backup_file}")
    
    # 2. Easy directory structure navigation
    print("\n2. Directory structure navigation:")
    print(f"Filename:    {ticker_file.name}")
    print(f"Stem (AAPL): {ticker_file.stem}")
    print(f"Extension:   {ticker_file.suffix}")
    print(f"Parent dir:  {ticker_file.parent}")
    print(f"Grandparent: {ticker_file.parent.parent}")
    
    # 3. Easy SEC filing path construction
    print("\n3. SEC filing path construction:")
    sec_base = Path("sec-edgar-filings")
    ticker = ticker_file.stem.upper()
    filing_path = sec_base / ticker / "10-Q" / "full-submission.txt"
    print(f"SEC filing:  {filing_path}")
    
    # 4. Easy output path construction
    print("\n4. Output path construction:")
    output_base = Path("output")
    parquet_file = output_base / f"{ticker_file.stem}_facts.parquet"
    print(f"Parquet:     {parquet_file}")
    
    # 5. Cross-platform compatibility
    print("\n5. Cross-platform path handling:")
    relative_path = ticker_file.relative_to(Path("input"))
    print(f"Relative:    {relative_path}")
    print(f"Parts:       {relative_path.parts}")


if __name__ == "__main__":
    # Demonstrate benefits
    demonstrate_path_benefits()
    
    # Example configuration
    config = {
        'input_dir': 'input/entry',
        'state_dir': 'input/processing',
        'processing_dir': 'input/processing',
        'sec_filings_dir': 'sec-edgar-filings',
        'output_dir': 'output'
    }
    
    # Start monitoring (commented out for safety)
    # start_path_based_monitoring(config)