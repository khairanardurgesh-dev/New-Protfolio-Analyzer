import requests

def get_github_repos(username):
    url = f"https://api.github.com/users/{username}/repos"

    response = requests.get(url)

    if response.status_code != 200:
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

def get_github_profile(username):
    url = f"https://api.github.com/users/{username}"

    response = requests.get(url)

    if response.status_code != 200:
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