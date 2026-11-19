# 공통 pgvector 엔진 격리 시험 — 2026-11-19

## 범위와 판정

**18/18 PASS** — 동일 PostgreSQL 클러스터에서 특허와 기술사 전용 DB 및 역할을 분리한 합성 SQL 실증. 이전 [MCP 계약 시험](09-mcp-contract-smoke.md)과는 분리된 검사. 운영 DB 공동 사용 또는 MCP→DB 통합 완료가 아니다.

- 검증 코드: [shared_vector_smoke.sh](../poc/shared_vector_smoke.sh), commit `a5db5384f67b318ee119388903782c368007f87b`.
- 기존 기술사 PoC의 고정 pgvector 0.8.7/PG16 이미지 재사용. 새 network-none, --rm 컨테이너; PostgreSQL 사용자, 읽기 전용 root, tmpfs 시험 저장소, memory 512MiB, CPU shares 128. 기존 volume/backup/model/credential 미마운트.
- 별도 DB 2개, 로그인 역할 2개, PUBLIC CONNECT/TEMP 제거, role별 CONNECT/SELECT/INSERT만 부여. loopback SCRAM 인증, 일회성 암호 로컬 생성; 암호 출력 없음.
- 384차원 합성 벡터 3개(특허), 1개(기술사). HNSW 인덱스 생성 및 cosine 거리 질의. 실모델 임베딩/실문헌/ANN 성능 평가 아님.
- 시험 중 PostgreSQL stop/start 후 동일 데이터 건수 확인. 컨테이너 종료 시 tmpfs 데이터 소멸; 영속 volume 또는 백업/복원 운영 보장 아님.

| 영역 | 검사 | 결과 |
|---|---|---|
| 버전/적재/조회 | extension, patent_count, study_count, exact_fetch, vector_dimension | 5/5 |
| 검색 | cosine_order, exact_distance | 2/2 |
| 중복/영역 | duplicate_count, no_study_leak | 2/2 |
| 교차 DB/인증 | cross_patent_to_study, cross_study_to_patent, bad_password | 3/3 |
| 권한/스키마 | no_delete, no_update, no_ddl, invalid_dimension | 4/4 |
| 재기동 | restart_patent_count, restart_study_count | 2/2 |

Gateway job `job_01M7RYJA1S0052FST33AHNNNH2`: succeeded, SHARED_VECTOR_SMOKE_PASS checks=18. 사전 inventory `job_01M7RYFMSP00BS1208Y6GC9HZD` 및 사후 `job_01M7RYMSKG00HSMKE43X3DW83E` succeeded: 기존 dev volume 존재, preview UP, 이번 시험 container 0. 기존 볼륨 미마운트로 내용 변경을 수행하지 않았다(기존 DB fingerprint 재측정은 하지 않음).

## 실제 연결 다음 단계

1. 위 ACL을 적용한 별도 synthetic DB와 제한적 MCP 도구(save/get/search) 통합 시험, 실제 E5-small 임베딩/모델 provenance. MCP 입력/DB parameter binding, 권한·idempotency 검증. 기존 기술사 배포 차단 유지.
2. Secure MCP Tunnel: [OpenAI 공식 가이드](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels), [공식 온보딩](https://github.com/openai/tunnel-client/blob/master/docs/onboarding.md). 개인 Platform org의 [Tunnels](https://platform.openai.com/settings/organization/tunnels)에서 tunnel ID 생성/확인; Tunnels Read+Manage 필요. [Runtime API keys](https://platform.openai.com/settings/organization/api-keys)에서 제한 키(Tunnels Read+Use). 활성 계정 권한/터널 존재 및 연결 미검증. 키는 Gateway의 저장 값 등 비밀 입력 경로로만, 채팅/공개 로그 금지. 현재 connector는 터널 CRUD 및 restricted runtime key 생성 권한을 확인하지 못함. 설치 전 공식 release/OS/architecture 확인. NAS에 인바운드 포트 추가 금지. `tunnel-client doctor`, 건강 상태 및 polling 후 설치.
3. [ChatGPT custom MCP](https://developers.openai.com/api/docs/guides/custom-mcp-server): 웹 Plugins → Add custom MCP server → Tunnel → 선택한 tunnel ID/인증 → 개인 설치 → 실제 도구 호출. 읽기/쓰기 도구 지원 안내 확인; 계정별 permission/confirmation/실행 E2E는 미확정. WIPS 원문/영구 적재 금지 유지.

NOT RUN: MCP→DB E2E, 실임베딩, 기존 기술사 영속 DB 통합, 실제 tunnel/ChatGPT 연결, 운영 부하/백업·복구, WIPS 저장. 사용자 조치와 별개로 합성 통합 시험은 계속 가능.
