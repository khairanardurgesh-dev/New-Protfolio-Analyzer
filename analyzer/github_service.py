import requests

def get_github_repos(username):
    try:
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ GitHub API error for repos: {response.status_code}")
            return None
        
        repos = response.json()
        repo_data = []
        
        for repo in repos:
            repo_data.append({
                "name": repo["name"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "language": repo["language"]
            })
        
        return repo_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub API request failed for repos: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in get_github_repos: {e}")
        return None

def get_github_profile(username):
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ GitHub API error for profile: {response.status_code}")
            return None
        
        user = response.json()
        
        return {
            "avatar_url": user.get("avatar_url"),
            "username": user.get("login"),
            "followers": user.get("followers"),
            "public_repos": user.get("public_repos"),
            "profile_url": user.get("html_url"),
            "name": user.get("name"),
            "bio": user.get("bio")
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub API request failed for profile: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in get_github_profile: {e}")
        return None