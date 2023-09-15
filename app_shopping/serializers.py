from rest_framework import serializers
from .models import *
import Useable.useable as uc
from passlib.hash import django_pbkdf2_sha256 as handler

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ["first_name", "last_name", "email", "password", "image", "phone"]
    
    def validate(self, attrs):
        requireFeilds_status = uc.requireFeildValidation(self.context['reqData'], self.context["requireFeilds"])
        if not requireFeilds_status["status"] :
            raise serializers.ValidationError({"error": requireFeilds_status["message"]})
        pass_status = uc.checkpasslen(attrs['password'])
        if not pass_status:
            raise serializers.ValidationError("Password Length must be greaterthan 8")
        email_status = uc.checkEmailPattern(attrs['email'])
        if not email_status:
            raise serializers.ValidationError("Email pattern is not valid")
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = handler.hash(password)
        return super().create(validated_data)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Admin
        fields = ["email", "password"]
            
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        fetch_user = Admin.objects.filter(email = email).first()
        if not fetch_user :
            raise serializers.ValidationError("Email not found . . .")
        check_pass = uc.checkPasswordValidation(fetch_user, password)
        if not check_pass['status']:
            raise serializers.ValidationError(f"{check_pass['message']}")
        attrs['fetch_user'] = fetch_user
        return attrs
    
class AdminForgotPassSerializer(serializers.Serializer):
    class Meta:
        model = Admin
        feilds = ["password","email"]
    def validate(self, attrs):
        email = attrs.get ("email")
        if not uc.checkEmailPattern(email):
            raise serializers.ValidationError("Incorrect email patterm")
        return attrs
        