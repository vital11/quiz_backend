from fastapi import HTTPException, status


class UnauthenticatedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 401"""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or "Could not validate credentials"
        )


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )



