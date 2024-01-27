from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class TicketModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    passenger_name: str
    passport: str
    id_airplane: int
    direction: str