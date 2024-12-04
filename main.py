from models import Restaurant, Slot, Booking
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

restaurants = {}
slots = {}
bookings = {}
locks = set()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Restaurant Booking System!"}


@app.post("/restaurants")
async def create_restaurant(restaurant: Restaurant):
    if restaurant.id in restaurants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant with this ID already exists"
        )
    
    restaurant_slots = []
    for slot in restaurant.slots:
        if slot.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slot's restaurant_id ({slot.restaurant_id}) must match the restaurant ID ({restaurant.id})"
            )

        existing_slot = next(
            (s for s in restaurant_slots if s.date == slot.date and s.hour == slot.hour),
            None
        )
        if existing_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot already exists at this date and hour for the restaurant"
            )
        
        if slot.id in slots:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slot with ID {slot.id} already exists"
            )
        
        slots[slot.id] = slot
        restaurant_slots.append(slot)
    
    restaurant.slots = restaurant_slots
    restaurants[restaurant.id] = restaurant

    return restaurant


@app.post("/restaurants/{restaurant_id}/slots")
async def add_slot(restaurant_id: str, slot: Slot):
    if restaurant_id not in restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    if slot.restaurant_id != restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slot's restaurant_id ({slot.restaurant_id}) must match the provided restaurant_id ({restaurant_id})"
        )
    
    existing_slot = next((s for s in restaurants[restaurant_id].slots if s.date == slot.date and s.hour == slot.hour), None)
    if existing_slot:
        raise HTTPException(status_code=400, detail="Slot already exists at this date and hour for the restaurant")

    if slot.id in slots:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot with this ID already exists")

    slots[slot.id] = slot
    restaurants[restaurant_id].slots.append(slot)

    return slot

@app.get("/restaurants")
async def search_restaurants(
    name: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    is_veg: Optional[bool] = None
):
    results = restaurants.values()
    if name:
        results = filter(lambda r: name.lower() in r.name.lower(), results)
    if city:
        results = filter(lambda r: city.lower() in r.city.lower(), results)
    if area:
        results = filter(lambda r: area.lower() in r.area.lower(), results)
    if is_veg is not None:
        results = filter(lambda r: r["is_veg"] == True, results)
    return list(results)

@app.get("/restaurants/{restaurant_id}/slots")
async def get_slots_for_restaurant(restaurant_id: str):
    if restaurant_id not in restaurants:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return [slot for slot in slots.values() if slot.restaurant_id == restaurant_id]


@app.post("/bookings")
async def book_table(booking: Booking):
    slot = slots.get(booking.slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if slot.booked + booking.number_of_people > slot.capacity:
        raise HTTPException(status_code=400, detail="Not enough capacity available")
    
    slot.booked += booking.number_of_people
    bookings[booking.id] = booking
    return {"message": "Booking confirmed", "booking": booking}


@app.get("/restaurants")
async def get_all_restaurants():
    return restaurants

@app.get("/slots")
async def get_all_slots():
    return slots

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)