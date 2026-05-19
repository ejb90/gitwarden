Gitconductor needs a GitLab Personal Access Token. The quickest setup is:

<!-- include: snippets/gitlab_token_steps.md -->

Then export the token:

<!-- include: snippets/token_env.md -->

For self-hosted GitLab, set the GitLab URL too:

```bash
export GITCONDUCTOR_GITLAB_URL=https://gitlab.example.com
```

Gitconductor can also store settings in a TOML file. By default, this is:

```text
~/.config/gitconductor/gitconductor.toml
```

The location can be changed via `GITCONDUCTOR_CONFIG` or the top-level `--cfg` CLI option.
