[CmdletBinding()]
param(
    [string]$Region = "eu-central-1",
    [ValidateSet("staging", "production")][string]$Environment = "staging",
    [ValidateRange(1, 90)][int]$Days = 30
)

# Read-only inventory, account costs, and utilization. Never reads runtime secrets.
$ErrorActionPreference = "Stop"
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    throw "Install AWS CLI v2 and authenticate with your AWS profile first."
}

function Read-Aws([string[]]$Arguments) {
    $response = & aws @Arguments --output json --no-cli-pager
    if ($LASTEXITCODE -ne 0) {
        throw "AWS read failed: $($Arguments[0]) $($Arguments[1]). No resources were changed."
    }
    return ($response | ConvertFrom-Json)
}

$end = [DateTime]::UtcNow.Date
$start = $end.AddDays(-$Days)
$cluster = "movena-$Environment"
$identity = Read-Aws -Arguments @("sts", "get-caller-identity", "--region", $Region)
Write-Host "Account $($identity.Account), $cluster in $Region"
Write-Host "Costs below cover the WHOLE ACCOUNT, grouped by service and region; they are not a Movena-only bill."
Write-Host "Cost Explorer can have reporting charges and delayed/estimated data. Failed reads are errors, never zero cost."
$costArgs = @("ce", "get-cost-and-usage", "--region", "us-east-1", "--time-period", "Start=$($start.ToString('yyyy-MM-dd')),End=$($end.ToString('yyyy-MM-dd'))", "--granularity", "MONTHLY", "--metrics", "UnblendedCost", "--group-by", "Type=DIMENSION,Key=SERVICE", "Type=DIMENSION,Key=REGION")
do {
    $page = Read-Aws -Arguments $costArgs
    foreach ($period in $page.ResultsByTime) {
        Write-Host "$($period.TimePeriod.Start) to $($period.TimePeriod.End) (end exclusive), estimated: $($period.Estimated)"
        $period.Groups | ForEach-Object {
            [PSCustomObject]@{
                Service = $_.Keys[0]
                Region = $_.Keys[1]
                Cost = $_.Metrics.UnblendedCost.Amount
                Currency = $_.Metrics.UnblendedCost.Unit
            }
        } | Format-Table -AutoSize
    }
    $costArgs = $costArgs[0..($costArgs.IndexOf("--group-by") + 2)]
    if ($page.NextPageToken) { $costArgs += @("--next-page-token", $page.NextPageToken) }
} while ($page.NextPageToken)

$service = Read-Aws -Arguments @("ecs", "describe-services", "--region", $Region, "--cluster", $cluster, "--services", "backend")
if ($service.failures.Count -gt 0 -or $service.services.Count -ne 1) { throw "Backend service unavailable; inspect AWS identity, region, and environment." }
$service.services | Select-Object serviceName, desiredCount, runningCount, pendingCount, taskDefinition | Format-List
$task = Read-Aws -Arguments @("ecs", "describe-task-definition", "--region", $Region, "--task-definition", $service.services[0].taskDefinition)
$task.taskDefinition | Select-Object cpu, memory | Format-List
$database = Read-Aws -Arguments @("rds", "describe-db-instances", "--region", $Region, "--db-instance-identifier", $cluster)
$database.DBInstances | Select-Object DBInstanceIdentifier, DBInstanceClass, DBInstanceStatus, MultiAZ, AllocatedStorage | Format-List

foreach ($metric in @("CPUUtilization", "MemoryUtilization")) {
    $usage = Read-Aws -Arguments @("cloudwatch", "get-metric-statistics", "--region", $Region, "--namespace", "AWS/ECS", "--metric-name", $metric, "--dimensions", "Name=ClusterName,Value=$cluster", "Name=ServiceName,Value=backend", "--start-time", $start.ToString("yyyy-MM-ddTHH:mm:ssZ"), "--end-time", $end.ToString("yyyy-MM-ddTHH:mm:ssZ"), "--period", "86400", "--statistics", "Average", "Maximum")
    Write-Host "$metric (% of allocated task capacity), daily average and peak:"
    if ($usage.Datapoints.Count -eq 0) {
        Write-Warning "No utilization measurements available. Do not interpret missing metrics as idle capacity."
    } else {
        $usage.Datapoints | Sort-Object Timestamp | Select-Object Timestamp, Average, Maximum | Format-Table -AutoSize
    }
}
