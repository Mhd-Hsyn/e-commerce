from rest_framework import serializers
from .models import *
import Useable.useable as uc
from passlib.hash import django_pbkdf2_sha256 as handler


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ["first_name", "last_name", "email", "password", "image", "phone"]

    def validate(self, attrs):
        pass_status = uc.checkpasslen(attrs["password"])
        if not pass_status:
            raise serializers.ValidationError("Password Length must be greaterthan 8")
        email_status = uc.checkEmailPattern(attrs["email"])
        if not email_status:
            raise serializers.ValidationError("Email pattern is not valid")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password"] = handler.hash(password)
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
        fetch_user = Admin.objects.filter(email=email).first()
        if not fetch_user:
            raise serializers.ValidationError("Email not found . . .")
        check_pass = uc.checkPasswordValidation(fetch_user, password)
        if not check_pass["status"]:
            raise serializers.ValidationError(f"{check_pass['message']}")
        attrs["fetch_user"] = fetch_user
        return attrs


class AdminForgotPassSerializer(serializers.Serializer):
    class Meta:
        model = Admin
        fields = ["password", "email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if not uc.checkEmailPattern(email):
            raise serializers.ValidationError("Incorrect email patterm")
        return attrs


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description"]

    def create(self, validated_data):
        return super().create(validated_data)


class AddProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_SubCategory
        fields = ["id", "category", "name", "description"]

    def create(self, validated_data):
        category_id = self.context["category_id"]
        name = validated_data["name"]
        description = validated_data["description"]
        fetch_category = ProductCategory.objects.get(id=category_id)
        if not fetch_category:
            raise serializers.ValidationError("Category doesnt exists")
        sub_category = Product_SubCategory.objects.create(
            category=fetch_category, name=name, description=description
        )

        return sub_category
