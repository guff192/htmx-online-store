from ...services.auth_service import get_auth_service


service = get_auth_service()


def test_create_access_token():
    token = service.create_access_token({'sub': '066b2931e8b4417b9801e6f89ab19b30'})
    print(token)

