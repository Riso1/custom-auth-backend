import bcrypt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .auth import create_token, decode_token
from .models import AuthToken, Role, User, AccessRule
from .serializers import LoginSerializer, RegistrationSerializer, UpdateProfileSerializer, AccessRuleSerializer
from .permissions import check_permission


def get_user_from_request(request) -> User | None:
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    payload = decode_token(token)

    if not payload:
        return None

    token_in_db = AuthToken.objects.filter(
        token=token,
        is_active=True
    ).first()

    if not token_in_db:
        return None

    return User.objects.filter(
        id=payload.get("user_id"),
        is_active=True
    ).first()


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        if data['password'] != data['password_repeat']:
            return Response(
                {'detail': 'Пароли не совпадают.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=data['email']).exists():
            return Response(
                {'detail': 'Пользователь с таким email уже существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        password_hash = bcrypt.hashpw(
            data['password'].encode(),
            bcrypt.gensalt(),
        ).decode()

        default_role = Role.objects.filter(name='Пользователь').first()

        user = User.objects.create(
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data.get('middle_name', ''),
            email=data['email'],
            password_hash=password_hash,
            role=default_role,
        )

        return Response({
            'id': user.id,
            'email': user.email,
            'detail': 'Пользователь зарегистрирован.',
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        user = User.objects.filter(
            email=data['email'],
            is_active=True,
        ).first()

        if not user:
            return Response(
                {'detail': 'Неверный email или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        password_is_correct = bcrypt.checkpw(
            data['password'].encode(),
            user.password_hash.encode()
        )

        if not password_is_correct:
            return Response(
                {'detail': 'Неверный email или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = create_token(user.id)

        AuthToken.objects.create(user=user, token=token,)

        return Response(
            {'token': token, 'detail':'Выполнен вход.'},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return Response(
                {'detail': 'Пользователь не авторизован.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        parts = auth_header.split()

        if len(parts) != 2:
            return Response(
                {'detail': 'Некорректный заголовок Authorization'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = parts[1]

        updated_count = AuthToken.objects.filter(token=token, is_active=True).update(is_active=False)

        if updated_count == 0:
            return Response(
                {'detail': 'Активная сессия не найдена.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {'detail': 'Выход выполнен.'},
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    def get(self,request):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Пользователь не авторизован.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                'id': user.id,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'middle_name': user.middle_name,
                'email': user.email,
                'role': user.role.name if user.role else None,
            }
        )

    def patch(self, request):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Пользователь не авторизован.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UpdateProfileSerializer(
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for field, value in serializer.validated_data.items():
            setattr(user, field, value)

        user.save()

        return Response(
            {'detail': 'Профиль обновлен.'},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Пользователь не авторизован.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.is_active = False
        user.save(update_fields=['is_active'])

        AuthToken.objects.filter(user=user).update(is_active=False)

        return Response(
            {'detail': 'Аккаунт удален.'},
            status=status.HTTP_200_OK,
        )


class ProductsView(APIView):
    def get(self, request):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Требуется авторизация.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_permission(user, 'products', 'read'):
            return Response(
                {'detail': 'Доступ запрещён.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            [
                {
                    'id': 1,
                    'name': 'Ноутбук',
                    'price': 75000,
                },
                {
                    'id': 2,
                    'name': 'Монитор',
                    'price': 20000,
                },
            ]
        )


class OrdersView(APIView):
    def get(self, request):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Требуется авторизация.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_permission(user, 'orders', 'read'):
            return Response(
                {'detail': 'Доступ запрещён.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            [
                {
                    'id': 1,
                    'number': 'ORD-001',
                },
                {
                    'id': 2,
                    'number': 'ORD-002',
                },
            ]
        )


class AccessRulesView(APIView):
    def get(self, request):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Требуется авторизация.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_permission(user, 'access_rules', 'read'):
            return Response(
                {'detail': 'Доступ запрещён.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        rules = AccessRule.objects.select_related('role', 'element').all()
        serializer = AccessRuleSerializer(rules, many=True)

        return Response(serializer.data)


class AccessRuleDetailView(APIView):
    def patch(self, request, rule_id):
        user = get_user_from_request(request)

        if not user:
            return Response(
                {'detail': 'Требуется авторизация.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_permission(user, 'access_rules', 'update'):
            return Response(
                {'detail': 'Доступ запрещён.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        rule = AccessRule.objects.filter(id=rule_id).first()

        if not rule:
            return Response(
                {'detail': 'Правило доступа не найдено.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AccessRuleSerializer(
            rule,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data)

