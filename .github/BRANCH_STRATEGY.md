# Branch Strategy

## Branch Map

```
main          ← Production (protected)
staging       ← QA / Staging (protected)
development   ← Integration (default branch)
feature/*     ← Individual features
hotfix/*      ← Urgent production fixes
```

## Flow

```
feature/my-feature
      │
      ▼  PR (CI must pass)
  development  ──► Auto-deploy to DEV environment
      │
      ▼  PR (CI must pass)
   staging     ──► Auto-deploy to STAGING environment
      │
      ▼  PR (CI + 1 reviewer approval + manual gate)
    main        ──► Auto-deploy to PRODUCTION
```

## Rules

| Branch        | Pushes allowed    | Requires CI | Requires review |
|---------------|-------------------|-------------|-----------------|
| `main`        | PRs from staging  | ✅ Yes      | ✅ 1 reviewer   |
| `staging`     | PRs from development | ✅ Yes   | ✅ 1 reviewer   |
| `development` | PRs from feature/* | ✅ Yes     | ❌ Optional     |
| `feature/*`   | Direct push       | —           | —               |
| `hotfix/*`    | Direct push       | —           | —               |

## Naming Conventions

| Type     | Pattern                    | Example                     |
|----------|----------------------------|-----------------------------|
| Feature  | `feature/<short-desc>`     | `feature/add-auth`          |
| Bug fix  | `fix/<short-desc>`         | `fix/input-validation`      |
| Hotfix   | `hotfix/<short-desc>`      | `hotfix/sql-injection-patch`|
| Release  | `release/<version>`        | `release/1.2.0`             |

## Hotfix Process (urgent production fix)

```
main ──► hotfix/fix-name ──► PR to main (approved)
                         └──► cherry-pick to development
```

## GitHub Secrets Required

Set these in: **Settings → Secrets and variables → Actions**

| Secret                | Used in              | Description                       |
|-----------------------|----------------------|-----------------------------------|
| `RAILWAY_TOKEN`       | All deploy workflows | Railway CLI auth token            |
| `VERCEL_TOKEN`        | deploy-production    | Vercel CLI auth token             |
| `DEV_API_URL`         | deploy-development   | Dev backend URL                   |
| `DEV_APP_URL`         | deploy-development   | Dev frontend URL                  |
| `STAGING_API_URL`     | deploy-staging       | Staging backend URL               |
| `STAGING_APP_URL`     | deploy-staging       | Staging frontend URL              |
| `PROD_API_URL`        | deploy-production    | Production backend URL            |
| `PROD_APP_URL`        | deploy-production    | Production frontend URL           |

## GitHub Environments to Create

Set these in: **Settings → Environments**

1. `development` — no protection rules
2. `staging` — no protection rules  
3. `production` — **Required reviewers: upendra062** (manual approval gate)
