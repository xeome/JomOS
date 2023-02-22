configuration = {
    "DRY_RUN": 1,
    "THIRD_PARTY_REPOS": 1,
    "THEMING": 1,
}

cli_args = {
    "disable_repos": [
        "THIRD_PARTY_REPOS",
        0,
        "Disables installation of third party repositories",
    ],
    "disable_theming": ["THEMING", 0, "Disables theming changes"],
    "enable_dry_run": ["DRY_RUN", 1, "Enables dry run mode, no changes to system will be made"],
}
