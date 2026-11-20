# P0-1 실행 계획서 — WIPS 검색+서지 자동 저장

- 목표: [설계서](P0-1-design.md) 기준으로 **첫 페이지 최대100건의 검색·저장 단일 실행 경로**를 배포·실측한다.
- 현재: 기존 [83건 실적재](../39-mvp-archive-100-live-acceptance.md)·중복0·독립 복원 PASS. **임의 WIPS MCP 호출 상시 연결/단일 도구는 없음**.
- 권리: 사용자가 **서지 목록 검색당 최대100건 NAS 보관** 허용. 문헌 본문·PDF·벡터는 이 단계 범위 밖.

## 실행 순서 (의존성 순, 한 단계씩 운영 적용)

| 순서 | 구현·파일 | 선행 확인 / 작업 | 실제 성공 증거 |
|---|---|---|---|
| 1. 서비스 경계 결정 | [기존 wrapper](../../poc/mvp37_search_archive.mjs) | 현재 ChatGPT WIPS MCP를 백엔드에서 재호출할 수 있는 endpoint/인증/계약이 있는지 **읽기 전용** 확인. 없으면 ChatGPT orchestrator A 명시 | 선택 A/B 결정과 불가 사유 기록 |
| 2. 도구 계약 구현 | `poc/mvp41_search_archive_tool.*` **신규 제안** | `{query,limit<=100}`, outitem=7 필드 고정, 반환 건수/total 분리, 실패 분류. A는 실제 ChatGPT 순차 호출 가이드+전용 좁은 save tool, B는 공급자 권한 확인 시 backend provider 호출 추가 | 계약 테스트·보호 필드 미포함 |
| 3. 저장 경계 연결 | `poc/mvp41_save_bridge.*` **신규 제안** | 승인 정책·role/host의 기존 `mvp37_local_transport.py` 경로 재사용. MCP에서 OS 명령 임의 실행 안 함. caller read token과 writer 분리 | auth denied, 100/101 cap, data projection, worker cleanup |
| 4. 운영 적용 | 기존 통합 특허 MCP API 또는 **별도 제한된 entrypoint** | diff, 백업, 최신 실제 DB role/PK 확인 → 해당 기능만 배포. 새 reader 재시작 승인 여부 사전 확인; 허가 없으면 독립 entrypoint 채택 | health/readiness, 기존 5개 MCP 도구 회귀, 기존 컨테이너 불변 |
| 5. 실제 검색 검증 | 검색 의도 1회, 재실행 | 첫 응답 row_list 실제 적재, 실패/재사용, 51~100 순위 및 내부 ACL 체크 | `saved/reused/failed` 합계·DB 건수·실제 반환 확인 |
| 6. 종료·기록 | TASKS/CURRENT_STATE/WORKS, 사용자 가이드 | 실제 시험 결과와 명시적 A/B 적용 범위 정리, 개인정보 출력 금지 | 새 채팅에서 같은 단일 요청 재현 PASS |

## 사전 체크리스트

- [ ] 최신 [AGENTS](../../AGENTS.md) → [TASKS](../../TASKS.md) → 이 설계서 → 최신 운영 문서 확인
- [ ] 이미 승인된 WIPS **서지정보** 외 새 데이터 저장/외부 전달 없음
- [ ] provider 호출 권한/인증이 A 또는 B와 맞는지 확인; WIPS 도구를 NAS가 무조건 호출 가능하다고 가정 금지
- [ ] 운용 DB `patent_archive` 4개 테이블/100 CHECK/role 상태 및 백업 복원 시점 확인
- [ ] NAS secret·정확한 image pin/worker-code·auth directory/real wheel root 확인(공개 저장소에는 경로·값 기록 안 함)
- [ ] 본문·벡터·PDF와 연결하지 않는 변경인지 diff 확인

## 검증 케이스 및 예상 처리

| ID | 조건 | 기대 결과 |
|---|---|---|
| S01 | WIPS 첫 페이지 1~100행 정상 | 검색 PASS, 저장 PASS, `returned_count<=100` |
| S02 | 같은 응답 재전송 | `REUSED_VERIFIED`, `saved=0`, 페이지/문헌 row fingerprint 동일 |
| S03 | 101건 입력, 비정상 XN_D/종류, SK​​EY 충돌 | fail closed, DB 트랜잭션 신규 쓰기0 |
| S04 | WIPS가 `success:false` 또는 timeout | `SEARCH_FAILED`, NAS writer 미실행 |
| S05 | WIPS 정상, NAS 인증 차단 | 검색 결과 표시 + `BLOCKED_POLICY`; 저장 성공 표시 금지 |
| S06 | DB 연결 실패/commit 상태 미확인 | `FAILED_OR_UNCONFIRMED`, 재실행 전 DB 내용 검사 |
| S07 | 서지 중복/기존 본문 카탈로그 다름 | 고유 문헌으로 보관/충돌 표시, 패밀리 합치지 않음 |
| S08 | 실제 ChatGPT 별도 새 대화 | 통합 경로에서는 자동 저장, 직접 독립 WIPS 호출은 자동 보장 없음 |
| S09 | NAS reader/tool 이전 기능 | search_patents/get_patent/search_documents/get_document/save_document 허용 범위 회귀 PASS |
| S10 | 백업·복원·유실 입력 | 새 검색 결과 및 ACL 복원 일치, 임시 worker/packet 정리 |

## 장애 대응/중단 기준

- 신규 writer bridge에서 **첫 권한 우회/100 초과/기존 DB 변조/민감 로그 출력** 확인 → 새 entrypoint disable, writer 정책 접근 차단. 기존 데이터 삭제·타 서비스 재시작 없이 원인 파악.
- 공급자 WIPS backend 직접 접근 미지원 → B 대안 중단, 이미 실증된 A 경로를 공식 사용 가이드로 유지하고 지원 범위 명시.
- 운영 조회 성공+저장 실패 → 검색 사용자에게 상태 표기, 동일 검색으로 blind 재호출 비용 발생시키지 않음; 저장 결과 ID를 통해 복구.
- 스크립트 계약, OS/DB Docker 경계 불일치 → 실제 명령 결과/버전 확인 후 핫픽스, 문서·코드 pin 동시 갱신.

## 작업 종료 산출물 및 인수

- 코드: 실제 구동 가능한 좁은 통합 entrypoint, 배포/설정/rollback, 계약·회귀 테스트.
- 운영: 권한/로그/백업 및 실패 시 차단 증거, 첫 적재/중복0, 기존 원문 불변.
- 문서: 연결 방식 A/B 결정, 테스트 PASS/NOT RUN, 남은 직접 WIPS 호출 후킹 지원 여부.
- 사용자: 다음 대화에서 "이 통합 도구로 검색해 NAS 목록 저장" 한 번 요청하면 실조회·저장·건수가 함께 표시돼야 한다. **독립 WIPS 도구 자동 후킹은 별도 기능임을 고지**.

## 외부 서비스 분리 사전 체크 (2026-11-20)
- [ ] 기존 WIPS 검색 MCP(`wipsclip`), 별도 WIPS MyFolder MCP, NAS RAG의 호출권한/툴을 **서로 다른 서비스**로 식별한다. [조사](../41-wips-myfolder-mcp-assessment.md)
- [ ] 별도 MyFolder가 설치되더라도 `myfolder_get_folder_skeys`가 **서버의 새 검색 결과를 NAS DB에 쓰는 도구가 아님**을 확인한다.
- [ ] P0-1은 MyFolder 없는 상태에서도 구현 가능해야 한다. MyFolder 도구 연결·별도 인증은 사용자 결정에 따른 P1 선택 범위로 유지한다.

## MVP41 A안 실운영 검증 반영 (2026-11-20)
[실제 코드·NAS 실행 결과](../42-mvp41-code-mode-gateway-archive.md): WIPS 검색→Code Mode→Gateway owner stdin wrapper→archive 재사용 인수 PASS. 계약 Node17/17, WIPS 83건/100한도, NAS 저장 2회 REUSED_VERIFIED(각 신규0, 재사용83), 운영 DB/기존 원문 불변 확인. 새 문헌 INSERT는 이 경로에서 NOT RUN(기존 archive83 최초 INSERT는 과거 PASS). **남은 체크:** 새로운 채팅에서 동일 워크플로 선택/실증, 독립 WIPS 호출 자동 hook을 지원할지 결정; 서버측 B안은 외부 WIPS 자격증명/호출권 확인 후 개별 구현. P0-2 등 다음 기능을 위해 기존 NAS 권한·재시작 범위 확대 금지.
