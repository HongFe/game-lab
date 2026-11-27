# NHC UI 키트 — 게임 '밖' UI 공용 부품 (2026-11-27)

게임 자체는 단순하게, 그 주변(시작 화면·레벨 선택·HUD·결과·안내·버튼·토스트)은 **명료하고 정확하게, 공들인 것처럼**.
근거: `research/2026-11-27_게임UI_정돈_기준.md` (15규칙)

## 쓰는 법
- 넣기/갱신: `python3 tools/ui_kit.py G003` (모두 갱신: `--all`) — `<body>` 바로 뒤 `<!-- nhc-ui-kit:start/end -->` 사이에 CSS·아이콘·도우미가 들어간다. 그 사이는 손으로 고치지 않는다
- 부품 전시: `python3 tools/ui_kit.py --preview` → `_shared/ui-kit/preview.html`
- 게임별로 바꾸는 값: `:root{--ui-accent:…;--ui-on-accent:…}` 두 개. 밝은 화면 게임은 `<html class="ui-light">`, 아이 게임은 `ui-kid`(터치 56px)

## 부품
| 클래스 | 용도 |
|---|---|
| `ui-screen`(+`dim`) · `ui-col` · `ui-center` | 시작·결과·일시정지 화면 (가운데 기둥, 최대 360px) |
| `ui-hero` · `ui-title` · `ui-h` · `ui-sub` · `ui-cap` | 대표 그림 1개, 제목(30), 카드 제목(20), 보조(14), 캡션(12) |
| `ui-btn` `primary`/`ghost`/`icon`/`round` | 버튼. **primary는 화면에 하나** |
| `ui-card`(`flat`) · `ui-stats`>`ui-stat` · `ui-big` | 카드, 수치 칸, 큰 결과 숫자 |
| `ui-levels`>`ui-level`(`cur`/`lock`) | 레벨 격자 |
| `UI.stars(n,max,'big')` · `UI.icon(name,'lg')` · `UI.toast(msg)` | 별, 아이콘, 토스트 |
| `ui-hud`>`ui-chip`(`accent`) · `ui-meter` | 위쪽 정보 칩, 진행 막대 |
| `ui-tip` · `ui-sheet` · `ui-list` · `ui-em` | 안내 카드(한 번에 하나), 아래 시트, 아이콘 목록, 이모지 고정 상자 |
| `ui-enter`/`-2`/`-3` · `ui-pop` | 등장 225ms, 보상 팝 |

아이콘(`icons/`, Lucide ISC): play pause lock store book-open undo-2 rotate-ccw lightbulb volume-2 volume-x menu x star trophy share-2 chevron-left chevron-right house settings coins clock heart info check arrow-right zap shield target trending-up trending-down users repeat circle-help.
더 필요하면 lucide-static 0.460.0 의 svg를 `icons/`에 넣고 `--all` 다시 실행.

## 지킬 것 (요약)
1. UI 버튼·HUD·목록 머리에는 이모지 대신 아이콘. 이모지는 캐릭터·보상 그림에만, `ui-em`/`ui-hero` 고정 상자 안에
2. 시작 화면 = 대표 그림 + 제목 + 한 줄 + 주 버튼 1개 + 보조 버튼 최대 2개. 규칙 설명 목록·면책 문구 금지(규칙은 첫 판에서 손짓으로, 면책은 설정/도감 안)
3. 한 화면 글자 크기 3단계 이하, 강조색은 주 버튼에만, 숫자는 `ui-num`(고정폭)
4. 간격·반경·그림자는 키트 변수만 (`var(--ui-s4)` 등). 임의 px 금지
5. 브라우저 기본 모양(목록 점, 버튼 테두리, 파란 탭 하이라이트) 노출 금지
