# MVP P0-1 — 운영 검색 목록 스키마 적용
2026-11-20 | 운영자/개발자 | 실제 NAS 운영 DB additive migration 및 백업 복원 PASS. 상시 자동 저장 미활성.

## 변경 범위
사용자의 운영 우선 개발 지시를 AGENTS에 반영했다. 기존 격리 시험을 반복하지 않고 실제 운영 DB에서 무중단 migration 후 검증했다. [migration](../poc/mvp37_archive.sql) 적용: 별도 archive 테이블 4개, 원문 보유 상태 view, append-only NOLOGIN 전용 역할과 private DB CONNECT. 실제 인증정보, 상시 승인, 새 MCP/외부 노출 미생성. [백업/복원](../poc/private_backup_restore.sh) 및 [격리 API rollback](../poc/private_rollback_drill.sh)에 신규 archive 4개 테이블 fingerprint 및 ACL/view/index/권한 검증과 NOLOGIN 역할 복원 준비를 추가했다. 별도 비공개 NAS 경로에 코드 5개 배치, Git blob 일치 확인.

```mermaid
flowchart LR
 A[운영 사전 백업] --> B[목록 schema 추가] --> C[권한과 트랜잭션 확인] --> D[실제 백업 복원] --> E[ChatGPT 읽기 회귀]
```

| 검증 | 운영 실측 |
|---|---|
| preflight | 기존 6문헌/10섹션/417청크; archive schema/role/기존 writer 연결 0 |
| 사전 백업 | 1,078,506 bytes, 0600, pg_restore 목록·SHA-256 PASS |
| migration | 실제 COMMIT, 4 tables/1 view, role NOLOGIN·멤버십 0 |
| 권한 | private DB CONNECT 명시, demo 접근 및 기존 원문 schema 직접 접근, archive UPDATE/DELETE 차단 PASS; 기존 공개 CONNECT 제한 유지 |
| 실제 문헌 상태 | 6건 중 상세·전체청구항 evidence 존재 5, 미충족 1; 전체 파일 보존을 보증하지 않음 |
| 트랜잭션 | 시험 fixture INSERT→ROLLBACK; 영속 archive 4개 테이블 0행 |
| 기존 원문/서비스 | 전 행 fingerprint, ACL/index 및 기존 컨테이너 상태 동일 |
| 적용 후 백업 | 1,087,974 bytes, 0600, SHA-256 PASS, network-none 새 DB 복원 fingerprint/ACL/view/index/vector top3 일치; 384D, pgvector 0.8.7; 시험 정리 PASS |
| ChatGPT 실제 NAS MCP | 검색 3건·상세 3/3, ID 및 source hash 일치, 근거9 |
| 최종 배치 | 5/5 Git blob 및 0600 일치, 운영 6/10/417, archive 문헌·페이지 0/0, role LOGIN false |

Gateway jobs: preflight job_01M7TVMKMK00VWM5VBKY9APV20; migration job_01M7TVS89Q000D573C8E42F0Y7; restore job_01M7TVT2QJ002QYK0KFTCPYRV1 exit=0; final pin job_01M7TVW26R00HR7R2D2C03R7XX. 새 API rollback drill은 sh syntax 확인만; 실제 운영 rollback 및 새 drill 실행 NOT RUN. 독립 AI 리뷰 NOT RUN(owner-approved optional). 기존 서비스 재시작 없음, WIPS 추가 조회/구매/영속 목록 쓰기 없음.

## 재개
[#34](https://github.com/son1004007/ai-agent-workflow-playbook/issues/34)의 지속 서지 보관 권리 및 상한 확인 후 승인 정책·전용 writer 인증 및 전송·실제 ChatGPT 검색 자동 연동/중복0 검증. 현재 빈 운영 schema만 적용됐으며 권한 확인 전 role 활성화 금지. 별도 저장 요청 없는 실제 저장 E2E가 완료 기준.

## 후속 운영 적용 — 저장 전송 경로(기본 비활성)
2026-11-20. [운영자 로컬 transport](../poc/mvp37_local_transport.py) 추가 및 운영 NAS 비공개 경로에 배치. 기존 0700 경로 하위 bin/auth 디렉터리, 실행 코드 및 0600 기본 정책 `{"enabled":false}` 생성. 기존 archive 및 CLI의 Git blob pin, 정책 파일 owner/mode/symlink 검사, 실제 허용 batch 식별 및 행 상한 검사. 승인된 경우에만 별도 role credential과 pinned DB/worker image, RO mount, offline 의존성, 무외부네트워크·비특권 일회성 컨테이너를 사용하도록 구현. stderr 및 비승인 응답 노출 금지, 반환 count 검증, timeout 후 확인되지 않은 commit 자동 재시도 금지. 이 프로그램은 신뢰 운영자 전용이며 일반 MCP/HTTP 도구가 아니다.

실제 Gateway job_01M7TZHYV500Y9TRYESX30N170 succeeded: TRANSPORT_DEPLOYED_DEFAULT_DISABLED, TRANSPORT_POLICY_AND_RESULT_VALIDATION_PASS, EXISTING_REAL_METADATA_POLICY_DENIAL_PASS, ALL_EXISTING_DATA_AND_CONTAINERS_UNCHANGED, PRODUCTION_TRANSPORT_FAIL_CLOSED_PASS. 운영 NAS native Python compile 및 blob pin 확인, disabled/잘못된 정책 및 성공 결과 검증. 기존 실제 승인 보유 문헌의 로컬 서지정보만 메모리/pipe에서 packet 형태로 구성하여 운영 transport 실행: BLOCKED_POLICY 및 writes=0. 실제 WIPS 신규 조회/응답 전달이 아닌 로컬 보유 자료 projection이며 실제 서지정보·원문·개별 hash를 Gateway stdout이나 공개 repo에 출력하지 않음. 기존 원문 전체 행 fingerprint 및 기존 컨테이너 불변, archive four tables rows 0, NOLOGIN, writer secret 없음, 새 worker 0 확인. 기존 서비스 재기동 없음.

이번에는 정책 미승인 차단 경로만 운영 실증했다. 새 transport의 허용 worker 분기/실제 쓰기 및 지속 승인 정책은 NOT RUN/미활성. 기존 CLI 허용 분기는 이전 격리 DB 시험에서 PASS했으나 새 transport 허용 분기 검증과 동일하지 않다. [#34](https://github.com/son1004007/ai-agent-workflow-playbook/issues/34) 확인 전 실제 writer 로그인 활성화, 상시 policy 생성 또는 신규 자료 적재 금지. 기본 transport 배치와 직접 ChatGPT WIPS 호출 자동 가로채기/상시 연동을 동일시하지 않는다. 다음 실행은 사용자 권리/호출 및 저장 한도 확인 이후 최소 권한 운영 인증과 정책·연동 및 실제 저장/reuse 검증. 추가 반복 합성 시험을 선행하지 않는다. 독립 AI 검토 NOT_RUN_OPTIONAL.
