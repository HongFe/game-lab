-- NHC POCKET 오락실 피드백 DB (Supabase Postgres) · 2026-11-26
-- 개인 식별 정보는 받지 않는다: 닉네임은 선택, IP·이메일·전화 저장 안 함.

create table if not exists feedback (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  game_id       text not null,             -- G001
  version       text,                      -- 빌드 시각
  tester        text,                      -- 선택 닉네임 (실명 X)
  anon_id       text not null,             -- 기기별 무작위 ID (같은 사람 중복 집계 방지용)
  liked         boolean,
  rating        smallint check (rating between 1 and 5),
  again         boolean,                   -- 시키지 않아도 한 판 더 하고 싶은가
  understood    boolean,                   -- 한 문장 설명으로 바로 이해했나
  comment       text check (char_length(comment) <= 2000),
  play_seconds  integer,                   -- 자동: 실제 플레이 시간
  levels_cleared integer,                  -- 자동
  fails         integer,                   -- 자동
  device        text check (device in ('mobile','desktop'))
);

create table if not exists compare_votes (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  anon_id     text not null,
  tester      text,
  game_a      text not null,
  game_b      text not null,
  winner      text not null,               -- game_a / game_b / 'tie'
  reason      text check (char_length(reason) <= 500)
);

alter table feedback      enable row level security;
alter table compare_votes enable row level security;
-- 테스터(익명)는 쓰기·읽기만. 수정·삭제는 대시보드(관리자)에서만
create policy "anon insert feedback" on feedback      for insert to anon with check (true);
create policy "anon read feedback"   on feedback      for select to anon using (true);
create policy "anon insert votes"    on compare_votes for insert to anon with check (true);
create policy "anon read votes"      on compare_votes for select to anon using (true);
