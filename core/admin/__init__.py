# Import de toutes les configurations admin pour maintenir la compatibilité
from .services import ServiceAdmin
from .users import UserAdmin
from .gaps import AuditSourceAdmin, ProcessAdmin, GapTypeAdmin, GapReportAdmin, GapAdmin, HistoriqueModificationAdmin
from .workflow import ValidateurServiceAdmin
from .notifications import NotificationAdmin, GapValidationAdmin

# Export explicite pour les imports directs
__all__ = [
    'ServiceAdmin', 'UserAdmin', 'AuditSourceAdmin', 'ProcessAdmin', 
    'GapTypeAdmin', 'GapReportAdmin', 'GapAdmin', 'HistoriqueModificationAdmin',
    'ValidateurServiceAdmin', 'NotificationAdmin', 'GapValidationAdmin'
]