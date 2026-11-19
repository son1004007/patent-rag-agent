# 온라인 백업 및 순차 기동 준비 — 2026-11-19

## 판정
PASS: 실행 중인 합성 특허 DB의 최신 4건 온라인 백업, 별도 빈 클러스터 복원, 데이터 fingerprint·ACL·HNSW 인덱스·P4 384D 검증. 기존 컨테이너 시작 시각 불변. 순차 기동 스크립트 점검 모드 PASS. **사용자 최신 지시: 실제 재기동 보류. NAS/기존 컨테이너 재기동 및 자동 시작 등록/실행 금지, 별도 사용자 승인까지 유지.**

## 코드 및 실행 증거
- [온라인 백업/복원](../poc/online_backup_restore.sh), [순차 기동](../poc/stage_start_order.sh), 최종 코드 commit `c4e0cc632ba0bedc23abc8991c54876f4075bc60`.
- Gateway job `job_01M7S4H5RM0067QRYYSPDVCYEN` succeeded: ONLINE_BACKUP_PASS, FRESH_CLUSTER_RESTORE_FINGERPRINT_ACL_INDEX_PASS, EXISTING_SERVICES_NOT_RESTARTED. 최신 dump 11,623 bytes, SHA256 `77e8fb30264987e398ea8f0e550c551f4d48520aa6c2a76173927464dd2c48f7`, NAS 전용 backup 디렉터리 내 0600 파일(공개 repo에 dump/장비 경로/비밀 미기록). 덤프 전후 원본 fingerprint, 전체 4건 및 복원 fingerprint 일치. 기존 pgvector 이미지의 완전히 새로운 network-none 임시 PostgreSQL 클러스터에서 NOLOGIN 제한 역할을 재생성해 데이터베이스 ACL 및 SELECT/INSERT 허용, UPDATE/DELETE/PUBLIC connect 차단, HNSW 인덱스, P4 384차원 확인. 임시 복원 컨테이너만 시험 종료 후 정리.
- 기존 모든 실행 컨테이너 ID와 StartedAt 동일 확인. 기존 서비스 stop/restart 없음, 기술사 원본 저장소/볼륨/DB/secret 미마운트 및 변경 없음.
- Gateway job `job_01M7S4HQPR002EE0X9S7G0VFW5`: 순차 기동 스크립트 sh 구문 PASS. `job_01M7S4JY9500VYTSP4JH7K5X6A`: --check 모드 NO_MUTATION_STARTUP_PLAN_PASS, DB/API/relay/tunnel running 및 network/port 경계 확인. ChatGPT NAS RAG get_document(DEMO-P4) 실제 found=true, 정상.
- 기동 순서: DB/ready → API/HTTP → relay/Unix socket → tunnel/추후 polling 및 ChatGPT 실제 호출 확인. --check 기본 모드 read-only; --start-stopped는 사용자 별도 승인 이후에만 사용. stale socket 발견 시 중단 및 수동 점검(강제 삭제 없음). 실제 순차 기동 및 NAS/container/daemon 재기동, 스케줄러/DSM 자동 시작 등록·검증 NOT RUN. 기존 시작 정책 유지.

## 한계 및 다음
백업은 합성 특허 DB 논리 덤프이며 로그인 암호·플러그인/터널 설정·전체 NAS 장애 복구 및 별도 장치 백업을 포함하지 않음. 백업 자동 스케줄 및 보존 정책 미구성. 운영 기술사 공용 DB 및 WIPS 권리 제한 유지. 재기동 금지 상태에서는 비파괴 작업(공용 DB 설계/격리 시험 및 synthetic 연계 검증)만 진행. 실제 재기동/자동 시작 설정은 사용자 명시 승인 시 재개.
