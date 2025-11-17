-- Enable UUIDs
create extension if not exists "uuid-ossp";

-- knowledge items
create table if not exists public.knowledge_items (
  id uuid primary key default uuid_generate_v4(),
  summary text not null,
  topics text[] null,
  decisions text[] null,
  key_points text[] null,
  action_items text[] null,
  faqs text[] null,
  source text null,
  date text null,
  project text null,
  raw_text text null,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- favorites
create table if not exists public.user_favorites (
  user_id uuid references auth.users(id) on delete cascade,
  item_id uuid references public.knowledge_items(id) on delete cascade,
  created_at timestamp with time zone default now(),
  primary key (user_id, item_id)
);

-- activity log
create table if not exists public.activity_log (
  id bigserial primary key,
  user_id uuid references auth.users(id) on delete set null,
  action text not null,
  item_id uuid references public.knowledge_items(id) on delete set null,
  created_at timestamp with time zone default now()
);

-- RLS
alter table public.knowledge_items enable row level security;
alter table public.user_favorites enable row level security;
alter table public.activity_log enable row level security;

-- Policies (basic: authenticated CRUD, read-all)
create policy if not exists ki_select on public.knowledge_items for select using (true);
create policy if not exists ki_insert on public.knowledge_items for insert with check (auth.role() = 'authenticated');
create policy if not exists ki_update on public.knowledge_items for update using (auth.role() = 'authenticated');
create policy if not exists ki_delete on public.knowledge_items for delete using (auth.role() = 'authenticated');

create policy if not exists fav_select on public.user_favorites for select using (auth.uid() = user_id);
create policy if not exists fav_insert on public.user_favorites for insert with check (auth.uid() = user_id);
create policy if not exists fav_delete on public.user_favorites for delete using (auth.uid() = user_id);

create policy if not exists act_select on public.activity_log for select using (auth.role() = 'authenticated');
create policy if not exists act_insert on public.activity_log for insert with check (auth.role() = 'authenticated');

-- Trigger for updated_at
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_updated_at on public.knowledge_items;
create trigger set_updated_at before update on public.knowledge_items
for each row execute function public.set_updated_at();

