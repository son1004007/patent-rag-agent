# 합성 전용 MCP 영속 시범 서비스 — 2026-11-19

## 구성
- [MCP 서버](../poc/stage_service.py), [실제 HTTP 검사](../poc/stage_http_test.py), [NAS 배포기](../poc/stage_deploy.sh), 코드 커밋 `05c5145960e72721b49d7ba4d8e940c6cdd28455`.
- 이전에 검증한 pgvector/PG16 및 Python 이미지, E5-small FP32 ONNX 모델과 SDK cache 재사용. 별도 새 named volume, 특허 합성 DB 및 최소 SELECT/INSERT role. 기존 기술사 DB/백업/volume 미마운트. 모델/cache는 읽기 전용.
- DB network none; API는 해당 컨테이너의 isolated network namespace 공유, loopback에만 바인딩. 호스트 port publish 및 외부 tunnel 연결 없음.
- 신규 local bearer와 DB 암호는 NAS에서 생성, 비공개 파일에 저장, 읽기 전용 mount. 값 GitHub/응답 출력 금지. SDK 기본 Host 보호 유지; 추가 guard: Host/Origin, bearer, 중복 singleton header, 길이 및 수신 시간, POST만 허용. 각 문헌 ID와 내용의 exact fixture allowlist. 외부 사용 인증/OAuth 아님. 자유 입력 저장 불가.
- 배포 계약: 기존 자원 충돌 시 중지; 실패 시 이번 단계 컨테이너만 정지하고 별도 stage artifacts는 점검용 보존. 자동 재기동 정책은 적용하지 않으며 NAS/daemon 재부팅 이후 시작 순서는 DB→API. 기존 DSM 네트워크/프록시 설정 변경 없음.

## 실행 중간 증거
- Preflight job `job_01M7S1WNDQ00EK5F3DFCDAS0V4` succeeded, Docker 24.0.2, pinned 이미지·stage 신규 경계 확인.
- Deploy job `job_01M7S21KDW00C1P28YKEYCR1ZE`: SOURCE_SYNTAX_AND_LOCAL_SECRET_SETUP_PASS, DB_PROVISION_PASS, 실제 소켓 HTTP 16/16 PASS, BACKUP_RESTORE_FINGERPRINT_PASS까지 관측. 초기 인증/Host/Origin/oversize/initialize/tools/list, 저장3, 중복·미승인 차단, get, foreign ID 차단, 실제 의미검색, 빈 질의 거부.
- 동일 클러스터 내 별도 복구 DB에 pg_dump custom archive 복원 및 row fingerprint 일치. 운영 전체 복구나 별도 빈 클러스터의 role/ACL 복원 보장은 아님.
- DB/API 순차 재시작 및 서비스 최종 상태 확인 대기. 실제 외부 ChatGPT 연결, 사용자별 OAuth, WIPS 자료 저장, 공용 운영 DB 전환, 대규모 검색 품질/부하 및 CVE 검토 NOT RUN.

## 다음
실측 최종 확인 후 상태 기록. [앞선 통합 시험](11-mcp-vector-integration.md), [터널 준비 조건](10-shared-vector-smoke.md) 참조. 개인 tunnel ID 및 제한 runtime key는 중앙 USER ACTION #24에서 관리한다. 고정 bearer는 local staging 전용이며 외부 노출 전에 정식 인증 설계를 검증한다. 공식 [MCP SDK deploy](https://py.sdk.modelcontextprotocol.io/run/deploy/), [Docker restart](https://docs.docker.com/engine/containers/start-containers-automatically/), [PG16 pg_dump](https://www.postgresql.org/docs/16/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/16/app-pgrestore.html) 참조.
