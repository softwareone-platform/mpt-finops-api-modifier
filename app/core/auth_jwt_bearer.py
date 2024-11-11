import logging
import time
from typing import Optional

import jwt
from fastapi import Request
from fastapi import status as http_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from app import settings
from app.core.error_formats import create_error_response

JWT_SECRET = settings.secret
JWT_ALGORITHM = settings.algorithm
JWT_AUDIENCE = settings.audience
JWT_ISSUER = settings.issuer

logger = logging.getLogger("auth_jwt")


def decode_jwt(token: str) -> Optional[dict]:
    """
    this function decodes a JWT token
    and validates time and issuer/audience claims.

    :param token:
    :type token:
    :return:
    :rtype:
    """
    try:
        # Decode token and validate critical claims
        decoded_token = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "nbf", "iss", "aud"]},
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER
        )

        # Check for expiration

        current_time = time.time()
        expire_in = float(decoded_token.get("exp", 0))

        if decoded_token.get("exp", 0) < current_time:
            logger.error("Token has expired")
            return None
        if expire_in < current_time:
            logger.error(f"The token {token} is expired")
            return None
        return decoded_token

    except ExpiredSignatureError:
        logger.error(f"Expired Signature for the {token}")
    except DecodeError:
        logger.error(f"The token {token} cannot be decoded")
    except InvalidTokenError:
        logger.error(f"The token {token} is not valid")
    except Exception as error:
        logger.error(f"General error {error} occurred trying to decode the token {token}")

    return None


def verify_jwt(jw_token: str) -> bool:
    """

    :param jw_token:
    :type jw_token:
    :return:
    :rtype:;
    """
    is_token_valid = False
    payload = decode_jwt(jw_token)
    if payload is not None:
        is_token_valid = True
    return is_token_valid


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        """

        :param auto_error: When auto_error=True, HTTPBearer will raise a 403 error
         without reaching any custom logic.
         To allow more granular error messages, set it to False.

        :type auto_error: bool
        """
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not verify_jwt(credentials.credentials):
                raise create_error_response(status_code=http_status.HTTP_401_UNAUTHORIZED,
                                            title="Invalid token or expired token.",
                                            errors={"reason":
                                                        "The token is invalid or has expired."}
                                            )
            return credentials.credentials
        else:
            # The authentication schema is not Bearer
            raise create_error_response(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                title="Invalid authorization scheme.",
                errors={"reason": "Invalid authorization scheme."}
            )
