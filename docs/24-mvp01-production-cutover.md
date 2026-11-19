# MVP-01 — 통합 MCP 운영 전환 및 개인 플러그인 갱신 (2026-11-19)

## 판정
**운영 MCP 배포 PASS, 56/56 회귀 테스트 통과. 개인 ChatGPT 신규 도구 갱신 및 실제 호출 대기.**
사용자가 2026-11-19 기존 MCP 서비스만 재시작하여 배포하도록 명시 승인하였다. NAS 전체, DB, relay, tunnel, 다른 컨테이너의 재시작 및 자동 기동 변경 금지는 유지한다. 이번에는 기존 API 컨테이너만 재시작했다.

## 실측 근거
- 기존 컨테이너 설정 확인 및 실제 데이터 5건/401청크. Preflight Gateway jobs `job_01M7SBKC0600FJDJCS3XS5MXSQ`, `job_01M7SBMYGD0009BJ6H3594JSMH` 성공. 기존 secrets 디렉터리는 API만 마운트. 개인 플러그인 USER/PRIVATE 범위 유지.
- [운영 코드](../poc/unified_mcp_production.py) commit `87ccadf46b1c9476da04c1970505001d610cb4a4`; 검증된 통합 후보의 포트(기존 8765) 및 기존 읽기 전용 마운트 경로만 맞춤. 실제 자료는 전용 reader role과 bounded evidence view로 조회, 기존 합성 저장은 정확한 fixture만 허용. writer credential, WIPS API key, DB admin credential, 외부 포트, 터널 설정 변경 없음.
- [기존 기능 회귀](../poc/unified_legacy_prod_test.py), [실제 특허 회귀](../poc/unified_reader_prod_test.py), [기존 Unix relay 경유 회귀](../poc/unified_tunnel_prod_test.py), 테스트 commit `2bcdcb590982813227394312dbc4a4498d40d73c` 기준.
- 실제 NAS deploy Gateway job `job_01M7SBT42R009C663F98PZTHMJ` terminal succeeded: PRODUCTION_AND_PREVIOUS_PINNED_SOURCE_PASS, RESTART_ONLY_PATENT_MCP_API, SOCKET_MCP_PASS checks=16, PRIVATE_READER_MCP_PASS checks=24, LOCAL_UNIX_MCP_PASS checks=16, UNIFIED_PRODUCTION_CUTOVER_PASS_OTHER_CONTAINERS_AND_DB_UNCHANGED.
- 로컬 실제 특허 검색 109.78ms(단일 테스트 질의, 모델 로딩 및 ChatGPT 왕복 제외). 실제 3개 distinct 문헌/근거 300자 상한, get_patent, 원본 및 신규 section_sources 직접 조회 거부, 쓰기/교차 DB 차단, 인증/Host/Origin 검증. 총 56개 체크(일부 중복 검증).
- 기존 API 컨테이너 ID와 HostConfig fingerprint 유지, API StartedAt 변경, 다른 실행 중인 모든 컨테이너의 StartedAt/Running 불변. DB 5건/401청크/8섹션 및 합성 4건 fingerprint 동일. 운영 포트 publish 0 유지. 실패 시 기존 원본 코드 복구 및 API만 재시작하는 rollback trap 준비했으나 성공하여 실행하지 않았다. 이전 코드 백업은 NAS API 코드 디렉터리에 별도 보존(경로/비밀 공개 저장소 미기록). 실제 rollback 복구 시험은 NOT RUN.
- 배포 후 기존 ChatGPT NAS RAG search_documents 실제 호출 정상(P4/P3/P1, synthetic scope). 이 대화에서 발견 가능한 도구는 여전히 기존 3개. 신규 2개의 ChatGPT 직접 호출은 아직 미검증.

## 사용자 수행 — 기존 개인 플러그인 도구 갱신
공식 [Connect and test your plugin — Refresh metadata](https://developers.openai.com/plugins/deploy/connect-chatgpt), [custom MCP server](https://developers.openai.com/api/docs/guides/custom-mcp-server) 확인(2026-11-19). 기존 플러그인/터널을 삭제하거나 재등록하지 않는다.

1. 웹 ChatGPT [Plugins](https://chatgpt.com/plugins) 열기.
2. 설치된 **NAS RAG** 선택 → 해당 연결의 상세/관리(Settings/Manage tools) 화면 열기.
3. **Refresh(새로 고침)**을 선택하고 갱신된 도구 목록에서 변경을 검토·저장(화면에서 요구하는 경우).
4. 기존 save_document/get_document/search_documents와 새로운 **search_patents/get_patent** 총 5개 확인. 둘은 실제 구매 특허 읽기 전용이며 기존 save_document는 가상 fixture 전용이다. 새 도구를 사용 가능하게 설정.
5. 새 대화에서 @NAS RAG 선택, "NAS RAG의 search_patents 도구로 태양광 모듈 봉지재의 내습성과 광투과율 관련 저장 특허 3건을 검색해줘. WIPS와 웹 검색은 하지 마." 실행. get_patent 실제 호출까지 검증하고 GitHub 상태 갱신.
6. Refresh가 안 보이면 설치된 플러그인의 연결 관리/설정 화면에서 확인. UI 차이로 찾기 어려우면 화면 공유/캡처 확인, 중복 신규 등록 금지. 이번에 사용자의 설정 화면을 직접 조작하지 않았으며 현재 커넥터에서 refresh 호출 기능이 발견되지 않음.

## 다음 범위
MVP-01 신규 도구 ChatGPT end-to-end(갱신 후); MVP-03 자동 적재 adapter는 별도(이번 배포는 실제 특허 읽기 전용); MVP-04 근거 기반 결과 통합; MVP-05 실제 dump 독립 복원/인수 및 rollback 확인; MVP-06 사용법. 구매 특허 개인 사용 범위 유지, 실제 자료 공개/대량 수집/기업 배포 금지. NAS/DB/다른 서비스 재기동과 자동 시작 등록은 계속 HOLD.

## 사용자 Refresh 수행 후 확인
- 사용자 확인: 권한 추가 부여 및 Refresh 수행. 현재 기존 대화에서 도구 발견 재확인 결과 기존 3개만 노출. 실제 get_document(DEMO-P4) found=true, 개인 플러그인 USER/PRIVATE 유지. 서버 재배포/권한 설정 변경 없음.
- OpenAI [공식 Refresh metadata 절차](https://developers.openai.com/plugins/deploy/connect-chatgpt)에 따라 신규 대화에서 @NAS RAG 선택 후 신규 search_patents 및 get_patent 호출 진행 필요. 사용자 설정에서의 새 도구 목록은 직접 확인하지 못했으며 Refresh 실패로 단정하지 않음. MVP-01 운영 배포 PASS 유지, 새로운 대화 직접 E2E 대기.
