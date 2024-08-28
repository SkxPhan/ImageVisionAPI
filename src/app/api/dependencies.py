from sqlalchemy.orm import Session

import app.models as models


def get_user(username: str | None, db: Session) -> models.UserORM | None:
    if username is None:
        return None

    user = (
        db.query(models.UserORM)
        .filter(models.UserORM.username == username)
        .first()
    )

    return user or None
