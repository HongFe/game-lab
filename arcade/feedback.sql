-- 다시 실행해도 안전: 표는 if not exists, 정책은 지우고 다시 만든다. 기록(행)은 절대 지우지 않는다 (2026-11-27 사용자 결정: 업데이트해도 기록은 쌓는다)
-- NHC POCKET 오락실 DB (Supabase Postgres) · 2026-11-26
-- 사용자(테스터)와 관리자를 나눈다:
--   테스터(anon 키) : 쓰기만 (피드백·비교 투표·플레이 기록)
--   관리자(로그인한 사용자) : 읽기 — admin.html 에서 Supabase 이메일·비밀번호로 로그인
-- 개인 식별 정보는 받지 않는다: 테스터 번호(T-XXXXX, 브라우저에서 발급), 선택 닉네임만. IP·이메일·전화 저장 안 함.
-- 관리자 계정: Supabase 대시보드 > Authentication > Users 에서 관리자 1명만 만들고, 회원가입(Sign ups)은 끈다.

create table if not exists feedback (
  id             uuid primary key default gen_random_uuid(),
  created_at     timestamptz not null default now(),
  game_id        text not null,
  version        text,
  anon_id        text not null,             -- 테스터 번호 T-XXXXX
  tester         text,                      -- 선택 닉네임
  liked          boolean,
  rating         smallint check (rating between 1 and 5),
  again          boolean,                   -- 시키지 않아도 한 판 더?
  understood     boolean,                   -- 한 줄 설명으로 바로 이해?
  comment        text check (char_length(comment) <= 2000),
  play_seconds   integer,
  levels_cleared integer,
  fails          integer,
  device         text check (device in ('mobile','desktop'))
);

create table if not exists compare_votes (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  anon_id     text not null,
  tester      text,
  game_a      text not null,
  game_b      text not null,
  winner      text not null,
  reason      text check (char_length(reason) <= 500)
);

create table if not exists sessions (       -- 게임에서 나올 때마다 한 줄 (플레이 시간·클리어 자동 기록)
  id             uuid primary key default gen_random_uuid(),
  created_at     timestamptz not null default now(),
  anon_id        text not null,
  tester         text,
  game_id        text not null,
  version        text,
  play_seconds   integer,
  levels_cleared integer,
  fails          integer,
  starts         integer,
  device         text
);

alter table feedback      enable row level security;
alter table compare_votes enable row level security;
alter table sessions      enable row level security;

-- 테스터: 쓰기만
drop policy if exists "tester insert feedback" on feedback;
create policy "tester insert feedback" on feedback      for insert to anon with check (true);
drop policy if exists "tester insert votes" on compare_votes;
create policy "tester insert votes"    on compare_votes for insert to anon with check (true);
drop policy if exists "tester insert sessions" on sessions;
create policy "tester insert sessions" on sessions      for insert to anon with check (true);
-- 관리자: 읽기
drop policy if exists "admin read feedback" on feedback;
create policy "admin read feedback"    on feedback      for select to authenticated using (true);
drop policy if exists "admin read votes" on compare_votes;
create policy "admin read votes"       on compare_votes for select to authenticated using (true);
drop policy if exists "admin read sessions" on sessions;
create policy "admin read sessions"    on sessions      for select to authenticated using (true);

-- 모두가 보는 게임별 집계 (2026-11-27): 테스터(anon)는 원본 행을 못 읽고 이 숫자만 받는다. 개인 단위 정보는 나가지 않는다
--   users = 최근 14일 플레이한 테스터 수, back = 그중 이틀 이상 다시 온 수 → 오락실 BEST 3
--   likes / rsum·rn = 좋아요 수, 별점 합·개수 → 목록 별점
create or replace function arcade_stats()
returns table (game_id text, users int, back int, likes int, rsum int, rn int)
language sql stable security definer set search_path = public as $$
  with d as (
    select game_id, anon_id, count(distinct (created_at at time zone 'Asia/Seoul')::date) as days
    from sessions where created_at > now() - interval '14 days' group by game_id, anon_id
  ), p as (
    select game_id, count(*)::int as users, count(*) filter (where days >= 2)::int as back from d group by game_id
  ), f as (
    select game_id, count(*) filter (where liked)::int as likes, coalesce(sum(rating), 0)::int as rsum, count(rating)::int as rn
    from feedback group by game_id
  )
  select coalesce(p.game_id, f.game_id), coalesce(p.users, 0), coalesce(p.back, 0), coalesce(f.likes, 0), coalesce(f.rsum, 0), coalesce(f.rn, 0)
  from p full join f on p.game_id = f.game_id;
$$;
revoke all on function arcade_stats() from public;
grant execute on function arcade_stats() to anon, authenticated;
