# Notes App

The app source and Dockerfiles are in this folder. Kubernetes manifests are
separate, in `deploy/notes-app`, which is the Argo CD source path.

Create a Secret in namespace `notes-dev` before syncing:

```powershell
kubectl create secret generic notes-app-db -n notes-dev `
  --from-literal=DB_NAME='notes' `
  --from-literal=DB_USER='notes_user' `
  --from-literal=DB_PASSWORD='<choose-a-password>'
```

Build from the repository root and load the images into your cluster:

```powershell
docker build -t notes-app-backend:latest app-source/notes-app/backend
docker build -t notes-app-frontend:latest app-source/notes-app/frontend
kind load docker-image notes-app-backend:latest notes-app-frontend:latest
```

Open the UI at `http://<node-address>:30051`.
