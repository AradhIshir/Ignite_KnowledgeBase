# Postman API Testing Guide

## 🚀 Backend API Endpoints

Base URL: `http://localhost:8080`

---

## 📋 Available Endpoints

### 1. Health Check (No Auth Required)
- **Method:** `GET`
- **URL:** `http://localhost:8080/health`
- **Headers:** None
- **Expected Response:**
  ```json
  {
    "ok": true
  }
  ```

---

### 2. List All Users (Admin Only)
- **Method:** `GET`
- **URL:** `http://localhost:8080/api/admin/users`
- **Headers:**
  ```
  Authorization: Bearer YOUR_ACCESS_TOKEN
  Content-Type: application/json
  ```
- **Expected Response:**
  ```json
  {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "full_name": "User Name",
        "role": "admin",
        "created_at": "2025-01-01T00:00:00Z"
      }
    ]
  }
  ```

---

### 3. Create New User (Admin Only)
- **Method:** `POST`
- **URL:** `http://localhost:8080/api/admin/users`
- **Headers:**
  ```
  Authorization: Bearer YOUR_ACCESS_TOKEN
  Content-Type: application/json
  ```
- **Body (JSON):**
  ```json
  {
    "email": "newuser@example.com",
    "password": "securepassword123",
    "full_name": "New User",
    "role": "project_lead"
  }
  ```
- **Valid roles:** `admin`, `project_lead`, `team_member`
- **Expected Response:**
  ```json
  {
    "id": "uuid",
    "email": "newuser@example.com",
    "full_name": "New User",
    "role": "project_lead",
    "created_at": "2025-01-01T00:00:00Z"
  }
  ```

---

### 4. Delete User (Admin Only)
- **Method:** `DELETE`
- **URL:** `http://localhost:8080/api/admin/users/{user_id}`
- **Headers:**
  ```
  Authorization: Bearer YOUR_ACCESS_TOKEN
  Content-Type: application/json
  ```
- **Example URL:** `http://localhost:8080/api/admin/users/99cea931-4581-489b-8556-da93d14841d7`
- **Expected Response:**
  ```json
  {
    "success": true,
    "message": "User deleted successfully"
  }
  ```

---

### 5. Update User Role (Admin Only)
- **Method:** `PATCH`
- **URL:** `http://localhost:8080/api/admin/users/{user_id}/role`
- **Headers:**
  ```
  Authorization: Bearer YOUR_ACCESS_TOKEN
  Content-Type: application/json
  ```
- **Body (JSON):**
  ```json
  {
    "role": "admin"
  }
  ```
- **Valid roles:** `admin`, `project_lead`, `team_member`
- **Example URL:** `http://localhost:8080/api/admin/users/99cea931-4581-489b-8556-da93d14841d7/role`
- **Expected Response:**
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "role": "admin"
  }
  ```

---

## 🔑 How to Get Your Access Token

### Option 1: From Browser (Easiest)

1. Open your frontend app and log in
2. Open Browser DevTools (F12)
3. Go to **Console** tab
4. Run this JavaScript:
   ```javascript
   const { data: { session } } = await supabase.auth.getSession();
   console.log('Access Token:', session?.access_token);
   ```
5. Copy the token that appears

### Option 2: From Supabase Dashboard

1. Go to Supabase Dashboard → Authentication → Users
2. Click on your user
3. Check the "Raw JSON" tab
4. Look for the session token (this is more complex, Option 1 is easier)

### Option 3: Sign In via API

1. **POST** to `https://wwmqodqqqrffxdvgisrd.supabase.co/auth/v1/token?grant_type=password`
2. **Headers:**
   ```
   apikey: YOUR_ANON_KEY
   Content-Type: application/json
   ```
3. **Body:**
   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```
4. Copy the `access_token` from the response

---

## 📝 Postman Setup Steps

### Step 1: Create a Collection
1. Open Postman
2. Click **New** → **Collection**
3. Name it "Knowledge Hub API"

### Step 2: Set Collection Variables
1. Click on your collection
2. Go to **Variables** tab
3. Add these variables:
   - `base_url`: `http://localhost:8080`
   - `access_token`: `YOUR_TOKEN_HERE` (update this after getting token)

### Step 3: Create Requests

#### Health Check Request
1. **New Request** → Name: "Health Check"
2. **Method:** GET
3. **URL:** `{{base_url}}/health`
4. Click **Send**

#### List Users Request
1. **New Request** → Name: "List Users"
2. **Method:** GET
3. **URL:** `{{base_url}}/api/admin/users`
4. **Headers:**
   - Key: `Authorization`, Value: `Bearer {{access_token}}`
   - Key: `Content-Type`, Value: `application/json`
5. Click **Send**

#### Create User Request
1. **New Request** → Name: "Create User"
2. **Method:** POST
3. **URL:** `{{base_url}}/api/admin/users`
4. **Headers:**
   - Key: `Authorization`, Value: `Bearer {{access_token}}`
   - Key: `Content-Type`, Value: `application/json`
5. **Body** → Select **raw** → **JSON**
6. Paste:
   ```json
   {
     "email": "test@example.com",
     "password": "test123456",
     "full_name": "Test User",
     "role": "team_member"
   }
   ```
7. Click **Send**

---

## ✅ Testing Checklist

- [ ] Health check returns `{"ok": true}`
- [ ] List users returns array of users (with valid token)
- [ ] Create user successfully creates a new user
- [ ] Update role changes user's role
- [ ] Delete user removes user from system
- [ ] All endpoints return 401/403 without valid admin token

---

## 🐛 Common Errors

### 401 Unauthorized
- **Cause:** Missing or invalid access token
- **Fix:** Get a fresh token and update the Authorization header

### 403 Forbidden
- **Cause:** User doesn't have admin role
- **Fix:** Make sure your user has `role: "admin"` in user metadata

### 500 Internal Server Error
- **Cause:** Backend not configured or Supabase keys missing
- **Fix:** Check backend `.env` file has all required variables

### Connection Refused
- **Cause:** Backend server not running
- **Fix:** Start backend with `poetry run uvicorn app.main:app --reload --port 8080`

---

## 📚 Additional Resources

- API Documentation: http://localhost:8080/docs (Swagger UI)
- Alternative API Docs: http://localhost:8080/redoc




