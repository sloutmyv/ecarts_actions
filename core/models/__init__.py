# Import de tous les modèles pour maintenir la compatibilité
from .services import Service
from .users import User
from .gaps import AuditSource, Process, GapType, GapReport, Gap, HistoriqueModification
from .attachments import GapReportAttachment, GapAttachment
from .workflow import ValidateurService
from .notifications import Notification, GapValidation

# Export explicite pour les imports directs
__all__ = ['Service', 'User', 'AuditSource', 'Process', 'GapType', 'GapReport', 'Gap', 'HistoriqueModification', 'GapReportAttachment', 'GapAttachment', 'ValidateurService', 'Notification', 'GapValidation']