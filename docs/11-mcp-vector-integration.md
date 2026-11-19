# MCP → E5 → pgvector 통합 실측 — 2026-11-19

**24/24 PASS**, Gateway terminal succeeded. 합성 자료에 한정한 NAS 일회성 통합 시험이다.

- 코드: [Python](../poc/mcp_vector_smoke.py) / [실행기](../poc/mcp_vector_smoke.sh), commit `bf2c368b6dbd75ccc017609f99bac361b130291c`.
- Preflight job `job_01M7S17GAV00K37FZJ9G1A1ATB` PASS: 기존 기술사 이미지/모델/cache, dev volume 및 preview 실행 확인.
- 실제 job `job_01M7S1C08J0051J5XXMB8GZKZK` succeeded: ASSET_MANIFEST_PASS, MCP_E5_PGVECTOR_PASS checks=24, DB_POSTCHECK_PASS, CLEANUP_AND_EXISTING_CONTAINERS_PASS.
- 기존 기술사 모델/SDK 캐시를 read-only mount, 파일별 pinned manifest hash/size 검증. E5-small FP32 ONNX, 384D, query/passage prefix 및 L2 normalization; MCP 1.30.0, ORT 1.20.1. 두 일회성 컨테이너의 network-none/shared isolated namespace; 비root, read-only root, 메모리 제한. 실제 기술사 원본 DB/volume/문헌/secret 미마운트.
- 테스트 클러스터 내 patent_demo/study_demo 별도 DB와 제한 role. 합성 문헌 3건을 MCP save로 임베딩하고 실제 pgvector INSERT, get, cosine search를 ASGI로 호출. 정확한 fixture allowlist만 저장 허용. parameter binding, model ID, duplicate 및 conflict, 미승인 입력, invalid limit/blank, cross DB SELECT 및 UPDATE/DELETE 권한 거부 검증.
- 모델 로드 2283ms. 따뜻한 상태 단일 ASGI 검색 (E5+SQL): 구리 대체 도체 73ms, 해양 부식 방지 72ms, 난연 절연 소재 67ms. 3/3 Top1 및 거리 순서 PASS. 3개 synthetic corpus에 대한 기능 smoke이며 실특허 정확도, 임계값/미보유 거부 및 운영 SLA 아님.
- 최종 DB 건수 patent3/study1, 시험 컨테이너0 및 이전 실행 컨테이너 ID 유지. 기존 원본 데이터 fingerprint는 이번 실행에서 측정하지 않음. 영속 DB/운영 공용 DB, 실제 소켓 HTTP/TLS/auth, OAuth, Secure MCP Tunnel, ChatGPT 플러그인 쓰기, WIPS 적재 NOT RUN.
- 다음: 합성 전용 지속 실행 MCP 서비스 후보와 정책/인증 검증, tunnel_id 및 제한 runtime key 확보 후 공식 Secure MCP Tunnel 실제 등록/호출. 기존 기술사 배포 차단/라이선스 제한 유지. 사용자 조치는 중앙 Issue #24 참조.
