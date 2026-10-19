# Publication to the existing GitHub repository

The public repository `RecomputableEvidence/lexiform-research` already exists and has an initial README and MIT license. **Do not invoke the old repository-creation flow.**

The release-publishing script copies all frozen archives and readable views into a **fresh clone** of `main`. It verifies every SHA256SUMS entry, all 13 experiment identities and 288 internal manifest members, checks unexpected existing remote files, refuses overwrites of an existing local worktree, creates one commit, performs a **non-force fast-forward push**, verifies the remote head and then pushes one annotated tag. No GitHub release asset, DOI or ORCID registration is created.

From PowerShell in the extracted `lexiform-research` directory:

```powershell
py -3 .\tools\publish_existing_repo.py
py -3 .\tools\publish_existing_repo.py --publish --confirmed-rights
```

The first command is **local preflight only**, with no network actions. The second command **publishes to the internet**. Verify the reviewer gates and expect Git authentication prompts if needed. Git for Windows must be installed and configured with the correct user.name/user.email. The script never force pushes or prints API keys. It will stop if `main` changes during publication.

The preservation worktree is created in the package's parent directory at `lexiform-release-git-worktree`. If a run stops after cloning, examine that directory before trying again; the script intentionally will not overwrite it automatically. If the push succeeds but the tag operation fails, the public commit can exist independently of the tag. The emitted status makes that distinction.
