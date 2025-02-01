from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Task:
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    progress: float
    parent_id: Optional[int]
    dependencies: List[int]
    resources: List[str]
    
@dataclass
class Resource:
    id: int
    name: str
    role: str
    cost_per_hour: float
    availability: float  # 0-1 사이의 가용성

@dataclass
class Project:
    name: str
    start_date: datetime
    end_date: datetime
    tasks: List[Task]
    resources: List[Resource] 