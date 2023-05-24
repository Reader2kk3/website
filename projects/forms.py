from django.forms import ModelForm
from django import forms
from .models import Project, Review

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title','demo_link', 'sourse_link', 'featured_image', 'description']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs ):
        super(ProjectForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['value', 'body']

        labels = {
            'value': 'Проголосуйте!',
            'body': 'Добавьте комментарий'
        }  

    def __init__(self, *args, **kwargs ):
        super(ReviewForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})



