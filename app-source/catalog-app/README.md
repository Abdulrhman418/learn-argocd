# Catalog App

The app source and Dockerfiles are in this folder. Kubernetes manifests are
separate, in `deploy/catalog-app`, which is the Argo CD source path.

Create a Secret in namespace `catalog-dev` before syncing:

```powershell
kubectl create secret generic catalog-app-db -n catalog-dev `
  --from-literal=DB_NAME='catalog' `
  --from-literal=DB_USER='catalog_user' `
  --from-literal=DB_PASSWORD='<choose-a-password>'
```

Build from the repository root and load the images into your cluster:

```powershell
docker build -t catalog-app-backend:latest app-source/catalog-app/backend
docker build -t catalog-app-frontend:latest app-source/catalog-app/frontend
kind load docker-image catalog-app-backend:latest catalog-app-frontend:latest
```

Open the UI at `http://<node-address>:30052`.
