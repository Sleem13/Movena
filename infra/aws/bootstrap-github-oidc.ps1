[CmdletBinding()]
param(
    [string]$AccountId = "720466551087",
    [string]$Region = "eu-central-1",
    [string]$Repository = "Sleem13/Movena",
    [string]$Branch = "main",
    [string]$RoleName = "MovenaGitHubDeploy",
    [string]$StateBucket = "movena-terraform-state-720466551087-eu-central-1"
)

$ErrorActionPreference = "Stop"

function Invoke-Aws {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & aws @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "AWS CLI command failed: aws $($Arguments -join ' ')"
    }
}

$identity = Invoke-Aws sts get-caller-identity --output json | ConvertFrom-Json
if ($identity.Account -ne $AccountId) {
    throw "Expected AWS account $AccountId but authenticated to $($identity.Account)."
}

$ErrorActionPreference = "Continue"
aws s3api head-bucket --bucket $StateBucket 2>$null | Out-Null
$bucketExists = $LASTEXITCODE -eq 0
$ErrorActionPreference = "Stop"
if (-not $bucketExists) {
    Invoke-Aws s3api create-bucket --bucket $StateBucket --region $Region --create-bucket-configuration "LocationConstraint=$Region" | Out-Null
}
Invoke-Aws s3api put-public-access-block --bucket $StateBucket --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
Invoke-Aws s3api put-bucket-versioning --bucket $StateBucket --versioning-configuration "Status=Enabled"
Invoke-Aws s3api put-bucket-encryption --bucket $StateBucket --server-side-encryption-configuration 'Rules=[{ApplyServerSideEncryptionByDefault={SSEAlgorithm=AES256},BucketKeyEnabled=true}]'

$providerArn = "arn:aws:iam::$AccountId`:oidc-provider/token.actions.githubusercontent.com"
$providers = Invoke-Aws iam list-open-id-connect-providers --query "OpenIDConnectProviderList[].Arn" --output text
if (($providers -split "\s+") -notcontains $providerArn) {
    Invoke-Aws iam create-open-id-connect-provider `
        --url "https://token.actions.githubusercontent.com" `
        --client-id-list "sts.amazonaws.com" `
        --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" | Out-Null
}

$trust = @{
    Version = "2012-10-17"
    Statement = @(@{
        Effect = "Allow"
        Principal = @{ Federated = $providerArn }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = @{
            StringEquals = @{ "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com" }
            StringLike = @{ "token.actions.githubusercontent.com:sub" = "repo:$Repository`:ref:refs/heads/$Branch" }
        }
    })
}

$iamPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Sid = "ManageMovenaRoles"
            Effect = "Allow"
            Action = @(
                "iam:CreateRole", "iam:DeleteRole", "iam:GetRole", "iam:TagRole", "iam:UntagRole",
                "iam:UpdateAssumeRolePolicy", "iam:PutRolePolicy", "iam:GetRolePolicy", "iam:DeleteRolePolicy",
                "iam:ListRolePolicies", "iam:AttachRolePolicy", "iam:DetachRolePolicy", "iam:ListAttachedRolePolicies",
                "iam:PassRole"
            )
            Resource = "arn:aws:iam::$AccountId`:role/movena-*"
        },
        @{
            Sid = "CreateRequiredServiceLinkedRoles"
            Effect = "Allow"
            Action = "iam:CreateServiceLinkedRole"
            Resource = "arn:aws:iam::$AccountId`:role/aws-service-role/*"
            Condition = @{
                StringLike = @{
                    "iam:AWSServiceName" = @(
                        "ecs.amazonaws.com", "elasticloadbalancing.amazonaws.com", "rds.amazonaws.com"
                    )
                }
            }
        }
    )
}

$trustFile = [IO.Path]::GetTempFileName()
$policyFile = [IO.Path]::GetTempFileName()
try {
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($trustFile, ($trust | ConvertTo-Json -Depth 10 -Compress), $utf8)
    [IO.File]::WriteAllText($policyFile, ($iamPolicy | ConvertTo-Json -Depth 10 -Compress), $utf8)

    $ErrorActionPreference = "Continue"
    aws iam get-role --role-name $RoleName --output json 2>$null | Out-Null
    $roleExists = $LASTEXITCODE -eq 0
    $ErrorActionPreference = "Stop"
    if ($roleExists) {
        Invoke-Aws iam update-assume-role-policy --role-name $RoleName --policy-document "file://$trustFile"
    }
    else {
        Invoke-Aws iam create-role --role-name $RoleName --description "GitHub OIDC deployer for Movena" --max-session-duration 7200 --assume-role-policy-document "file://$trustFile" | Out-Null
    }

    Invoke-Aws iam attach-role-policy --role-name $RoleName --policy-arn "arn:aws:iam::aws:policy/PowerUserAccess"
    Invoke-Aws iam put-role-policy --role-name $RoleName --policy-name "MovenaIamDeployment" --policy-document "file://$policyFile"
}
finally {
    Remove-Item -LiteralPath $trustFile, $policyFile -Force -ErrorAction SilentlyContinue
}

[PSCustomObject]@{
    RoleArn = "arn:aws:iam::$AccountId`:role/$RoleName"
    StateBucket = $StateBucket
    Region = $Region
    Repository = $Repository
} | ConvertTo-Json
