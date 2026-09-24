"""Stop the existing staging stack without deleting application data.

Read-only by default. Uses GitHub OIDC credentials and the existing AWS CLI.
The load balancer is stateless and is recreated by Terraform upon authorized resume.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ACCOUNT = "720466551087"
REGION = "eu-central-1"
STACK = "movena-staging"
DOMAIN = "d1ylxhoq5y66vd.cloudfront.net"


def aws(*args):
    result = subprocess.run(
        ["aws", *args, "--region", REGION, "--output", "json", "--no-cli-pager"],
        check=True, capture_output=True, text=True, timeout=90,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


def suspend(call=aws, apply=False):
    identity = call("sts", "get-caller-identity")
    if identity["Account"] != ACCOUNT:
        raise RuntimeError("Refusing to operate in a different AWS account")

    service = call("ecs", "describe-services", "--cluster", STACK,
                   "--services", "backend")["services"][0]
    database = call("rds", "describe-db-instances", "--db-instance-identifier",
                    STACK)["DBInstances"][0]
    lbs = [lb for lb in call("elbv2", "describe-load-balancers")["LoadBalancers"]
           if lb["LoadBalancerName"] == STACK]
    distributions = call("cloudfront", "list-distributions")["DistributionList"].get("Items", [])
    distributions = [d for d in distributions if d["DomainName"] == DOMAIN]
    if len(distributions) != 1 or distributions[0]["Comment"] != STACK:
        raise RuntimeError("Expected CloudFront distribution identity did not match")
    schedules = call("scheduler", "list-schedules", "--name-prefix", STACK + "-").get("Schedules", [])
    autoscaling = call("application-autoscaling", "describe-scalable-targets",
                       "--service-namespace", "ecs", "--resource-ids",
                       f"service/{STACK}/backend").get("ScalableTargets", [])
    # Do not allow an unknown scaling policy to restart tasks behind our back.
    if autoscaling:
        raise RuntimeError("Unexpected ECS autoscaling target; review before suspension")

    state = {
        "apply": apply, "cluster": STACK,
        "ecs_desired": service["desiredCount"], "ecs_running": service["runningCount"],
        "ecs_pending": service["pendingCount"], "database_status": database["DBInstanceStatus"],
        "load_balancers": [lb["LoadBalancerName"] for lb in lbs],
        "cloudfront_enabled": distributions[0]["Enabled"],
        "cloudfront_status": distributions[0]["Status"],
        "schedules": [{"name": s["Name"], "state": s["State"]} for s in schedules],
    }
    print(json.dumps(state), flush=True)
    if not apply:
        return state

    # Preserve schedule definitions but prevent any old startup schedule firing.
    for schedule in schedules:
        if schedule["State"] == "DISABLED":
            continue
        definition = call("scheduler", "get-schedule", "--name", schedule["Name"],
                          "--group-name", schedule["GroupName"])
        fields = ["Name", "GroupName", "Description", "ScheduleExpression",
                  "ScheduleExpressionTimezone", "StartDate", "EndDate",
                  "FlexibleTimeWindow", "Target", "KmsKeyArn", "ActionAfterCompletion"]
        update = {k: definition[k] for k in fields if k in definition}
        update["State"] = "DISABLED"
        call("scheduler", "update-schedule", "--cli-input-json", json.dumps(update))
    if service["desiredCount"] != 0:
        call("ecs", "update-service", "--cluster", STACK, "--service", "backend",
             "--desired-count", "0")
        print("Requested ECS scale-down to zero", flush=True)
    if database["DBInstanceStatus"] == "available":
        call("rds", "stop-db-instance", "--db-instance-identifier", STACK)
        print("Requested RDS stop; database storage and backups retained", flush=True)
    elif database["DBInstanceStatus"] not in {"stopped", "stopping", "starting", "backing-up", "modifying", "maintenance"}:
        raise RuntimeError("Unexpected RDS state: " + database["DBInstanceStatus"])
    else:
        print("RDS state: " + database["DBInstanceStatus"] + "; hourly guard will retry if necessary", flush=True)
    distribution = distributions[0]
    if distribution["Enabled"]:
        current = call("cloudfront", "get-distribution-config", "--id", distribution["Id"])
        config = current["DistributionConfig"]
        config["Enabled"] = False
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "distribution.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            call("cloudfront", "update-distribution", "--id", distribution["Id"],
                 "--if-match", current["ETag"], "--distribution-config", "file://" + str(path))
        print("Disabled CloudFront serving", flush=True)
    for lb in lbs:
        # Only the stateless ALB is removed; never delete RDS, EFS, S3 or secrets.
        call("elbv2", "modify-load-balancer-attributes", "--load-balancer-arn", lb["LoadBalancerArn"],
             "--attributes", "Key=deletion_protection.enabled,Value=false")
        call("elbv2", "delete-load-balancer", "--load-balancer-arn", lb["LoadBalancerArn"])
        print("Removed stateless load balancer to stop hourly charges", flush=True)
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    suspend(apply=parser.parse_args().apply)
