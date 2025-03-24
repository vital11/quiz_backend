import jwt

from typing import Optional, Annotated

from fastapi import HTTPException, status, Depends, Security
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


class VerifyToken:
    """Does all the token verification using PyJWT"""
    def __init__(self):
        self.config = settings

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f'https://{self.config.auth0.DOMAIN}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(
            self,
            security_scopes: SecurityScopes,
            token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())
    ):
        """
        https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/
        The verify method consists of three steps to validate the integrity of the token:
        1. It grabs the token from the Authorization header.
        2. This method uses the key ID (kid claim present in the token header) to grab
        the key used from the JWKS to verify the token signature. If this step fails
        by any of the possible errors, the error message is returned.
        3. Then, the method tries to decode the JWT by using the information gathered so far.
        In case of errors, it returns the error message. When successful, the token payload
        is returned.
        """
        if token is None:
            raise UnauthenticatedException

        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        try:
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=self.config.auth0.ALGORITHMS,
                audience=self.config.auth0.API_AUDIENCE,
                issuer=self.config.auth0.ISSUER,
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        return payload


auth0_token = VerifyToken()

VerifyTokenDep = Annotated[str, Security(auth0_token.verify)]
