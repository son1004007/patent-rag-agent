# MVP-03 — 승인된 NAS 로컬 적재 실행 경로
2026-11-19 | 개인 MVP | 실제 NAS 격리 transport PASS. 구매 자료의 운영 사용 승인과 최종 사용자 인수 대기.

## 구현 및 보안 경계

```mermaid
flowchart LR
  O[운영자가 승인한 단건 packet] --> S[로컬 stdin launcher]
  S --> P[코드 hash / 파일 소유권 / 이미지·DB ID 검증]
  P --> C[새 일회성 worker 컨테이너]
  C --> L[동일 inode writer lock]
  L --> V[기존 승인 adapter 및 E5 / pgvector]
  V --> R[검증 집계만 반환]
```

- [로컬 전달 스크립트](../poc/mvp03_local_transport.py)는 신뢰된 NAS 호스트의 운영자 전용 CLI이며 실제 서버 API나 MCP 쓰기 도구가 아니다. 입력은 900000-byte 상한의 stdin만; 임의 shell 명령, NAS 경로, Docker 대상은 packet으로 받지 않는다.
- 기존 3개 Python worker 파일의 Git blob SHA-1 pin, Docker 이미지 ID pin, 운영자가 지정한 전체 DB 컨테이너 ID 및 실행/격리 상태 확인. private root/code/auth/locks 소유권·0700 및 파일 0600 확인, 심볼릭 링크 및 파일 다중 hardlink 거부. 동일 로컬 inode 잠금 디렉터리를 공유한다.
- worker는 기존 DB namespace 연결, 외부 포트 없음, nonroot/read-only root/cap-drop/no-new-privileges, 3 GiB 메모리·CPU shares 제한, 임시 /tmp, --pull never, --log-driver none, 오프라인 wheel 설치, 코드·모델·wheel·개별 승인/암호 파일·잠금 디렉터리 read-only mount. 운영 secret 디렉터리 전체, 호스트 root, Docker socket, DB 볼륨 미마운트. 승인 검증 및 권한 보장 자체는 기존 어댑터에서 수행한다.
- 구조화된 DRY_RUN/PASS/REUSED_VERIFIED 및 실패 상태의 허용 필드만 반환. 모호한 실행 실패는 FAILED_OR_PARTIAL로 보고하며 원문/식별자/secret/worker stderr를 출력하지 않는다. 자동 반복 호출 또는 데이터 수정은 하지 않는다.
- Docker 실행 권한을 가진 운영자는 신뢰 주체다. 본 CLI는 권한 제한을 우회하는 사용자/모델에게 Docker 권한을 주지 않는다. 자산 및 실행 파일은 신뢰된 로컬 운영자가 관리하며 운영 중 교체 금지. JS submitApprovedPacket의 실제 WIPS→NAS 연결과 실제 운영 배치는 아직 하지 않았다.

## 실제 NAS 검증
[시험 스크립트](../poc/mvp03_local_transport_test.sh), Gateway job `job_01M7SKB3HB00WGBY0VN5CBCCNK` succeeded exit=0. 기존 운영 DB schema-only 복제(실제 rows/secret 없음), 별도 임시 SCRAM 계정/합성 fixture 승인, 같은 기존 이미지와 모델/오프라인 wheels 사용. Python compile 및 shell syntax 검사 PASS.

| 검사 | 결과 |
|---|---|
| 서로 다른 두 컨테이너의 공용 inode 잠금 경합 | PASS |
| 실제 로컬 transport --check 쓰기 0 | PASS |
| 실제 로컬 transport --apply 신규 적재 | PASS |
| DB 독립 집계 1건/2섹션/5청크/384D | PASS |
| 별도 worker 재실행 REUSED_VERIFIED, 쓰기 0 | PASS |
| worker 소스 변경 pin 차단 및 건수 불변 | PASS |
| 운영 DB 전체 row fingerprint 및 모든 기존 실행 컨테이너 상태 | 전후 동일 |
| 시험용 컨테이너 정리 | PASS |

SCHEMA_ONLY_RESTORE_PASS, CROSS_CONTAINER_LOCK_PASS, LOCAL_TRANSPORT_CHECK_PASS, LOCAL_TRANSPORT_INSERT_PASS, LOCAL_TRANSPORT_DB_COUNTS_PASS, LOCAL_TRANSPORT_REUSE_PASS, LOCAL_TRANSPORT_CODE_PIN_DENIAL_PASS, SOURCE_FINGERPRINT_UNCHANGED, PATENT_CONTAINERS_UNCHANGED, ALL_EXISTING_CONTAINERS_UNCHANGED, LOCAL_TRANSPORT_CLEANUP_PASS. 운영 DB 쓰기·WIPS 신규 구매/호출·서버 재시작/권한 변경 없음. 외부 독립 AI 검토 NOT RUN(owner-approved optional).

## 실제 운영 시 재개 절차 (승인 전 실행 금지)

1. [중앙 사용자 조치 #30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30)의 구매/개인 NAS 저장 및 로컬 임베딩 권리 범위를 확인하고, 승인된 단건의 정확한 로컬 packet과 소유자가 관리하는 승인 파일을 작성한다. 실제 자료·해시·secret은 GitHub/공개 Issue에 적지 않는다. 구매/외부 전송 권리 확인을 별도로 유지한다.
2. 운영자는 이전 worker 사용 경로 배제/직렬화, 기존 백업, private root와 절대 canonical model/wheel 경로 및 실제 운영 DB 전체 ID pin을 확인한다. `PATENT_INGEST_ROOT` 아래 code(고정 3파일), auth(승인 파일·기존 writer_password), locks(ingest.lock) 각 0700/0600으로 준비하고 유지한다. 실제 운영 배치·인증 파일 생성은 NOT RUN.
3. 운영자 로컬 환경에서 `PATENT_INGEST_ROOT`, `PATENT_MODEL_ROOT`, `PATENT_WHEEL_ROOT`, `PATENT_DB_CONTAINER_ID`를 승인된 대상으로 설정하고 `python3 mvp03_local_transport.py --check < approved-packet.json` 실행. 검증 후 명시적으로 승인된 `--apply` 실행한다. 실제 구매 자료를 외부 도구/공개 로그로 전달하지 않는다. 별도 운영 변경 및 writer 실행 승인이 필요하다.
4. 실제 운영 DB 및 approved reader 재조회·반복 재사용, 무결성, 기존 서비스 불변 검증을 완료해야 MVP-03/05 완료로 표시한다. 실제 ChatGPT 직접 신규 쓰기 호출을 성공한 것으로 간주하지 않는다. 사용자 실제 검색 평가 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) 별도.
5. 구현 범위와 격리 시험은 준비됨. 신규 문헌 권리 및 사용자 평가 대기 상태에서 추가 가상 시험을 반복하거나 P1/P2/P3로 선행하지 않는다. 사용자 조치 후 위 운영 적용/인수 재개.
