import calendar
import json
from calendar import HTMLCalendar
from datetime import datetime, date, timedelta

import ics
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.safestring import mark_safe
from django.views import generic
# from requests import Response
from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .calendar_importer import country_list, ics_import
# from .forms import EventForm
from .models import Event, CustomUser
from .serializers import UserSerializer, TokenObtainPairSerializer, EventSerializer
from .utils import Calendar
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from django.contrib.auth import get_user_model
from .tasks import *
from src import settings

User = get_user_model()


# registration
class RegisterView(APIView):
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        serializer = UserSerializer(data=self.request.data)
        if serializer.is_valid():
            new_user = get_user_model().objects.create_user(**serializer.validated_data)
            # check if country is present in data and import it
            if "country" in self.request.data:
                if self.request.data['country'] in country_list:
                    ics_import(self.request.data['country'], new_user)
                else:
                    new_user.delete()
                    return Response(status=HTTP_400_BAD_REQUEST, data={'error': "Invalid country"})
            return Response(status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})


# email login
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


# see users
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# see user events
class EventViewSet(viewsets.GenericViewSet):
    queryset = Event.objects.all().order_by('-date_begin')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = User.objects.all()
        serializer = EventSerializer(Event.objects.filter(user=self.request.user), many=True)
        print(settings.EMAIL_HOST_USER)
        send_email_cel.delay("your_subject", "your_message", settings.EMAIL_HOST_USER, "cabronas.max@mail.ru")
        return Response(serializer.data)

    def retrieve(self, request, pk):
        try:
            serializer = EventSerializer(Event.objects.get(pk=pk, user=self.request.user))
        except Event.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    def create(self, request):
        data = self.request.data

        # Convert date_remind
        try:
            date_remind, date_start = int(data["date_remind"]), parse_datetime(data["date_begin"])
            if date_remind == 0:
                data["date_remind"] = date_start - timedelta(hours=1)
            elif date_remind == 1:
                data["date_remind"] = date_start - timedelta(hours=2)
            elif date_remind == 2:
                data["date_remind"] = date_start - timedelta(hours=4)
            elif date_remind == 3:
                data["date_remind"] = date_start - timedelta(days=1)
            elif date_remind == 4:
                data["date_remind"] = date_start - timedelta(days=7)
            else:
                raise serializers.ValidationError("Bad date_remind")
        except:
            raise serializers.ValidationError("Bad date_remind")
        if data['date_end'] == "":
            data['date_end'] = data['date_begin']

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})

    def destroy(self, request, pk):
        try:
            event = Event.objects.get(pk=pk, user=self.request.user)
        except Event.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        event.delete()
        return Response(status=HTTP_200_OK)


class List_Events_By_Day(APIView):
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = self.request.data
        if "date" in data:
            try:
                date = datetime.strptime(data["date"], '%Y-%m-%d').date()
            except:
                return Response(status=HTTP_400_BAD_REQUEST, data={'error': "Invalid date"})
            events = Event.objects.filter(date_begin__date=date, user=request.user)
            serializer = EventSerializer(events, many=True)
            return Response(serializer.data)
        else:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': "No date field"})


class List_Events_By_Day_In_Month(APIView):
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = self.request.data
        if "date" in data:
            try:
                date = datetime.strptime(data["date"], '%Y-%m-%d').date()
            except:
                return Response(status=HTTP_400_BAD_REQUEST, data={'error': "Invalid date"})
            events = Event.objects.filter(date_begin__month=date.month, date_begin__year=date.year,
                                          user=request.user).order_by('-date_begin')
            events_dict = {}
            for event in events:
                if event.date_begin.day not in events_dict:
                    events_dict[event.date_begin.day] = 1
                else:
                    events_dict[event.date_begin.day] += 1
            return Response(events_dict)
        else:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': "No date field"})
# def get_events_day(request):
#     data = json.loads(request.body)
#     if "date" in data:
#         # try:
#             date = datetime.strptime(data["date"], '%Y-%m-%d')
#             # date = parse_datetime(data["date"])
# # -            try:
#             events = Event.objects.get(date_begin__date=date, user=request.user)
#             serializer = EventSerializer(events, many=True)
#             return Response(serializer.data)
#             # except Event.DoesNotExist:
#             #     return Response(status=HTTP_404_NOT_FOUND)
# except:
#     return Response(status=HTTP_400_BAD_REQUEST, data={'error': "Incorrect date"})
# else:
#     return Response(status=HTTP_400_BAD_REQUEST, data={'error': "No date field"})

# def view_day(request, year, month, day):
#     context = {}
#     context['year'] = year
#     context['month'] = month
#     context['day'] = day
#     context['month_name'] = get_month_name(month)
#     events = Event.objects.filter(date__year=year, date__month=month, date__day=day)
#     context['events'] = list(events)
#     return render(request, 'day.html', context=context)
#     # return  HttpResponse('kek')


# def event_form(request, event_id=None):
#     instance = Event()
#     if event_id:
#         instance = get_object_or_404(Event, pk=event_id)
#     else:
#         instance = Event()
#
#     form = EventForm(request.POST or None, instance=instance)
#     if request.POST and form.is_valid():
#         event: Event = form.save()
#         event.user = request.user
#         form.save()
#         return HttpResponseRedirect(reverse('cal'))
#     return render(request, 'event.html', {'form': form})


# def get_month_name(month):
#     if month == 1:
#         return "January"
#     elif month == 2:
#         return "Februrary"
#     elif month == 3:
#         return "March"
#     elif month == 4:
#         return "April"
#     elif month == 5:
#         return "May"
#     elif month == 6:
#         return "June"
#     elif month == 7:
#         return "July"
#     elif month == 8:
#         return "August"
#     elif month == 9:
#         return "September"
#     elif month == 10:
#         return "October"
#     elif month == 11:
#         return "November"
#     elif month == 12:
#         return "December"


# class CalendarView(generic.ListView):
#     model = Event
#     template_name = 'test.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         d = self.get_date(self.request.GET.get('month', None))
#         cal = Calendar(d.year, d.month).formatmonth()
#         context['calendar'] = mark_safe(cal)
#         context['prev_month'] = self.prev_month(d)
#         context['next_month'] = self.next_month(d)
#         return context
#
#     @staticmethod
#     def prev_month(d):
#         first = d.replace(day=1)
#         # 1 - 1 = 31
#         prev_month = first - timedelta(days=1)
#         month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
#         return month
#
#     @staticmethod
#     def next_month(d):
#         # Return last day in a current month
#         days_in_month = calendar.monthrange(d.year, d.month)[1]
#         last = d.replace(day=days_in_month)
#         next_month = last + timedelta(days=1)
#         month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
#         return month
#
#     @staticmethod
#     def get_date(req_day):
#         if req_day:
#             year, month = (int(x) for x in req_day.split('-'))
#             return date(year, month, day=1)
#         return datetime.today()
