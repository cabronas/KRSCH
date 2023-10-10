# from django.forms import *
# from .models import Event
#
# Event_choices = [
#     ('1', 'An hour before'),
#     ('2', 'Two hours before'),
#     ('4', 'Four hours before'),
#     ('24', 'A day before'),
#     ('168', 'A week before'),
# ]
# class EventForm(ModelForm):
#     class Meta:
#         model = Event
#         widgets = {
#             'date_begin': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
#             'date_remind': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
#         }
#         fields = ("name", "description", "date", "date_remind")
#
#
#     def __init__(self, *args, **kwargs):
#         super(EventForm, self).__init__(*args, **kwargs)
#         # input_formats to parse HTML5 datetime-local input to datetime field
#         self.fields['date_begin'].input_formats = ('%Y-%m-%dT%H:%M',)
