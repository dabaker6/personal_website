---
title: "Containerized Deployment"
date: 2026-04-18
tags:
  - release
  - deployment

summary: The web app and Cricsheet API are now containerised and deploy from Azure Container Registry using Azure App Service container settings.
---

The deployment pipeline has been updated so both the web app and the Cricsheet API are now containerised. Container images are built and stored in Azure Container Registry, and Azure App Service now deploys the app as a container image.

The web app uses its system-assigned managed identity to authenticate with ACR. The GitHub workflow was updated to use OIDC so the repository can pull, build, and push the image securely.

Initial deployment was performed with PowerShell scripts, then migrated to a GitHub Actions workflow. A service principal was created for the federated token, and the token has been configured to use the correct branch. A secondary fix was adding `gunicorn` to `requirements.txt`, since App Service expects it to be present for Python container deployments. During a non container build of the app service gunicorn is automatically used by the app service.

Future updates will include ACA and/or AKS solutions.