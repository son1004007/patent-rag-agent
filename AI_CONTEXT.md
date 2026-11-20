# AI Context

개인 PoC. 목표는 연구자가 짧은 질문으로 특허를 찾고 근거 기반 후보 기술을 비교하며, 승인된 자료를 자동 적재해 재사용하는 서비스다. 화학·소재 비개발자에게 이해되는 별도 사업 설명서 유지.

- Python/FastAPI, HTML/JS, PostgreSQL+pgvector, Docker Compose 제안. LLM/검색 제공자는 어댑터 분리.
- 300자 확장은 실험 조건이지 필수 조건/정확도 보장이 아니다. 원문 보존 및 명시 profile 반영.
- WIPS AI·키워드 검색/명세서 조회는 채팅에서 제한적으로 성공했지만 독립 앱/영구 적재 미검증.
- 외부 네트워크 IP 제한은 운영자 관리. NAS HTTPS/인증/내부 격리. IP allowlist 앱 구현 불필요.
- 데이터 저장·embedding·공유·LLM 처리 권리, 호출 가격·독립 인증은 미확인. 허가 전 적재 금지.
- 공개 repo: 실제 고객/조직 데이터, 네트워크 정보, 키 기록 금지.

- 2026-11-19 최신 사용자 결정: AGY/Gemini 제외. 독립 AI 검토는 선택 사항이며 배포 필수 게이트가 아니다. 작은 변경 → 최소 점검 → 시범 배포 → 실제 환경 테스트·수정 반복. 기존 계약/인증/HTTPS/외부 접근 및 기밀 보호는 유지.

- 최신 사용자 지시: UI 퍼블리싱 먼저, 사설 HTTPS 배포 후 사용자 확인. 실기능 일괄 구현은 화면 확인 이후. 최종 사용/관리자 설명서도 구현 완료 후 작성.

- 최신 사용자 결정: ChatGPT 중심 MCP 연동을 우선 실증. 기존 기술사 RAG와 pgvector 엔진·로컬 임베딩 자산 공동 사용 검토, 도메인 DB/역할/접근 분리. 상세 우선 설계는 README/아키텍처. 기존 웹 시안 보존; 실제 기능 확대보다 MCP 쓰기·조회 및 연결 검증 먼저. WIPS 자료 적재는 권한 확인 전 금지.

- 최신 사용자 결정(2026-11-19): 개인 ChatGPT 기반 MVP 우선. [TASKS.md](TASKS.md)의 MVP-01~06 실행 순서를 따른다. 고급 검색·웹 관리·공용 DB·기업/SSH는 MVP 이후 backlog, 기업 배포 별도 착수 필요. 기존 NAS/컨테이너 재기동 금지 유지. 실제 특허는 사용자 구매·개인 내부 적재 지시 범위에서 3건 실증 완료, 공급자 계약상 범위 확대 및 외부 반환 확인은 별도 gate. 이전 문구는 계획 당시 기록이며 최신 상태는 CURRENT_STATE/TASKS 우선.

- 최신 사용자 승인: 특허 MCP API만 재시작/배포. 실제 운영 56/56 PASS, 기존 ChatGPT 합성 검색 정상, 새 2개 읽기 도구 Refresh 및 새 ChatGPT 대화 실제 검색/조회 PASS(3/3), 실제 rollback/쓰기 adapter 미완료. 다른 컨테이너/DB/NAS 재기동 금지. [실측](docs/24-mvp01-production-cutover.md).

- MVP-04 기본 통합·근거 비교 참조 모듈 및 실제 두 소스 한정 시험 PASS: 27/27 합성, 6→5, 추천 근거 부족 시 HOLD, 무관 EXCLUDE, 유사도와 검증된 성능 구분. [실측](docs/25-mvp04-candidate-comparison.md). 별도 상시 자동 실행/쓰기 adapter 및 복원 미완료. 다음 MVP-03 잔여와 MVP-05.

- MVP-03 승인된 단건 적재 adapter 구현·합성 PASS(29 JS, 23 NAS Python), 기존 운영 reader DB 5건/401청크/4건 상세/384D 재확인. 실제 구매 신규 후보/권리 및 operator 승인된 private transport/직렬화가 준비된 뒤 실제 E2E 진행; MCP writer 권한 확대 금지. [실측](docs/26-mvp03-approved-ingest-adapter.md). 다음 비파괴 MVP-05 실제 자료 격리 복원.

- MVP-05 실제 특허 온라인 backup/격리 복원 PASS, 5건/8섹션/401청크, fingerprint·ACL·HNSW·384D·Top3, 원본/기존 컨테이너 불변 및 최종 SHA256. [실측](docs/27-mvp05-private-backup-restore.md). 다음 격리 rollback 및 인수 시나리오, 권리 확인 후 실제 신규 쓰기. 운영 재기동/rollback 별도 승인.

- MVP-05 격리 rollback 96/96 PASS, 실제 개인 ChatGPT 읽기/안전 차단 4/5 시나리오 PASS. [실측](docs/28-mvp05-rollback-acceptance.md). 신규 쓰기 인수 BLOCKED [#30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30); 운영 rollback/재기동 별도 승인. 다음 MVP-06 최소 안내 준비 및 사용자 확인, 승인 후 신규 쓰기.

- MVP-06 [사용자 설명서](docs/29-mvp06-user-guide.md)/[관리자 설명서](docs/30-mvp06-operator-guide.md) 작성, [새 실제 연구 질문 시험](docs/31-mvp06-user-trial.md) PASS(3+3→5, 근거18, HOLD4/EXCLUDE1). 사용자 평가 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) 대기; 실제 신규 적재 [#30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30) 유지. 변경은 문서만.

- MVP-03 실제 DB 엔진 기반 합성 격리 적재 17/17 PASS — 2건/4섹션/10청크/384D, CLI/LocalBackend/worker 실제 실행, 운영 fingerprint/기존 컨테이너 불변. [실측](docs/32-mvp03-isolated-backend-test.md). 신규 구매 운영 쓰기/transport는 #30, 사용자 평가 #31 대기.

- MVP-03 [writer 직렬화](docs/33-mvp03-writer-serialization.md) 구현 및 NAS native 35/35·실제 격리 DB 18/18 PASS. 운영 공용 lock 배치/legacy writer 배제 및 실제 신규 쓰기·transport #30, 사용자 평가 #31 대기. 기존 서비스 변경 없음.

- MVP-03 [로컬 단건 transport](docs/34-mvp03-local-transport.md) 구현·실제 NAS 격리 E2E PASS. 교차 컨테이너 lock, 승인 check/신규/재사용/코드 pin 차단. 운영 배치 및 구매 권리 #30/사용자 평가 #31 대기. 추가 가상 시험 반복/후속 고도화 선행 금지; 승인 후 운영 인수.

- 사용자 승인 실제 WIPS 신규 1건의 NAS 운영 transport 적재·중복 0·ChatGPT 신규 조회 PASS [실측](docs/35-mvp03-actual-ingest-acceptance.md): 운영 6/10/417, 384D, 기존 전 행·컨테이너 불변. 별도 구매 증빙 독립 검증/상시 자동 쓰기 MCP·JS wiring/운영 rollback NOT RUN. 단건 승인 파일과 duplicate secret/packet 정리 완료. 사용자 평가 #31 대기.

- 최신 사용자 요구: WIPS 검색 시 NAS 자동 저장 및 원문 보존/조회. [P0 요구사항](docs/36-mvp-automatic-archive.md). 기존 단건 운영 PASS와 상시 자동 보관 미구현 분리; 권리와 접근 경계 유지. 다음 작업 자동 보관 연결 및 원문 읽기 경로.

- 원본 PDF는 WIPS MCP 텍스트와 별도 보관 경로로 설계. [공식 API 후보](docs/36-mvp-automatic-archive.md): KIPRIS Plus 국내 공보 우선, EP Publication Server/OPS 및 WIPS 별도 계약 검토. PDF 원본 파일과 파생 텍스트/벡터를 문헌 ID로 연결; 실제 API·권리·다운로드 미검증.

- P0-1 [목록 보관 기반](docs/37-mvp-search-list-archive.md) 작성, JS 9/9 및 실제 WIPS callback 1행(저장 보류). NAS 격리 DB 실행 미확인(EXECUTOR_LOST, 재시도 queued 취소), 다음 시험 재실행→복원 호환→정책·writer 및 실제 연결. 상시 자동 보관 권리 #34, 본문/벡터 쓰기 없음.

- P0-1 [NAS DB/복원 재검증](docs/37-mvp-search-list-archive.md) PASS: 10 DB + 2 CLI, 최종 실제 운영 schema-only 기반 migration 및 별도 격리 복원 데이터/ACL 동일, 운영 불변. 다음 기존 backup/rollback 도구 보완 및 #34 권리 확인 후 실제 저장 경로 연결. 운영 migration/신규 원문/목록 쓰기 없음.

- 2026-11-20 사용자 운영 우선 지시 AGENTS 반영. [P0-1 운영 schema 및 복구 실측](docs/38-mvp-archive-production-migration.md) PASS: 실제 4 tables/1 view, writer NOLOGIN, 5개 배치 코드 blob 일치. 실제 원문 상태 6건 중 5건 상세/전체청구항 evidence 보유, 트랜잭션 rollback 이후 영속 0행, 기존 원문 6/10/417 및 기존 ACL/index/컨테이너 불변. 전후 백업·실제 신규 dump 격리 복원, ChatGPT 3/3 조회 PASS. 새 API rollback drill 실행 NOT RUN. #34 권리와 실제 자동 저장 연결 잔여.

- 2026-11-20 P0-1 [운영자 로컬 전송 배치/차단 실측](docs/38-mvp-archive-production-migration.md): 운영 배치, 기본 정책 disabled, 기존 실제 승인 보유 서지자료의 local projection BLOCKED_POLICY. 정책/반환 검증, 원문 fingerprint·컨테이너 불변, archive rows 0, writer NOLOGIN/secret 없음/worker 0. 허용 분기·상시 policy·실제 WIPS 자동 연결 및 영속 목록 적재 미완료, #34 승인 권리·한도 확인 대기. 반복 시험 대신 사용자 조치 후 실제 연동.

- 2026-11-20 사용자 명시 확인: WIPS 서지 NAS 지속 보관 허용, 검색당 최대100건. [운영 실측](docs/39-mvp-archive-100-live-acceptance.md): 실제 WIPS 첫 페이지 83건, 운영 archive 83/83/1/83, 동일 응답 재실행 신규0, rank51~83 저장, 본문·벡터 6/10/417 불변, 운영 독립 backup/restore 및 ChatGPT 기존 조회 PASS. 별도 writer role LOGIN+secret0600, 불필요한 worker 0, 원본 응답 임시 파일 제거. 일반 WIPS 플러그인 전체 호출의 상시 자동 가로채기 미구현; 다음 P0. 계약 권리는 사용자 확인(독립 증빙 미검증), 원문/PDF 저장 아님.

- WIPS 기능·구현 상태를 질문받으면 우선 [WIPS MCP 28개 도구·응답 카탈로그](docs/40-wips-mcp-capability-catalog.md)를 확인한다. 도구 정의/실제 호출/운영 구현 구분 필수. WIPS 공보 PDF 다운로드 직접 도구 없음(현재 연결 한정); 도면은 경로 반환·실제 이미지 다운로드 미검증; 청크와 384차원 E5 임베딩은 NAS 로컬. 83건 서지와 기존 6문헌·10섹션·417청크/PDF0건을 서로 혼동하지 않는다. P0 순서: 통합 검색·서지 자동 연결→공보 PDF 경로 검증→승인된 본문/벡터 증분 적재→전체 원문·PDF 열람→실사용 인수.

- 2026-11-20: 다른 채팅/AI가 P0 구현을 시작할 때 [작업별 상세 설계·실행 계획서 인덱스](docs/mvp-implementation/INDEX.md) 필수 탐색. P0-1(통합 검색→서지 자동보관), P0-2(공식 공보 PDF), P0-3(승인 본문·벡터), P0-4(전체 원문/공보 보기), P0-5(인수) 각각 design+plan 링크. 문서는 설계·진입점이며 현재 운영 실증 아닌 신규 코드/서비스 내용은 제안안. 기존 서지83/원문6·10/벡터417/PDF0과 기존 보안·권리 제한 유지.

- 2026-11-20 **최신 WIPS 검색·서지 저장 A안 운영 진입:** [MVP41 Code Mode Gateway runbook](docs/42-mvp41-code-mode-gateway-archive.md) → [P0-1 설계·계획](docs/mvp-implementation/INDEX.md). 현재 ChatGPT WIPS MCP + owner Gateway stdin adapter를 하나의 코드모드 실행에서 합성하여 실제 첫 페이지83건 조회·기존 보관 재사용 83건/새 저장0 PASS, 계약17/17, 기존 원문 불변. WIPS 키를 NAS로 옮기지 않음. B안(단일 backend MCP의 WIPS 직접 호출) 미검증, 독립 WIPS 조회의 무조건 자동 보관 미구현. 서지 검색당 첫100만. WIPS MyFolder 후속 작업은 **사용자 요청 전 HOLD**, 재제안/추적 중지.

- 2026-11-20 신규 **우선 개발은 기능 추가가 아니라 MVP 실효성 검증**: [evaluation/INDEX](docs/evaluation/INDEX.md), [DECISION-01](docs/44-mvp-evaluation-decision-criteria.md), [EVAL-01 검색 근거 비교](docs/45-search-quality-comparison-plan.md), [EVAL-02 반복 재사용](docs/46-reuse-value-verification-plan.md) 순서. 각 문서는 실행 가능한 **계획**이며 실제 테스트·데이터셋·라벨링은 NOT RUN. WIPS/NAS corpus 불일치/기존 metadata83 vs text6/vector417, 인간 검증·실제 WIPS 호출 vs DB 중복/가정 절감 분리. 10문항/판정 초기 임계값은 의사결정 제안 기준; 사용자 #31 평가 없이는 MVP 사업 가치/인수 완료 주장 금지. MyFolder HOLD.


## 2026-11-20 AI 자율 평가 전환

개인 특허 EVAL-01/02는 최신 사용자 명시 지시에 따라 ChatGPT가 관련성 및 근거를 직접 판정한다. 사람/사용자 관련성 라벨은 필수 게이트가 아니며 중앙 #31은 불필요한 사용자 액션으로 갱신 예정이다. AI 평가는 반드시 `AI_REVIEWED`로 표기하며 독립 전문가 확인/원문 전체 법적 감정은 하지 않았다고 구분. 최신 진행: [EVAL-01 query rewrite](docs/evaluation/2026-11-20-eval01-targeted-query-rewrite.md), [EVAL-02 warm replay](docs/evaluation/2026-11-20-eval02-warm-nas-replay.md). EVAL-02 NAS 읽기20회+상세 감사8회, WIPS0; 직접 근거 있는 4/10만 과거 자료 재사용 가능. EVAL-02 금액·지연·COLD 절감은 미측정.


- 2026-11-20 **EVAL-02 읽기 전용 통합 경로 구현/실행**: [`poc/eval02_live_read_adapter.mjs`](poc/eval02_live_read_adapter.mjs) → [실측](docs/evaluation/2026-11-20-eval02-live-read-adapter-acceptance.md). 실제 연결 NAS search2+detail3의 4 선별질문에서 AI 근거 Q01/Q04 REUSE, Q05/Q08 HOLD, freshness query0. Code Mode V8 합성 16+23=39 PASS. 기존 NAS MCP 서버/툴 자동 등록·배포는 NOT RUN. Code Mode는 ChatGPT가 별도 호출해야 실행됨. ROI 미측정.


- 2026-11-20 EVAL-02 **10문항 실제 NAS 어댑터 판정 완료(기존4+신규6)**: [총괄](docs/evaluation/2026-11-20-eval02-full10-feature-grounding.md). Q01~Q04 REUSE, Q05~Q10 HOLD, 추가6문항 실도구 adapter 검색12+상세18/WIPS0, Q01 다중섹션(봉지/끝단/수분) 인용 검증3 PASS. 기존 정책16+신규어댑터29 = Code Mode V8 합성45 PASS. 자동 운영 도구배포는 NOT_RUN, WIPS 대비 비용·지연 ROI 미측정.


- 2026-11-20 **EVAL-03 요청형 NAS RAG→WIPS fallback 실제 연결**: [실측](docs/evaluation/2026-11-20-eval03-on-demand-nas-wips-router.md), [라우터](poc/eval03_patent_router.mjs). 기존 ChatGPT 두 MCP를 Code Mode에서 순차 합성, Q01 NAS 근거 충족 search2/detail3 WIPS0, Q06 NAS 직접관련 부족 search2/detail3 WIPS1 top3. V8 합성/계약 16+29+14=59 PASS. **벡터 top3 부재는 전체 DB에 특허가 없다는 증명이 아니며**, 정확한 문헌번호 존재 확인 API/서버 상시 routing 미구현. 원문/DB/권한/서비스 변경 없음.
