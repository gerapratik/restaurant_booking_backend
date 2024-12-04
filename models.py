from pydantic import BaseModel, validator

from typing import List
from datetime import datetime

import uuid

class Restaurant(BaseModel):
    id: str
    name: str
    city: str
    area: str
    cuisine: str
    rating: float
    cost_for_two: float
    is_veg: bool
    slots: List['Slot'] = []

    @validator('slots')
    def validate_slots(cls, slots, values, **kwargs):
        restaurant_id = values.get('id')
        if restaurant_id is None:
            raise ValueError('Restaurant id must be set before validating slots.')

        for slot in slots:
            if slot.restaurant_id != restaurant_id:
                raise ValueError(f"Slot's restaurant_id ({slot.restaurant_id}) must match the Restaurant's id ({restaurant_id}).")
        
        return slots

class Slot(BaseModel):
    id: str = str(uuid.uuid4())
    restaurant_id: str
    date: datetime
    hour: int
    capacity: int
    booked: int = 0
    
    @validator('hour')
    def validate_hour(cls, value):
        if not (0 <= value < 24):
            raise ValueError('Hour must be between 0 and 23.')
        return value
    @validator('date')
    def validate_date(cls, value):
        if value < datetime.now():
            raise ValueError('Date must be in the future.')
        return value
    




class Booking(BaseModel):
    id: str = str(uuid.uuid4()) 
    slot_id: str  
    number_of_people: int  

    status: str = "confirmed"


Restaurant.update_forward_refs()
