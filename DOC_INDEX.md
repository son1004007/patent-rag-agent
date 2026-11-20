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
| [EVAL-01 10문항 실제 검색 기준선](docs/evaluation/2026-11-20-eval01-live-retrieval-baseline.md) | 사용자·AI — 공개 질문 10개 검색/중복/요약·발췌 실제 결과와 사람 라벨 미완료 범위 |
| [04 품질 평가](docs/04-evaluation.md) | 연구/개발자 — 검색 정확도 검증 |
| [05 보안·배포](docs/05-deployment.md) | 운영자 — HTTPS·네트워크·복구 |
| [06 연동 및 계약](docs/06-provider-policy.md) | 사업/개발자 — 비용·권한·MCP |
| [07 테스트](docs/07-test-plan.md) | QA — 검증 기준 |
| [MVP 잔여 구현 설계·계획 진입점](docs/mvp-implementation/INDEX.md) | 모든 AI/개발자 — P0-1~P0-5 의존관계, 선행 차단·설계서/계획서 1:1 목록 |
| [P0-1 WIPS 검색·서지 자동저장 — 설계서](docs/mvp-implementation/P0-1-design.md) | 구현 AI — 기술 구성·API/DB 계약·위험·권한·오류 대응 |
| [P0-1 WIPS 검색·서지 자동저장 — 실행 계획](docs/mvp-implementation/P0-1-plan.md) | 구현 AI/운영자 — 선행 점검·단계별 코드·시험·배포·인수 |
| [P0-2 공식 특허 공보 PDF 확보 — 설계서](docs/mvp-implementation/P0-2-design.md) | 구현 AI — 기술 구성·API/DB 계약·위험·권한·오류 대응 |
| [P0-2 공식 특허 공보 PDF 확보 — 실행 계획](docs/mvp-implementation/P0-2-plan.md) | 구현 AI/운영자 — 선행 점검·단계별 코드·시험·배포·인수 |
| [P0-3 WIPS 본문·벡터 증분 적재 — 설계서](docs/mvp-implementation/P0-3-design.md) | 구현 AI — 기술 구성·API/DB 계약·위험·권한·오류 대응 |
| [P0-3 WIPS 본문·벡터 증분 적재 — 실행 계획](docs/mvp-implementation/P0-3-plan.md) | 구현 AI/운영자 — 선행 점검·단계별 코드·시험·배포·인수 |
| [P0-4 전체 원문·공보 PDF 열람 — 설계서](docs/mvp-implementation/P0-4-design.md) | 구현 AI — 기술 구성·API/DB 계약·위험·권한·오류 대응 |
| [P0-4 전체 원문·공보 PDF 열람 — 실행 계획](docs/mvp-implementation/P0-4-plan.md) | 구현 AI/운영자 — 선행 점검·단계별 코드·시험·배포·인수 |
| [P0-5 실사용 종단간 인수·복구 — 설계서](docs/mvp-implementation/P0-5-design.md) | 구현 AI — 기술 구성·API/DB 계약·위험·권한·오류 대응 |
| [P0-5 실사용 종단간 인수·복구 — 실행 계획](docs/mvp-implementation/P0-5-plan.md) | 구현 AI/운영자 — 선행 점검·단계별 코드·시험·배포·인수 |
| [평가·의사결정 통합 인덱스](docs/evaluation/INDEX.md) | 모든 사용자·AI — MVP 실증 후 두 가지 검증 작업, 실행·인수 순서 및 판단 기준 탐색 |
| [44 MVP 가치·MCP/API/NAS 판단 기준](docs/44-mvp-evaluation-decision-criteria.md) | 사용자·개발자 — 근거 신뢰·추가 후보·반복 사용 효용·안전·GO/NO-GO 규칙 |
| [45 EVAL-01 검색·근거 품질 비교 계획](docs/45-search-quality-comparison-plan.md) | 개발자·AI — WIPS 단독/NAS 단독/통합, 10문항·사람 라벨·동일 K·평가 기준·실행 절차 |
| [46 EVAL-02 저장 자료 재사용 가치 계획](docs/46-reuse-value-verification-plan.md) | 개발자·AI — cold/warm, 실제 호출·추정 절감 분리, 비용/시간·품질 저하·신선도 통제 |
| [43 MVP 진행·잔여 기능 구분 및 MCP/API 선택](docs/43-mvp-milestone-mcp-api-tradeoff.md) | 사용자·AI/개발자 — 1차 핵심 기능 실증 범위, 정식 인수/자동화 미완료, MCP·API·공보 PDF 권고 및 품질 평가 기준 |
| [42 P0-1 ChatGPT WIPS→NAS Code Mode 연동 운영 인수](docs/42-mvp41-code-mode-gateway-archive.md) | ChatGPT/다른 AI/운영자 — 기존 WIPS 인증 재사용, 고정 Gateway 입력, 첫100건 저장, 83건 재사용, 17/17 테스트 및 잔여 제한 |
| [41 WIPS MyFolder MCP 별도 기능·연결/자동저장 판단](docs/41-wips-myfolder-mcp-assessment.md) | 사용자/개발자/AI — 읽기 전용 폴더/SKEY 조회, 기존 WIPS와 차이, 현재 플러그인 상태 및 NAS 적용 범위 |
| [40 WIPS MCP 제공 데이터·28개 도구·구현 현황](docs/40-wips-mcp-capability-catalog.md) | 사용자/개발자/AI — 28개 검색·명세서·권리 도구, 응답 구조, 공보 PDF/벡터 구분, 구현·미완료 목록 |
| [39 검색당 100건 운영 실자료 저장 검증](docs/39-mvp-archive-100-live-acceptance.md) | 사용자/운영자 — WIPS 83건 운영 저장, 중복0, 백업 복원 및 자동 호출 연결 잔여 |
| [38 운영 목록 스키마 적용 및 복구 검증](docs/38-mvp-archive-production-migration.md) | 운영자 — 실제 migration·권한·백업 복원·회귀, 자동 연결 잔여 |
| [37 검색 목록 자동 보관 기반](docs/37-mvp-search-list-archive.md) | 개발자/운영자 — 별도 목록 schema, wrapper, 승인 경계, 실제 연계 및 DB 시험 상태 |
| [36 검색 연동 자동 보관 및 원문 조회](docs/36-mvp-automatic-archive.md) | 사용자/개발자 — 검색 결과 자동 저장, 원문 보존, 공식 PDF 수집 API 후보, 권리·중복·조회 인수 조건 |
| [35 MVP-03/05 실제 단건 운영 인수](docs/35-mvp03-actual-ingest-acceptance.md) | 운영자/연구자 — 실제 신규 적재·중복 방지·ChatGPT 원문 근거 조회 및 제한 |
| [34 MVP-03 승인 NAS 로컬 실행 경로](docs/34-mvp03-local-transport.md) | 운영자 — 단건 stdin launcher, 코드·대상 pin, 교차 컨테이너 잠금 및 최종 적용 절차 |
| [33 MVP-03 승인 적재 CLI 직렬화](docs/33-mvp03-writer-serialization.md) | 개발자/운영자 — 공용 inode 잠금, 경합 차단 및 격리 DB 회귀 |
| [32 MVP-03 실제 DB 엔진 격리 적재 시험](docs/32-mvp03-isolated-backend-test.md) | 개발자/운영자 — 합성 자료 CLI, LocalBackend, 실제 E5·pgvector, 중복·부분복구 시험 |
| [29 사용자 설명서](docs/29-mvp06-user-guide.md) | 사용자 — ChatGPT 시작, 검색 프롬프트, 결과 해석 및 장애 대응 |
| [30 관리자 설명서](docs/30-mvp06-operator-guide.md) | 운영자 — 권한, 점검, 장애·백업·복구 및 승인된 적재 |
| [31 MVP-06 실제 사용 및 평가](docs/31-mvp06-user-trial.md) | 사용자/개발자 — 실제 연구 질의 시험 및 사용자 평가 기준 |
| [28 MVP-05 격리 rollback·인수 시험](docs/28-mvp05-rollback-acceptance.md) | 운영자/연구자 — 현재→이전→현재 실제 HTTP 시험 및 5개 인수 시나리오 |
| [27 MVP-05 실제 특허 DB 백업·복원](docs/27-mvp05-private-backup-restore.md) | 운영자 — 실제 격리 복원·ACL·벡터·무결성 및 남은 인수 조건 |
| [26 MVP-03 승인된 적재 어댑터](docs/26-mvp03-approved-ingest-adapter.md) | 개발자/운영자 — 단건 승인 패킷, 로컬 worker 연결, 테스트 및 쓰기 gate |
| [25 MVP-04 기본 통합·근거 비교](docs/25-mvp04-candidate-comparison.md) | 개발자/연구자 — 문헌 키 중복 제거, 근거 판정, 실제 양 소스 E2E 및 제한 |
| [24 MVP-01 통합 MCP 운영 전환](docs/24-mvp01-production-cutover.md) | 운영자/사용자 — API만 재시작, 56개 검증, Refresh 절차 및 새 ChatGPT 실제 특허 읽기 E2E 결과 |
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
