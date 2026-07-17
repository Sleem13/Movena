import pytest
import jwt
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password

def test_password_hash_and_verification():
    hashed=get_password_hash("StrongPassword123")
    assert hashed != "StrongPassword123" and verify_password("StrongPassword123",hashed)
    assert not verify_password("wrong",hashed)

def test_jwt_round_trip_and_expiry():
    token=create_access_token("user-1","patient")
    assert decode_access_token(token)["sub"]=="user-1"
    expired=create_access_token("user-1","patient",expires_minutes=-1)
    with pytest.raises(jwt.ExpiredSignatureError): decode_access_token(expired)
