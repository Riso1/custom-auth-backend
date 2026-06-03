from rest_framework import serializers
from .models import AccessRule


class RegistrationSerializer(serializers.Serializer):
    last_name = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    email = serializers.EmailField()

    password = serializers.CharField(
        min_length=6,
        write_only=True,
    )

    password_repeat = serializers.CharField(
        min_length=6,
        write_only=True,
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UpdateProfileSerializer(serializers.Serializer):
    last_name = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)

    middle_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )


class AccessRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)
    element_code = serializers.CharField(source='element.code', read_only=True)

    class Meta:
        model = AccessRule
        fields = (
            'id',
            'role',
            'role_name',
            'element',
            'element_name',
            'element_code',
            'read_permission',
            'read_all_permission',
            'create_permission',
            'update_permission',
            'update_all_permission',
            'delete_permission',
            'delete_all_permission',
        )

