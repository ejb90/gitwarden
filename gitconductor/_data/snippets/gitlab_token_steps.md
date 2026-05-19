To create a GitLab Personal Access Token:

1. Log in to GitLab.
2. Click your user icon.
3. Click **Preferences** in the dropdown.
4. Click **Access tokens** or **Personal access tokens** in the sidebar.
5. Click **Add new token**.
6. Select **legacy** if your GitLab instance asks for a token type.
7. Give the token a useful name.
8. Set an expiry date. For closed systems, the longest permissible expiry is usually easiest.
9. Select the scopes needed for your workflow:

   - `read_user`
   - `read_repository`
   - `read_api`
   - `write_repository`

10. Click **Generate token**.
11. Copy the token immediately; GitLab will not show it again.

For read-only inspection, you may not need every write scope. For recursive git commands such as `push`, the token and your git credentials must allow the operation on the target projects.
