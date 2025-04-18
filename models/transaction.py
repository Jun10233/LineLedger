from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    amount: float
    category: str
    note: str
    date: datetime
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    id: Optional[int] = None
