from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.connections import get_db
from app.models.personnel import Personnel


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_personnel(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> Personnel:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required or token is invalid.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        personnel_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise unauthorized

    personnel = db.get(Personnel, personnel_id)

    if personnel is None or not personnel.is_active:
        raise unauthorized

    return personnel


def require_roles(*allowed_roles: str):
    normalized_roles = {
        role.strip().lower()
        for role in allowed_roles
    }

    def role_checker(
        current_personnel: Personnel = Depends(get_current_personnel),
    ) -> Personnel:
        current_role = (current_personnel.role or "").strip().lower()

        if current_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_personnel

    return role_checker