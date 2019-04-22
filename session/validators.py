from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_session_id(session_id):
    from .models import Session
    if not Session.objects.filter(session_id=session_id, live=True).exists():
        raise ValidationError(
            _('%(session_id)s does not exist!'),
            params={'session_id': session_id},
        )
