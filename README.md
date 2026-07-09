# cyrano

**미팅 상대를 만나기 전에, 그 사람이 누구인지 귀에 속삭여주는 스킬.**

시라노 드 베르주라크가 그림자에 숨어 완벽한 대사를 넘기듯 — cyrano는 당신의 AI
에이전트 뒤에 숨어, 비즈니스 미팅 전에 상대방과 그 회사를 조사해 **소스가 인용된
브리핑**을 당신에게 넘긴다.

이메일 주소(또는 그날 캘린더) 하나면 된다:

```
🗓️ 10:00 — Intro call · Jane Doe (Acme Health)
👤 Jane Doe · VP Growth @ Acme Health · ~2yr · ex-Shopify · linkedin.com/in/janedoe
🏢 Acme Health — 치과 클리닉용 예약+청구 SaaS, Series A $8M, ~40명, Toronto
📈 Series A 직후 세일즈 채용중 · 지난달 AI recall 출시 · Jane, no-show 관련 포스트
🎯 no-show 통증 ↔ reactivation 플레이 · 질문: 멀티로케이션 어떻게 처리?
🔗 linkedin · acme.co · techcrunch  ·  Confidence: 사람 High · 회사 High · 시그널 Med
```

## 무엇인가

- **입력:** 이메일 주소, 또는 호스트 에이전트가 읽은 그날의 캘린더.
- **처리:** 외부 참석자 감지 → 인물+회사 웹 리서치(차단 사이트는 번들된
  [insane-search](https://github.com/fivetaku/insane-search) 엔진으로 뚫음) →
  환각·동명이인 가드레일 → 브리핑 작성.
- **출력:** 인물 프로필 / 회사 개요 / 최근 시그널 / 미팅 앵글·질문 + 소스 + confidence.
- **전송:** `return`(호스트가 전달) · `slack` · `telegram` · `email` 중 설정.
- **포터블:** 채널·도메인·수신자를 하드코딩하지 않는다. 어떤 에이전트든 설치해
  자기 주인에게 브리핑을 보낼 수 있다.

## 설계

두 종류의 작업을 올바른 실행자에게 나눈다:

| 실행자 | 담당 |
|---|---|
| **호스트 에이전트 (LLM)** | 리서치 전략·판단·요약·소스 검증 (`skills/cyrano/SKILL.md`) |
| **`engine/` (파이썬, 의존성 0)** | 참석자 필터 · dedup · 채널 전송 |
| **번들 insane-search** | LinkedIn/X 등 차단 사이트 fetch |

`engine/`은 stdlib만 쓴다(HTTP는 `urllib`) — 어떤 환경에도 깨끗이 설치된다.

## 빠른 시작

```bash
# 1) 설정 부트스트랩
bash skills/cyrano/setup/setup.sh

# 2) 내 도메인 + 전송 채널 채우기  (skills/cyrano/config.json)
#    own_domains, delivery.mode, 채널 시크릿은 env로

# 3) 확인
cd skills/cyrano && python -m engine config
```

에이전트에게: *"cyrano로 오늘 외부 미팅 브리핑해줘"* 또는
*"cyrano로 john@acme.com 리서치해줘"*.

## 엔진 CLI

```
python -m engine filter  [--events FILE] [--all]      # 캘린더 → 외부 대상
python -m engine deliver --brief FILE [--mark EVT EMAIL]  # 설정된 채널로 전송
python -m engine check  EVT EMAIL                     # dedup 확인 (0=fresh)
python -m engine state  show|clear                    # dedup 원장
python -m engine fetch  URL                           # insane-search 프록시
python -m engine config                               # 해석된 설정(시크릿 마스킹)
```

## 프라이버시

공개된 비즈니스 정보만, 환각 금지, 신원 오인 방지, 목적 한정.
`skills/cyrano/DISCLAIMER.md` 참조.

## 크레딧 / 라이선스

차단 사이트 접근 엔진은 [fivetaku/insane-search](https://github.com/fivetaku/insane-search)
(MIT)를 번들·재활용한다. `LICENSE.insane-search` 참조. cyrano 자체는 MIT.
