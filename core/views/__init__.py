# Import de toutes les vues pour maintenir la compatibilité
from .dashboard import dashboard
from .services import (
    services_list, service_detail, service_create, service_edit, service_delete,
    export_services_json, import_services_json, import_services_form
)
from .users import (
    users_list, user_detail, user_create, user_edit, user_delete,
    user_reset_password, export_users_json
)

# Export explicite pour les imports directs
__all__ = [
    'dashboard',
    'services_list', 'service_detail', 'service_create', 'service_edit', 'service_delete',
    'export_services_json', 'import_services_json', 'import_services_form',
    'users_list', 'user_detail', 'user_create', 'user_edit', 'user_delete',
    'user_reset_password', 'export_users_json'
]