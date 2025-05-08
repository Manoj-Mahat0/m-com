from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.auth_route import auth_router
from routes.profile_route import router as profile_router
from routes.photo_route import photo_router
from routes.admin_route import admin_router
from routes.admin.category_route import router as category_router
from routes.admin.product_route import router as admin_product_router
from routes.product_route import router as user_product_router
from routes.watchlist import router as watchlist_router
from routes.cart_route import router as cart_router  # ✅ NEW: Import cart route
from routes.purchase_checkout_route import router as check_router  # ✅ NEW: Import cart route

from strawberry.fastapi import GraphQLRouter
from gql.profile_schema import ProfileQuery
import strawberry

@strawberry.type
class Query(ProfileQuery):
    pass

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, context_getter=lambda request: {"request": request})

app = FastAPI()

# ✅ Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(profile_router, prefix="/user")
app.include_router(photo_router, prefix="/photo")
app.include_router(admin_router, prefix="/auth")
app.include_router(category_router, prefix="/category")
app.include_router(admin_product_router, prefix="/admin/products")
app.include_router(user_product_router, prefix="/products")
app.include_router(watchlist_router, prefix="/user/watchlist")  # ✅ Watchlist routes
app.include_router(cart_router, prefix="/cart")  # ✅ NEW: Mount cart API
app.include_router(check_router, prefix="/purchase")  # ✅ NEW: Mount cart API

# ✅ GraphQL
app.include_router(graphql_app, prefix="/graphql")

# ✅ Static files (e.g., profile_photos, product images)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
