# 작업 진행 기록

실제 완료 상태는 [CURRENT_STATE.md](CURRENT_STATE.md), 다음 작업은 [TASKS.md](TASKS.md), 전체 문서는 [DOC_INDEX.md](DOC_INDEX.md) 참조. 이곳은 진행 과정/검증 근거의 시간순 기록이다.

## 2026-11-19

| 단계 | 결과 및 증거 |
|---|---|
| 설계/화면 시안 | [아키텍처](docs/02-architecture.md), NAS 정적 가상 UI 및 사설 HTTPS 접속 검증 |
| ChatGPT 중심으로 전환 | README 도식 갱신, 기존 독립 웹 Agent는 대체안 유지 |
| 합성 MCP 계약 | [실측](docs/09-mcp-contract-smoke.md), save/get/문자열 검색 및 중복/충돌 거부 PASS |
| 공동 pgvector 격리 | [실측](docs/10-shared-vector-smoke.md), 같은 시험 PG 클러스터 내 도메인별 DB/role 분리 및 18/18 SQL 체크 PASS |
| MCP와 실제 E5/pgvector 통합 | 코드 [Python](poc/mcp_vector_smoke.py), [실행기](poc/mcp_vector_smoke.sh), 커밋 `bf2c368b6dbd75ccc017609f99bac361b130291c`; 24/24 PASS — [실측 및 한계](docs/11-mcp-vector-integration.md); NAS 임시 DB와 실제 E5 통합, 사후 건수/정리 PASS. |
| 합성 전용 영속 MCP 시범 서비스 | [서비스](poc/stage_service.py) / [HTTP 시험](poc/stage_http_test.py) / [배포기](poc/stage_deploy.sh), commit `05c5145960e72721b49d7ba4d8e940c6cdd28455`; NAS 코드 구문·전용 DB 구성 PASS, 실제 HTTP·재기동/복원 검증 실행 중. |

실제 운영 데이터나 WIPS 원문 저장은 하지 않는다. 기존 기술사 개발 볼륨과 시안 서비스 유지. 작업별 실행 증거를 확인한 뒤 결과를 갱신한다. 개인 터널 및 실제 ChatGPT 도구 호출은 별도 검증이 필요하다.
