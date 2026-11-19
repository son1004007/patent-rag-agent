# 기존 NAS RAG 개인 플러그인 확인 및 통합 MCP 후보 검증 — 2026-11-19

## 판정
**기존 개인 연결 정상, 실제 특허 기능 통합 후보 39/39 PASS. 운영 전환 HOLD.** 사용자가 이미 연결했다고 기억한 NAS RAG와 WIPS 개인 플러그인을 재확인했다. 기존 플러그인 중복 등록 불필요.

## 실제 연결
- 개인 플러그인 목록: NAS RAG, wipsclip 모두 USER/PRIVATE. 실제 식별자/터널 ID/키는 공개 repository 미기록.
- 현재 연결의 NAS RAG 도구는 save_document/get_document/search_documents 3개. 실제 search_documents 호출은 scope=synthetic_candidates_only, DEMO-P4 Top1. search_patents/get_patent는 현재 연결에 제공되지 않는다.
- NAS preflight Gateway job `job_01M7S7N2PA0037PAV55FM25E6V` succeeded: DB/API/relay/tunnel running, 외부 publish 0, 실제 특허 3건/10청크.

## 통합 후보 검증
- [통합 서비스](../poc/unified_mcp_candidate.py), [기존 기능 회귀](../poc/unified_mcp_legacy_test.py), [실제 특허 기능 회귀](../poc/unified_mcp_reader_test.py).
- 최초 시험 `job_01M7S7SPQ1009QS68FK3CEFKHP` failed: legacy 16/16, reader unknown_document 실패. get_patent가 synthetic DB conn을 참조한 오류. 별도 작업 생성 전 서버 식별자 입력 오류도 정확한 장비 매핑으로 수정.
- 수정 commit `e6f37d363590519dada8011e86989b4eddf5ebe9`: synthetic_conn 3개 호출, reader_conn 2개 호출; 실제 특허는 전용 reader role/view만 사용.
- 수정 시험 `job_01M7S7YAQ3006AAZKHCRNWCG18` terminal succeeded: CORRECTED_PINNED_SOURCE_PASS, SOCKET_MCP_PASS checks=16, PRIVATE_READER_MCP_PASS checks=23, SEARCH_LATENCY_MS 86.54, UNIFIED_CANDIDATE_AND_EXISTING_START_TIMES_PASS. 기존 합성 4건 및 실제 특허 3건 유지, 일회성 컨테이너 정리, 기존 StartedAt 동일. 검색 지연은 단일 NAS 로컬 HTTP 시험이며 ChatGPT 통신이나 서비스 SLA 아님.
- 실제 서비스에 이 버전을 배포하거나 도구 목록을 갱신하지 않았다. 기존 플러그인/터널 재등록 없이, 별도 승인 후 기존 MCP endpoint의 통합 cutover와 tool refresh/review를 계획한다. 기존 서버/컨테이너 재기동 HOLD. 개인 실제 문헌의 ChatGPT 반환 권리 및 기업 배포는 별도 범위. 기업 네트워크 설계는 [기업용 연결 가이드](21-enterprise-connectivity-firewall-ssh.md).
