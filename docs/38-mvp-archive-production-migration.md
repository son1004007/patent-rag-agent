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
