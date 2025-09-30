# 🧪 Backend Tests Directory

This directory contains integration tests, API tests, and debugging utilities for the Book Bartering Social Network backend.

## 📁 Test Files

### **Integration Tests**
- `test_api_integration.py` - Complete API endpoint testing
- `test_server.py` - Server testing utilities with multiple modes

### **Debug Utilities**
- `test_auth_debug.py` - Authentication debugging and troubleshooting
- `debug_auth.py` - Comprehensive authentication diagnostics

## 🚀 How to Run Tests

### **Easy Test Runner (Recommended)**
```bash
cd backend
python run_tests.py
```
This provides an interactive menu with all testing options.

### **Individual Test Scripts**

#### **Quick API Test**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python tests/test_api_integration.py
```

#### **Server Testing Options**
```bash
# Test with Django client (no server needed)
python tests/test_server.py test

# Start server and test with HTTP requests
python tests/test_server.py test-live

# Just start the server
python tests/test_server.py server

# Show available URLs
python tests/test_server.py urls

# Interactive mode
python tests/test_server.py
```

#### **Authentication Debugging**
```bash
# Simple authentication test
python tests/test_auth_debug.py

# Comprehensive authentication diagnostics
python tests/debug_auth.py
```

## 🔧 Test Categories

### **1. Integration Tests**
- Test complete API workflows
- Verify database integration
- Check JWT token generation
- Validate response formats

### **2. Authentication Tests**
- Test user registration
- Test user login (username and email)
- Test password reset flow
- Test social authentication framework

### **3. Debug Utilities**
- Isolate authentication issues
- Check user model configuration
- Verify database connections
- Test Django authentication backends

## 📊 Expected Test Results

### **Successful Test Output**
```
Testing Book Bartering Authentication API
==================================================

✅ User Registration: Working (201 Created)
✅ User Login: Working (200 OK, JWT token received)
✅ Password Reset: Working (200 OK, code sent)
✅ Social Auth Framework: Working (400 expected with mock token)
✅ Database Integration: Working (users created successfully)

Ready for frontend integration!
Frontend should connect to: http://10.0.2.2:8000/auth/
```

## 🛠️ Troubleshooting

### **If tests fail:**
1. **Check virtual environment**: Make sure you're in the activated venv
2. **Check database**: Run `python manage.py migrate`
3. **Check dependencies**: Run `pip install -r requirements-dev.txt`
4. **Check Django setup**: Run `python manage.py check`

### **Common Issues:**
- **Import errors**: Make sure you're in the `backend` directory
- **Database errors**: Delete `db.sqlite3` and run migrations again
- **Port conflicts**: Change port in test scripts if 8000 is busy

## 📱 Frontend Integration Testing

Once backend tests pass, test with your Android app:

1. **Update RetrofitClient.kt**:
   ```kotlin
   private const val BASE_URL = "http://10.0.2.2:8000/"
   ```

2. **Test login/signup flows** in your Android app

3. **Check server logs** for any issues

## 🎯 Future Unit Tests

This directory is prepared for comprehensive unit test coverage:

- **accounts/tests.py** - User model and authentication unit tests
- **books/tests.py** - Book model and catalog unit tests
- **social/tests.py** - Social features unit tests
- **barter/tests.py** - Barter system unit tests
- **notify/tests.py** - Notification system unit tests

### **Running Unit Tests (Future)**
```bash
# Run all unit tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test books

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📝 Notes

- **Integration tests** test the complete API workflows
- **Unit tests** (in individual app directories) test specific components
- **Debug utilities** help troubleshoot issues during development
- All tests use Django's test client for consistency
- Tests are designed to work without external dependencies

---

**Last Updated**: September 29, 2025  
**Test Framework**: Django Test Client + Custom Integration Tests
