# Available at any hour, with measured cost reductions

The first change removes scheduled downtime. It does not itself reduce the bill:
running ECS and RDS continuously costs more than running them only during working hours.
One API task and single-instance RDS provide an inexpensive baseline, not uninterrupted
availability during failures or database maintenance.

## Apply and verify the availability change

Use the existing GitHub Actions deployment after reviewing these local changes. It
sets `enable_staging_schedule=false`, removes the four Terraform-managed schedules
and their scheduler IAM resources, starts a database left stopped by the previous
schedule, and waits for backend readiness before publishing the frontend. The
workflow no longer shuts the application down after deployment, including failure
cleanup. Do not apply a saved Terraform plan from before this change.

The expected plan must retain the database, EFS, frontend bucket, and application
resources. Investigate any replacement of persistent storage before proceeding.
After deployment confirm one running ECS task, RDS status `available`, no enabled
Movena stop schedules, and `/ready` returning ready. Exercise login, a care-data
read, and a synthetic video analysis. Repeat the readiness check after the old
20:15 Africa/Cairo shutdown boundary. Manually created schedules outside Terraform
must also be inspected in the AWS account.

The manual `deploy.ps1` path does not wake a stopped RDS instance. Prefer GitHub
Actions for this transition, or start the database and wait for availability before
using that script.

## Collect evidence before changing capacity

With AWS CLI v2 and an authenticated read-access profile:

```powershell
./infra/aws/cost-report.ps1 -Region eu-central-1 -Environment staging -Days 30
```

This script reads account-wide service/region costs, ECS capacity and daily
CPU/memory averages and peaks, and RDS configuration. It does not fetch application
secrets or modify resources. Cost Explorer requests may incur reporting charges.
Costs cover completed UTC days, exclude today's partial usage, and may be delayed
or estimated. Account totals include other projects; attribute shared services
before claiming Movena savings. Required reads are `sts:GetCallerIdentity`,
`ce:GetCostAndUsage`, `ecs:DescribeServices`, `ecs:DescribeTaskDefinition`,
`rds:DescribeDBInstances`, and `cloudwatch:GetMetricStatistics`.

Use these results to identify the actual largest costs. Daily averages can conceal
analysis bursts; examine peaks and correlate them with representative video jobs.
Missing metrics and access failures must never be treated as zero usage.

## Reduction candidates, in order

1. Keep the existing no-NAT network, short staging log retention, ECR image expiry,
   and artifact retention. These controls already avoid some unnecessary costs.
2. Benchmark 1 vCPU / 2 GiB (`ecs_cpu=1024`, `ecs_memory=2048`) in an isolated test
   environment against the current 2 vCPU / 4 GiB baseline. Halving both allocations
   halves task CPU/memory charges at the same runtime and rates, not the whole bill.
   Use synthetic videos up to the supported upload limit; verify peak memory,
   concurrent care requests, analysis correctness, and proxy timeout headroom.
   Do not promote if there are OOMs, failed jobs, or unacceptable latency. Restore
   2048/4096 if a later rollout fails. No downsizing is applied by this change.
3. If analysis prevents downsizing, separate it into durable queued jobs with
   on-demand workers while keeping the API warm. This is a separate application
   change requiring persisted job state, retries, idempotency, authorization,
   upload storage and result polling. The current in-process analysis concurrency
   limit is not a durable queue. Do not scale the whole API to zero.
4. Only after establishing steady usage, compare a Compute Savings Plan with
   on-demand rates. Do not buy a commitment against capacity about to be reduced.

No Savings Plan purchase, Spot migration, database replacement, or live capacity
reduction is included. Actual savings require billing evidence and a successful
benchmark. Availability improvements alone are not reported as cost savings.
