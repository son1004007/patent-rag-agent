# EVAL-02 — NAS 실제 읽기→AI 근거 판정→재사용 차단 연결 인수

- 실행일: **2026-11-20**
- 상태: **ChatGPT Code Mode LIVE_READ_INTEGRATION_PASS (선별 4문항)**, **운영 NAS MCP 서비스 배포/자동 플러그인 후킹 NOT_RUN**
- Source of Truth: [AGENTS](../../AGENTS.md), [TASKS](../../TASKS.md), [반복 사용 평가](2026-11-20-eval02-warm-nas-replay.md), [평가 인덱스](INDEX.md).
- 실제 대상: 기존 구매 문헌의 NAS RAG 도구 `search_patents`/`get_patent` **읽기 전용**. 기존 공용 운영 서비스·DB·원문·벡터·서지·PDF, 인증/터널/권한과 WIPS/MyFolder 상태는 **변경하지 않음**.
- 공개 GitHub에는 실제 특허ID, SKEY, 발췌·원문, source/chunk 해시, 사용자 질의 전체 또는 private NAS 경로를 포함하지 않음.

## 1. 구현

- [실제 read-only 연결 어댑터](../../poc/eval02_live_read_adapter.mjs): 기존 [구조/반복 판정기](../../poc/eval02_reuse_policy.mjs)를 호출하는 dependency-injected async runner.
- **동작:** `search({query,limit:3})`를 동일 질문으로 두 번 호출 → 문헌 ID·chunk hash·출처/섹션·offset 순서 동일성과 source/ranking/scope 검증 → 상위 최대3개에 `detail({document_id})` 호출 → 상세 문헌 ID, publication, kind, country, title, source hash, 증거 필드 일치 확인 → **ChatGPT가 제공한 `review` 콜백**이 기술 목적/필수 속성을 근거로 `label=2` 선택 → 상세증거의 동일 section+chunk_sha256과 **실제 인용 문자열** 포함 여부 검증 → `AI_REVIEWED_REUSABLE` 또는 HOLD.
- **보수성:** AI 콜백 미제공, 상세 근거/해시 불일치, 순위 변동, 인용구 불일치/짧은 이유, provider 오류, 2점이 아닌 후보 = **fail closed**. `freshnessRequired:true`면 provider 호출 **0회**로 `FRESHNESS_REQUIRED`.
- 반환 데이터는 `caseId`/판정/호출수/랭크/근거 참조가 일치했다는 boolean/한계만. 후보 원문/문헌 식별자/해시/인용 문자열 **반환·저장·출력하지 않음**.
- **중요:** 이 코드는 임의 원문을 스스로 이해하는 모델이 아니다. 문헌 관련성은 **현재 채팅의 ChatGPT가** 상세 근거를 읽고 private-memory로 전달하는 `review` callback에 의존한다. 자동 LLM 모델 호출을 내장하거나 다른 외부 AI에게 구매 문헌을 전송하지 않음.

## 2. 실제 NAS MCP E2E 검증

| Case | 주제 | 두 번 검색+상세근거+AI 확인 | 최종 판정 |
|---|---|---|---|
| Q01 | 태양광 봉지재 끝단 밀봉 | 요약과 대표청구항에 관련 기술 근거. 처음 *대표청구항에만 핵심 어휘 요구*하는 엄격한 AI 선별안은 false HOLD였음; 요약+청구항의 종합 확인으로 재실행 | **AI_REVIEWED_REUSABLE / citation matched** |
| Q04 | 형광 태양광 봉지재 | 형광/태양광/봉지재 제목과 요약 근거, 동일 청크의 인용 문자열 직접 확인 | **AI_REVIEWED_REUSABLE / citation matched** |
| Q05 | 봉지재 저온 접합과 습열 내구성 | 두 필수 기술 조건의 직접 근거 동시 확인 실패 | **INSUFFICIENT_DIRECT_EVIDENCE** |
| Q08 | SiC 전력반도체 저손실 | 기존 NAS 저장 문헌은 주로 태양광 봉지재; 직접 관련 증거 없음 | **INSUFFICIENT_DIRECT_EVIDENCE** |
| Freshness | Q08에 최신성 요구 플래그 주입 | 호출 전 보호 경로 | **FRESHNESS_REQUIRED** / NAS 0, WIPS 0 |

- **성공적으로 응답을 받은 5건의 실제 Code Mode 어댑터 실행**(Q01 첫 HOLD + Q08 HOLD + Q01 수정 후 재실행 + Q04 재사용 + Q05 HOLD)에 한정하여 NAS search **10회**, `get_patent` **15회**, WIPS **0회**. 별도 상세 포맷 사전 진단·초기 도구 호출 상한 초과로 응답이 없었던 실행은 이 좁은 분모에 포함하지 않음. 따라서 **전체 세션 WIPS/NAS billing 사용량**이나 10문항 전체 라이브 어댑터 완료로 오해하지 말 것.
- 안정성·인용 출처 일치 검증과 모델의 기술 의미 해석은 별개이며, 모든 참조 인용은 **문서 일부**만 확인. `AI_REVIEWED`는 독립 human-gold가 아님.
- Q01 초기 false HOLD는 **안전 차단이 작동함**과 **단일 발췌의 누락이 재현율을 낮춤**을 함께 보여 준다. reviewer는 요약+청구항 전체 가용 발췌를 함께 읽되 인용은 반드시 실제 chunk에 존재해야 한다.

## 3. 계약/회귀 검증

- [기존 순수 판정기 테스트](../../poc/eval02_reuse_policy.test.mjs): **16개 PASS**.
- [신규 라이브 어댑터 테스트](../../poc/eval02_live_read_adapter.test.mjs): **23개 PASS** — 정확한 AI 청구항 인용, 불일치/부분 관련 보류, 고정 해시/출처/문헌 검증, 최신성 차단, provider 오류의 비밀 문구 비노출, 잘못된 리뷰 실패·로컬 리더만 호출.
- **실제 실행 환경:** GitHub main에서 코드를 읽어 **Code Mode V8 격리 실행**으로 39개 계약·합성 테스트 PASS; 이후 같은 코드 본문을 실제 NAS 읽기 MCP 함수에 주입해 선별 4문항 실증. **Node.js CI나 별도 NAS 운영 기동 테스트를 실제로 수행했다는 의미는 아님**.
- 계약/허가, 데이터 정본 외부 이동, 비용, e2e 서비스 응답시간, 앱 네트워크 레벨 자동 라우팅 및 PDF·본래 청구항의 전체 페이지 검증은 **NOT_RUN/NOT_IMPLEMENTED**.

## 4. 사용 기준 / 다음 작업

1. ChatGPT Code Mode에서 저장소 `poc/eval02_live_read_adapter.mjs`와 `poc/eval02_reuse_policy.mjs`를 로드하고 **이미 연결된** NAS `search_patents`/`get_patent` 도구를 `search`/`detail` callback으로 전달한다. `review` callback은 ChatGPT가 이 채팅에서 근거를 읽고 반환하며 **특허 제목·청구항의 복합적 일치를 반드시 검증**한다.
2. `AI_REVIEWED_REUSABLE`에서만 과거 특허 근거 재사용 허용. `INSUFFICIENT_DIRECT_EVIDENCE`, `INVALID_OR_UNSTABLE_EVIDENCE`, `EVIDENCE_GROUNDING_FAILED`, `FRESHNESS_REQUIRED`는 인용/추천 **HOLD**. 최신 공보·권리상태는 WIPS 별도 갱신이 필요.
3. 독립 사용자 채점은 사용자 최신 결정으로 **필수가 아니다**. 각 결과에 `AI_REVIEWED` 표시. 실행 데이터의 개인/고객 기밀·원문·해시를 공개 GitHub에 쓰지 않는다.
4. **다음 P0:** 해당 안전 판정 조건을 NAS 전체 10문항에 재적용해 변형 질의/대표청구항 누락/다른 언어의 false HOLD를 최소화하고, 권한·배포 게이트를 검토한다. NAS 운영 MCP에 신규 도구를 실제 등록하거나 배포하려면 기존 전역 Control의 승인된 변경 범위·복구 기준을 별도 적용한다.

**결론:** `CODE_MODE_READ_PATH_LIVE_PASS`, `REUSE_ACCEPT_Q01_Q04`, `HOLD_Q05_Q08`, `FRESHNESS_BLOCKED_WITHOUT_PROVIDER_CALLS`, `MCP_SERVER_UNCHANGED`, `COLD_ROI_UNMEASURED`.
