from django import forms
from .models import Topic, Entry


class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}


class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ['text', 'date_worked', 'hours_spent']
        labels = {'text':'', 'date_worked': 'Date Worked On','hours_spent': 'Hours Spent'}
        widgets = {'text': forms.Textarea(attrs={'cols': 80}),
                   'date_worked': forms.DateInput(attrs={'type': 'date'}),
                   'hours_spent': forms.NumberInput(attrs={'step': '0.25'})}




