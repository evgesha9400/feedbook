from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from .validators import validate_session_id
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from user.models import Subject
from .models import Session
from django import forms


class SessionConnectForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session_id']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            FieldWithButtons('session_id', StrictButton('Connect', css_class="btn btn-light border border-dark", type='Submit'))
        )
        super(SessionConnectForm, self).__init__(*args, **kwargs)
        self.fields['session_id'].required = True
        self.fields['session_id'].validators = [validate_session_id]
        self.fields['session_id'].widget.attrs.update({'placeholder': 'Enter ID'})
        self.fields['session_id'].label = ""

    def validate_unique(self):
        pass


class SessionCreateForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), required=True)

    def __init__(self, user, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            FieldWithButtons('subject', StrictButton('Create', css_class="btn btn-light border border-dark", type='Submit'))
        )
        super(SessionCreateForm, self).__init__(*args, **kwargs)
        self.fields['subject'].queryset = user.subjects.all()
        self.fields['subject'].empty_label = None
