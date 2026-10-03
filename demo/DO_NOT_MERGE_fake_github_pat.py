"""DEMO ONLY. Do not merge this pull request.

This file is a screenshot fixture for the security gate. The value below
is synthetic: it was never issued by GitHub, it authorizes nothing, and
it must not be replaced with a real token.

Expected result: gitleaks and trivy-filesystem fail on this file.
The image scan stays clean because the Docker build context excludes demo/.
"""

# Synthetic string in the shape of a GitHub personal access token.
github_pat = "ghp_FAKEDEMODoNotMergeThisKey00000000000"
