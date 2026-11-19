# Tasks — MVP 우선 실행 계획

> 2026-11-19 최신 사용자 결정: 기업용 구축 등 확장 기능은 MVP 이후 백로그로 이동한다. 지금은 개인 ChatGPT + WIPS + NAS RAG 조합에서 실제 연구 질문을 끝까지 처리하는 최소 기능을 우선 완성한다. 이 파일이 실행 순서의 정본이다. [현재 검증 상태](CURRENT_STATE.md), [실측 이력](WORKS.md), [변경 전 계획](https://github.com/son1004007/patent-rag-agent/blob/5822b64649a867340d84fc321900fcec93c3a6ba/TASKS.md).

## P0 — 개인용 MVP (최우선)

목표: 사용자가 자연어로 연구 목적만 설명하면 ChatGPT가 NAS 기존 특허 검색 → WIPS 추가 검색 → 허용 자료 수집/적재 → 중복 제거 → 근거 기반 후보 비교·추천을 수행하고, 이후 동일 질문에서 저장 자료를 재사용할 수 있다. 별도 웹 Agent/관리 UI/외부 모델 API는 MVP 필수 조건이 아니다. 기존 개인 플러그인과 권한 경계를 활용한다.

| ID | 우선순위 / 작업 | 현재 상태 | 완료 기준 |
|---|---|---|---|
| MVP-01 | 기존 NAS RAG 통합 MCP 전환 및 개인 ChatGPT 도구 갱신 | 운영 배포 PASS 56/56, 개인 플러그인 신규 읽기 E2E PASS; 실제 rollback NOT RUN (MVP-05 잔여) ([실측](docs/24-mvp01-production-cutover.md)) | 기존 플러그인을 유지하면서 실제 search_patents/get_patent 호출 성공, 기존 읽기 기능 회귀; 실제 rollback은 MVP-05 안전/복구 gate에서 별도 검증 |
| MVP-02 | 실제 문헌 상세 조회 및 증분 적재 | 로컬 PASS — 기존 3건 보강·신규 1건, 167청크/384D, 4배치 중복/충돌 검증 ([실측](docs/22-mvp02-incremental-patent-ingest.md)) | 기존 3건의 허용된 요약·청구항·상세설명 보강 또는 권리 명시 시험 자료, 2개 이상 소량 배치 신규/중복/충돌 검증, 문헌/섹션별 provenance와 건수/벡터 검증 |
| MVP-03 | 자연어 연구 질문 → 검색 계획 → NAS/WIPS 호출 | 운영 단건 실제 적재·재사용·ChatGPT 읽기 PASS ([실측](docs/35-mvp03-actual-ingest-acceptance.md)); 상시 자동 쓰기 연계 미구현 ([adapter](docs/26-mvp03-approved-ingest-adapter.md)) ([실측](docs/23-mvp03-research-flow.md)) | ChatGPT가 질문에 따라 검색어 확장, 검색 범위 결정, 두 소스 구분, 권한 내 신규 자료만 수집 및 적재 재사용; 자유로운 대량 수집 없이 제한된 on-demand batch |
| MVP-04 | 기본 검색·중복 제거·근거 기반 후보 비교/추천 | PASS — 참조 모듈 및 실제 두 소스 한정 시험, 27/27; 6→5, HOLD 3/EXCLUDE 2/후보 0 ([실측](docs/25-mvp04-candidate-comparison.md)) | NAS 벡터 결과와 WIPS 키워드 검색을 출처별로 수집 후 문헌번호/종류 단위 중복 제거; 근거 위치·문헌 출처·불확실성 표시, 무관하거나 근거 부족 시 추천 보류. 고급 Hybrid/RRF·reranker는 P1 |
| MVP-05 | 최소 안전·복구·종단간 인수 시험 | 실제 복원 PASS, 격리 rollback 96/96 및 범위 한정 인수 5/5 PASS ([신규 운영 실측](docs/35-mvp03-actual-ingest-acceptance.md)) ([rollback/인수](docs/28-mvp05-rollback-acceptance.md)) ([실측](docs/27-mvp05-private-backup-restore.md)) | 실제 자료별 백업 복원/ACL/무결성, 인증/권한/실패 시 차단, 회귀 및 rollback, 최소 5개 질의(정상·반복 재사용·신규 적재·근거 부족·실패/거부)의 기대 결과/실측 기록, 개인 ChatGPT의 실제 end-to-end 증거 |
| MVP-06 | 최소 사용자 확인 및 사용법 | 설명서 작성·실제 읽기 시험 PASS; 사용자 직접 평가 대기 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) ([실측](docs/31-mvp06-user-trial.md)) | ChatGPT에서 실제 연구 질문 한 건으로 사용자가 결과 평가 가능; 짧은 사용법·제약·운영/복구 런북 제공 |

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
- [x] MVP-03 P0-1 검색 목록 자동 저장 기반 코드 작성 및 JS wrapper 9/9·실제 WIPS 읽기 callback 1/1 검증. [실측](docs/37-mvp-search-list-archive.md). DB 통합 시험은 Gateway 실행기 장애로 미확인.
- [ ] MVP-03 P0-1 목록 자동 저장 — 격리 DB/CLI 시험 재실행, 기존 backup/restore 호환, 전용 writer·운영 정책 및 ChatGPT 자동 연결, 실제 허용 목록 저장/중복0 E2E. 권리 범위 [중앙 #34](https://github.com/son1004007/ai-agent-workflow-playbook/issues/34). [구현/재개](docs/37-mvp-search-list-archive.md).
- [ ] MVP-03 추가 사용자 요구(P0) — WIPS 검색 결과 자동 NAS 보관, 승인 자료 원문/벡터 증분 적재, 전체 원문 조회 및 PDF·도면 제공 경로 확인. [요구사항](docs/36-mvp-automatic-archive.md). 상시 연결 및 실제 운영 E2E 대기. 원본 PDF 별도 수집은 KIPRIS Plus 국내 공보 API 우선 검증, EPO/WIPS 별도 경로 후속 검토. 텍스트 보관과 PDF 보관 상태 분리.
- [ ] MVP-06 사용자 직접 결과 평가/피드백 — [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) 대기.

**다음 실행 규칙:** MVP-01~05 범위 한정 인수 PASS, 사용자 승인 단건 실제 운영 쓰기 및 반복 재사용/ChatGPT 조회 완료 ([실측](docs/35-mvp03-actual-ingest-acceptance.md)). MVP-06 사용자 직접 평가(#31) 대기. 사용자 최신 피드백에 따라 자동 NAS 보관/원문 조회를 P0 잔여 우선 작업으로 진행([요구사항](docs/36-mvp-automatic-archive.md)); 운영 writer 연결 및 계약 범위 확대 미구현, 권리 및 실행 경계 유지. 추가 가상 시험 반복 및 P1/P2/P3 선행 금지. NAS/DB/relay/tunnel/기타 기존 서비스 재기동·자동 시작 및 기술사·기업 환경 변경은 별도 승인 전 금지. 신규 구매/대량 수집·재배포 권리 확대 금지.

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
