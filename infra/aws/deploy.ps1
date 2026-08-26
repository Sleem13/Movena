[CmdletBinding()]
param(
    [string]$Region = "eu-central-1",
    [ValidateSet("staging", "production")][string]$Environment = "staging",
    [string]$AppVersion = (Get-Date -Format "yyyyMMddHHmmss"),
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$TerraformDir = $PSScriptRoot
$SecretName = "physiovision/$Environment/app"

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is required but was not found in PATH."
    }
}

function New-RandomSecret {
    $bytes = New-Object byte[] 48
    [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes)
}

function Get-PlainText([Security.SecureString]$Value) {
    return ([PSCredential]::new("secret", $Value)).GetNetworkCredential().Password
}

Require-Command aws
Require-Command docker
Require-Command terraform
Require-Command npm

$Identity = aws sts get-caller-identity --region $Region --output json | ConvertFrom-Json
Write-Host "AWS account: $($Identity.Account) | principal: $($Identity.Arn) | region: $Region" -ForegroundColor Cyan
Write-Warning "This stack creates billable ECS Fargate, Application Load Balancer, RDS PostgreSQL, EFS, CloudFront, S3, ECR, CloudWatch, and Secrets Manager resources."

$SecretArn = aws secretsmanager describe-secret --secret-id $SecretName --region $Region --query ARN --output text 2>$null
if ($LASTEXITCODE -ne 0) {
    if (-not $Apply) {
        throw "Secret $SecretName does not exist. Re-run with -Apply to create it interactively."
    }
    $AdminEmail = Read-Host "Protected super-admin email"
    $AdminName = Read-Host "Protected super-admin display name"
    $AdminPasswordSecure = Read-Host "Protected super-admin password" -AsSecureString
    $SecretPayload = @{
        SECRET_KEY          = New-RandomSecret
        SUPER_ADMIN_EMAIL   = $AdminEmail
        SUPER_ADMIN_FULL_NAME = $AdminName
        SUPER_ADMIN_PASSWORD = Get-PlainText $AdminPasswordSecure
    }
    $SecretFile = [IO.Path]::GetTempFileName()
    try {
        $SecretPayload | ConvertTo-Json -Compress | Set-Content -LiteralPath $SecretFile -Encoding utf8NoBOM
        $SecretArn = aws secretsmanager create-secret --name $SecretName --description "PhysioVision $Environment runtime secrets" --secret-string "file://$SecretFile" --region $Region --query ARN --output text
        if ($LASTEXITCODE -ne 0) { throw "Failed to create the application secret." }
    }
    finally {
        if (Test-Path -LiteralPath $SecretFile) { Remove-Item -LiteralPath $SecretFile -Force }
        $SecretPayload.Clear()
        $AdminPasswordSecure.Dispose()
    }
}

terraform -chdir=$TerraformDir init
if ($LASTEXITCODE -ne 0) { throw "terraform init failed." }

if (-not $Apply) {
    terraform -chdir=$TerraformDir plan -var "aws_region=$Region" -var "environment=$Environment" -var "app_version=$AppVersion" -var "app_secret_arn=$SecretArn"
    exit $LASTEXITCODE
}

# Bootstrap the private registry before building the application image.
terraform -chdir=$TerraformDir apply -auto-approve -target=aws_ecr_repository.backend -var "aws_region=$Region" -var "environment=$Environment" -var "app_version=$AppVersion" -var "app_secret_arn=$SecretArn"
$RepositoryUrl = terraform -chdir=$TerraformDir output -raw ecr_repository_url
$Registry = $RepositoryUrl.Split('/')[0]
$Image = "$RepositoryUrl`:$AppVersion"

aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $Registry
docker build --pull --tag $Image $RepoRoot
docker push $Image

$PlanFile = Join-Path $TerraformDir "physiovision.tfplan"
terraform -chdir=$TerraformDir plan -out=$PlanFile -var "aws_region=$Region" -var "environment=$Environment" -var "app_version=$AppVersion" -var "app_secret_arn=$SecretArn" -var "backend_image=$Image"
$Confirmation = Read-Host "Review the Terraform plan above. Type DEPLOY to create/update AWS resources"
if ($Confirmation -cne "DEPLOY") {
    Remove-Item -LiteralPath $PlanFile -Force -ErrorAction SilentlyContinue
    throw "Deployment cancelled before infrastructure changes."
}
terraform -chdir=$TerraformDir apply $PlanFile
Remove-Item -LiteralPath $PlanFile -Force -ErrorAction SilentlyContinue

$ApplicationUrl = terraform -chdir=$TerraformDir output -raw application_url
$FrontendBucket = terraform -chdir=$TerraformDir output -raw frontend_bucket
$DistributionId = terraform -chdir=$TerraformDir output -raw cloudfront_distribution_id

Push-Location (Join-Path $RepoRoot "frontend")
try {
    $env:VITE_API_BASE_URL = $ApplicationUrl
    npm ci
    npm test -- --run
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend verification failed." }
    aws s3 sync dist "s3://$FrontendBucket" --delete --region $Region --cache-control "public,max-age=31536000,immutable" --exclude "index.html"
    aws s3 cp dist/index.html "s3://$FrontendBucket/index.html" --region $Region --cache-control "no-cache,no-store,must-revalidate" --content-type "text/html"
}
finally {
    Remove-Item Env:VITE_API_BASE_URL -ErrorAction SilentlyContinue
    Pop-Location
}

aws cloudfront create-invalidation --distribution-id $DistributionId --paths "/*" | Out-Null
aws ecs wait services-stable --cluster "physiovision-$Environment" --services backend --region $Region

$ReadyUrl = "$ApplicationUrl/ready"
for ($attempt = 1; $attempt -le 20; $attempt++) {
    try {
        $Ready = Invoke-RestMethod -Uri $ReadyUrl -TimeoutSec 20
        if ($Ready.status -eq "ready") {
            Write-Host "Deployment ready: $ApplicationUrl" -ForegroundColor Green
            exit 0
        }
    }
    catch { Start-Sleep -Seconds 15 }
}
throw "AWS resources were deployed, but $ReadyUrl did not become ready in time. Check ECS and CloudWatch logs."
