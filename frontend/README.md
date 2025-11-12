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

## 🚩 Important Keywords

- UI issues
- Dashboard
- Mia Chatbot
- Recommendations
-Pending approval
- order history
- Manage Orders
- catalog
- Cart
- Practice
- Edit
- Responsiveness
- Mobile
- Admin
- User
- SuperAdmin
- Mia
- Orders
- Delivered
- Shipped
- error
- Practice Admin
- Practice User



> Use these keywords in your pull requests, commit messages, and GitHub issues to help the team quickly identify areas of focus and to streamline collaboration.
>
> For UI-related problems, tag with `UI issues`.  
> For anything affecting analytics or navigation, use `Dashboard`.  
> If you're working on or reporting enhancements to the conversational assistant, use `Mia Chatbot`.  
> For feature ideas or feedback, tag with `Recommendations`.
