# Current State

2026-11-19 / MVP-01 통합 MCP 운영 배포 56/56 PASS; 기존 ChatGPT 정상, 신규 도구 Refresh 대기; 실제 5건·401청크

| 영역 | 상태 |
|---|---|
| GitHub 저장소/쓰기 | CONFIRMED |
| 공개 여부 | PUBLIC 확인 — 일반 설계만 기록 |
| 초기 목차·사업 설명서·기술 설계 | DRAFT COMMITTED — dbeb0a3b; 15 indexed documents fetched, 7 Mermaid blocks, relative link check PASS. Mermaid rendering NOT RUN. |
| 채팅 내 MCP 검색/명세서 조회 | CONFIRMED (별도 수동 실험) |
| 독립 MCP 인증/호출 | NOT RUN |
| 영구 저장·LLM 처리 권리 | UNKNOWN |
| 독립 AI 설계 리뷰 | NOT RUN — 사용자 승인으로 선택 사항, 배포 차단 사유 아님 |
| MVP 정적 화면 | CODE COMMITTED — 가상 데이터, 검색/비교/보관/설정/운영 화면 흐름 |
| 실제 독립 웹 API/LLM/사용자 OAuth | NOT RUN — 합성 MCP 별도 검증 |
| NAS 시안 컨테이너 | RUNNING — dcd740d7; HTML/CSS/JS HTTP 200 on loopback; read-only non-root, memory limit applied |
| 사설 HTTPS 접근 | PASS — Tailscale Serve tailnet-only, 기존 경로 보존; 별도 Windows 클라이언트 TLS 검증 및 HTML/CSS/JS HTTP 200 |
| 브라우저 UI 동작 검증 | 사용자 확인 대기 — 별도 기기 HTTPS 응답 PASS, 실제 브라우저 조작 NOT RUN |

전역 registry 및 문서 목차 규칙 연결 확인. 설계 초안; 실제 실행으로 검증 예정.

다음 (최신 사용자 결정): [TASKS.md](TASKS.md)의 MVP-01~06을 우선한다. 통합 MCP 운영 전환 완료(승인받은 API만 재시작), 신규 도구 Refresh 및 실제 ChatGPT 조회 대기 동안 MVP-02 로컬 및 MVP-03 한정 실제 흐름/재사용 검증 완료 후 MVP-04(기본 통합 및 근거 추천)의 비파괴 구현/격리 검증과 실제 자료 백업 복원을 진행한다. 전환 후 전체 E2E와 최소 사용 안내로 MVP 인수. 고급 검색·웹 UI/관리·공용 DB 전환·기업/SSH는 MVP 이후; 기업 별도 착수 요청 전 진행하지 않는다. 기존 보안·계약·기술사 배포 gate 및 재기동 금지는 유지.

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

| MVP-01 통합 MCP 운영 전환 | PASS — API 단독 재시작, 로컬 HTTP 16+24 및 Unix relay 16=56/56, 실제 특허 검색 109.78ms, DB fingerprint/기타 StartedAt/기존 API ID·HostConfig 불변. 기존 ChatGPT 합성 호출 정상, 신규 2개 도구 Refresh 및 직접 호출 대기. [실측 및 Refresh 절차](docs/24-mvp01-production-cutover.md) |

## 최신 운영 지시
- 사용자 최신 결정: 특허 MCP API만 재시작·배포 승인 및 완료. NAS/DB/relay/tunnel/다른 컨테이너 stop/restart 금지 유지, 자동 시작 등록/실행 승인 대기.
- 최신 4건 온라인 dump 및 별도 빈 클러스터 복원·ACL·인덱스·384D PASS; 기존 컨테이너 StartedAt 불변. 순차 시작 --check PASS 및 ChatGPT P4 조회 정상. [실측](docs/15-online-backup-startup-plan.md).

- 사용자 구매 특허의 개인 NAS 내부 적재 지시 반영. 유료 구매의 구체적 계약 범위는 별도, 상업 이용·재배포·대량 수집으로 확대하지 않는다. 기존 재기동 금지 유지.
