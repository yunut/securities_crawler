import inspect
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.util.common import print_with_newline


@dataclass(init=True)
class PosSchedule:
    id: str
    pos_name: str
    pos_start_date: datetime
    pos_end_date: datetime
    pos_confirmed_price: Optional[int]
    pos_desired_min_price: int
    pos_desired_max_price: int
    pos_competition_rate: Optional[Decimal]
    pos_taken_company: str

    @classmethod
    def from_dict(cls, env):
        return cls(**{k: v for k, v in env.items() if k in inspect.signature(cls).parameters})

    def __repr__(self):
        return print_with_newline(self, cur_indent="")
