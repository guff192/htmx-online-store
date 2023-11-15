from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from exceptions.auth_exceptions import ErrWrongCredentials
from services.auth_service import AuthService


class LoginMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        auth_service: AuthService
    ) -> None:
        super().__init__(app)
        self._service = auth_service

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        session_cookie = request.cookies.get('_session')
        if not session_cookie:
            request.state.user = None
            return await call_next(request)

        try:
            user = self._service.verify_session_token(session_cookie)
        except ErrWrongCredentials:
            user = None

        request.state.user = user

        return await call_next(request)


class AdminMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        admin_path: str = '/admin',
    ) -> None:
        super().__init__(app)
        self.admin_path = admin_path

    def _check_admin(
        self,
        request: Request,
    ) -> bool:
        if not hasattr(request.state, 'user'):
            return False

        if request.state.user and request.state.user.is_admin:
            return True
        return False

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        client, path = request.client, request.url.path
        logger.debug(f'{path = }\n\n')

        # Check the path
        if not path.startswith(self.admin_path):
            return await call_next(request)
        if path.startswith(self.admin_path + '/static'):
            return await call_next(request)

        if not client or not client.host or not self._check_admin(request):
            return RedirectResponse('/')

        return await call_next(request)

