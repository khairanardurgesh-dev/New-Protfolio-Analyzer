def analyze_portfolio(repos):

    repo_count = len(repos)

    total_stars = sum(repo["stars"] for repo in repos)

    language_counts = {}
    for repo in repos:
        lang = repo.get("language")
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
            top_languages_data.append({"name": lang, "count": count, "percent": percent})

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
        "score": score,
        "repo_count": repo_count,
        "stars": total_stars,
        "languages": languages,
        "language_counts": language_counts,
        "top_languages": top_languages_data,
        "strengths": strengths,
        "weaknesses": weaknesses
    }