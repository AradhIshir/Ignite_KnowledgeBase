# Ignite Knowledge - Frontend

## Setup

1. Copy `.env.local` and set env vars:

```
NEXT_PUBLIC_SUPABASE_URL=your_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

2. Install deps and run dev

```
pnpm i
pnpm dev
```

## Scripts
- `dev` Next.js dev server
- `build` Production build
- `start` Start production server

## Notes
- Uses styled-components with blue/green theme and theme switcher.
- Auth via Supabase. Update roles using `user_metadata.role` (e.g., `admin`).

