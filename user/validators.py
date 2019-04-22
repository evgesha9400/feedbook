from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SubjectCodeValidator(object):
    def __init__(self, user):
        self.user = user

    def __call__(self, s_code):
        if self.user.subjects.filter(code=s_code).exists():
            raise ValidationError(
                _('%(s_code)s already exists!'),
                params={'s_code': s_code},
            )
