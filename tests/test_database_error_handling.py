import asyncio
import json

from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.main import database_exception_handler


def _payload(response):
    return json.loads(response.body.decode("utf-8"))


def test_missing_column_is_reported_as_outdated_schema():
    error = OperationalError(
        "SELECT reviewed_at FROM recovery_coaching_check_ins",
        {},
        Exception("no such column: recovery_coaching_check_ins.reviewed_at"),
    )

    response = asyncio.run(database_exception_handler(None, error))

    assert response.status_code == 503
    assert _payload(response)["error_code"] == "DATABASE_SCHEMA_OUTDATED"


def test_other_database_errors_remain_temporarily_unavailable():
    response = asyncio.run(
        database_exception_handler(None, SQLAlchemyError("connection refused"))
    )

    assert response.status_code == 503
    assert _payload(response)["error_code"] == "DATABASE_UNAVAILABLE"
