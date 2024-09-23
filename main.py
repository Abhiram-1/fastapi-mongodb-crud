from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
import uvicorn
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
import re
from enum import Enum

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['local']
collection = db['test']

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    address: str
    gender: Gender
    phone_number: str

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('phone_number')
    def phone_number_validation(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[Gender] = None
    phone_number: Optional[str] = None

    @field_validator('password', 'phone_number', mode='before')
    def validate_optional_fields(cls, v, info):
        if v is None:
            return v
        field_name = info.field_name
        if field_name == 'password':
            return UserBase.password_strength(v)
        elif field_name == 'phone_number':
            return UserBase.phone_number_validation(v)
        return v

@app.get("/getallusers/")
async def get_all_users():
    users = []
    for user in collection.find():
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@app.post("/adduser")
async def create_user(user: UserCreate):
    user_dict = user.model_dump()
    user_id = collection.insert_one(user_dict).inserted_id
    return {"message": "User created", "user_id": str(user_id)}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = collection.find_one({"_id": user_id})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/userschange/{user_id}")
async def update_user(user_id: str, user: UserUpdate):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    updated_data = {k: v for k, v in user.model_dump().items() if v is not None}

    result = collection.update_one({"_id": user_id}, {"$set": updated_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "User updated"}

@app.put("/userschangeall/")
async def update_users(users: list[UserUpdate]):
    updated_count = 0

    for user_update in users:
        user_id = user_update.model_dump().get("_id")
        if not user_id:
            continue

        try:
            user_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        updated_data = {k: v for k, v in user_update.model_dump().items() if k != "_id" and v is not None}

        result = collection.update_one({"_id": user_id}, {"$set": updated_data})
        updated_count += result.modified_count

    if updated_count == 0:
        raise HTTPException(status_code=404, detail="No users found or no changes made")

    return {"message": f"{updated_count} users updated"}

@app.delete("/usersdelete/{user_id}")
async def delete_user(user_id: str):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = collection.delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted"}

@app.get("/getalluserspagination/")
async def get_all_users(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    users = []
    
    cursor = collection.find().skip(skip).limit(page_size)
    
    for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)

    return {
        "page": page,
        "page_size": page_size,
        "total_users": collection.count_documents({}),
        "users": users,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)