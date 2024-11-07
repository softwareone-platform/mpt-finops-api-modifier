import time
import logging
import jwt
from app import settings
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError

JWT_SECRET = settings.secret
JWT_ALGORITHM = settings.algorithm
JWT_AUDIENCE = settings.audience
JWT_ISSUER = settings.issuer

logger = logging.getLogger("auth_jwt")


def decode_jwt(token: str) -> dict | None:
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
    def __init__(self, auto_error: bool = True):
        """

        :param auto_error: When auto_error=True, HTTPBearer will raise a 403 error
         without reaching any custom logic.
         To allow more granular error messages, set it to False.

        :type auto_error: bool
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not verify_jwt(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            # The authentication schema is not Bearer
            raise HTTPException(status_code=401, detail="Invalid authorization scheme.")
