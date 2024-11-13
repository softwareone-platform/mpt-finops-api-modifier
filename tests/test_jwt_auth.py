import time

import jwt
import pytest
from fastapi import HTTPException

from app import settings
from app.core.auth_jwt_bearer import JWTBearer, decode_jwt, verify_jwt

JWT_SECRET = settings.secret
JWT_ALGORITHM = settings.algorithm
JWT_ISSUER = settings.issuer
JWT_AUDIENCE = settings.audience
SUBJECT = "test"


def create_jwt_token(subject: str, expires_in: int = 3600) -> str:
    """
    Generates a JWT token with the required claims: exp, nbf, iss, aud.

    :param subject: The subject (sub) claim
    :param expires_in: Token validity period in seconds.
    :return: A signed JWT token as a string.
    """
    now = int(time.time())
    expire_time = now + expires_in

    payload = {
        "sub": subject,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": expire_time
    }

    # Encode the token with the specified algorithm and secret
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


class MockRequest:
    def __init__(self, authorization: str = None):
        self.headers = {"Authorization": authorization} if authorization else {}


class TestDecodeJWT:
    def test_decode_jwt_valid_token(self):
        subject = "test"
        token = create_jwt_token(subject=SUBJECT)

        decoded_token = decode_jwt(token)
        assert decoded_token is not None
        assert decoded_token["sub"] == subject
        assert decoded_token["iss"] == JWT_ISSUER
        assert decoded_token["aud"] == JWT_AUDIENCE

    def test_decode_jwt_expired_token(self):
        token = create_jwt_token(subject=SUBJECT, expires_in=-10)  # Expired token

        decoded_token = decode_jwt(token)
        assert decoded_token is None

    def test_invalid_signature(self):
        # modify a token to invalidate the signature
        token = create_jwt_token(subject=SUBJECT)
        invalid_token = token + "AnotherOneBitestheDust"

        # Decode the token and expect None due to signature mismatch
        decoded_token = decode_jwt(invalid_token)
        assert decoded_token is None
        invalid_token_2 = token[:-1] + "ciaocioao"

        # Decode the token and expect None due to invalid token
        decoded_token = decode_jwt(invalid_token_2)
        assert decoded_token is None

    def test_decode_error(self):
        # Provide an invalid token format
        invalid_token = "this.is.not.a.jwt"
        # Decode the token
        decoded_token = decode_jwt(invalid_token)

        # Assert that None is returned due to decode error
        assert decoded_token is None

    def test_decode_jwt_missing_issuer(self):
        payload = {
            "sub": SUBJECT,
            "aud": JWT_AUDIENCE,
            "iat": int(time.time()),
            "nbf": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        decoded_token = decode_jwt(token)
        assert decoded_token is None

    def test_decode_jwt_missing_audience(self):
        payload = {
            "sub": SUBJECT,
            "iss": JWT_ISSUER,
            "iat": int(time.time()),
            "nbf": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        decoded_token = decode_jwt(token)
        assert decoded_token is None

    def test_missing_expires_key(self):
        # Create a token without the "exp" key
        payload = {
            "sub": SUBJECT,
            "iss": JWT_ISSUER,
            "iat": int(time.time()),
            "nbf": int(time.time()),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        decoded_token = decode_jwt(token)
        assert decoded_token is None

    def test_missing_nbf_key(self):
        # Create a token without the "nbf" key
        payload = {
            "sub": SUBJECT,
            "iss": JWT_ISSUER,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,

        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        decoded_token = decode_jwt(token)
        assert decoded_token is None


class TestVerifyJWT:
    def test_valid_jwt(self):
        token = create_jwt_token(subject=SUBJECT)
        assert verify_jwt(token) is True

    def test_invalid_jwt(self):
        invalid_token = "this.is.not.a.jwt"
        assert verify_jwt(invalid_token) is False


@pytest.mark.asyncio
class TestJWTBearer:
    async def test_valid_bearer_token(self):
        token = create_jwt_token(subject=SUBJECT)
        jwt_bearer = JWTBearer(auto_error=False)
        request = MockRequest(authorization=f"Bearer {token}")
        credentials = await jwt_bearer(request)
        assert credentials == token

    async def test_invalid_scheme(self):
        token = create_jwt_token(subject=SUBJECT)
        jwt_bearer = JWTBearer(auto_error=False)
        request = MockRequest(authorization=f"Basic {token}")
        with pytest.raises(HTTPException) as exc_info:
            await jwt_bearer(request)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["title"] == "Invalid authorization scheme."

    async def test_invalid_token(self):
        invalid_token = "invalid.token.here"
        jwt_bearer = JWTBearer(auto_error=False)
        request = MockRequest(authorization=f"Bearer {invalid_token}")
        with pytest.raises(HTTPException) as exc_info:
            await jwt_bearer(request)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["title"] == "Invalid token or expired token."

    async def test_missing_authorization(self):
        jwt_bearer = JWTBearer(auto_error=False)
        request = MockRequest()
        with pytest.raises(HTTPException) as exc_info:
            await jwt_bearer(request)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["title"] == "Invalid authorization scheme."
