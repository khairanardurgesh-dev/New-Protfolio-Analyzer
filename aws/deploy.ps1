# CodePulse PWA AWS Deployment Script (PowerShell)
# Deploy serverless backend to AWS Lambda + API Gateway

Write-Host "🚀 CodePulse AWS Deployment Started" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

# Check AWS CLI
try {
    $awsVersion = aws --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
        Write-Host "Download from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error checking AWS CLI" -ForegroundColor Red
    exit 1
}

# Check AWS credentials
try {
    $awsIdentity = aws sts get-caller-identity --query 'Account' --output text 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ AWS credentials not configured. Run 'aws configure' first." -ForegroundColor Red
        exit 1
    }
    Write-Host "🔐 AWS Account: $awsIdentity" -ForegroundColor Green
    Write-Host "🌍 Region: us-east-1" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials error" -ForegroundColor Red
    exit 1
}

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow

# Create temp directory
$tempDir = Join-Path $env:TEMP "codepulse-deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Copy Lambda function
$packageDir = Join-Path $tempDir "deployment"
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null
Copy-Item "aws\lambda_function.py" -Destination $packageDir

# Install dependencies
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Yellow
try {
    Set-Location $packageDir
    pip install -r "aws\requirements.txt" --target .
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create ZIP package
Write-Host "🗜️ Creating deployment package..." -ForegroundColor Yellow
$zipPath = Join-Path $tempDir "deployment.zip"
Compress-Archive -Path $packageDir -DestinationPath $zipPath -Force

# Deploy CloudFormation stack
Write-Host "🚀 Deploying CloudFormation stack..." -ForegroundColor Yellow

$stackName = "codepulse-stack"
$templateFile = "aws\template.yaml"

try {
    # Check if stack exists
    $stackExists = aws cloudformation describe-stacks --stack-name $stackName --query 'Stacks[0].StackStatus' --output text 2>$null
    
    if ($LASTEXITCODE -eq 0 -and $stackExists -eq "UPDATE_COMPLETE") {
        Write-Host "🔄 Stack exists, updating..." -ForegroundColor Yellow
        aws cloudformation update-stack `
            --stack-name $stackName `
            --template-body file://$templateFile `
            --parameters ParameterKey=TableName,ParameterValue=codepulse-analyses `
                        ParameterKey=GitHubToken,ParameterValue="" `
            --capabilities CAPABILITY_IAM `
            --region us-east-1
    } else {
        Write-Host "🆕 Creating new stack..." -ForegroundColor Yellow
        aws cloudformation create-stack `
            --stack-name $stackName `
            --template-body file://$templateFile `
            --parameters ParameterKey=TableName,ParameterValue=codepulse-analyses `
                        ParameterKey=GitHubToken,ParameterValue="" `
            --capabilities CAPABILITY_IAM `
            --region us-east-1 `
            --on-failure ROLLBACK
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Stack deployment failed"
    }
    
    Write-Host "⏳ Waiting for stack deployment..." -ForegroundColor Yellow
    
    # Wait for deployment
    $maxAttempts = 60
    $attempt = 0
    
    do {
        $attempt++
        Write-Host "Checking deployment status... (Attempt $attempt/$maxAttempts)" -ForegroundColor Cyan
        
        $status = aws cloudformation describe-stacks --stack-name $stackName --query 'Stacks[0].StackStatus' --output text 2>$null
        
        if ($status -eq "CREATE_COMPLETE" -or $status -eq "UPDATE_COMPLETE") {
            Write-Host "✅ Stack deployment complete!" -ForegroundColor Green
            break
        } elseif ($status -eq "CREATE_FAILED" -or $status -eq "UPDATE_FAILED" -or $status -eq "ROLLBACK_COMPLETE") {
            Write-Host "❌ Stack deployment failed!" -ForegroundColor Red
            $errorReason = aws cloudformation describe-stacks --stack-name $stackName --query 'Stacks[0].StackStatusReason' --output text 2>$null
            Write-Host "Error: $errorReason" -ForegroundColor Red
            exit 1
        }
        
        Start-Sleep -Seconds 10
    } while ($attempt -lt $maxAttempts)
    
} catch {
    Write-Host "❌ Stack deployment failed: $_" -ForegroundColor Red
    exit 1
}

# Update Lambda function code
Write-Host "🔄 Updating Lambda function code..." -ForegroundColor Yellow

try {
    aws lambda update-function-code `
        --function-name codepulse-analysis `
        --zip-file file://$zipPath `
        --region us-east-1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Lambda update failed"
    }
    
    Write-Host "✅ Lambda function updated!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Lambda update failed: $_" -ForegroundColor Red
    exit 1
}

# Get API endpoint
Write-Host "🌐 Getting API endpoint..." -ForegroundColor Yellow

try {
    $apiEndpoint = aws cloudformation describe-stacks --stack-name $stackName --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Green
        Write-Host "🌐 API Endpoint: $apiEndpoint" -ForegroundColor Cyan
        Write-Host "📱 PWA Manifest: $apiEndpoint/static/manifest.json" -ForegroundColor Cyan
        Write-Host "🔧 Service Worker: $apiEndpoint/static/service-worker.js" -ForegroundColor Cyan
        Write-Host "=" * 50 -ForegroundColor Green
        Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
        Write-Host "1. Update frontend API calls to use: $apiEndpoint" -ForegroundColor White
        Write-Host "2. Test PWA installation in browser" -ForegroundColor White
        Write-Host "3. Configure GitHub token in AWS Lambda environment" -ForegroundColor White
        Write-Host "4. Set up environment variables in AWS Lambda console" -ForegroundColor White
        Write-Host "=" * 50 -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to get API endpoint" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error getting API endpoint: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item $tempDir -Recurse -Force
Write-Host "🧹 Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 AWS Deployment Summary:" -ForegroundColor Green
Write-Host "✅ CloudFormation Stack: $stackName" -ForegroundColor White
Write-Host "✅ Lambda Function: codepulse-analysis" -ForegroundColor White
Write-Host "✅ API Gateway: codepulse-api" -ForegroundColor White
Write-Host "✅ Region: us-east-1" -ForegroundColor White
Write-Host "✅ Runtime: Python 3.9" -ForegroundColor White
Write-Host "✅ Architecture: Serverless (Lambda + API Gateway)" -ForegroundColor White
