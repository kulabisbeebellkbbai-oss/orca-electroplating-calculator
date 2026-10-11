# Release checklist

## Prepare

1. Review the intended public owner/name and license. Package URLs must match the eventual repository. Increment `project.version` and update the README, changelog, and proposed listing.
2. Build in a clean checkout using the README commands; run the full tests. Inspect both wheel and source distribution for required resources, license, and unwanted files. Rebuild a wheel from the source distribution to verify completeness.
3. Install the exact candidate wheel into an isolated native Orca data directory and smoke-test opening the calculator with the known cube. Record the exact host and plugin versions. Existing user evidence for another wheel is not a substitute.
4. Audit public file contents and Git history for secrets and personal information, including author email, paths, logs, screenshots, private models, and configuration. Use a fresh allowlisted snapshot when the development history contains private records. Keep the original development repository intact.
5. Record the public commit, file manifest, source-archive/wheel SHA-256 values, test results, and remaining limitations in a private review packet. Publication approval applies to that concrete snapshot.

## Publish after approval

1. Create the public GitHub repository with the approved name and push only the reviewed public history. Do not push the original private development history or all local branches/tags.
2. Enable Issues and private vulnerability reporting. Run the included GitHub Actions workflow and inspect both platform jobs. Hosted CI checks Python/browser behavior; native compatibility remains separately documented.
3. Create tag `v0.2.1` on the reviewed public commit and prepare a GitHub prerelease. Attach the tested wheel, source distribution, source ZIP, and SHA256SUMS. Include the changelog and compatibility limits. Keep the beta designation until broader native testing supports removing it.
4. Publish the GitHub prerelease, then follow the [Orca Cloud guide](orca-publication.md) using the same version and exact wheel. Public GitHub availability alone does not create an Orca listing or grant maintainer approval.
5. Subscribe through Orca Cloud in a separate test setup, refresh/activate the plugin, and repeat the cube check. Record the listing URL and actual result. Link the repository and listing in both directions.

## Subsequent releases

Keep `main` current, test the exact candidate, and preserve old release assets for rollback. Recheck Orca's evolving nightly API and publication requirements. Upgrade tests should include saved settings, since local versioned package identity can change. Do not overwrite assets under an existing released version; use a new version.

Optional Orca Cloud OIDC automation should be enabled only after the repository is connected to a listing, publishing permissions are approved, and the workflow is reviewed. The CI workflow here only builds/tests and saves run artifacts; it cannot publish a GitHub Release or an Orca Cloud plugin.
