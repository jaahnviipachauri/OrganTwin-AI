# OrganTwin AI — deployment guide

## Docker Compose (recommended for demos)

From the repo root:

```bash
docker compose up --build
```

- UI: http://localhost:3000  
- API: http://localhost:8000  
- OpenAPI: http://localhost:8000/docs  

The frontend image is built with `NEXT_PUBLIC_API_URL=http://localhost:8000` so the browser can reach the API on the host. Change it if you publish behind a real domain.

## Individual images

### API

```bash
cd backend
docker build -t organtwin-api .
docker run -p 8000:8000 -v organtwin-data:/app organtwin-api
```

SQLite file `app.db` and `ml/artifacts` live in the container working directory. Mount a volume if you want persistence.

### Web

```bash
cd frontend
docker build --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 -t organtwin-web .
docker run -p 3000:3000 organtwin-web
```

## Cloud sketch

1. **API** on a small VM or Cloud Run/Fly.io (`uvicorn app.main:app --host 0.0.0.0 --port 8080`). Swap SQLite for Postgres if you need multiple replicas.
2. Set CORS in `backend/app/config.py` to your UI origin.
3. **Frontend** on Vercel/Netlify: set `NEXT_PUBLIC_API_URL` to the public API URL and `npm run build`.
4. Do not commit `app.db` or trained artifacts if they contain private assay data (this demo uses synthetic data only).

## Production notes

- The organ lab is **in-process memory**. Multiple API workers will diverge. Run a **single uvicorn worker** for the live twin, or move the lab to Redis.
- Retrain with `python -m ml.train_model` when you replace `synthesize_dataset()` with real chip CSVs.
- PDFs are generated on request from the current live state — generate after a perfusion run.
