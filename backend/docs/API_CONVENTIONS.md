# API Conventions

This document defines the **actual API URL conventions** used in this project.

## 📋 Table of Contents

- [Overview](#overview)
- [URL Structure](#url-structure)
- [Current Endpoints](#current-endpoints)
- [Adding New Endpoints](#adding-new-endpoints)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Authentication](#authentication)

## 🎯 Overview

**For this MVP, we use semantic, direct paths instead of `/api/v1/` prefixes.**

### 📌 Important Context

**Using `/api/v1/` is generally the better approach** for production APIs because:
- ✅ Provides clear API versioning from the start
- ✅ Makes future breaking changes easier to manage
- ✅ Follows industry-standard REST API conventions
- ✅ Allows running multiple API versions simultaneously (e.g., `/api/v1/` and `/api/v2/`)
- ✅ Widely recognized pattern in the industry

**However, for our MVP (Minimum Viable Product), we chose simpler paths because:**
- 🚀 **Speed of Development**: Shorter URLs mean faster iteration during MVP phase
- 🎯 **MVP Focus**: Prioritize features over infrastructure
- 📱 **Frontend Simplicity**: Easier integration during rapid prototyping
- 🔄 **Migration Path**: We can migrate to `/api/v1/` in future iterations when needed
- ⚡ **Current Needs**: Our current scale doesn't require versioning yet

### Our Current Approach

We use **semantic, direct paths** that are:
- ✅ Simpler and more readable for MVP development
- ✅ Easier to maintain during rapid iteration
- ✅ Consistent with frontend expectations
- ✅ RESTful without unnecessary nesting
- ✅ Sufficient for initial release

## 🌐 URL Structure

### General Pattern

```
/{resource-group}/{resource}/{action}
```

### Current Resource Groups

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `/auth/` | Authentication & user management | `/auth/login/`, `/auth/signup/` |
| `/library/` | User's library (books, reviews) | `/library/reviews/` |
| `/social/` | Social features (future) | `/social/posts/` |
| `/barter/` | Barter/trade features (future) | `/barter/offers/` |

### Why We Chose This Approach for MVP

**Short Answer**: Speed and simplicity for MVP, with a clear migration path to `/api/v1/` later.

**Detailed Reasoning**:

1. **MVP Development Speed**: Shorter URLs mean less boilerplate code
2. **Frontend Simplicity**: Easier integration during rapid prototyping
3. **Current Scale**: Our MVP doesn't need multiple API versions yet
4. **Future Flexibility**: We can migrate to `/api/v1/` when needed via:
   - URL prefix migration (`/auth/` → `/api/v1/auth/`)
   - HTTP headers (`Accept: application/vnd.api.v2+json`)
   - Separate domains (`api-v2.example.com`)
5. **Team Agreement**: Consistent pattern across all MVP endpoints

**When to Migrate to `/api/v1/`**:
- When we need to introduce breaking changes
- When we have external API consumers
- When we move from MVP to production-scale
- When we need to support multiple API versions simultaneously

## 📍 Current Endpoints

### Authentication (`/auth/`)

```python
# User Registration
POST   /auth/signup/
Request:  {"username": "string", "email": "string", "password": "string"}
Response: {"ok": true, "user": {...}, "message": "Registration successful"}

# User Login
POST   /auth/login/
Request:  {"username": "string", "password": "string"}
Response: {"ok": true, "token": "...", "refresh": "...", "user": {...}}

# User Profile
GET    /auth/profile/
Response: {"id": 1, "username": "...", "email": "...", ...}

PATCH  /auth/profile/
Request:  {"first_name": "...", "bio": "...", ...}
Response: {"id": 1, "username": "...", "first_name": "...", ...}

# Password Reset
POST   /auth/forgot/start/
POST   /auth/forgot/verify/
POST   /auth/forgot/reset/

# Social Authentication
POST   /auth/social/google/
POST   /auth/social/kakao/
```

### Library (`/library/`)

```python
# User's Book Reviews
GET    /library/reviews/
Response: {"results": [{"id": 1, "bookTitle": "...", "likeCount": 5, "isLiked": false, ...}]}

POST   /library/reviews/
Request:  {"bookTitle": "...", "authorName": "...", "content": "...", "imageUrls": [...]}
Response: {"id": 1, "bookTitle": "...", "userName": "...", "likeCount": 0, "isLiked": false, ...}

# Review Likes
POST   /library/reviews/{id}/like/
Response: {"review": {"id": 1, "likeCount": 5, "isLiked": true, ...}}
```

### API Documentation (`/api/`)

```python
# OpenAPI Schema
GET    /api/schema/
GET    /api/docs/        # Swagger UI
GET    /api/redoc/       # ReDoc UI
```

## ➕ Adding New Endpoints

### Step 1: Check Existing Patterns

Before creating new endpoints, review:
1. `backend/core/urls.py` - Main URL configuration
2. Existing app URLs (e.g., `backend/books/urls.py`, `backend/accounts/urls.py`)
3. This document

### Step 2: Choose the Right Resource Group

Determine which resource group your endpoint belongs to:

- **Authentication/User**: Use `/auth/`
- **User's Library**: Use `/library/`
- **Social Features**: Use `/social/`
- **Barter/Trade**: Use `/barter/`
- **New Feature**: Create a new semantic prefix

### Step 3: Follow RESTful Principles

```python
# ✅ Good Examples
GET    /library/books/              # List user's books
POST   /library/books/              # Add a book
GET    /library/books/{id}/         # Get book details
PATCH  /library/books/{id}/         # Update book
DELETE /library/books/{id}/         # Delete book

# Actions on resources
POST   /library/books/{id}/lend/    # Lend a book
POST   /library/books/{id}/return/  # Return a book

# ❌ Bad Examples
GET    /library/getBooks/           # Don't use verbs in URL
POST   /library/book/create/        # Unnecessary 'create'
GET    /library/books/delete/{id}/  # Wrong HTTP method
POST   /api/v1/library/books/       # Don't use /api/v1/
```

### Step 4: Update Documentation

After adding new endpoints:
1. Update `backend/docs/API_DOCUMENTATION.md`
2. Add OpenAPI schema decorators (`@extend_schema`)
3. Update this file if introducing a new resource group

### Step 5: Write Tests

Always write tests for new endpoints:
```python
# backend/app_name/tests/test_views_feature.py
class FeatureViewTestCase(APITestCase):
    def test_endpoint_success(self):
        # Test successful case
        
    def test_endpoint_unauthorized(self):
        # Test authentication
        
    def test_endpoint_validation(self):
        # Test input validation
```

## 📦 Response Format

### Success Response

```json
{
    "ok": true,
    "data": {...},
    "message": "Operation successful"
}
```

Or for list endpoints:
```json
{
    "results": [...]
}
```

### Error Response

```json
{
    "ok": false,
    "message": "Error message",
    "errors": {
        "field_name": ["Error detail"]
    }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input/validation error |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

## 🔒 Authentication

### JWT Token Authentication

Most endpoints require authentication via JWT tokens:

```http
Authorization: Bearer <access_token>
```

### Public Endpoints

The following endpoints are public (no authentication required):
- `POST /auth/signup/`
- `POST /auth/login/`
- `POST /auth/social/google/`
- `POST /auth/social/kakao/`
- `POST /auth/forgot/start/`

All other endpoints require authentication.

## 🔄 Versioning Strategy

### Current Approach

We currently do NOT version our API. All endpoints are considered v1.

### Future Versioning

If versioning becomes necessary, we will use:

1. **HTTP Headers** (Preferred):
   ```http
   Accept: application/vnd.bookbarter.v2+json
   ```

2. **Separate Domains**:
   ```
   api-v1.example.com
   api-v2.example.com
   ```

3. **URL Versioning** (Last Resort):
   ```
   /v2/library/reviews/
   ```

We will NOT use `/api/v1/` prefix as it's redundant and verbose.

## 📝 Examples

### Example 1: Adding a Book Wishlist Feature

```python
# backend/books/urls.py
urlpatterns = [
    # Existing endpoints
    path("reviews/", UserReviewListCreateView.as_view()),
    
    # New wishlist endpoints
    path("wishlist/", WishlistListCreateView.as_view()),
    path("wishlist/<int:pk>/", WishlistDetailView.as_view()),
]

# URLs will be:
# GET/POST  /library/wishlist/
# GET/PATCH/DELETE  /library/wishlist/{id}/
```

### Example 2: Adding Social Features

```python
# backend/core/urls.py
urlpatterns = [
    path("auth/", include("accounts.urls")),
    path("library/", include("books.urls")),
    path("social/", include("social.urls")),  # New
]

# backend/social/urls.py
urlpatterns = [
    path("posts/", PostListCreateView.as_view()),
    path("posts/<int:pk>/", PostDetailView.as_view()),
    path("posts/<int:pk>/like/", PostLikeView.as_view()),
]

# URLs will be:
# GET/POST  /social/posts/
# GET/PATCH/DELETE  /social/posts/{id}/
# POST  /social/posts/{id}/like/
```

## 🚫 Common Mistakes to Avoid

1. ❌ **Using `/api/v1/` prefix**
   ```python
   # Wrong
   path("api/v1/books/", include("books.urls"))
   
   # Correct
   path("library/", include("books.urls"))
   ```

2. ❌ **Using verbs in URLs**
   ```python
   # Wrong
   path("books/getAll/", views.get_all_books)
   
   # Correct
   path("books/", views.BookListView.as_view())
   ```

3. ❌ **Inconsistent naming**
   ```python
   # Wrong - mixing patterns
   path("auth/", ...)
   path("api/v1/books/", ...)
   
   # Correct - consistent pattern
   path("auth/", ...)
   path("library/", ...)
   ```

4. ❌ **Not documenting new endpoints**
   - Always update `API_DOCUMENTATION.md`
   - Always add OpenAPI schema decorators

## 📚 References

- [RESTful API Design Best Practices](https://restfulapi.net/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [OpenAPI Specification](https://swagger.io/specification/)
- Project Documentation: `backend/docs/API_DOCUMENTATION.md`

---

**Last Updated**: 2025-10-19  
**Maintained By**: Backend Team  
**Questions?**: Check `backend/docs/API_DOCUMENTATION.md` or ask the team

