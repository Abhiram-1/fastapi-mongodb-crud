# FastAPI MongoDB CRUD Application

This project is a RESTful API built with FastAPI and MongoDB for managing user data. It provides a robust backend for user management with features like data validation, pagination, and bulk operations.

## Features

- CRUD operations for user management
- Data validation using Pydantic
- MongoDB integration
- Pagination support
- Bulk update functionality
- Gender enumeration
- Password strength validation
- Phone number format validation

## Technologies Used

- FastAPI
- MongoDB
- Pydantic
- Python 3.7+

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/fastapi-mongodb-crud.git
   cd fastapi-mongodb-crud
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up MongoDB:
   - Install and start MongoDB on your local machine
   - Update the MongoDB connection string in `main.py` if necessary

4. Run the application:
   ```
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `GET /users/`: Retrieve all users
- `POST /users/`: Create a new user
- `GET /users/{user_id}`: Retrieve a specific user by ID
- `PUT /users/{user_id}`: Update a specific user by ID
- `DELETE /users/{user_id}`: Delete a specific user by ID
- `PUT /users/bulk-update/`: Bulk update multiple users
- `GET /users/paginated/`: Get paginated list of users

## Data Models

### User Model

- `username`: string
- `email`: valid email string
- `password`: string (with strength validation)
- `first_name`: string
- `last_name`: string
- `date_of_birth`: string
- `address`: string
- `gender`: enum ("male" or "female")
- `phone_number`: string (with format validation)

## Validation

- Password must be at least 8 characters long and contain a mix of uppercase, lowercase, digits, and special characters.
- Phone number must match the format: `^\+?1?\d{9,15}$`
- Email is validated using Pydantic's EmailStr

## Pagination

The `/users/paginated/` endpoint supports pagination with the following query parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10)

## Error Handling

The API provides appropriate error responses for various scenarios:
- 400 Bad Request: For invalid input data or ID formats
- 404 Not Found: When a requested resource doesn't exist
- 422 Unprocessable Entity: For validation errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
