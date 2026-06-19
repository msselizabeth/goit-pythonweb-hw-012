from app.services.auth import hash_helper


def test_password_hash_and_verify():
    """Hashing a password and verifying it should match."""
    password = "mysecret123"
    hashed = hash_helper.get_password_hash(password)

    assert hashed != password  # password should not be stored as plain text
    assert hash_helper.verify_password(password, hashed) is True


def test_wrong_password_fails_verification():
    """Verifying with an incorrect password should fail."""
    password = "mysecret123"
    hashed = hash_helper.get_password_hash(password)

    assert hash_helper.verify_password("wrongpassword", hashed) is False