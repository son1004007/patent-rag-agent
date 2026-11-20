# Tasks — MVP 우선 실행 계획

> 2026-11-19 최신 사용자 결정: 기업용 구축 등 확장 기능은 MVP 이후 백로그로 이동한다. 지금은 개인 ChatGPT + WIPS + NAS RAG 조합에서 실제 연구 질문을 끝까지 처리하는 최소 기능을 우선 완성한다. 이 파일이 실행 순서의 정본이다. [현재 검증 상태](CURRENT_STATE.md), [실측 이력](WORKS.md), [변경 전 계획](https://github.com/son1004007/patent-rag-agent/blob/5822b64649a867340d84fc321900fcec93c3a6ba/TASKS.md).

## 2026-11-20 최신 실행 — 검색 품질 AI 채점·반복 재사용 실측 완료 범위와 잔여

[**평가 계획 통합 진입점**](docs/evaluation/INDEX.md) → [**의사결정 판단 기준**](docs/44-mvp-evaluation-decision-criteria.md) → 아래 EVAL-01/EVAL-02 계획을 순서대로 읽는다. EVAL-01 AI 채점/질의 개선 및 EVAL-02 NAS 재조회 실측을 수행했다. **최신 사용자 결정: 사람 채점·#31 실사용 피드백을 필수 검증으로 요구하지 않는다.** AI 판정과 독립 인간 평가를 구분하고 미측정 ROI/권리/운영 상태를 PASS로 위장하지 않는다.

- [x] **DECISION-01: MVP 1차 이후 WIPS MCP+NAS 유지/API 전환 판단 규칙 문서화** — 근거 정확성·직접 관련 추가 문헌·호출/시간/비용 절감·운영 복잡도·공보 PDF 필요성, 조건부 GO/LIMITED_GO/NO_GO/INCONCLUSIVE 초기 임계값. [문서](docs/44-mvp-evaluation-decision-criteria.md). **실측/최종 결론 NOT RUN**.
- [x] **EVAL-01 실행 계획서 작성** — 동일 질문10개(기존 corpus 범위5+미보유 범위5), WIPS/NAS 각 top3, 통합 ≤6 고유 문헌, AI 0/1/2 라벨·근거 검증/중복, corpus 공정성·권한/예산/복구. [계획](docs/45-search-quality-comparison-plan.md). **계획서 작성 이후 EVAL-01/02 실측 수행 — 개별 결과 링크 참고**.
- [x] **EVAL-01 첫 실제 검색 단계:** 10개 공개·일반 연구 질문을 IN5/OUT5로 정하고 WIPS/NAS top3 10/10, 통합 후보 고유58·중복2, ABK/CLK 30/30 및 NAS 발췌30/30 확인. WIPS 3개 초기 오류는 각 1회 재시도 후 성공. [실제 읽기 검증](docs/evaluation/2026-11-20-eval01-live-retrieval-baseline.md). **정식 정확도·사람 0/1/2 라벨·최종 결과는 NOT RUN/INCONCLUSIVE**.
- [x] **EVAL-01 AI 1차 관련성 채점:** 10문항 총 WIPS 1/30·NAS 5/30 직접 관련 (AI P@3=3.3%/16.7%). IN 5문항 NAS 5/15, OUT 5문항 양쪽 0/15, Q04 공개/등록 중복 가능성. [익명 결과](docs/evaluation/2026-11-20-eval01-ai-provisional-score.md). **사람 gold label 0/10, 검색 조건/정렬 편향 및 최종 GO 판정 미검증.**
- [x] **EVAL-01 WIPS AI 설명길이 A/B 실험:** 사용자 지시 반영, 10문항 동일 `get_patent_ai_search` KR top3, 단문23~29자 vs 장문413~520자, 상세 `get_patent_by_skey` 60/60, AI 직접관련 **6/30(20.0%) vs 8/30(26.7%)**. 동떨어진 U 노이즈13→0, 장문 개선3/악화2/동일5. [실측](docs/evaluation/2026-11-20-eval01-wips-ai-300char-ab.md). **300자 보장/인과 주장 금지, 사람 평가 미완료.**
- [x] **EVAL-01 실패 문항 검색식 개선 실측:** Q04/Q05/Q06/Q08에서 각 300자 이상 A/B 검색×2 및 근거·청구항 AI 재판정. 기존 4문항 직접관련 1/12, 개선 A 5/12(**사후 튜닝이라 holdout 아님**), Q05 여전히0. [결과](docs/evaluation/2026-11-20-eval01-targeted-query-rewrite.md).
- [x] **EVAL-01 AI 직접 채점 실행:** 질문10개에서 ChatGPT가 요약·대표청구항·NAS 근거를 평가. 사람 라벨 필수 아님(2026-11-20 사용자 결정). [초기 채점](docs/evaluation/2026-11-20-eval01-ai-provisional-score.md), [WIPS AI A/B](docs/evaluation/2026-11-20-eval01-wips-ai-300char-ab.md), [실패 개선](docs/evaluation/2026-11-20-eval01-targeted-query-rewrite.md). 정식 외부 검증/검색식 홀드아웃/법적 의견은 별도 미수행. 
- [ ] **EVAL-01 실제 검색 정확도/근거 비교 실행** — 사용자 허용 질문·공급자 호출 범위에서 read-only WIPS/NAS 검색, AI 기반 0/1/2 판정, 직접 관련 추가 후보·근거 오류·동일 입력 재현성. **완료 기준:** 10문항 실측/원시 분모/근거·판정과 출처·비용 범위 보고, corpus in/out 분리.
- [x] **EVAL-02 실행 계획서 작성** — 남은 단계는 동일 조건 통제 COLD/WIPS 대조의 실제 시간·금액 비교와 holdout 재검증(가능한 권리·예산 범위). WARM 및 AI 근거 재사용 검증은 완료. 사용자 채점은 요구하지 않음. [계획](docs/46-reuse-value-verification-plan.md). **계획서 작성 이후 EVAL-01/02 실측 수행 — 개별 결과 링크 참고**.
- [x] **EVAL-02 NAS warm replay + AI 근거 판단:** 10문항 동일 질문 두 차례, NAS search20/20 PASS, 검색 문헌·청크 완전 동일10/10, 근거60/60, 개별 `get_patent` 4/4 검증. WARM 단계 NAS reader 총28/WIPS0, 직접 근거 재사용 IN4/5·OUT0/5. [실측](docs/evaluation/2026-11-20-eval02-warm-nas-replay.md), [합성 코드+테스트](poc/eval02_reuse_policy.test.mjs) 16 PASS. ROI·COLD 지연 **미측정**.
- [ ] **EVAL-02 실제 반복 재사용 가치 검증** — EVAL-01의 질문·라벨·snapshot 기준, 첫 조회 vs NAS-only 반복(질문마다 최소2회), 외부 재호출 절감 주장과 DB 중복0 명확히 구분. **완료 기준:** 실제/추정 호출·지연·품질 분리 보고, 권리·신선도 보류, 최종 유지/축소 판단.
- [ ] **평가 결과 기반 후속 개발 결정** — GO(품질/후보 이득)·LIMITED_GO(재사용 이득)·NO_GO·INCONCLUSIVE 가운데 실측·사용자 평가로 판정. 판단 전 API 전면 전환/신규 공보 PDF/대규모 RAG 추가 개발을 **자동 착수하지 않는다**. 사용자 지시가 새로 바뀌면 우선한다.

## 2026-11-20 MVP 핵심 기능 재분류 — 진행한 것 / 진행할 것

[1차 핵심 기능 실증 현황·MCP vs API 비교 및 권고](docs/43-mvp-milestone-mcp-api-tradeoff.md)를 먼저 확인한다.

- **진행한 것(실증 완료):** WIPS 검색, WIPS+NAS 기본 근거 비교, 승인된 실제 문헌 단건의 상세설명/청구항→로컬 E5 청크·벡터 증분 적재, NAS RAG 근거 조회, 서지 83건 보관(첫 페이지 최대100), 승인된 ChatGPT→Gateway→NAS 지정 경로, DB 백업·복원. 현재 DB **서지83건 / 원문 문헌6건·섹션10 / 벡터417청크 / 공식 공보 PDF0건**. 서지83건 전체 임베딩된 것은 아님.
- **진행할 것(인수):** AI 자체 평가로 대체되어 종료된 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31), 같은 연구 질문에서 WIPS 단독 vs NAS 단독 vs 양쪽 비교의 근거·정확도/재사용 효용 측정. 기능 실증 PASS를 사용자 정식 인수 PASS로 확대 금지.
- **진행할 것(선택 개선):** 허용된 신규 본문 자동 증분 적재, 공식 공보 PDF 원본 파일 보관, 사람용 전체 명세서·PDF 열람, 서버 독립 단일 도구/모든 WIPS 호출 자동 후킹. **PDF는 기본 대화형 검색·비교·RAG 기능 실증의 필수 게이트가 아님**. 다만 공보 보존이 사용자 필수 업무 요구라면 별도 미완료로 추적한다.
- **기술 선택:** 현재 개인 ChatGPT 연구에는 **WIPS MCP + NAS pgvector** 유지, 필요 시 **공보 PDF 파일만 공식 API로 보완**. MCP도 로컬 청킹/임베딩은 필요. API가 XML/JSON 원문을 제공한다면 PDF 파싱이 필수는 아님. 백엔드 반복 대량 수집 요구가 생길 때 API 중심으로 재평가.
- 기존 P0-1~P0-5의 세부 작업·설계와 상태는 유지하되, **핵심 기능 실증 완료 vs 미완료 확장/사용자 인수**를 혼동하지 않는다. MyFolder는 사용자 지시 HOLD.

## P0 — 개인용 MVP (최우선)

목표: 사용자가 자연어로 연구 목적만 설명하면 ChatGPT가 NAS 기존 특허 검색 → WIPS 추가 검색 → 허용 자료 수집/적재 → 중복 제거 → 근거 기반 후보 비교·추천을 수행하고, 이후 동일 질문에서 저장 자료를 재사용할 수 있다. 별도 웹 Agent/관리 UI/외부 모델 API는 MVP 필수 조건이 아니다. 기존 개인 플러그인과 권한 경계를 활용한다.

| ID | 우선순위 / 작업 | 현재 상태 | 완료 기준 |
|---|---|---|---|
| MVP-01 | 기존 NAS RAG 통합 MCP 전환 및 개인 ChatGPT 도구 갱신 | 운영 배포 PASS 56/56, 개인 플러그인 신규 읽기 E2E PASS; 실제 rollback NOT RUN (MVP-05 잔여) ([실측](docs/24-mvp01-production-cutover.md)) | 기존 플러그인을 유지하면서 실제 search_patents/get_patent 호출 성공, 기존 읽기 기능 회귀; 실제 rollback은 MVP-05 안전/복구 gate에서 별도 검증 |
| MVP-02 | 실제 문헌 상세 조회 및 증분 적재 | 로컬 PASS — 기존 3건 보강·신규 1건, 167청크/384D, 4배치 중복/충돌 검증 ([실측](docs/22-mvp02-incremental-patent-ingest.md)) | 기존 3건의 허용된 요약·청구항·상세설명 보강 또는 권리 명시 시험 자료, 2개 이상 소량 배치 신규/중복/충돌 검증, 문헌/섹션별 provenance와 건수/벡터 검증 |
| MVP-03 | 자연어 연구 질문 → 검색 계획 → NAS/WIPS 호출 | 운영 단건 실제 적재·재사용·ChatGPT 읽기 PASS ([실측](docs/35-mvp03-actual-ingest-acceptance.md)); 상시 자동 쓰기 연계 미구현 ([adapter](docs/26-mvp03-approved-ingest-adapter.md)) ([실측](docs/23-mvp03-research-flow.md)) | ChatGPT가 질문에 따라 검색어 확장, 검색 범위 결정, 두 소스 구분, 권한 내 신규 자료만 수집 및 적재 재사용; 자유로운 대량 수집 없이 제한된 on-demand batch |
| MVP-04 | 기본 검색·중복 제거·근거 기반 후보 비교/추천 | PASS — 참조 모듈 및 실제 두 소스 한정 시험, 27/27; 6→5, HOLD 3/EXCLUDE 2/후보 0 ([실측](docs/25-mvp04-candidate-comparison.md)) | NAS 벡터 결과와 WIPS 키워드 검색을 출처별로 수집 후 문헌번호/종류 단위 중복 제거; 근거 위치·문헌 출처·불확실성 표시, 무관하거나 근거 부족 시 추천 보류. 고급 Hybrid/RRF·reranker는 P1 |
| MVP-05 | 최소 안전·복구·종단간 인수 시험 | 실제 복원 PASS, 격리 rollback 96/96 및 범위 한정 인수 5/5 PASS ([신규 운영 실측](docs/35-mvp03-actual-ingest-acceptance.md)) ([rollback/인수](docs/28-mvp05-rollback-acceptance.md)) ([실측](docs/27-mvp05-private-backup-restore.md)) | 실제 자료별 백업 복원/ACL/무결성, 인증/권한/실패 시 차단, 회귀 및 rollback, 최소 5개 질의(정상·반복 재사용·신규 적재·근거 부족·실패/거부)의 기대 결과/실측 기록, 개인 ChatGPT의 실제 end-to-end 증거 |
| MVP-06 | 최소 사용자 확인 및 사용법 | 설명서 작성·실제 읽기 시험 PASS; 사용자 직접 평가는 최신 결정으로 불필요·[이슈 #31 종료](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31), AI 자체 근거 검토 진행 ([실측](docs/31-mvp06-user-trial.md)) | ChatGPT에서 실제 연구 질문 한 건으로 사용자가 결과 평가 가능; 짧은 사용법·제약·운영/복구 런북 제공 |

- [x] MVP-01 승인된 기존 API만 재시작 및 통합 MCP 운영 배포, 회귀 56/56, DB 및 기타 서비스 불변 ([실측](docs/24-mvp01-production-cutover.md)).
- [x] MVP-01 사용자 Refresh·권한 추가 및 새 채팅 신규 search_patents/get_patent 실제 읽기 E2E PASS — 실제 3건 검색/조회, 9개 근거, 반복·미존재·기존 읽기 회귀 ([실측](docs/24-mvp01-production-cutover.md)). 실제 rollback 검증은 아래 MVP-05 잔여 항목.
- [x] MVP-02 기존 3건 상세설명/전체 청구항 32개 보강, 신규 문헌 1건, 4개 배치 적재·중복/충돌·출처·벡터 확인 ([실측](docs/22-mvp02-incremental-patent-ingest.md)). 신규 1건 상세 수집·자동 흐름은 MVP-03 이후.
- [x] MVP-03 연구 목적 분석·질의 확장·제한된 WIPS/NAS 오케스트레이션과 실제 신규 1건 상세 적재·동일 질의 재사용 검증, 정책 21/21 ([실측](docs/23-mvp03-research-flow.md)).
- [x] MVP-03 운영 승인 기반 단건 adapter 구현/합성 검증 — JS 29/29, NAS native Python 23/23, 문헌별 허용/중복/실패·부분 재개/사후 검증. [실측](docs/26-mvp03-approved-ingest-adapter.md).
- [x] MVP-03 실제 PostgreSQL·pgvector·E5 기반 합성 단건 적재 시험 17/17 — CLI 승인/변조 차단·신규·중복·부분 복구/충돌/ACL, 운영 원본/컨테이너 불변. [실측](docs/32-mvp03-isolated-backend-test.md).
- [x] MVP-03 승인 CLI 단건 writer 직렬화 구현 및 실제 NAS native/격리 DB 검증 53/53. [실측](docs/33-mvp03-writer-serialization.md). 운영 공용 lock mount/legacy writer 배제 및 실제 신규 적재는 별도.
- [x] MVP-03 단건 NAS 로컬 stdin transport 및 교차 컨테이너 lock 구현·격리 E2E PASS. [실측](docs/34-mvp03-local-transport.md). 실제 운영 배치/승인 및 ChatGPT 신규 쓰기 연결은 미실행.
- [x] MVP-03 사용자 승인 실제 WIPS 1건 수집, 기존 NAS 운영 private transport check/apply/reuse 및 실제 ChatGPT 조회 — [실측](docs/35-mvp03-actual-ingest-acceptance.md), 6/10/417·384D, 기존 서비스/원문 불변. 상시 자동 쓰기 tool/JS wiring 미구현, 기존 reader 유지.
- [x] MVP-04 기본 결과 통합·중복 제거·근거 표시 및 후보 비교/추천 보류 — 합성 27/27, 실제 NAS 3+WIPS 3 통합 5건·근거 18개·HOLD 3·EXCLUDE 2, 실제 물성 근거 부족 추천 0. [실측](docs/25-mvp04-candidate-comparison.md). 상시 자동 연계와 전체 인수는 MVP-03/MVP-05.
- [x] MVP-05 실제 자료 온라인 dump 독립 격리 복원 — 데이터 5/8/401, fingerprint·ACL·HNSW·384D·Top3 일치, 운영 상태 불변 및 cleanup PASS; ChatGPT 실제 읽기 회귀 PASS. [실측](docs/27-mvp05-private-backup-restore.md).
- [x] MVP-05 격리 rollback 96/96 및 실제 읽기/안전 차단 인수 4/5 시나리오 — 현재→이전→현재 HTTP·임시 SCRAM/ACL·교차 DB·운영 불변. [실측](docs/28-mvp05-rollback-acceptance.md).
- [x] MVP-05 실제 신규 단건 운영 적재/재사용 인수 — [실측](docs/35-mvp03-actual-ingest-acceptance.md), 사전·사후 backup, 기존 행 보존, 중복 쓰기0, 실제 ChatGPT 조회 PASS. 최신 dump 격리 복원·실제 운영 rollback·재기동/다른 계정 검증 별도.
- [x] MVP-06 실제 연구 질문 읽기 시험 및 최소 안내 — [사용자](docs/29-mvp06-user-guide.md), [관리자](docs/30-mvp06-operator-guide.md), [실측](docs/31-mvp06-user-trial.md) (3+3→5, 근거18, HOLD4/EXCLUDE1).
- [x] MVP-03 P0-1 검색 목록 자동 저장 기반 코드 작성 및 JS wrapper 9/9·실제 WIPS 읽기 callback 1/1 검증. [실측](docs/37-mvp-search-list-archive.md). 기존 실행기 장애는 재검증으로 해소.
- [x] MVP-03 P0-1 실제 NAS 격리 DB/CLI 시험 12/12 및 운영 schema-only 기반 migration/별도 DB backup restore·ACL/데이터 일치 PASS. [실측](docs/37-mvp-search-list-archive.md). 운영 변경 없음.
- [x] MVP-03 P0-1 운영 schema/NOLOGIN 역할 및 코드 배치, backup/rollback script archive 호환, 실제 운영 권한/트랜잭션/복원/ChatGPT 읽기 PASS. [실측](docs/38-mvp-archive-production-migration.md); 새 API rollback drill 실행 NOT RUN.
- [x] MVP-03 P0-1 운영자 전용 목록 전송 경로 코드·NAS 배치 및 기본 비활성 차단 운영 실증. [실측](docs/38-mvp-archive-production-migration.md). 신규 transport 허용 worker 분기 미검증.
- [x] MVP-03 P0-1 사용자가 지속 서지 보관 **검색당 100건** 허용 확인(별도 계약 증빙 미확인), 운영 writer 활성 및 WIPS 실제 첫 페이지 83건 보관·동일 페이지 신규0·백업 복원·기존 MCP 읽기 회귀 PASS. [운영 실측](docs/39-mvp-archive-100-live-acceptance.md).
- [x] **P0-1~P0-5 작업별 설계서·실행 계획서 10개 및 실행 인덱스** 작성. [전체 진입점](docs/mvp-implementation/INDEX.md). 각 단위: 기능/기술/데이터흐름/API·DB/권한·사전 위험/단계별 변경·테스트/복구/완료 기준. **문서화 완료**이며 작업별 실제 신규 구현/운영 시험 완료와 다름.
- [x] **WIPS MyFolder MCP 별도 서비스 조사**: WIPS 공식 2026-10-12 발표, 별도 MyFolder 폴더 이름/건수·SKEY 페이지 조회 **읽기 전용** 기능(도구명/제한은 제3자 카탈로그 근거·미실측). 현재 사용자 개인 연결 도구에는 MyFolder 없음, 기존 WIPS 검색 MCP와 구분. [조사결과](docs/41-wips-myfolder-mcp-assessment.md). 추가 설치/서버 변경 없음.
- [ ] **HOLD — 사용자 명시 중지, MyFolder 최초 읽기 인증 정상화:** 신규 플러그인 도구 2개 노출 PASS, 실제 `myfolder_list_folders`는 공급자 응답 '아이디/비밀번호 확인, 맞다면 MyFolder 미생성' 실패. 윈텔립스 계정/폴더 생성 여부 사용자 측 확인 → 폴더 조회/정확한 폴더의 SKEY 1페이지 실증. [실측](docs/41-wips-myfolder-mcp-assessment.md). 비밀번호를 GitHub/채팅에 공유하지 않음.
- [ ] **HOLD — 사용자 최신 지시로 WIPS MyFolder 작업 중지(재요청 전 재개 금지).** 과거에는 **P1 선택 — WIPS MyFolder에 사용자가 이미 모아 둔 특허를 NAS로 가져오기**: MyFolder MCP 별도 발급 키/권한 연결 후 실제 `myfolder_list_folders`·`myfolder_get_folder_skeys` 조회, SKEY→WIPS 검색 서지→NAS 승인된 최대100 적재·중복0. **P0-1 자동 검색 저장의 대체/필수 전제 아님.** [설계 검토](docs/41-wips-myfolder-mcp-assessment.md).
- [x] **MVP41 — ChatGPT Code Mode WIPS 검색→Gateway NAS 저장기 실제 연결 A안**: [JS 도구 합성](poc/mvp41_orchestrate.mjs)·[계약 테스트](poc/mvp41_orchestrate.test.mjs)·[NAS owner stdin bridge](poc/mvp41_receive_and_archive.sh) 구현, Node 17/17 PASS, owner private wrapper mode700/code pin·invalid input 차단 PASS. 실제 WIPS 1회(100 요청, 83 반환) → Gateway 저장 2회 **REUSED_VERIFIED / 각 saved0·reused83**, DB archive83/83/1/83·원문6/10/417 불변·worker0 PASS. [운영 실행/다른 AI 인계](docs/42-mvp41-code-mode-gateway-archive.md). **독립 WIPS 호출 자동 hook 또는 신규 서비스 MCP 등록 NOT RUN**.
- [ ] MVP-03 P0-1 임의 WIPS 검색이 별도 ChatGPT 오케스트레이션 없이도 자동 저장되는 상시 도구·연동 구현과 새 대화 실증. 기존 WIPS MCP 호출은 자동으로 NAS에 전달되지 않음. [잔여](docs/39-mvp-archive-100-live-acceptance.md).
- [ ] MVP-03 추가 사용자 요구(P0) — WIPS 검색 결과 자동 NAS 보관, 승인 자료 원문/벡터 증분 적재, 전체 원문 조회 및 PDF·도면 제공 경로 확인. [요구사항](docs/36-mvp-automatic-archive.md). 상시 연결 및 실제 운영 E2E 대기. 원본 PDF 별도 수집은 KIPRIS Plus 국내 공보 API 우선 검증, EPO/WIPS 별도 경로 후속 검토. 텍스트 보관과 PDF 보관 상태 분리.
- [x] WIPS MCP **28개 도구 전체 카탈로그**와 실제 검증/도구 정의 구분, PDF·벡터·NAS 구현 현황 기록 — [카탈로그](docs/40-wips-mcp-capability-catalog.md). 문서화만, 나머지 도구 전체 호출/운영 구현을 PASS로 취급하지 않음.
- [ ] **P0-2: 특허 공보 PDF 수집 경로 확인** — 현재 WIPS MCP에는 PDF 다운로드 기능 없음. WIPS 별도 제공파일/다운로드 경로 확인 → 불가하면 KIPRIS Plus/EPO 등 공식 제공처 1건 다운로드, 문헌번호·종류·파일 hash·이용권한 검증 → 비공개 NAS 보관. [검증 범위](docs/40-wips-mcp-capability-catalog.md).
- [ ] **P0-3: 권한 내 선택 문헌의 상세설명/청구항→NAS 청크·벡터 증분 적재** — 기존 83건 서지목록에서 원문/벡터/PDF 상태 분리, 중복·실패 복구. 서지 최대100건 허용을 본문/벡터 전수 수집 허가로 확장 금지. [검증 범위](docs/40-wips-mcp-capability-catalog.md).
- [ ] **P0-4: 사람이 읽는 전체 명세서/공보 PDF 열람** — 현재 get_patent 제한 발췌와 구분, 인증된 페이지 조회 및 PDF 확보 후 열람. [검증 범위](docs/40-wips-mcp-capability-catalog.md).
- [ ] **P0-5: 실제 통합 인수** — 검색/서지 저장/원문 상태/보류·중복/백업 복원 확인 및 MVP-06 AI 자체 근거 검증(#31 사용자 조치 취소). [기준](docs/40-wips-mcp-capability-catalog.md).
- [x] MVP-06 사용자 직접 결과 평가 요청은 최신 결정으로 취소 — [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) not_planned 종료. AI 자체 연구 적합성 검증은 [EVAL-01](docs/evaluation/2026-11-20-eval01-ai-provisional-score.md), [EVAL-02](docs/evaluation/2026-11-20-eval02-warm-nas-replay.md)에서 계속.

**P0-1 A안 실사용 진입점:** [실제 ChatGPT 검색→NAS 재사용 운영 인수](docs/42-mvp41-code-mode-gateway-archive.md). Code Mode에서 WIPS/Gateway를 한 흐름으로 직접 호출하는 경로는 PASS, 모든 독립 WIPS 호출의 자동 저장 및 자체 MCP 서비스 등록은 미구현. 사용자 MyFolder 작업은 별도 재요청 전 HOLD. 

**P0 구현 인계 규칙:** [P0-1~P0-5 상세 설계/실행 인덱스](docs/mvp-implementation/INDEX.md) → 해당 [설계서+계획서] 2종 → 기존 코드·운영 preflight → 최소 변경/운영 실측. P0-1 통합 도구 연결이 다음 구현 대상, P0-2 공식 공보 API 범위 사전 조사 병행 가능. P0-1 설계는 backend에서 다른 WIPS MCP를 직접 호출할 권한이 미검증임을 선행 차단. P0-3 서지7필드와 기존 원문 ingest7필드 계약이 다름을 선행 차단. 모든 권리·재시작·보안 제한 유지.

**다음 실행 규칙:** MVP-01~05 범위 한정 인수 PASS, 사용자 승인 단건 실제 운영 쓰기 및 반복 재사용/ChatGPT 조회 완료 ([실측](docs/35-mvp03-actual-ingest-acceptance.md)). MVP-06 사용자 직접 평가(#31) 취소·AI 자체 근거 검증으로 전환. 사용자 최신 피드백에 따라 자동 NAS 보관/원문 조회를 P0 잔여 우선 작업으로 진행([요구사항](docs/36-mvp-automatic-archive.md)); 서지 writer 운영 연결 및 실제83건 적재 완료, 원문/PDF 별도 권리 및 상시 검색 hook 미구현. 권리 및 실행 경계 유지. 추가 가상 시험 반복 및 P1/P2/P3 선행 금지. NAS/DB/relay/tunnel/기타 기존 서비스 재기동·자동 시작 및 기술사·기업 환경 변경은 별도 승인 전 금지. 신규 구매/대량 수집·재배포 권리 확대 금지.

## P1 — MVP 사용 피드백 이후 품질 고도화 (BACKLOG)

- [ ] NAS 키워드 검색 + 벡터 검색 Hybrid RAG, RRF/재정렬, 근거 정확도 및 중복 제거 개선.
- [ ] 검색어 확장 A/B/C/D 및 300자 실험, 평가용 질의 세트/연구자 판단과 검색 품질·지연·비용 측정 고도화.
- [ ] 지속적 연구 profile/개인화, 이력/검색 조건 관리, 후보 기술 비교 기능 확장.
- [ ] 승인된 corpus의 수집량 확대·대량/정기 동기화·문헌 보강/갱신, 보존·삭제·재시도 정책. 권리/정식 요금·동시성 확인 전 범위 확대 금지.
- [ ] 사용자 피드백 후 기존 정적 UI 실제 브라우저 확인 및 개선. 필요 시 별도 FastAPI/UI 계정·profile·mock provider/독립 웹 Agent 대체안, 로그인/OAuth·사용량 제한. 실제 독립 모델 API/LLM 연동은 별도 필요성/비용/권리를 확인한 뒤 선택.

## P2 — MVP 이후 운영 및 공용 인프라 확장 (BACKLOG)

- [ ] 관리자 웹페이지, 수집/적재 현황, 접근 권한/로그, 운영 상태 및 관리 기능.
- [ ] 자동 백업·보존 주기/복원 자동화, 장애복구 및 관측. MVP 최소 실제 DB 복원은 MVP-05에 포함.
- [ ] HOLD — NAS/daemon 및 기존 컨테이너 실제 재기동·자동 시작 등록/실증 (별도 사용자 승인 필요, 순차 기동 --check PASS).
- [ ] 실제 기술사·특허 공용 영속 DB 운영 전환 및 migration/인증/복원 회귀 — 기술사 기존 배포 차단 정식 해소 및 승인 후.
- [ ] 인덱스/상대 링크 검사 CI, 승인된 격리 Docker staging 및 운영 배포, 실제 환경 테스트·회귀·rollback·HTTPS/인증/허용·비허용 접근 시험의 규모 확대.
- [ ] 최종 화면 기반 사용자 및 관리자 설명서. 독립 AI 설계 자문은 선택(배포 선행 게이트 아님).

## P3 — 기업용 구축 및 관리용 SSH (MVP 이후; 별도 착수 승인)

- [x] [기업용 ChatGPT 연결·방화벽 5-tuple·SSH 가이드](docs/21-enterprise-connectivity-firewall-ssh.md) 작성 및 공식 자료 조사.
- [ ] 실제 기업 제품(Workspace Business/Enterprise vs Azure OpenAI 자체 앱), 계약/데이터·조직 권한 확인.
- [ ] 회사 FQDN/IP/port/NAT/proxy/IdP를 반영한 방화벽 신청서 확정 및 승인.
- [ ] 회사 전용 터널/MCP/DB, OAuth/네트워크·권한·기업 RAG E2E.
- [ ] 운영 관리 전용 MCP + 내부 SSH, 최소권한/승인/감사/차단 검증. 외부 Gateway는 별도 공급사 승인 시 대안.
- [ ] 기업용 설치 패키지·기업 실제 배포/인수 및 운영 가이드 완성. 회사 서버/방화벽 변경 NOT RUN.
- 위 기업 업무는 개인 MVP의 완료 조건이 아니다. 기존 문서 보존, 추가 구현·기업 환경 조작은 별도 착수 요청까지 제외.

## 완료한 기반 작업 (기존 검증 이력 보존)

- [x] 저장소 생성 및 쓰기 권한 확인
- [x] 목차/초안 커밋 및 중앙 registry 연결 검증 (15 문서 조회 및 상대 링크 PASS; Mermaid 렌더 미검증)
- [x] 배포 우선 반복 개발 정책 반영 (독립 AI 검토 선택, AGY/Gemini 제외)
- [x] 가상 자료 기반 반응형 정적 UI (검색/후보 상세/비교/보관소/연구 설정/운영 현황)
- [x] NAS 정적 시안 컨테이너 배포 및 loopback HTML/CSS/JS 응답 검증
- [x] 사설 HTTPS 경로 연결 및 별도 기기 TLS/HTML/CSS/JS HTTP 200 검증
- [x] README/아키텍처 단순화 및 기존 기술사 RAG DB/SDK 현황 확인
- [x] 합성 문서 MCP save/get/부분문자열 search 및 중복/ID scope/conflict 검증 (ASGI 일회성; [실측](docs/09-mcp-contract-smoke.md))
- [x] 실제 pgvector SQL 검색/저장 및 DB 도메인 격리 시험 (합성 384D, 18/18 PASS; [실측](docs/10-shared-vector-smoke.md))
- [x] MCP→pgvector 통합 및 로컬 E5 실제 임베딩 검증 (24/24 PASS; [실측](docs/11-mcp-vector-integration.md); 합성 ASGI/임시 DB)
- [x] 합성 전용 지속 실행 MCP 서버 및 실제 HTTP·인증·영속 저장/복원 검사 (초기/재시작 각16/16 PASS; [실측](docs/12-persistent-mcp-stage.md))
- [x] Secure MCP Tunnel NAS 측 준비 (공식 CLI v0.0.21 설치 및 Unix socket 14/14 PASS; [실측](docs/13-secure-tunnel-preflight.md))
- [x] 사용자 runtime key 생성 및 Gateway saved metadata 확인 (값 미조회; 이후 실제 터널 인증 PASS)
- [x] 개인 tunnel_id 생성/확인, Gateway key 파일 안전 전달 및 실제 터널 인증/doctor/polling 검증 ([실측](docs/13-secure-tunnel-preflight.md))
- [x] ChatGPT 개인 플러그인 생성/설치 및 실제 write/get/vector search E2E; 신규 INSERT, 중복/미승인 차단, USER/PRIVATE 확인 ([실측](docs/14-chatgpt-plugin-e2e.md)); 합성 전용, 외부 공개 금지
- [x] 신규 P4 포함 최신 온라인 백업 및 별도 클러스터 복원/ACL/index 검증 ([실측](docs/15-online-backup-startup-plan.md)); 기존 전 서비스 재기동 없음
- [x] 순차 기동 스크립트 작성 및 read-only --check PASS
- [x] 공용 pgvector 엔진 별도 DB/role·개별 복원·동시 부하 사전 시험 (24/24, 400/400; [실측](docs/16-shared-db-coexistence.md); 합성/격리)
- [x] WIPS와 자체 MCP 동일 대화 순차 읽기 연계, 기존 합성 save/idempotency 및 mock 정책 17/17 ([실측](docs/17-dual-mcp-workflow.md))
- [x] 사용자 구매 특허 소량 실제 비공개 적재/provenance/chunk/embedding, 3건/10청크/384D 및 중복·권한 시험 ([실측](docs/18-private-patent-ingest.md))
- [x] README 목표 서비스 흐름 추가 및 실제 특허 읽기 전용 MCP 로컬 HTTP·권한 23/23 검증 ([실측](docs/19-private-patent-reader-mcp.md)); 기존 서비스 유지
- [x] 기존 NAS RAG/wipsclip 개인 플러그인 연결 재확인 및 통합 MCP 후보 39/39 로컬 시험 ([실측](docs/20-unified-mcp-candidate.md))

기존 개인 연결/실제 특허 5건(4건 상세 보강)/401청크/통합 후보 39/39, MVP-03 한정 실제 흐름/재사용 및 정책 21/21까지 확인됨. 운영 전환 56/56 PASS. 기존 ChatGPT 합성 검색 정상; 신규 도구 Refresh/실제 ChatGPT 읽기 E2E PASS; 운영 자동 적재 adapter/실제 rollback·복원 미완료. 별도 웹 시안의 실제 사용자 조작은 P1으로 이동. 이전 세부 작업과 미완료 내역은 [변경 전 계획](https://github.com/son1004007/patent-rag-agent/blob/5822b64649a867340d84fc321900fcec93c3a6ba/TASKS.md) 및 [실측 로그](WORKS.md)에서 추적한다.


## 2026-11-20 최신 후속 우선순위 — 사용자 인간 채점 제외

1. **P0 완료(범위 한정)**: [WIPS AI 300자+ 실패 문항 검색안 A/B](docs/evaluation/2026-11-20-eval01-targeted-query-rewrite.md), [NAS 읽기 전용 warm 반복 실측](docs/evaluation/2026-11-20-eval02-warm-nas-replay.md), [합성 안전 평가 코드](poc/eval02_reuse_policy.mjs). 실제 검색 도구 검증·로컬 합성 테스트 완료.
2. **P0 이번 작업 완료(범위 한정)**: [라이브 읽기-only 어댑터](poc/eval02_live_read_adapter.mjs)를 실제 연결 NAS `search_patents`/`get_patent`에 적용해 [4문항 및 freshness E2E](docs/evaluation/2026-11-20-eval02-live-read-adapter-acceptance.md) 확인. Q01/Q04 REUSE, Q05/Q08 HOLD, `freshnessRequired`는 호출0. 기존16+신규23 = Code Mode V8 39 PASS. **운영 플러그인 전역 자동 라우팅 미구현·운영 NAS 서버 변경 없음**. 사용자 검토 요청하지 않음.
3. **P0 이번 작업 완료**: [NAS 전체10문항 실경로 AI 판정](docs/evaluation/2026-11-20-eval02-full10-feature-grounding.md) — 기존4+신규6건에서 REUSE4/HOLD6. 신규6건 NAS search12 + get18, WIPS0. 근거가 섹션별로 분리된 Q01의 false HOLD 해소를 위해 `requiredFeatures` 복수 인용 검증 추가·Q01 실제 3특성 PASS. **V8 합성45 PASS**, Node CI·NAS 운영 서버 자동 연결 NOT_RUN.
4. **P0 다음**: 검색 의도별 필수 속성/제외 조건을 최소한으로 모델링하고 형식·거부 근거/안전 조건을 고정한 뒤, 운영 경로에 적용할지 검토. 이때 신규 WIPS 청구항/본문 저장, 별도 외부 AI 전송·운영 재기동/권한확대는 금지.
5. **P1 선택**: 표본 질문·검색 조건 동등화 후 통제된 COLD/WIPS 대비 실제 provider 호출·지연·비용 측정. 수치가 확인되지 않으면 ROI `INCONCLUSIVE` 유지. 새 유료/권리/서버 작업 자동 승인 아님.
6. **HOLD**: MyFolder 개발/83건 일괄 원문·벡터/PDF 적재, 무승인 기업 자료 전송·서비스 재시작, 근거 없는 범용 RAG 추천. 사용자 직접 평가 #31은 최신 지시로 취소하지만 기존 별도 신규 적재 보안 권한 #30은 유지.


- [x] **EVAL-02 NAS 실제 read-only 통합/근거 인용 게이트(선별4문항)** — 기존 구조검증 판정기와 NAS 검색2회·상세(Top3)·AI 리뷰 콜백 연결, 같은 source/문헌/청크 quote 일치 필수, 근거없으면 HOLD; 실제 Q01/Q04 ACCEPT, Q05/Q08 HOLD, freshness 0 호출. [코드](poc/eval02_live_read_adapter.mjs), [결과](docs/evaluation/2026-11-20-eval02-live-read-adapter-acceptance.md). V8 합성39 PASS, Node CI·NAS 서비스 배포 NOT RUN.


- [x] **EVAL-02 NAS live adapter 남은6문항 전부 실행 및 Q01 multi-evidence 개선** — [실측](docs/evaluation/2026-11-20-eval02-full10-feature-grounding.md), [코드](poc/eval02_live_read_adapter.mjs), [29 테스트](poc/eval02_live_read_adapter.test.mjs). 총10문항 관련자료4/근거부족6, 새6문항 search12/detail18·WIPS0, Q01 feature3 실제 PASS, 전체 V8 contract45 PASS. 다만 Node/운영 NAS 서버 배포·자동 전체 대화 적용은 아직 아님.


- [x] **WIPS MCP 외부 현황 설명에 필요한 읽기 경로 3종 최신 확인** — [실측](docs/evaluation/2026-11-20-wips-mcp-read-smoke.md), 검색식2/2·AI 자연어388자 top2 2/2·상세조회1/1 `success=true`. 개인 연결 테스트 기준이며 고객 조직 환경 연동·실제 서비스 설치/권한·PDF/전체 기능 검증은 NOT RUN. 고객 전달 시 '기본 기능 시험 PASS, 실제 적용 별도 검증'으로 범위 제한.


- [x] **EVAL-03 ChatGPT 요청형 NAS RAG→WIPS MCP 분기 실제 연결** — [코드](poc/eval03_patent_router.mjs), [Q01/Q06 실측](docs/evaluation/2026-11-20-eval03-on-demand-nas-wips-router.md), [14 테스트](poc/eval03_patent_router.test.mjs). NAS 직접 관련 근거 충분 Q01→NAS-only/WIPS0; NAS 근거 부족 Q06→WIPS1 top3. 합성 계약 총59 PASS V8. 기존 두 MCP를 ChatGPT에서 명시적 실행·읽기 전용으로 연결한 것이며 상시 자동 플러그인/서버 새 도구 등록은 아님.
- [ ] **EVAL-03 보유 여부 정확 판별** — 조회 대상이 문헌번호·종류로 특정된 경우 NAS 전체 존재 여부를 확인할 최소권한 read-only lookup 제공 여부/안전한 대안 검토. 현재 `search_patents`는 상위3 근접 문헌만 반환하므로 `INSUFFICIENT_DIRECT_EVIDENCE`를 `NOT_IN_DATABASE`로 표현하지 않는다. 인증·계약·운영 재기동 승인 없이 새 도구 강제 배포 금지.

- [x] **EVAL-03 화면 P0-1 — WIPS 검색 결과 표시**: [검증](docs/evaluation/2026-11-21-eval03-p0-1-wips-search-result-display.md). WIPS top3 문헌번호·명칭·요약·대표청구항 표시, 누락/절단 상태 및 미승인 필드 분리. 기존 서지 NAS 자동 저장 P0-1과 구별. Code Mode V8 70 PASS, 95% 미적용, NAS 운영 불변.

- [x] **화면 P0-1 수정 라우터 실제 연결 재검증** — Q01 NAS-only(WIPS0), Q06 WIPS fallback 1회/특허3건 4필드/절단 메타데이터 실제 반환 PASS. [기록](docs/evaluation/2026-11-21-eval03-p0-1-wips-search-result-display.md). 전역 MCP 배포 및 PDF·원문/벡터 자동 적재는 별도.
