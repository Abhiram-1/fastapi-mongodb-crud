# FastAPI MongoDB CRUD Application

This project is a RESTful API built with FastAPI and MongoDB for managing user data.

## Features

- CRUD operations for user management
- Data validation using Pydantic
- MongoDB integration
- Pagination support

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up MongoDB and update connection string if necessary
4. Run the application: `uvicorn main:app --reload`

## API Endpoints

- GET /getallusers/: Retrieve all users
- POST /adduser: Create a new user
- GET /users/{user_id}: Retrieve a specific user
- PUT /userschange/{user_id}: Update a user
- DELETE /usersdelete/{user_id}: Delete a user
- GET /getalluserspagination/: Get paginated list of users

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
