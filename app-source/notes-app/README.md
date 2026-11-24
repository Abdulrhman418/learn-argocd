# Notes App

The app source and Dockerfiles are in this folder. Kubernetes manifests are
separate, in `deploy/notes-app`, which is the Argo CD source path.

Argo CD creates the `notes-app-db` Secret from `deploy/notes-app/database-secret.yaml`
in the database Application, before the PostgreSQL Deployment. The checked-in
password is for learning only; replace it before using this outside a local demo.

Build from the repository root and load the images into your cluster:

```powershell
docker build -t notes-app-backend:latest app-source/notes-app/backend
docker build -t notes-app-frontend:latest app-source/notes-app/frontend
kind load docker-image notes-app-backend:latest notes-app-frontend:latest
```

Open the UI at `http://<node-address>:30051`.
