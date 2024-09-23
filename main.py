from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
import uvicorn
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
import re
from enum import Enum

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['user_management']
user_collection = db['users']

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
    def validate_password_strength(cls, v):
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
    def validate_phone_number(cls, v):
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
            return UserBase.validate_password_strength(v)
        elif field_name == 'phone_number':
            return UserBase.validate_phone_number(v)
        return v

@app.get("/users/")
async def get_all_users():
    users = []
    for user in user_collection.find():
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@app.post("/users/")
async def create_user(user: UserCreate):
    user_dict = user.model_dump()
    user_id = user_collection.insert_one(user_dict).inserted_id
    return {"message": "User created", "user_id": str(user_id)}

@app.get("/users/{user_id}")
async def get_user_by_id(user_id: str):
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = user_collection.find_one({"_id": user_object_id})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}")
async def update_user_by_id(user_id: str, user: UserUpdate):
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    updated_data = {k: v for k, v in user.model_dump().items() if v is not None}

    result = user_collection.update_one({"_id": user_object_id}, {"$set": updated_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "User updated successfully"}

@app.put("/users/bulk-update/")
async def bulk_update_users(users: List[UserUpdate]):
    updated_count = 0

    for user_update in users:
        user_id = user_update.model_dump().get("_id")
        if not user_id:
            continue

        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        updated_data = {k: v for k, v in user_update.model_dump().items() if k != "_id" and v is not None}

        result = user_collection.update_one({"_id": user_object_id}, {"$set": updated_data})
        updated_count += result.modified_count

    if updated_count == 0:
        raise HTTPException(status_code=404, detail="No users found or no changes made")

    return {"message": f"{updated_count} users updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user_by_id(user_id: str):
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = user_collection.delete_one({"_id": user_object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@app.get("/users/paginated/")
async def get_paginated_users(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    users = []
    
    cursor = user_collection.find().skip(skip).limit(page_size)
    
    for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)

    return {
        "page": page,
        "page_size": page_size,
        "total_users": user_collection.count_documents({}),
        "users": users,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
