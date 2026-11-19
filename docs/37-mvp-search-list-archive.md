# MVP P0-1 — WIPS 검색 목록 자동 보관 기반
2026-11-20 | 1순위 착수 | 코드 작성, JS 9/9 및 실제 WIPS 읽기 연계 확인. DB 통합 시험·운영 적용 미완료.

## 구현 범위
- [검색 wrapper](../poc/mvp37_search_archive.mjs): 명시 설정한 adapter에서 WIPS 성공 응답의 실제 반환 페이지를 자동으로 보관 callback에 전달하고 승인 보류/실패/verified 저장을 구분한다. 외부 검색 정책 선확인. 전체 검색 건수를 자동 페이지 순회하지 않으며 1회 최대 50행. 기존 WIPS 플러그인 자체의 호출을 감시하는 기능이나 실제 새 ChatGPT writer 연결은 아니다.
- [목록 저장 모듈](../poc/mvp37_archive.py) / [PostgreSQL 스키마](../poc/mvp37_archive.sql): 독립 patent_archive 스키마. 문헌 identity와 공급자 SKEY unique, metadata revision SHA-256, 검색 페이지 hash 및 실제 반환 순위의 relation. 본문/청구항/원시 전체 응답·원시 질의는 저장하지 않는다. 질의 hash는 비밀 보호를 보장하지 않으므로 NAS 비공개 데이터로 유지.
- [로컬 CLI](../poc/mvp37_archive_cli.py): 신뢰 운영자의 고정 0600 정책 파일에 명시 승인된 정확한 배치 digest 및 행 상한이 있어야 한다. 승인 생성 기능 없음. 별도 writer secret/DB role 사용. 현 단계에서는 배치별 승인 방식만 존재하며 권리 확인 후 운영자가 설정하는 지속 승인 정책은 아직 구현하지 않았다. 모델에 writer credential/임의 SQL/SSH 권한을 주지 않는다.
- 목록 저장과 원문 보유 상태를 구분(complete/partial/missing). 기존 reader view의 국가·문헌번호·종류코드로 대조하며 해당 기존 view에는 SKEY가 없으므로 기존 원문 SKEY까지 대조했다고 간주하지 않는다. 신규 목록 내부는 두 키 충돌 검사. complete는 상세설명/전체청구항의 evidence 존재 표시일 뿐, 원본 PDF나 전체 본문 무결성 보증은 아니다.
- 한 트랜잭션 범위 목록/페이지/순위 및 metadata 검증, append-only, advisory transaction lock. 중복 재실행과 변경된 서지정보 revision을 분리. 본문/벡터 쓰기 0. 기존 특허 reader와 ACL 미변경.

```mermaid
flowchart TD
 A[WIPS 검색 wrapper] --> B[실제 반환 페이지]
 B --> C{운영자 보관 정책 허용}
 C -->|아니오| X[목록 표시 / 저장 보류]
 C -->|예| D[목록 전용 writer / 한 트랜잭션]
 D --> E[(검색 목록 / 메타데이터 이력)]
 F[(기존 특허 원문 DB)] --> G[원문 보유 상태 읽기 대조]
 E --> H[저장 건수와 재사용 표시]
 G --> H
```

## 이번 검증
| 검증 | 상태 |
|---|---|
| JS wrapper의 실제 반환 페이지 전달, 정책 거부, 제공자 오류, 본문 제외, 저장 건수 검증, 재사용, 원문 상태 합계, 상한 등 | PASS 9/9 — [테스트](../poc/mvp37_search_archive.test.mjs), 격리 V8 평가; native Node 실행은 하지 않음 |
| 실제 WIPS MCP, 기존 승인 문헌의 메타데이터만 1건 조회 | PASS, 검색 결과 1/1 및 callback 입력 1행; 7개 지정 서지 필드, 저장 정책 BLOCKED_POLICY (실제 DB 쓰기 0; 의도적으로 저장 모듈 대신 보류 응답 연결) |
| [격리 PostgreSQL 통합 시험](../poc/test_mvp37_archive.py), [실행 스크립트](../poc/mvp37_archive_test.sh) | NOT RUN/UNCONFIRMED. 첫 job job_01M7TG7KGX008VA3RM34AJW4JJ EXECUTOR_LOST(출력 및 exit 없음). 재실행 job_01M7TGC6ES00C6VCYKXC64EF28 queued 지속, 취소 확인 |
| NAS read-only preflight | job_01M7TGB1KH003YM4BPGQW5MQC0 succeeded: 원문 문헌 6 / 섹션 10 / 청크 417, 신규 스키마 0, 시험 컨테이너 0 |
| 운영 스키마/role/권한 생성, 실제 저장, 전체 자동 연동 | NOT RUN |

실제 구매 자료의 식별자/텍스트·질의·개별 digest·credential을 공개 repo에 기록하지 않았다. 이번 변경은 원격 테스트 시도와 실제 WIPS 읽기만; NAS 운영 DB 쓰기/배포/재시작 없음. 독립 AI 리뷰 NOT RUN(owner-approved optional).

## 재개 순서
1. Gateway 실행 복구 후 격리 DB 통합 시험 10개 및 CLI 최초/반복 적재 검증, 운영 원문 행 fingerprint 및 기존 컨테이너 상태 불변 확인. 시험 DB는 운영 view 컬럼 계약을 모사한 합성 자료만 사용. 실제 운영 view와 권한의 호환성 및 실제 승인 자료 검증은 별도.
2. 적용 전 전용 schema/NOLOGIN role migration, 기존 private DB의 CONNECT 권한(기존 PUBLIC 제한 유지)과 별도 운영 인증 provisioning 검토. 기존 백업/복원 스크립트는 신규 schema/role을 포함할 때 복원 호환 검증 필요. 운영 백업·보안·재시작 제한 유지.
3. [중앙 #34](https://github.com/son1004007/ai-agent-workflow-playbook/issues/34) 실제 목록의 지속 저장 권리 및 한도 확인. 지속 승인 정책/보관 transport/ChatGPT 자동 wrapper 연결은 미구현. 사용자가 검색만 수행하면 허용 범위의 목록만 일반 흐름에서 자동 보관되는 E2E가 완료 기준. 기존 단건 승인을 무제한으로 확대하지 않는다.
4. 실제 허가된 소량 목록에서 저장·재사용·원문 보유 상태·권한·보류/실패 반환 검증 후 1순위 완료. 이후 원문 수집 및 벡터 적재/공식 PDF/원문 조회 단계 진행.
