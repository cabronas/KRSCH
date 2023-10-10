from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from rest_framework import serializers, permissions
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, Event
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializer


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    permission_classes = [permissions.IsAuthenticated]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'],
                                        password=validated_data['password'],
                                        first_name=validated_data['first_name'],
                                        )
        return user


class EventSerializer(serializers.ModelSerializer):
    current_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Event
        fields = ('id', 'name', 'description', 'date_begin', 'date_end', 'date_remind', 'user', 'current_user')

    def create(self, validated_data):
        event = Event.objects.create(name=validated_data['name'],
                                          description=validated_data['description'],
                                          date_begin=validated_data['date_begin'],
                                          date_end=validated_data['date_end'],
                                          date_remind=validated_data['date_remind'],
                                          user=validated_data['user'],
                                          )
        return event
