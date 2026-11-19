# MCP 계약 1차 실측 (2026-11-19)

공개 가능한 합성 자료 전용 단위 실측. 실제 개인 ChatGPT 플러그인 여부와 별도이다.

- [검증 코드](../poc/mcp_contract_smoke.py), commit `8d637258dd72e9dbe5d06689c13c3f958348a16b`.
- 공식 MCP Python SDK 1.30.0, httpx 0.28.1, Python 3.12.14. NAS 기존 wheel cache read-only 재사용, 일회성 network-none 컨테이너, 비root 실행. 실제 데이터베이스/백업/사용자 자료 미마운트.
- 초기 실패: native library mapping 실패, loopback Host 검증(421), structuredContent 없는 v1 text payload 처리 실패. 임시 컨테이너에 실행 가능한 private tmpfs 설정, 올바른 loopback Host, text/structured payload 호환 처리로 해결. 호스트/기존 컨테이너 설정 변경 없음.
- 최종 Gateway job `job_01M7RVND4Q00AQDP7FQ9KJZVWJ`: succeeded, MCP_CONTRACT_PASS, protocol 2025-11-25.
- 검증: initialize, initialized, tools/list, annotation, save, idempotency, get, substring search, missing, synthetic ID namespace denial, conflict denial.
- NOT RUN: DB 저장, vector similarity, 실제 HTTP socket/TLS, 외부 호출, Tunnel/ChatGPT 개인 plugin 등록, 실제 계정 쓰기, OAuth/도메인 DB role 권한 검증. 합성 namespace 검증은 DB 격리 증거가 아니다.
- 기존 기술사 영속 배포 차단 및 WIPS 저장권 제한 유지.

## 다음
[OpenAI custom MCP](https://developers.openai.com/api/docs/guides/custom-mcp-server), [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels): 개인 Platform 조직, tunnel_id, runtime credential 권한, 연결 정책 실제 확인. 공식 문서와 계정별 지원 차이를 실제 등록/도구 호출로 검증. 모델 API 사용과 Tunnel 인증 키 구별. 실제 데이터 전송/영구 저장은 권한 확보 이후.
