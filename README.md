# BEFA Backend — Django REST API

Single Django backend serving both the **user-facing frontend** and the **admin portal**.

## Architecture

```
┌──────────────────┐     ┌──────────────────┐
│  User Frontend   │     │  Admin Portal    │
│  (React/Vite)    │     │  (React/Vite)    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         │  /api/*                │  /api/admin/*
         │                        │
         └────────┬───────────────┘
                  │
         ┌────────▼─────────┐
         │   Django API     │
         │   (DRF + JWT)    │
         ├──────────────────┤
         │  PostgreSQL      │  ← Neon (prod) / MySQL (dev)
         │  Cloudinary      │  ← Image CDN + Blob Storage
         │  Redis           │  ← Cache (prod) / LocMem (dev)
         └──────────────────┘
```

## API Routes

### Auth (`/api/auth/`)
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/auth/register/` | Public | Register user |
| POST | `/api/auth/admin-login/` | Public | Admin login (returns JWT) |
| GET | `/api/auth/me/` | Auth | Current user |
| POST | `/api/auth/jwt/create/` | Public | Get JWT tokens (Djoser) |
| POST | `/api/auth/jwt/refresh/` | Auth | Refresh JWT (Djoser) |

### Public API (User Frontend)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/players/player-of-the-month/` | Player of the month |
| GET | `/api/players/featured-players/` | Featured players |
| GET | `/api/content-hub/posts/` | Published posts |
| GET | `/api/content-hub/posts/<id>/` | Post detail |
| POST | `/api/content-hub/posts/<id>/like/` | Toggle like |
| GET | `/api/schedule/events/` | Upcoming events |
| GET | `/api/ecommerce/products/` | Products in stock |
| GET | `/api/ecommerce/products/<id>/` | Product detail |
| POST | `/api/ecommerce/cart/add/` | Add to cart |
| GET | `/api/ecommerce/cart/` | View cart |
| POST | `/api/ecommerce/orders/` | Place order |
| GET | `/api/ecommerce/my-orders/` | User's orders |

### Admin API (Admin Portal) — Requires `is_staff=True`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard/stats/` | Dashboard statistics |
| GET | `/api/admin/dashboard/recent-players/` | 5 most recent players |
| GET | `/api/admin/dashboard/position-breakdown/` | Players by position |
| GET/POST | `/api/admin/players/` | List / Create players |
| GET/PATCH/DELETE | `/api/admin/players/<id>/` | Player CRUD |
| POST | `/api/admin/players/<id>/upload-photo/` | Upload player photo |
| GET/POST | `/api/admin/posts/` | List / Create posts |
| GET/PATCH/DELETE | `/api/admin/posts/<id>/` | Post CRUD |
| POST | `/api/admin/posts/<id>/upload-image/` | Upload post image |
| GET/POST | `/api/admin/events/` | List / Create events |
| GET/PATCH/DELETE | `/api/admin/events/<id>/` | Event CRUD |
| GET/POST | `/api/admin/products/` | List / Create products |
| GET/PATCH/DELETE | `/api/admin/products/<id>/` | Product CRUD |
| POST | `/api/admin/products/<id>/upload-image/` | Upload product image |
| GET | `/api/admin/orders/` | All orders |
| PATCH | `/api/admin/orders/<id>/` | Update order status |
| POST | `/api/admin/uploads/image/` | Generic image upload |

## Setup

```bash
# Clone & install
git clone <repo-url> && cd befa-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env   # Edit with your credentials

# Migrate & create admin
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver
```

## Create Admin User

```bash
python manage.py createsuperuser
# Enter email, username, password
# This user will have is_staff=True and can access admin portal
```

## Deployment (Render)

1. Push to GitHub
2. Connect repo on Render
3. Set environment variables (see `.env.example`)
4. Set `ENVIRONMENT=production`
5. Deploy — migrations run automatically via Procfile

## System Design Principles Applied

- **Client-Server**: Headless API, two separate frontend SPAs
- **REST API**: Standard resource-based URLs, proper HTTP methods
- **Database Indexing**: All frequently queried fields indexed
- **Caching**: Multi-tier (Redis prod, LocMem dev) with TTL and invalidation
- **Rate Limiting**: DRF throttling (100/hr anon, 1000/hr auth)
- **CDN + Blob Storage**: Cloudinary for all media
- **Horizontal Scaling**: Stateless API, external DB/cache/storage
- **API Gateway**: `/api/` prefix, public vs admin route separation
- **Security**: JWT auth, CORS, HTTPS, HSTS in production
- **Idempotency**: Safe GET operations, proper POST/PATCH/DELETE semantics
