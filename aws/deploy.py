#!/usr/bin/env python3
"""
AWS Deployment Script for CodePulse PWA
Deploy serverless backend to AWS Lambda + API Gateway
"""

import os
import json
import boto3
import zipfile
import subprocess
from pathlib import Path

# Configuration
AWS_REGION = 'us-east-1'
FUNCTION_NAME = 'codepulse-analysis'
STACK_NAME = 'codepulse-stack'
TEMPLATE_FILE = 'aws/template.yaml'
LAMBDA_FILE = 'aws/lambda_function.py'
REQUIREMENTS_FILE = 'aws/requirements.txt'

def create_deployment_package():
    """Create ZIP package for Lambda deployment"""
    print("📦 Creating deployment package...")
    
    # Create temporary directory
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    package_dir = os.path.join(temp_dir, 'deployment')
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy Lambda function
    shutil.copy2(LAMBDA_FILE, package_dir)
    
    # Install requirements
    print("📚 Installing dependencies...")
    subprocess.run([
        'pip', 'install', '-r', REQUIREMENTS_FILE, 
        '--target', package_dir
    ], check=True)
    
    # Create ZIP file
    zip_path = os.path.join(temp_dir, 'deployment.zip')
    print("🗜️ Creating deployment package...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Package created: {zip_path}")
    return zip_path

def deploy_stack():
    """Deploy CloudFormation stack"""
    print("🚀 Deploying CloudFormation stack...")
    
    cloudformation = boto3.client('cloudformation', region_name=AWS_REGION)
    
    # Read template
    with open(TEMPLATE_FILE, 'r') as f:
        template_body = f.read()
    
    # Deploy parameters
    parameters = [
        {
            'ParameterKey': 'TableName',
            'ParameterValue': 'codepulse-analyses'
        },
        {
            'ParameterKey': 'GitHubToken',
            'ParameterValue': os.getenv('GITHUB_TOKEN', '')
        }
    ]
    
    try:
        response = cloudformation.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_IAM'],
            OnFailure='ROLLBACK'
        )
        
        print(f"✅ Stack creation initiated: {response['StackId']}")
        return True
        
    except cloudformation.exceptions.ClientError as e:
        if 'already exists' in str(e):
            print("🔄 Stack already exists, updating...")
            response = cloudformation.update_stack(
                StackName=STACK_NAME,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_IAM']
            )
            print(f"✅ Stack update initiated: {response['StackId']}")
        else:
            print(f"❌ Stack deployment failed: {e}")
            return False
    
    return True

def update_lambda_code():
    """Update Lambda function code"""
    print("🔄 Updating Lambda function code...")
    
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    try:
        with open(zip_path, 'rb') as f:
            lambda_client.update_function_code(
                FunctionName=FUNCTION_NAME,
                ZipFile=f.read()
            )
        
        print("✅ Lambda function code updated")
        
        # Clean up
        os.unlink(zip_path)
        return True
        
    except Exception as e:
        print(f"❌ Lambda update failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 CodePulse AWS Deployment Started")
    print("=" * 50)
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"🔐 AWS Account: {identity['Account']}")
        print(f"🌍 Region: {AWS_REGION}")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return
    
    # Deploy stack
    if deploy_stack():
        print("⏳ Waiting for stack deployment...")
        
        # Wait for stack creation
        cloudformation = boto3.client('cloudformation', region_name=AWS_REGION)
        
        waiter = cloudformation.get_waiter('stack_create_complete')
        waiter.wait(
            StackName=STACK_NAME,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 60
            }
        )
        
        print("✅ Stack deployment complete")
        
        # Update Lambda code
        if update_lambda_code():
            print("✅ Lambda function updated")
            
            # Get API endpoint
            response = cloudformation.describe_stacks(
                StackName=STACK_NAME
            )
            
            for output in response['Stacks'][0]['Outputs']:
                if output['OutputKey'] == 'ApiEndpoint':
                    api_endpoint = output['OutputValue']
                    print(f"🌐 API Endpoint: {api_endpoint}")
                    print(f"📱 PWA Manifest: {api_endpoint}/static/manifest.json")
                    print("=" * 50)
                    print("🎉 Deployment complete!")
                    print("\nNext steps:")
                    print("1. Update frontend API calls to use:", api_endpoint)
                    print("2. Test PWA installation")
                    print("3. Configure GitHub token in AWS Lambda environment")
        else:
            print("❌ Lambda update failed")

if __name__ == '__main__':
    main()
