import json
import os
import boto3
import requests
from botocore.exceptions import ClientError

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'codepulse-analyses')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

def lambda_handler(event, context):
    """AWS Lambda handler for GitHub portfolio analysis"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    try:
        # Parse request
        if event['httpMethod'] == 'POST':
            body = json.loads(event.get('body', '{}'))
            username = body.get('username', '').strip()
            
            if not username:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Username is required'})
                }
            
            # Get GitHub profile
            profile_data = get_github_profile(username)
            if not profile_data:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'GitHub profile not found'})
                }
            
            # Get GitHub repositories
            repos_data = get_github_repos(username)
            if not repos_data:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': 'Failed to fetch repositories'})
                }
            
            # Analyze portfolio
            analysis = analyze_portfolio(repos_data)
            
            # Save to DynamoDB
            save_analysis(username, analysis)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'profile': profile_data,
                    'analysis': analysis,
                    'timestamp': context.aws_request_id
                })
            }
        
        elif event['httpMethod'] == 'GET':
            # Get analysis history
            username = event.get('queryStringParameters', {}).get('username', '')
            if username:
                history = get_analysis_history(username)
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'history': history})
                }
            
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid request'})
            }
    
    except Exception as e:
        print(f"❌ Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }

def get_github_profile(username):
    """Get GitHub profile with caching"""
    try:
        headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
        response = requests.get(
            f'https://api.github.com/users/{username}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            return None
            
        user = response.json()
        return {
            'avatar_url': user.get('avatar_url'),
            'username': user.get('login'),
            'followers': user.get('followers'),
            'public_repos': user.get('public_repos'),
            'profile_url': user.get('html_url'),
            'name': user.get('name'),
            'bio': user.get('bio')
        }
        
    except Exception as e:
        print(f"❌ GitHub profile error: {e}")
        return None

def get_github_repos(username):
    """Get GitHub repositories with caching"""
    try:
        headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
        response = requests.get(
            f'https://api.github.com/users/{username}/repos',
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            return None
            
        repos = response.json()
        repo_data = []
        
        for repo in repos:
            repo_data.append({
                'name': repo['name'],
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'language': repo['language']
            })
        
        return repo_data
        
    except Exception as e:
        print(f"❌ GitHub repos error: {e}")
        return None

def analyze_portfolio(repos):
    """Analyze GitHub portfolio"""
    repo_count = len(repos)
    total_stars = sum(repo['stars'] for repo in repos)
    
    language_counts = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1
    
    languages = list(language_counts.keys())
    language_count = len(languages)
    
    score = min(100, repo_count * 3 + total_stars * 1 + language_count * 6 - repo_count * 2)
    score = max(0, score)
    
    top_languages_data = []
    if language_counts:
        highest = max(language_counts.values())
        for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:6]:
            percent = int((count / highest) * 100) if highest else 0
            top_languages_data.append({
                'name': lang, 
                'count': count, 
                'percent': percent
            })
    
    strengths = []
    if repo_count > 5:
        strengths.append("Good number of projects")
    if total_stars > 10:
        strengths.append("Projects receiving community interest")
    if language_count > 3:
        strengths.append("Experience with multiple languages")
    
    weaknesses = []
    if repo_count < 3:
        weaknesses.append("Build more projects")
    if language_count < 2:
        weaknesses.append("Learn another programming language")
    
    return {
        'score': score,
        'repo_count': repo_count,
        'stars': total_stars,
        'languages': languages,
        'language_counts': language_counts,
        'top_languages': top_languages_data,
        'strengths': strengths,
        'weaknesses': weaknesses
    }

def save_analysis(username, analysis):
    """Save analysis to DynamoDB"""
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        item = {
            'username': username,
            'timestamp': str(int(context.aws_request_id)),
            'analysis': analysis,
            'ttl': int(time.time()) + 86400 * 30  # 30 days TTL
        }
        
        table.put_item(Item=item)
        print(f"✅ Analysis saved for {username}")
        
    except ClientError as e:
        print(f"❌ DynamoDB save error: {e}")

def get_analysis_history(username):
    """Get analysis history from DynamoDB"""
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        response = table.query(
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': username},
            ScanIndexForward=False,
            Limit=10
        )
        
        return response.get('Items', [])
        
    except ClientError as e:
        print(f"❌ DynamoDB query error: {e}")
        return []
