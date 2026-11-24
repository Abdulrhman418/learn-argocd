# Catalog App

The app source and Dockerfiles are in this folder. Kubernetes manifests are
separate, in `deploy/catalog-app`, which is the Argo CD source path.

Argo CD creates the `catalog-app-db` Secret from `deploy/catalog-app/database-secret.yaml`
in the database Application, before the PostgreSQL Deployment. The checked-in
password is for learning only; replace it before using this outside a local demo.

Build from the repository root and load the images into your cluster:

```powershell
docker build -t catalog-app-backend:latest app-source/catalog-app/backend
docker build -t catalog-app-frontend:latest app-source/catalog-app/frontend
kind load docker-image catalog-app-backend:latest catalog-app-frontend:latest
```

Open the UI at `http://<node-address>:30052`.
