# Current State

2026-11-19 / MVP-01 통합 MCP 운영 배포 56/56 PASS; 새 ChatGPT 실제 특허 읽기 및 MVP-04 양 소스 기본 통합/비교 PASS; MVP-03 적재 어댑터 구현·합성 및 실제 DB 엔진 격리 시험 17/17 PASS, writer 직렬화 및 회귀 53/53 PASS, 로컬 transport 실제 운영 단건 E2E PASS; MVP-05 실제 DB 백업·격리 복원 및 격리 rollback 96/96 PASS; DB 6건·10섹션·417청크; MVP-06 실제 읽기 시험 PASS 및 설명서 작성, 사용자 평가 대기

| 영역 | 상태 |
|---|---|
| GitHub 저장소/쓰기 | CONFIRMED |
| 공개 여부 | PUBLIC 확인 — 일반 설계만 기록 |
| 초기 목차·사업 설명서·기술 설계 | DRAFT COMMITTED — dbeb0a3b; 15 indexed documents fetched, 7 Mermaid blocks, relative link check PASS. Mermaid rendering NOT RUN. |
| 채팅 내 MCP 검색/명세서 조회 | CONFIRMED (별도 수동 실험) |
| 독립 MCP 인증/호출 | PASS — 이전 배포 인증 검증 및 새 ChatGPT 실제 읽기 E2E; 다른 계정 비인가 재시험 NOT RUN |
| 영구 저장·LLM 처리 권리 | UNKNOWN |
| 독립 AI 설계 리뷰 | NOT RUN — 사용자 승인으로 선택 사항, 배포 차단 사유 아님 |
| MVP 정적 화면 | CODE COMMITTED — 가상 데이터, 검색/비교/보관/설정/운영 화면 흐름 |
| 실제 독립 웹 API/LLM/사용자 OAuth | NOT RUN — 합성 MCP 별도 검증 |
| NAS 시안 컨테이너 | RUNNING — dcd740d7; HTML/CSS/JS HTTP 200 on loopback; read-only non-root, memory limit applied |
| 사설 HTTPS 접근 | PASS — Tailscale Serve tailnet-only, 기존 경로 보존; 별도 Windows 클라이언트 TLS 검증 및 HTML/CSS/JS HTTP 200 |
| 브라우저 UI 동작 검증 | 사용자 확인 대기 — 별도 기기 HTTPS 응답 PASS, 실제 브라우저 조작 NOT RUN |

전역 registry 및 문서 목차 규칙 연결 확인. 설계 초안; 실제 실행으로 검증 예정.

다음 (최신 사용자 결정): MVP-01~05 범위 한정 실제 인수 PASS; 신규 실제 WIPS 문헌 1건에 대한 사용자 승인으로 기존 운영 DB에 로컬 transport 적용 및 check/apply/reuse, ChatGPT 실제 검색·조회(신규 1위)까지 검증했다. [실측](docs/35-mvp03-actual-ingest-acceptance.md). 실제 운영 총 6건·10섹션·417청크, 기존 행/컨테이너 불변. 기존 read-only MCP 유지, 상시 자동 쓰기 MCP/JS wiring 및 추가 자료 권리 확대 미실행. 사용자 직접 평가 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) 대기; 새로운 고도화 및 추가 적재는 승인/인수 이후. 기존 보안·계약·재기동·기술사/기업 별도 경계 유지.

배포 환경 제한: CPU CFS hard quota 및 pids limit 미지원, CPU shares와 128 MiB 메모리 제한 사용. 공식 Docker resource constraints 및 실제 runtime 결과 기준. 실제 장비 식별자/URL은 공개 repo에 기록하지 않음.

| 추가 검증 항목 | 상태 |
|---|---|
| 개인 WIPS MCP 플러그인 존재 | CONFIRMED — 개인 플러그인 목록 확인 (기존 성공 호출 이력) |
| 기술사 RAG 개발 pgvector volume/SDK cache | CONFIRMED — NAS 읽기 전용 inventory, 상시 RAG 컨테이너 없음 |
| 합성 MCP 계약 시험 | PASS — NAS disposable ASGI, protocol 2025-11-25, save/get/substring/idempotency/denial; [실측](docs/09-mcp-contract-smoke.md) |
| 독립 NAS MCP ChatGPT 등록/write E2E | PASS — 개인 플러그인 실제 최초 INSERT/조회/검색 및 중복 거부; [실측](docs/14-chatgpt-plugin-e2e.md) |
| 공동 pgvector SQL 시험 | PASS 18/18 — 합성 384D, 동일 클러스터 DB/role 분리, 실제 교차 접속 거부, DB 재기동; [실측](docs/10-shared-vector-smoke.md) |
| MCP→E5→pgvector 통합 | PASS 24/24 — [실측](docs/11-mcp-vector-integration.md), 합성 자료·ASGI·일회성 DB |
| 합성 전용 영속 MCP 시범 서비스 | RUNNING — [실측](docs/12-persistent-mcp-stage.md), 실제 HTTP 32/32 (초기/재시작 각16), dump 복원·재기동 fingerprint PASS, 외부 포트 0, NAS 재부팅 자동 시작 HOLD — 사용자 승인 대기 |
| 기술사와 특허 DB 엔진 공동 운영 | 사전 시험 PASS 24/24, 동시 검색 400/400, 평균 SQL 2.130/2.210ms, 개별 복원 및 ACL 검증 — [실측](docs/16-shared-db-coexistence.md). 실제 영속 DB 통합 NOT RUN(기술사 배포 차단 유지); 기존 DB 미변경 |
| Secure MCP Tunnel NAS 측 | PASS — 공식 CLI v0.0.21 SHA/기동, Unix 소켓 14/14, 기존 HTTP 16/16, relay 실행·외부 포트 0; [실측](docs/13-secure-tunnel-preflight.md) |
| OpenAI Secure MCP Tunnel | CONNECTED — [실측](docs/13-secure-tunnel-preflight.md), secret 0600, doctor PASS, OpenAI metadata fetched, MCP session initialized, /healthz /readyz 200, active polling success, 외부 port publish 0 |
| ChatGPT 개인 플러그인 등록/쓰기·조회 | PASS — USER/PRIVATE, 실제 ChatGPT 신규 P4 저장 created=true; DB 4건, 384D, Top1 일치; [실측](docs/14-chatgpt-plugin-e2e.md). WIPS 실제 원문 적재 미검증 |
| WIPS/NAS MCP 동일 대화 연계 | PASS — 실제 WIPS 식별정보 3건, 독립 주제 NAS 검색 P4 Top1, 기존 fixture 중복 차단; 참조 정책 17/17 mock PASS, live ingest/통합 ranking NOT RUN. [실측](docs/17-dual-mcp-workflow.md) |
| 구매 특허 비공개 적재 | PASS — 사용자 구매·적재 지시, 실제 3건·10 chunks·384D·검색·중복 차단·별도 dump, 전용 DB; [실측](docs/18-private-patent-ingest.md). 기존 플러그인 실제 데이터 조회 및 전체 명세서/다중 배치 미검증 |

| 실제 특허 읽기 전용 MCP | 로컬 HTTP PASS 23/23 — 실제 3건 검색·조회, 87.15ms 단일 질의, 별도 read-only role/view·교차 DB 거부, [실측](docs/19-private-patent-reader-mcp.md); ChatGPT 연결/상시 배포 NOT RUN |

| 통합 MCP 후보 | 로컬 HTTP PASS 39/39 (기존 16 + 실제 특허 23), 86.54ms 단일 질의; 현재 기존 개인 NAS RAG 연결 정상, 실제 특허 도구는 아직 미등록; [근거](docs/20-unified-mcp-candidate.md). 기존 운영 cutover/재기동 HOLD |
| 기업용 ChatGPT 연결·SSH | [설계 및 방화벽 신청표 작성](docs/21-enterprise-connectivity-firewall-ssh.md) — 공식 문서 기반, 실제 기업 제품·테넌트·네트워크·운영 SSH 승인/검증 NOT RUN |

| MVP-02 실제 특허 상세·증분 적재 | PASS — 기존 3건 상세/청구항 32개, 신규 1건 metadata, 누적 4건·6섹션·167청크/384D, 4개 배치 중복 0/충돌 차단, 원본과 StartedAt 불변, 최신 dump 448,812 bytes; [실측](docs/22-mvp02-incremental-patent-ingest.md). 자동 수집 및 실제 ChatGPT E2E 미완료 |

| MVP-03 자연어 질의 검색·수집 | PASS (한정 실제 시험) — 정책 21/21, 실제 NAS/WIPS 3+3 후보, 신규 1건·234청크, 누적 5건·8섹션·401청크/384D, 신규 문헌 재검색 2순위/기존 판정/추가 쓰기 0, 최신 dump 1,037,393 bytes. [실측](docs/23-mvp03-research-flow.md). 실제 개인 플러그인 운영 자동 연계 및 dump 복원 미완료 |

| MVP-01 통합 MCP 운영 전환 | PASS — API 단독 재시작, 로컬 HTTP 16+24 및 Unix relay 16=56/56, 실제 특허 검색 109.78ms, DB fingerprint/기타 StartedAt/기존 API ID·HostConfig 불변. 기존 ChatGPT 합성 조회/검색 정상, 신규 2개 도구 Refresh 및 새 대화 실제 검색/조회 PASS(3/3); 실제 rollback NOT RUN. [실측 및 Refresh 절차](docs/24-mvp01-production-cutover.md) |

| MVP-04 기본 통합·근거 비교 | PASS (참조 구현·한정 실제 양 소스) — 27/27 합성, NAS 3 + WIPS 3 → 중복 1/unique 5, HOLD 3·EXCLUDE 2·검토 후보 0, 근거 18개. 중간 WIPS 검증 실패 후 실제 재호출 PASS; 상시 자동 실행/물성 검증/DB 변경 NOT RUN. [실측](docs/25-mvp04-candidate-comparison.md) |

| MVP-03 승인된 단건 적재 adapter | CODE + SYNTHETIC PASS — NAS Python 23/23, JS 정책/연계 29/29; 실제 운영 reader DB 5건/401청크/4건 상세/384D 일치. 격리 LocalBackend PASS, 실제 운영 신규 쓰기/transport NOT RUN, 문헌별 권리·운영 승인 및 직렬화 유지. [실측](docs/26-mvp03-approved-ingest-adapter.md) |

| MVP-05 실제 DB 백업·복원 | PASS — 1,037,393 bytes/0600, 격리 복원 5건·8섹션·401청크·384D, 전체 row fingerprint/ACL/HNSW/Top3 일치, SET ROLE 원본 테이블 거부, 운영 상태 불변·임시 정리·SHA256 검증. 이후 ChatGPT 실제 조회 3/3 PASS. 전체 인수/rollback/신규 적재 NOT RUN. [실측](docs/27-mvp05-private-backup-restore.md) |

| MVP-05 격리 API rollback·인수 | PASS 96/96 (현재40→이전16→현재40) 및 읽기/안전 차단 4/5. 복제본 및 운영 fingerprint·컨테이너 상태 불변, cleanup PASS. 실제 신규 쓰기 BLOCKED [#30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30); 실제 운영 rollback/다른 계정 NOT RUN. [실측](docs/28-mvp05-rollback-acceptance.md) |

| MVP-06 사용자·관리자 안내 | 문서 작성 및 실제 연구 질문 읽기 시험 PASS — 3+3→5, 근거18, HOLD4/EXCLUDE1/후보0. 사용자 직접 평가 대기 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31); 실제 신규 쓰기 [#30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30). [사용자](docs/29-mvp06-user-guide.md) / [관리자](docs/30-mvp06-operator-guide.md) / [실측](docs/31-mvp06-user-trial.md) |

| MVP-03 실제 DB 엔진 격리 적재 | PASS 17/17, 가상 2건·4섹션·10청크·384D, 신규·무쓰기·부분 복구·충돌·ACL, 운영 전체 fingerprint 및 컨테이너 불변. [실측](docs/32-mvp03-isolated-backend-test.md). 실제 신규 특허/운영 transport 및 사용자 평가 대기. |

| MVP-03 승인 CLI writer 직렬화 | PASS 53/53 (native 35, 격리 DB 18), 공유 inode lock·경합 차단·FD 승계. 운영 DB fingerprint 및 기존 컨테이너 불변. 운영 배포/legacy writer 배제/교차 컨테이너 검증·신규 승인/사용자 평가 대기. [실측](docs/33-mvp03-writer-serialization.md) |

| MVP-03 NAS 로컬 단건 transport | 코드 및 실제 격리 E2E PASS — check/신규/1·2·5·384D/재사용 쓰기0/코드 pin 차단/교차 컨테이너 lock, 운영 fingerprint·모든 기존 실행 컨테이너 불변. [실측](docs/34-mvp03-local-transport.md). 실제 운영 배치/구매 승인 #30 및 사용자 평가 #31 대기. |

| MVP-03/05 실제 승인 단건 운영 인수 | PASS — 6/10/417, 384D, 운영 check/apply/reuse, 기존 전 행 및 컨테이너 불변, 전후 backup, 신규 실제 ChatGPT 검색 1위/반복 및 상세 근거 3개. [실측](docs/35-mvp03-actual-ingest-acceptance.md). 상시 자동 쓰기 경로 및 사용자 평가 별도. |

## 최신 운영 지시
- 사용자 최신 결정: 특허 MCP API만 재시작·배포 승인 및 완료. NAS/DB/relay/tunnel/다른 컨테이너 stop/restart 금지 유지, 자동 시작 등록/실행 승인 대기.
- 최신 4건 온라인 dump 및 별도 빈 클러스터 복원·ACL·인덱스·384D PASS; 기존 컨테이너 StartedAt 불변. 순차 시작 --check PASS 및 ChatGPT P4 조회 정상. [실측](docs/15-online-backup-startup-plan.md).

- 사용자 구매 특허의 개인 NAS 내부 적재 지시 반영. 유료 구매의 구체적 계약 범위는 별도, 상업 이용·재배포·대량 수집으로 확대하지 않는다. 기존 재기동 금지 유지.

- 사용자 Refresh·권한 추가 수행 확인. 기존 대화에서는 NAS RAG 3개 도구만 발견; 기존 get_document 실제 정상 및 PRIVATE 유지. 새 대화에서 신규 search_patents/get_patent 직접 검증 PASS. 동일 질의 재검색 순위 일치, 실제 상세 3/3, 근거 9개, 제한 및 미존재 처리 PASS. 실제 DB 재계수/쓰기/rollback NOT RUN. MVP-04 기본 비교 시험 PASS. 다음 MVP-03 쓰기 adapter 잔여 및 MVP-05 복원·인수. [기록](docs/24-mvp01-production-cutover.md).

- 2026-11-19 사용자 최신 피드백: WIPS MCP 검색 결과 NAS 자동 저장 및 사람용 원문 보관/조회 요구. [P0 요구사항](docs/36-mvp-automatic-archive.md). 텍스트 원문 단건 저장 PASS, 자동 연결/전체 원문 조회/PDF·도면 파일 검증 미완료. 추가 실자료 저장·배포는 이번에 미실행.

- 원본 PDF 확보 경로 보완: [공식 API 후보 및 파일 수집 설계](docs/36-mvp-automatic-archive.md) — KIPRIS Plus 국내 공보 API 우선, EPO 및 공급자 별도 경로 검토. WIPS MCP 텍스트 저장 PASS와 PDF 수집 미구현 분리. 공식 서비스 안내 확인, 실제 API 인증/다운로드/권리 검증 NOT RUN.

- 2026-11-20 P0-1 검색 목록 자동 저장 착수: [구현/검증](docs/37-mvp-search-list-archive.md), JS 9/9·실제 WIPS 기존 승인 문헌 1행 callback PASS(저장 보류). DB 통합 시험 EXECUTOR_LOST/재시도 queued 취소; 운영 preflight 6/10/417, 신규 schema 0, 시험 컨테이너 0. 실제 저장/운영 배포 자동 연결 미실행. 권리 범위 [#34](https://github.com/son1004007/ai-agent-workflow-playbook/issues/34) 대기.

- 2026-11-20 P0-1 [재검증](docs/37-mvp-search-list-archive.md): 이전 Gateway 장애 해소, DB/CLI 12/12 PASS, 실제 운영 schema-only 복제·명시 CONNECT/역할 분리·신규 archive 데이터/ACL 별도 복원 PASS. 기존 운영 원문 fingerprint 및 실행 컨테이너 불변, 시험 정리 완료. 운영 backup/rollback 도구 갱신 및 권리 #34·운영 writer/ChatGPT 연결 잔여. 실제 운영 migration/적재/재시작 미실행.

- 2026-11-20 사용자 운영 우선 지시 AGENTS 반영. [P0-1 운영 schema 및 복구 실측](docs/38-mvp-archive-production-migration.md) PASS: 실제 4 tables/1 view, writer NOLOGIN, 5개 배치 코드 blob 일치. 실제 원문 상태 6건 중 5건 상세/전체청구항 evidence 보유, 트랜잭션 rollback 이후 영속 0행, 기존 원문 6/10/417 및 기존 ACL/index/컨테이너 불변. 전후 백업·실제 신규 dump 격리 복원, ChatGPT 3/3 조회 PASS. 새 API rollback drill 실행 NOT RUN. #34 권리와 실제 자동 저장 연결 잔여.
