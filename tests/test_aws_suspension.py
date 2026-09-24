import runpy
from pathlib import Path

import pytest


MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "infra/aws/suspend.py"))


def fake_aws(account="720466551087", already_stopped=False):
    calls = []

    def call(*args):
        calls.append(args)
        responses = {
            ("sts", "get-caller-identity"): {"Account": account},
            ("ecs", "describe-services"): {"services": [{"desiredCount": 0 if already_stopped else 1, "runningCount": 0, "pendingCount": 0}]},
            ("rds", "describe-db-instances"): {"DBInstances": [{"DBInstanceStatus": "stopped" if already_stopped else "available"}]},
            ("elbv2", "describe-load-balancers"): {"LoadBalancers": [] if already_stopped else [
                {"LoadBalancerName": "other-app", "LoadBalancerArn": "other"},
                {"LoadBalancerName": "movena-staging", "LoadBalancerArn": "target"}]},
            ("cloudfront", "list-distributions"): {"DistributionList": {"Items": [{
                "Id": "distribution", "DomainName": MODULE["DOMAIN"], "Comment": "movena-staging",
                "Enabled": not already_stopped, "Status": "Deployed"}]}},
            ("cloudfront", "get-distribution-config"): {"ETag": "etag", "DistributionConfig": {"Enabled": True}},
            ("scheduler", "list-schedules"): {"Schedules": []},
            ("application-autoscaling", "describe-scalable-targets"): {"ScalableTargets": []},
        }
        return responses.get(args[:2], {})

    return call, calls


def mutations(calls):
    return [c for c in calls if c[1].startswith(("update-", "stop-", "delete-", "modify-"))]


def test_inspection_never_mutates_resources():
    call, calls = fake_aws()
    MODULE["suspend"](call)
    assert not mutations(calls)


def test_suspension_stops_compute_but_deletes_only_matching_stateless_alb():
    call, calls = fake_aws()
    MODULE["suspend"](call, apply=True)
    assert ("rds", "stop-db-instance", "--db-instance-identifier", "movena-staging") in calls
    assert any(c[:2] == ("ecs", "update-service") and c[-2:] == ("--desired-count", "0") for c in calls)
    assert [c for c in calls if c[1].startswith("delete-")] == [
        ("elbv2", "delete-load-balancer", "--load-balancer-arn", "target")]


def test_guard_is_idempotent_when_stack_is_stopped():
    call, calls = fake_aws(already_stopped=True)
    MODULE["suspend"](call, apply=True)
    assert not mutations(calls)


def test_wrong_account_is_rejected_before_mutation():
    call, calls = fake_aws(account="other")
    with pytest.raises(RuntimeError, match="different AWS account"):
        MODULE["suspend"](call, apply=True)
    assert not mutations(calls)
