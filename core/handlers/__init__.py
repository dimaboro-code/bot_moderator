from .admin_group_handlers import admin_group_router
from .admin_private_handlers import admin_private_router
from .user_private_handlers import user_private_router
from .debug_handlers import debug_router
from .service_handlers import service_router
from .user_group_handlers import user_group_router

all_routers = [
    admin_group_router,
    admin_private_router,
    user_private_router,
    debug_router,
    service_router,
    user_group_router
]

__all__ = [
    'admin_group_router',
    'admin_private_router',
    'user_private_router',
    'debug_router',
    'service_router',
    'all_routers',
    'user_group_router'
]
