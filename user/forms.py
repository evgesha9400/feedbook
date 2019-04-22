from crispy_forms.bootstrap import FieldWithButtons, StrictButton, PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, HTML, Fieldset, Div, Field
from .models import QuestionChoice, Lesson, Subject, Question
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelformset_factory
from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                PrependedText('code', 'Code'),
                PrependedText('name', 'Name'),
            ),
            HTML('{% if s_form.instance.id %}'
                 '      <input type="submit" class="btn btn-light float-right" value="Update">'
                 '{% else %}'
                 '      <input type="submit" class="btn btn-light float-right" value="Add">'
                 '{% endif %}'),
            HTML('<a class="btn btn-light" href="{% url \'subjects\' %}">Back</a>'),
        )
        super(SubjectForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get('code')
        try:
            subject = self.user.subjects.get(code=code)
        except Subject.DoesNotExist:
            return code

        if subject.id == self.instance.id:
            return code
        else:
            raise ValidationError(
                _('%(code)s already exists!'),
                params={'code': code},
            )


class LessonForm(forms.ModelForm):

    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Lesson
        fields = ['number', 'description']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                PrependedText('number', 'Lesson #'),
                PrependedText('description', 'Description'),
            ),
            HTML('{% if s_form.instance.id %}'
                 '      <input type="submit" class="btn btn-light float-right" value="Update">'
                 '{% else %}'
                 '      <input type="submit" class="btn btn-light float-right" value="Add">'
                 '{% endif %}'),
            HTML('<a class="btn btn-light" href="{% url \'lessons\' s_id=subject.id %}">Back</a>')
        )
        super(LessonForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'rows': '2'})


class QuestionForm(forms.ModelForm):

    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Question
        fields = ['text', 'label', 'timeout', 'image']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'rows': '6'})


class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ['text', 'correct']

    def __init__(self, *args, **kwargs):
        super(QuestionChoiceForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'form-control answer_text'})
        self.fields['correct'].empty_label = None


class QCFormset(forms.BaseModelFormSet):
    class Meta:
        model = QuestionChoice
        fields = ['text', 'correct']

    def __init__(self, *args, **kwargs):
        super(QCFormset, self).__init__(*args, **kwargs)


QuestionChoiceFormset = modelformset_factory(
    QuestionChoice,
    form=QuestionChoiceForm,
    fields=('text', 'correct'),
    extra=4,
    max_num=4,
)



