# game-lab — 게임 공장 (1주 1프로토, 만들고 버리기 반복)

- 프로젝트명: `game-lab` · 타입: 게임 실험 공장 (game-hypercasual 템플릿 변형)
- 시작일: 2026-11-25 · 출처: business 아이디어 `I01`, business 실험 `E01`
- 목표: 작은 게임을 7일 단위로 만들고, 플레이테스트 숫자로 유지/폐기를 가른다. '한 판 더'가 나오는 게임 하나를 찾는다
- KPI (가설): 테스터 5명 중 3명이 시키지 않았는데 재플레이, 또는 플레이 시간 중앙값 10분 이상
- Kill 판단: 게임마다 프로토 7일 + 플레이테스트. 프로젝트 전체는 3개 연속 폐기 시 기준을 고쳐 business에 보고(E02)
- 규칙 원문: `README.md` · 단일 출처: `games.json` · 관리 보드: `board.html`, 오락실: `arcade/index.html` (`python3 tools/build_board.py && python3 tools/build_arcade.py`로 생성, 직접 고치지 않음)

## 에이전트 역할 분담 (`.claude/agents/`)

| 에이전트 | 맡는 일 | 쓰기 범위 |
|---|---|---|
| `game-designer` | 아이디어 한 문장 → 심사 점수, 승격된 게임의 `brief.md`(보상·성장 설계 포함) | `games.json`(아이디어·점수), `G###_*/brief.md` |
| `proto-builder` | `brief.md` → `game/index.html` 단일 파일 프로토 제작 | `G###_*/game/`, `_shared/` |
| `qa-tester` | 사람 테스트 전 자동 검수: 풀림 검사·난이도/보상 곡선·화면·오류·오락실 연결 → `qa.md` (코드 수정 안 함) | `G###_*/qa.md` |
| `playtest-recorder` | 테스트 기록 정리, 판정 계산, 폐기 시 `result.md`·살릴 부품 정리 | `G###_*/playtest.md`, `result.md`, `games.json`(단계·판정) |

## 작업 흐름

```
game-designer (아이디어·점수 → 18점 이상 승격 → brief.md)
  → proto-builder (7일 안에 game/index.html, 품질 기준·자체 검사·오락실 연결)
  → qa-tester (자동 검수 → '사람 테스트 가능' 판정)
  → 오락실(GitHub Pages)에 올려 사람 플레이테스트 (사용자 + 지인 5명, 피드백은 오락실에서)
  → playtest-recorder (판정: 유지 / 폐기)
  → 보드 재생성: python3 tools/build_board.py
  → 유지: 외부 공개(itch.io·스팀) 계획은 사용자 확인 후 별도
  → 폐기: result.md + 레슨 → business에 전달 (business/domains/game/lessons.md는 business의 lesson-keeper가 반영)
```

## 절대 규칙

- 동시 진행 8개까지(프로토 + 플레이테스트 합산, 2026-11-26 사용자 결정). 유지 최대 1개
- 게임 하나 = `G###_<slug>/` 폴더 하나 = `game/index.html` 하나. 설치·CDN·웹 글꼴 금지(오프라인 동작). 글꼴은 `~/Desktop/NHC/command-center/docs/FONTS.md` 표준
- ID 재사용 금지, 폐기해도 폴더 삭제 금지
- 원작 게임 복제 금지(이름·캐릭터·그림·레벨). 장르·메커닉 참고만
- 재미 판정은 사람이 한다. 에이전트는 만들고, 검수하고, 기록하고, 센다
- 공개 배포: GitHub `HongFe/game-lab` → GitHub Pages(오락실). push는 사용자가 요청할 때만

## 오락실: 사용자와 관리자 (2026-11-26)
- 사용자(테스터) `arcade/index.html`: 첫 방문에 테스터 번호(T-XXXXX)를 이 브라우저에 발급 → 다음에 와도 같은 번호로 플레이 기록(sessions)·의견(feedback)·비교 투표가 쌓인다. B 버튼 = 내 기록(닉네임, 다른 기기에서 번호 입력해 이어 가기)
- 관리자 `arcade/admin.html`: 게임별 판정(테스터 5명부터), 테스터 표, 의견 표, 비교 투표, CSV/JSON 내보내기, 카톡으로 받은 피드백 텍스트 붙여넣기
- 저장: `arcade/config.js` feedback=local(기본: 이 기기 + 텍스트 공유) / supabase(공유 DB). `arcade/feedback.sql` — 테스터는 쓰기만, 읽기는 로그인한 관리자만(RLS)
- IP·이메일·실명은 받지 않는다
- 외부 업로드·계정·결제·새 패키지 설치는 사용자에게 먼저 묻는다
- Git: `~/Desktop/NHC/shared/git/standard.md`. 사용자가 "커밋해줘"라고 할 때만 커밋

## business와의 관계

- business(`~/Desktop/NHC/agents/business/`)가 아이디어를 검증하고 이 프로젝트로 승격했다. 단방향: business 조사 → 여기 실행
- 이 프로젝트의 상태는 business의 아이디어 파이프라인 보드(`ideas.html`)가 `games.json`을 읽어 요약한다
- 참고 조사: business `research/2026-11-25_게임_인디게임_AI개발_사업분석.md`, `research/2026-11-24_1인AI게임_사업구조.md`, `domains/game/playbook.md`

## 공통 인프라

- 디자인 토큰: `../../shared/design/tokens.css`
- Phaser 보일러(필요 시): `../../shared/templates/game-phaser/`
- 배포 체크리스트: `../../shared/deploy/poki-checklist.md`
