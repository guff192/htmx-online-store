from fastapi import HTTPException, status


class ErrWrongCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Failed authentication: wrong credentials!'
        )


class ErrUserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

