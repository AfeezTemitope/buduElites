BEFA (Budu Elite Academy) User Authentication API
This documentation describes the user registration and JWT login endpoints for the BEFA mobile and web applications. The API uses Djoser with JSON Web Token (JWT) authentication.

**📌 Base URL**

http://localhost:8080/


**1️⃣ User Registration**
Endpoint

POST /api/users/

**{
  "email": "john.doe@example.com",
  "username": "johndoe123",
  "password": "SecurePassword123!",
  "re_password": "SecurePassword123!"
}**


**2️⃣ User Login (JWT)**
Endpoint


POST /api/jwt/create/

**{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!"
}**


