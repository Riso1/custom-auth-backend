from .models import AccessRule, User


def check_permission(
    user: User,
    resource_code: str,
    action: str,
) -> bool:
    """
    Проверяет, может ли пользователь выполнить действие
    над указанным ресурсом.
    """

    if not user.role:
        return False

    rule = (
        AccessRule.objects
        .filter(
            role=user.role,
            element__code=resource_code,
        )
        .first()
    )

    if not rule:
        return False

    permissions_map = {
        'read': (
            rule.read_permission
            or rule.read_all_permission
        ),
        'create': rule.create_permission,
        'update': (
            rule.update_permission
            or rule.update_all_permission
        ),
        'delete': (
            rule.delete_permission
            or rule.delete_all_permission
        ),
    }

    return permissions_map.get(action, False)