# Import de toutes les vues pour maintenir la compatibilité
from .dashboard import dashboard
from .services import (
    services_list, service_detail, service_create, service_edit, service_delete,
    export_services_json, import_services_json, import_services_form
)

# Export explicite pour les imports directs
__all__ = [
    'dashboard',
    'services_list', 'service_detail', 'service_create', 'service_edit', 'service_delete',
    'export_services_json', 'import_services_json', 'import_services_form'
]