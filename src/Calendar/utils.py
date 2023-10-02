
from calendar import HTMLCalendar

from django.urls import reverse

from .models import Event


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatmonth(self):
        events = Event.objects.filter(date__year=self.year, date__month=self.month)
        cal = f'<table border="1" cellpadding="1" cellspacing="0" class="calendar" style = "width: 100%; margin-left: auto; margin-right: auto; table-layout: fixed; padding-top: 20%;">\n'

        # Calendar header display type
        cal += f'{self.formatmonthname(self.year, self.month, withyear=True)}\n'
        # Week name display type
        cal += f'{self.formatweekheader()}\n'

        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events, self.year, self.month)}\n'
        return cal

    def formatweek(self, inp_week, events, year, month):
        week = ''
        for cal_d, week_day in inp_week:
            week += self.formatday(cal_d, events, year, month)
        return f'<tr> {week} </tr>'

    def formatday(self, cal_d, events, year, month):
        day_events = events.filter(date__day=cal_d)
        events_to_cal = ''
        for event in day_events:
            events_to_cal += f'<li> {event.name} </li>'

        if cal_d != 0:
            return f"<td style ='text-align: center; vertical-align: middle;'>" \
                   f"<a class='btn btn-secondary rounded-0 w-100 btn-block' " \
                   f"href='{reverse('day', args=[year,month,cal_d])}'>" \
                   f"{cal_d}" \
                   f"<ul> " \
                   f"{events_to_cal} " \
                   f"</ul> " \
                   f"</a> " \
                   f"</td>"

        return '<td></td>'
