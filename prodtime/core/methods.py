import json

from django.core.exceptions import BadRequest
from pybitrix24 import Bitrix24

from core.bitrix24.bitrix24 import UserB24


def initial_check(request, entity_type='deal_id'):
    """Метод начальной проверки на тип запроса."""
    auth_id = ''

    if request.method == 'POST':
        member_id: str = request.POST['member_id']
        entity_id: int = int(json.loads(
            request.POST['PLACEMENT_OPTIONS'])['ID'])
        if 'AUTH_ID' in request.POST:
            auth_id: str = request.POST.get('AUTH_ID')
    elif request.method == 'GET':
        member_id: str = request.GET.get('member_id')
        entity_id: int = int(request.GET.get(entity_type))
    else:
        raise BadRequest

    return member_id, entity_id, auth_id


def get_current_user(request, auth_id, portal, is_admin_code):
    """Метод получения текущего пользователя."""
    user_id = 0
    print(auth_id)

    if auth_id:
        bx24_for_user = Bitrix24(portal.name)
        bx24_for_user._access_token = auth_id
        user_result = bx24_for_user.call('user.current')
        if 'result' in user_result:
            user_id = user_result.get('result').get('ID')
    elif 'user_id' in request.COOKIES and request.COOKIES.get('user_id'):
        user_id = request.COOKIES.get('user_id')
    else:
        return {
            'user_id': 0,
            'name': 'Анонимный',
            'lastname': 'пользователь',
            'photo': None,
            'is_admin': 'N',
        }

    user = UserB24(portal, int(user_id))
    return {
        'user_id': user_id,
        'name': user.properties[0].get('NAME'),
        'lastname': user.properties[0].get('LAST_NAME'),
        'photo': user.properties[0].get('PERSONAL_PHOTO'),
        'is_admin': user.properties[0].get(is_admin_code),
    }
