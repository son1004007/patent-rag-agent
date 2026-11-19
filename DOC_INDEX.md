# 전체 문서 목차

| 문서 | 대상 및 내용 |
|---|---|
| [README](README.md) | 모든 사용자 — 진입점 |
| [AGENTS](AGENTS.md) | AI — 작업·목차 규칙 |
| [DOC_INDEX](DOC_INDEX.md) | 모든 사용자 — 전체 탐색 |
| [AI_CONTEXT](AI_CONTEXT.md) | AI — 목적·제약 |
| [CURRENT_STATE](CURRENT_STATE.md) | AI/개발자 — 검증 현황 |
| [WORKS](WORKS.md) | 모든 AI/개발자 — 작업 진행 기록 및 실측 근거 |
| [TASKS](TASKS.md) | 개발자 — 작업 순서·게이트 |
| [00 사업 설명서](docs/00-business-guide.md) | 연구/사업 담당자 — 그림 중심 업무 흐름, 활용 예 |
| [01 요구사항](docs/01-requirements.md) | 담당자/개발자 — 범위·인수 기준 |
| [02 아키텍처](docs/02-architecture.md) | 개발자 — 구성·검색·적재 |
| [03 데이터/API](docs/03-data-api.md) | 개발자 — DB·API |
| [04 품질 평가](docs/04-evaluation.md) | 연구/개발자 — 검색 정확도 검증 |
| [05 보안·배포](docs/05-deployment.md) | 운영자 — HTTPS·네트워크·복구 |
| [06 연동 및 계약](docs/06-provider-policy.md) | 사업/개발자 — 비용·권한·MCP |
| [07 테스트](docs/07-test-plan.md) | QA — 검증 기준 |
| [23 MVP-03 자연어 연구 질의·검색/수집 흐름](docs/23-mvp03-research-flow.md) | 개발자/운영자 — 질의 계획·범위/권한 정책·실제 소량 연계 시험 |
| [22 MVP-02 실제 상세 수집·증분 적재](docs/22-mvp02-incremental-patent-ingest.md) | 개발자/운영자 — 4건·167청크 실제 적재, 중복/충돌/원본 보존 검증 |
| [21 기업용 ChatGPT 연동·방화벽·SSH 가이드](docs/21-enterprise-connectivity-firewall-ssh.md) | 기업 보안/네트워크/운영 담당자 — 제품 구분, 방화벽 5-tuple 신청표, SSH 관리 및 승인·검증 절차 |
| [20 기존 플러그인 확인 및 통합 MCP 후보](docs/20-unified-mcp-candidate.md) | 개발자/운영자 — 기존 연결과 실제 특허 통합 후보 39/39 실측, 운영 전환 보류 |
| [19 실제 특허 읽기 전용 MCP](docs/19-private-patent-reader-mcp.md) | 개발자/운영자 — 실제 특허 조회·검색·권한 제한 HTTP 실측 |
| [18 실제 구매 특허 자료 적재](docs/18-private-patent-ingest.md) | 개발자/운영자 — 개인 NAS 비공개 적재·벡터 실측 |
| [17 WIPS·NAS MCP 연계](docs/17-dual-mcp-workflow.md) | 개발자/사업 담당자 — 동일 대화 실측, 저장 정책 및 공급자 확인 항목 |
| [16 공용 DB 공동 운영 사전 검증](docs/16-shared-db-coexistence.md) | 개발자/운영자 — 도메인 분리·동시 검색·독립 복원 실측 |
| [15 온라인 백업·순차 기동 준비](docs/15-online-backup-startup-plan.md) | 운영자 — 최신 복원 실측, 무중단 기동 점검 및 실제 재기동 보류 |
| [14 ChatGPT 개인 플러그인 E2E](docs/14-chatgpt-plugin-e2e.md) | 개발자/운영자 — ChatGPT 실제 신규 저장·조회·벡터 검색 실측 |
| [13 Secure MCP Tunnel 연결 준비](docs/13-secure-tunnel-preflight.md) | 운영자 — 공식 CLI·Unix 소켓 실측·개인 터널 인증 절차 |
| [12 영속 MCP 시범 서비스](docs/12-persistent-mcp-stage.md) | 개발자/운영자 — 로컬 HTTP 인증·영속 DB·재시작·복구 검증 |
| [11 MCP·E5·pgvector 통합 실측](docs/11-mcp-vector-integration.md) | 개발자 — 실제 임베딩과 DB의 종단간 합성 시험 |
| [10 공동 pgvector 실측](docs/10-shared-vector-smoke.md) | 개발자 — 실제 DB 권한 분리·벡터 검색 시험 및 터널 조건 |
| [09 MCP 계약 실측](docs/09-mcp-contract-smoke.md) | 개발자 — 합성 데이터 MCP 로컬 시험과 연결 잔여 조건 |
| [08 설계 결정](docs/08-decisions.md) | AI — 결정과 가정 |

새 AI는 AGENTS → 이 목차 → AI_CONTEXT → CURRENT_STATE → TASKS 순으로 읽고 필요한 상세 문서만 탐색한다. 모든 신규 문서에 링크를 추가한다.
