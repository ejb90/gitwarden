Gitconductor needs a GitLab Personal Access Token. The quickest setup is:

<!-- include: snippets/gitlab_token_steps.md -->

Then export the token:

<!-- include: snippets/token_env.md -->

Pass the full GitLab group or project URL to `gitconductor clone`. Gitconductor derives the GitLab instance from that URL.

Gitconductor can also store settings in a TOML file. By default, this is:

```text
~/.config/gitconductor/gitconductor.toml
```

The location can be changed via `GITCONDUCTOR_CONFIG` or the top-level `--cfg` CLI option.
