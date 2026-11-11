# Publish this profile

GitHub displays the root README of the public repository `3rw-1n/3rw-1n` on the account's profile.

From this directory, initialize Git and set your commit identity:

```bash
git init -b main
git config user.name "Berwin"
git config user.email "REPLACE_WITH_YOUR_GITHUB_COMMIT_EMAIL"
git add .
git commit -m "Create personal profile with stats and contribution graph"
gh repo create 3rw-1n/3rw-1n --public --source=. --remote=origin --push
```

Replace the email placeholder with a verified address or the exact noreply address from GitHub email settings before committing. If the profile repository already exists, use its existing remote rather than creating another repository.

## Included content

- `README.md`: the English profile introduction, badges, live stats cards, contribution graph, and nano-agent demonstration.
- `assets/header.svg`: a decorative introduction banner; its illustration does not represent contribution data.
- `assets/activity.svg`: the most recently generated contribution graph.
- `scripts/update_activity.py`: an updater using Python's standard library and the public GitHub contribution calendar. It does not need an API key or a personal access token.
- `.github/workflows/activity.yml`: a daily update and manual trigger. It also runs on the initial push. Its GitHub token is used to commit the generated SVG.

The graph shows the last 31 days. The workflow retains the previous graph if GitHub's calendar cannot be parsed. Changes to the public calendar's HTML may require updating the parser.

To refresh it manually after publishing, open Actions, select Update contribution graph, and choose Run workflow. The daily schedule is 08:23 UTC and may be delayed by GitHub. A workflow commit can itself appear in the public contribution calendar under GitHub's attribution rules.

Statistics and language cards are served by GitHub Stats Extended and can be affected by that service's availability or caching. Language proportions describe repository code; they are not a measure of proficiency.

## Sources

- [GitHub profile README](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)
- [GitHub Stats Extended](https://github.com/stats-organization/github-stats-extended)
