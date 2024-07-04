from typing import Annotated
from typing_extensions import Doc
from fastapi import HTTPException, status


class ErrUserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
                )


class ErrAccessDenied(HTTPException):
    def __init__(
        self,
        object_name: Annotated[
            str,
            Doc(
                '''Additional human-readable object name to identify object on client-side'''
            )
        ] = ''
    ) -> None:
        additional_detail = f' to {object_name}' if object_name else ''

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied' + additional_detail
        )


class ErrWrongCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Failed authentication: wrong credentials!'
        )


class ErrUnauthorized(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized'
        )


class ErrUserInvalid(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid user'
        )

