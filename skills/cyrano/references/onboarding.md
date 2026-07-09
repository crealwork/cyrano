# 온보딩 상세 — "설치하면 알아서 셋업"

목표: 설치한 사람이 config 파일을 안 건드리고도, 몇 번의 컨펌만으로 매일 아침 미팅
브리핑이 자동으로 오게 만든다. 질문(사람 판단)은 유저에게, 저장(결정론)은 엔진에.

## 언제 도나

호스트 에이전트가 cyrano를 처음 쓰려 할 때 `python -m engine config`를 보고
`onboarded=false`면 이 흐름을 **먼저** 실행. 이미 온보딩됐으면 건너뛴다.

## 대화 스크립트 (에이전트가 유저에게)

에이전트가 쓸 수 있는 질문 UI로(Claude Code면 AskUserQuestion, Slack이면 그냥 메시지)
아래를 **한 번에 하나씩** 묻는다. 유저 답을 모아 마지막에 한 방에 저장.

1. 도메인
   - 먼저 유저 이메일에서 도메인을 뽑아 **후보로 제시**: "브리핑은 '외부' 사람만
     대상이에요. 당신·팀 도메인이 `crealwork.com` 맞죠? 내부로 칠 도메인 더 있어요?
     (예: 자회사·형제 프로젝트 도메인)"
   - 개인메일 쓰는 내부 인원이 있으면 그 이메일도 받는다 → `--internal-emails`.
2. 채널
   - "브리핑을 지금 이 채널(여기 Slack DM)로 받을까요?" → 예면 `--mode return`
     (호스트인 에이전트가 브리핑을 받아 이 대화로 보냄).
   - "다른 곳(전용 Slack 채널/텔레그램/이메일)로 직접 쏠까요?" → `channel-adapters.md`
     대로 webhook/token env를 안내하고 `--mode slack|telegram|email` + 관련 플래그.
3. 시간
   - "매일 아침 몇 시에 그날 외부 미팅 브리핑을 받을래요? (기본: 평일 08:03)"
   - cron으로 변환. 평일 8시 → `3 8 * * 1-5`. (분은 0/30 피해서 서버 몰림 방지.)

## 저장 (한 방)

```bash
python -m engine configure \
  --own-domains "crealwork.com,sundayable.com,vflo.app" \
  --internal-emails "contractor@gmail.com" \
  --mode return \
  --schedule "3 8 * * 1-5"
```
부분 재설정도 안전 — 준 플래그만 덮고 나머지는 보존. 나중에 "채널 바꿔줘"는
`configure --mode slack --slack-webhook-env CYRANO_SLACK_WEBHOOK`만.

## 자동화 걸기 (호스트별)

`configure`는 스케줄을 **기록**만 한다(참고용). 실제 데일리 작업은 호스트의 스케줄러로
에이전트가 만든다. 데일리 프롬프트(고정):

> "cyrano로 오늘 내 외부 미팅을 브리핑해서 이 채널로 보내줘."

- **Claude Code / 세션 기반**: `CronCreate`(durable) 또는 `schedule` 스킬로 위 프롬프트를
  `--schedule` cron에 건다.
- **클라우드 루틴 에이전트(선데이/헤르메스 등)**: 자기 routine 시스템에 같은 프롬프트로
  데일리 루틴 등록. 캘린더는 자기 커넥터로 읽고 Slack으로 보냄.
- **스케줄 도구가 없는 호스트**: 로컬 스케줄러(`schtasks`/`launchd`)로 `claude -p
  "cyrano로 오늘 외부 미팅 브리핑"` 등록 — `references/deployment-recipes.md` 참고.

## 컨펌 게이팅 (중요)

자동으로 하지 말고 **유저에게 물어라**: 도메인 확정, 외부 직접 발송 켜기, 매일 스케줄
걸기·시간, 첫 브리핑 실제 발송. 이건 [[feedback_no_auto_activate_campaigns]]와 같은
결: 셋업까지는 에이전트가, "진짜 켠다/보낸다"는 유저 승인. 나머지(감지·리서치·작성·
저장·dedup)는 자동.

## 끝 확인

저장·스케줄 완료 후: "셋업 끝. 평일 08:03에 그날 외부 미팅 브리핑을 여기로 보낼게요.
지금 오늘 미팅으로 테스트 한번 해볼까요?" → 예면 온디맨드 1회 실행으로 검증.
