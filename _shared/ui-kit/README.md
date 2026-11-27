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

아이콘(`icons/`, Lucide ISC 0.460.0): `ls _shared/ui-kit/icons` 참고 (54개 — play·pause·lock·store·book-open·award·star·trophy·coins·zap·shield·target·pointer·hand·gift·flag·sparkles·car·train-front·puzzle 등).
더 필요하면 lucide-static 0.460.0 의 svg를 `icons/`에 넣고 `--all` 다시 실행.

## 지킬 것 (요약)
1. UI 버튼·HUD·목록 머리에는 이모지 대신 아이콘. 이모지는 캐릭터·보상 그림에만, `ui-em`/`ui-hero` 고정 상자 안에
2. 시작 화면 = 대표 그림 + 제목 + 한 줄 + 주 버튼 1개 + 보조 버튼 최대 2개. 규칙 설명 목록·면책 문구 금지(규칙은 첫 판에서 손짓으로, 면책은 설정/도감 안)
3. 한 화면 글자 크기 3단계 이하, 강조색은 주 버튼에만, 숫자는 `ui-num`(고정폭)
4. 간격·반경·그림자는 키트 변수만 (`var(--ui-s4)` 등). 임의 px 금지
5. 브라우저 기본 모양(목록 점, 버튼 테두리, 파란 탭 하이라이트) 노출 금지

## v1.1 (2026-11-27, G003 시범 반영)
- 키트 기본값은 `:where(:root)` → 게임 쪽 `:root{--ui-accent:…}`가 항상 이긴다(우회 불필요)
- 지금 레벨 칸(`cur`)은 강조색 대신 테두리. `ui-sub` 16px(제목30·버튼20/16과 합쳐 3단계)
- `ui-screen`은 길면 위부터 스크롤(위 잘림 없음)
- 추가 부품: `ui-head`(머리), `ui-item`(+`ui-grow`, 목록 줄), `ui-line`(한 줄 수치 카드), `ui-dock`(아래 고정 버튼), `ui-pips`(단계 막대), `ui-strike`, `ui-good`/`ui-bad`, 아이콘 버튼 위 `ui-badge`
- `UI.toast(msg, ms, "top")` — 판 중엔 위쪽

## v1.2 (2026-11-27, G001·G004 적용 반영)
- 아이콘 phone·mail 추가. `ui-scrim`(시트 뒤 어두운 막), 닫힌 시트 그림자 제거, 토스트 줄바꿈·최대 폭
- `ui-warm`(따뜻한 밝은 화면, `ui-light`와 함께), `ui-chip small`(값/한도의 한도 쪽), `ui-hand`(+`tap`, 첫 판 손짓 — 👆 이모지를 넣고 left/top으로 옮김)
- **게임에서 키트 부품 모양을 덮을 때는 두 단계로**: `.ui-btn.g-mode{…}` (키트 블록이 body 안 뒤쪽에 있어 한 단계 선택자는 진다)

## v1.3 (2026-11-27, G012 반영)
- 아이콘 hammer·wrench·gavel·handshake·ticket·graduation-cap·piggy-bank·landmark·newspaper·lock-open 추가
- 숨김은 `hidden` 속성(또는 `ui-screen.hide`) — 게임 쪽 `display:none`이 키트에 지는 문제 방지
- `ui-item>.ui-val`(줄 오른쪽 값), `ui-tip.sm`(정보 많은 게임용 14px), `ui-badge.good`/`muted`

## v1.4 (2026-11-27, G021·G022 반영)
- 밝은 화면 `ui-screen.dim`은 어두운 막, `ui-screen.off` 숨김, `ui-levels.five`(5칸 고정), `ui-btn.float`(그림 위 흰 버튼), 칩 안 별 색 유지

## v1.5 (2026-11-27, G002·G006 반영)
- 아이콘 calendar·utensils·soup 추가. 배지·칩·버튼·줄의 `hidden` 동작, `button.ui-item`(고르는 목록), `ui-pips>i.bad/good`, `ui-hud.static`(흐름 안 HUD)
