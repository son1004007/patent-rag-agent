# MVP P0-1 — 사용자 승인 100건 상한 및 운영 WIPS 실자료 저장 인수
- 날짜: 2026-11-20
- 용도: 개발자/운영자 및 사용자, 실제 NAS 운영 증거
- 상태: 검색 목록 저장 경로 **실제 83건 적재·동일 페이지 0건 재적재·운영 백업/독립 복원 PASS**. 모든 WIPS 원시 MCP 호출의 자동 가로채기는 아직 미구현.

## 범위 및 승인
사용자는 WIPS **서지정보**의 개인 NAS 지속 자동 보관이 허용된다고 명시적으로 확인했고 **검색당 최대 100건**이라고 정정했다. user-confirmed, contract-not-independently-verified. 이전 50건 제안은 폐기. `SKEY, XN_D, CC, KC_D, TIK, APSTH, XD` 7개 메타데이터 필드만 저장; 요약·청구항·상세설명·벡터·PDF·도면의 자동 수집/상업 재배포 허가가 아니다.

```mermaid
flowchart LR
 A[ChatGPT WIPS MCP 실제 검색] --> B[첫 페이지 최대100건 서지 결과]
 B --> C[운영자 로컬 저장 transport]
 C --> D[개인 NAS archive schema]
 D --> E[중복 0 재확인 및 보유 원문 상태]
 E --> F[기존 ChatGPT NAS 읽기 MCP 회귀]
```

## 변경
- [목록/정규화](../poc/mvp37_archive.py): `MAX_ROWS=100`, 첫 페이지 저장 시 page 전달, metadata-only.
- [CLI 정책](../poc/mvp37_archive_cli.py): 운영 소유자만 설정하는 `owner-approved-autosave-100-v1`, `max_rows=100`, `page=1`만 지속 자동 허용. 예전 단건 digest 승인과 별도. 공급자 응답의 총 검색 건수가 100건을 넘어도 첫 100건만 대상으로 하며 자동 다음 페이지를 호출하지 않는다.
- [검색 wrapper](../poc/mvp37_search_archive.mjs): 기본·최대 `page_size=100`, 실패·보류 상태 별도, 본문 제외. 실제 독립 WIPS 플러그인 호출을 hook하는 구현은 아님.
- [운영 제약 migration](../poc/mvp39_archive_100.sql): `search_pages.page_size`, `page_hits.rank` CHECK 상한을 50→100으로 변경, 기존 자료/원문 무변경.
- [운영 전송](../poc/mvp37_local_transport.py): 별도 권한의 owner-only 한 번 실행 코드. Docker image에 `/code`, `/auth` 디렉터리가 없었기 때문에 개별 파일 bind 대신 0700 전용 worker-code/auth 디렉터리를 각각 RO bind. 코드 blob pin 및 디렉터리 정확한 엔트리·소유자·0600 확인. NAS wheel asset symlink 경로는 정규화한 절대 경로를 사용. 노출 서버/외부 포트/기존 서비스 재시작 없음. 원문/청크 write 0.
- writer role은 NOINHERIT/기존 append-only(SELECT+INSERT)·기존 private database CONNECT만 유지하며 신규 SCRAM 로그인만 활성화; credential 및 정책은 개인 NAS 0600 파일, 공개 GitHub에는 저장하지 않는다.

## 실제 운영 검증
| 증거 | 결과 |
|---|---|
| WIPS MCP | 100건 요청·첫 페이지 83건 반환, 83개 SKEY 유일, 일곱 필드 타입·날짜 검증 |
| 운영 schema | 100건 CHECK migration PASS |
| 직접 쓰기 시작 전 백업 | 0600 및 SHA-256 검사 PASS, 세부 백업 경로/해시 비공개 |
| 첫 운영 적재 | `PASS verified=true saved=83 reused=0 returned=83`, archive documents83 / metadata revisions83 / search pages1 / hits83 |
| 실제 50위 초과 저장 | 페이지 순위 51~83 총 33건 확인 PASS |
| 동일 실제 페이지 재사용 | `REUSED_VERIFIED saved=0 reused=83`, 세 번들 행 fingerprint 변화 0 |
| 기존 원문·벡터 | `documents=6, section_sources=10, chunks=417`, 기존 모든 row fingerprint 및 실행 컨테이너 불변 |
| 독립 복원 | 실운영 backup 1,101,659 bytes, archive 전체 row/ACL/view/index, original fingerprint, vector top3/384D 복원 PASS, 임시 컨테이너 정리 및 SHA-256 PASS |
| ChatGPT NAS RAG | 기존 검색 3 / get_patent 3건, ID/source hash 일치 및 근거9 PASS |
| 일회성 비공개 검색 응답 파일 | 성공 후 삭제 완료; 공개 GitHub에 실제 목록/식별자·원문·개별 hash 미기록 |

원격 작업: Gateway 대기 실행은 시작 전 취소(운영 미적용), Synology Remote Desktop Commander 경로로 전환하여 Git blob pin·native Python 컴파일 PASS, 직접 운영 마이그레이션/쓰기 수행. 첫 실행은 코드 및 인증 bind 대상 디렉터리가 이미지에 없고 NAS wheel 경로가 symlink여서 차단되었고 당시 archive rows0 확인. worker-code/auth 디렉터리 RO bind 및 canonical wheel root 수정·실제 재검증 후 성공. 후속 운영 재사용 exit0 및 실제 [기존 백업·복원 도구](../poc/private_backup_restore.sh) exit0. 독립 AI 검토: NOT_RUN_OPTIONAL.

## 남은 P0
이 대화의 승인된 ChatGPT 실행자가 **WIPS MCP 호출 후 NAS 전용 operator transport를 명시적으로 순차 호출**하여 실자료 저장에 성공했다. 하지만 **다른 대화/임의 WIPS MCP 검색 호출을 자동 감지하는 상시 hook·단일 MCP 도구는 없음**. 범용 자동 저장을 위해 제한된 WIPS→NAS orchestration entrypoint를 배포하고 실제 새 대화에서 재검증해야 한다. 기존 NAS reader에 writer 권한을 부여하거나 기존 DB/API/relay/tunnel을 재시작하지 않는다. 원문 자동 저장/PDF는 별도 권리·연동 작업.
