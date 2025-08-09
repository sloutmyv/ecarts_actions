# Import de toutes les vues pour maintenir la compatibilité
from .dashboard import dashboard
from .services import (
    services_list, service_detail, service_create, service_edit, service_delete,
    export_services_json, import_services_json, import_services_form
)
from .users import (
    users_list, user_detail, user_create, user_edit, user_delete, user_delete_confirm,
    user_reset_password, export_users_json, import_users_json, import_users_form
)
from .gaps import (
    gap_list, gap_report_list, gap_report_detail, gap_report_create, gap_report_edit,
    gap_create, gap_edit, get_gap_types, get_process_field
)
from .workflow import (
    workflow_management, assign_validator, remove_validator, 
    search_users, service_detail_api, workflow_stats
)
from .niveau_partial import get_niveau_partial

# Export explicite pour les imports directs
__all__ = [
    'dashboard',
    'services_list', 'service_detail', 'service_create', 'service_edit', 'service_delete',
    'export_services_json', 'import_services_json', 'import_services_form',
    'users_list', 'user_detail', 'user_create', 'user_edit', 'user_delete', 'user_delete_confirm',
    'user_reset_password', 'export_users_json', 'import_users_json', 'import_users_form',
    'gap_list', 'gap_report_list', 'gap_report_detail', 'gap_report_create', 'gap_report_edit',
    'gap_create', 'gap_edit', 'get_gap_types', 'get_process_field',
    'workflow_management', 'assign_validator', 'remove_validator',
    'workflow_stats', 'search_users', 'service_detail_api', 'get_niveau_partial'
]