# Versioning: Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/). A version is written
`MAJOR.MINOR.PATCH`, for example `0.1.0`.

## What Each Number Means

The app has no public API, so "compatible" is judged from the user's side: their saved data and
the way they install and run the app.

| Part | Raise it when | Examples |
| :--- | :--- | :--- |
| **MAJOR** | A release breaks something the user relies on | Stored subscriptions cannot be read without manual steps; a feature is removed; a new requirement to run the app |
| **MINOR** | A release adds something and existing use keeps working | A new page, a new provider, a new setting |
| **PATCH** | A release only fixes or polishes | Bug fixes, wording, styling, dependency updates with no visible change |

Raising a number resets the ones to its right to zero (`0.3.2` → `0.4.0`).

## From Commits to a Version

The commit types in [commit-convention.md](commit-convention.md) decide the next version. Take
the highest bump among the commits since the last release:

| Commits since the last release | Bump |
| :--- | :--- |
| Any breaking change: `!` after the type (`feat!: ...`) or a `BREAKING CHANGE:` footer | MAJOR |
| At least one `feat` | MINOR |
| Only `fix`, `perf`, `refactor`, `style`, `build`, or `chore` | PATCH |
| Only `docs`, `test`, or `ci` | No release needed |

## Before 1.0.0

While the version is `0.y.z`, the app is still taking shape and anything may change:

- A breaking change raises **MINOR** instead of MAJOR (`0.3.2` → `0.4.0`).
- New features still raise MINOR and fixes still raise PATCH.
- `1.0.0` is released by decision, once the app is stable enough that breaking saved data
  should be rare and announced.

## One Version for the Whole Project

The reader version is recorded in `frontend/package.json` and its lockfile.

## Releasing

Raise the version on a branch with `npm version <version> --no-git-tag-version` inside `frontend/`.
Commit the change as `chore: release v<version>` and merge through a reviewed PR.
Tag the merge commit on main with `git tag -a v<version> -m "v<version>"` and push that tag.
Tags are never moved or reused.

A pushed version tag triggers the Release workflow. It verifies the package and lockfile versions, tests the backend, builds the frontend, and publishes a GitHub Release with generated notes and the runnable ZIP. Re-running for the same tag replaces its ZIP.
