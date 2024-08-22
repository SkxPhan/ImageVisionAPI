from datetime import datetime

import pytest

from app.database import TokenBlacklistORM


@pytest.mark.integration
def test_create_token_blacklist(db_session):
    token = "testtoken123"
    expires_at = datetime.now()

    new_token = TokenBlacklistORM(token=token, expires_at=expires_at)
    db_session.add(new_token)
    db_session.commit()

    result = db_session.query(TokenBlacklistORM).filter_by(token=token).first()
    assert result is not None
    assert result.token == token
    assert result.expires_at == expires_at
