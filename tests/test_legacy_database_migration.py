import pytest

from backend.app.scripts.migrate_legacy_database import (
    target_only_account_emails,
    topological_table_order,
)


def test_orders_tables_with_parents_before_children():
    order = topological_table_order(
        {"users", "patient_profiles", "exercise_plans", "exercise_plan_items"},
        [
            ("patient_profiles", "users"),
            ("exercise_plans", "patient_profiles"),
            ("exercise_plan_items", "exercise_plans"),
        ],
    )
    assert order.index("users") < order.index("patient_profiles")
    assert order.index("patient_profiles") < order.index("exercise_plans")
    assert order.index("exercise_plans") < order.index("exercise_plan_items")


def test_rejects_foreign_key_cycles():
    with pytest.raises(RuntimeError, match="cycle"):
        topological_table_order({"one", "two"}, [("one", "two"), ("two", "one")])


def test_detects_accounts_created_only_in_movena():
    assert target_only_account_emails(
        ["existing@example.com"],
        [" EXISTING@example.com ", "new@movena.example"],
    ) == {"new@movena.example"}
