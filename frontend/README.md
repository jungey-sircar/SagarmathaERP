# Sagarmatha Frontend (Next.js)

Minimal Next.js scaffold that talks to the Django backend via JWT.

Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start dev server (assumes Django running at http://localhost:8000):

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000/api npm run dev
```

Login

- Open http://localhost:3000 and provide staff credentials. The app will request `/api/token/` and store the access token in `localStorage`.

Notes

- This is a minimal scaffold for the HOD dashboard and auth flow. Further pages and styling will be added as needed.
