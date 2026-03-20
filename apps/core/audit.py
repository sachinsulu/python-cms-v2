"""
apps/core/audit.py
==================
Backwards-compatibility shim.
Logic has moved to apps/core/services/audit_service.py.
Import from there in new code.
"""

from apps.core.services.audit_service import (  # noqa: F401
    get_client_ip,
    log_action,
    log_bulk_action,
)
