import calendar
from calendar import HTMLCalendar
from datetime import datetime, date, timedelta

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views import generic

from .models import Event
from .utils import Calendar


class CalendarView(generic.ListView):
    model = Event
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = self.get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month).formatmonth()
        context['calendar'] = mark_safe(cal)
        context['prev_month'] = self.prev_month(d)
        context['next_month'] = self.next_month(d)
        return context

    @staticmethod
    def prev_month(d):
        first = d.replace(day=1)
        # 1 - 1 = 31
        prev_month = first - timedelta(days=1)
        month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
        return month

    @staticmethod
    def next_month(d):
        # Return last day in a current month
        days_in_month = calendar.monthrange(d.year, d.month)[1]
        last = d.replace(day=days_in_month)
        next_month = last + timedelta(days=1)
        month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
        return month

    @staticmethod
    def get_date(req_day):
        if req_day:
            year, month = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
        return datetime.today()
