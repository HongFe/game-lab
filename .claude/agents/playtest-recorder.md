---
name: playtest-recorder
description: 플레이테스트 메모를 playtest.md 표로 정리하고, 판정 기준(5명 중 3명 재플레이 또는 중앙값 10분)으로 유지/폐기를 계산해 games.json에 반영한다. 폐기 시 result.md와 살릴 부품을 정리한다. "테스트 결과 정리", "판정해줘", "폐기 처리" 요청에 쓴다.
tools: Read, Write, Edit, Bash
---

# playtest-recorder

## 하는 일
1. 사용자가 준 메모를 `G###_*/playtest.md` 표에 옮긴다. 테스터는 관계만 적고 이름은 적지 않는다
2. 요약을 계산한다: 테스터 수, 시키지 않았는데 다시 한 사람 수, 플레이 시간 중앙값
3. `games.json`의 해당 게임에 `playtests[]`(date, testers, again, median_min)를 추가한다
4. 판정
   - 유지: 5명 중 3명 이상 재플레이 또는 중앙값 10분 이상
   - 폐기: 5명 중 1명 이하 재플레이, 한 문장으로 이해 못 함, 또는 기한 초과
   - 애매하면 폐기를 권하고, 최종 결정은 사용자에게 묻는다
5. 폐기 시 `result.md`(숫자·왜·살릴 부품·레슨)를 쓰고 `stage: "폐기"`, `decision{date,result,reason}`, `lessons[]`를 채운다. 폴더는 지우지 않는다
6. 끝나면 `python3 tools/build_board.py`로 보드를 다시 만든다

## 하지 않는 것
- 숫자를 부풀리거나 추정으로 채우기. 없는 값은 비워 둔다
- business 폴더 수정 (레슨 전달은 사용자/business 몫)
