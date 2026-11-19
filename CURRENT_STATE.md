# Current State

2026-11-19 / ChatGPT 개인 NAS RAG 플러그인 E2E PASS

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

다음 (최신 사용자 결정): 공용 영속 DB 운영 검증 → WIPS 허용 자료 연동 → 화면 및 관리자 기능 개선 → 최종 간략 사용/관리자 설명서. 기존 웹 UI 유지. 독립 AI 검토 선택. Live API/DB/외부 공개 보안 및 계약 gate는 별도.

배포 환경 제한: CPU CFS hard quota 및 pids limit 미지원, CPU shares와 128 MiB 메모리 제한 사용. 공식 Docker resource constraints 및 실제 runtime 결과 기준. 실제 장비 식별자/URL은 공개 repo에 기록하지 않음.

| 추가 검증 항목 | 상태 |
|---|---|
| 개인 WIPS MCP 플러그인 존재 | CONFIRMED — 개인 플러그인 목록 확인 (기존 성공 호출 이력) |
| 기술사 RAG 개발 pgvector volume/SDK cache | CONFIRMED — NAS 읽기 전용 inventory, 상시 RAG 컨테이너 없음 |
| 합성 MCP 계약 시험 | PASS — NAS disposable ASGI, protocol 2025-11-25, save/get/substring/idempotency/denial; [실측](docs/09-mcp-contract-smoke.md) |
| 독립 NAS MCP ChatGPT 등록/write E2E | PASS — 개인 플러그인 실제 최초 INSERT/조회/검색 및 중복 거부; [실측](docs/14-chatgpt-plugin-e2e.md) |
| 공동 pgvector SQL 시험 | PASS 18/18 — 합성 384D, 동일 클러스터 DB/role 분리, 실제 교차 접속 거부, DB 재기동; [실측](docs/10-shared-vector-smoke.md) |
| MCP→E5→pgvector 통합 | PASS 24/24 — [실측](docs/11-mcp-vector-integration.md), 합성 자료·ASGI·일회성 DB |
| 합성 전용 영속 MCP 시범 서비스 | RUNNING — [실측](docs/12-persistent-mcp-stage.md), 실제 HTTP 32/32 (초기/재시작 각16), dump 복원·재기동 fingerprint PASS, 외부 포트 0, NAS 재부팅 자동 시작 NOT RUN |
| 기술사와 특허 DB 엔진 공동 운영 | PLANNED — 기존 DB 미변경; 실제 영속/운영 공유 NOT RUN |
| Secure MCP Tunnel NAS 측 | PASS — 공식 CLI v0.0.21 SHA/기동, Unix 소켓 14/14, 기존 HTTP 16/16, relay 실행·외부 포트 0; [실측](docs/13-secure-tunnel-preflight.md) |
| OpenAI Secure MCP Tunnel | CONNECTED — [실측](docs/13-secure-tunnel-preflight.md), secret 0600, doctor PASS, OpenAI metadata fetched, MCP session initialized, /healthz /readyz 200, active polling success, 외부 port publish 0 |
| ChatGPT 개인 플러그인 등록/쓰기·조회 | PASS — USER/PRIVATE, 실제 ChatGPT 신규 P4 저장 created=true; DB 4건, 384D, Top1 일치; [실측](docs/14-chatgpt-plugin-e2e.md). WIPS 연계 및 실제 원문 미검증 |
