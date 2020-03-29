from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        label = _("Password"),
        style = {'input_type': 'password'},
        trim_whitespace = False,
        required = True,
    )
    password2 = serializers.CharField(
        label = _("Password Confirmation"),
        style = {'input_type': 'password'},
        trim_whitespace = False,
        required = True
    )

    def get_clean_password(self):
        password1 = self.data.get("password1")
        password2 = self.data.get("password2")
        print(password1, password2)
        if not password1 or not password2 or password1 != password2:
            raise serializers.ValidationError(_('passwords must match'))
        return password2

    def create(self, validated_data):
        clean_password = self.get_clean_password()
        user, _ = User.objects.get_or_create(username = validated_data['username'])
        user.set_password(clean_password)
        user.save()
        print('user saved')
        profile, _ = Profile.objects.get_or_create(user = user)
        return user

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        write_only_fields = ('password1', 'password2') #to make sure passwords are not displayed
