import os
import json
import tempfile
from src.file_watcher import TickerFileHandler
from typing import Optional

class DummyCallback:
	"""
	Dummy callback to capture ticker symbol for testing.
	"""
	def __init__(self):
		self.ticker: Optional[str] = None
	def __call__(self, ticker: str) -> None:
		self.ticker = ticker

def test_file_watcher_detects_ticker() -> None:
	"""
	Test that TickerFileHandler detects ticker in a new JSON file.
	"""
	callback = DummyCallback()
	handler = TickerFileHandler(callback)
	with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as tmp:
		json.dump({'ticker': 'AAPL'}, tmp)
		tmp_path = tmp.name
	class Event:
		def __init__(self, src_path: str):
			self.src_path = src_path
			self.is_directory = False
	event = Event(tmp_path)
	handler.on_created(event)
	os.unlink(tmp_path)
	assert callback.ticker == 'AAPL'
