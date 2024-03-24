from dataclasses import dataclass
from datetime import datetime
from typing import Callable, TypeAlias


@dataclass
class TimeTick:
    now: datetime
    correlation_id: str

Sender: TypeAlias = Callable[[TimeTick], None]

