# P0-5 실행 계획서 — 통합 인수·회귀·복구

- [설계서](P0-5-design.md), [전체 작업 목차](INDEX.md). 착수 조건: P0-1~P0-4 실제 구현 결과(또는 권리/기술상 불가로 명시된 기능별 제한)를 확인.
- 기존 부분 인수는 실제 PASS이나 **전체 PDF/전체 원문/상시 자동 저장 통합 인수는 NOT RUN**.

## 단계별 실행

| 순서 | 작업 | 산출물 |
|---|---|---|
| 1. 인수 범위 고정 | 최신 [AGENTS](../../AGENTS.md), [CURRENT_STATE](../../CURRENT_STATE.md), 각 P0 설계/계획·실제 버전 확인 | 인수 대상 기능·플러그인/사용자권한/환경/지원 제외 경계 |
| 2. 운영 사전 상태 | 검색 API, archive 83건, body 6건/10섹션/417청크, PDF 현황을 당시 DB로 재실측. 백업·컨테이너 시작시각·ACL | Baseline + 사전 backup |
| 3. 실제 정상 검색 | 1~100 서지 + NAS 검색 + 후보 중복/근거 표시, 저장 숫자 일치 | E2E group A/B/C/F |
| 4. 본문·PDF 상태별 검증 | 없는 텍스트, 승인된 텍스트, PDF 실제 확보/미보유 비교 | group D/E와 NONE/HOLD 명시 |
| 5. 실패·보안·중복 | WIPS 실패, NAS 다운, writer 거부, stale cursor, 잘못된 kind, 무효 PDF, 재실행 | group G 및 rollback 계획 |
| 6. 독립 백업·복원 | DB dump + PDF object/manifest, reader ACL, chunk vector/search | group H, 데이터·role·file integrity |
| 7. 사용자 평가 | 최소 실연구 질문으로 실제 문서·PDF 직접 읽기 및 후보 비교 | group I, #31 사용자 피드백 |
| 8. 상태 확정 | 각 feature PASS/FAIL/HOLD/NOT_RUN, 남은 blocker와 코드 pointer, UI 안내 업데이트 | WORKS/TASKS/CURRENT_STATE 및 DOC_INDEX |

## 운영 테스트 표준 시나리오 (실행 전 예상)

| ID | 상황 | 기대 출력 |
|---|---|---|
| E01 | 일반 검색·서지 저장 | `total` vs `returned<=100`, insert/reuse 정확 |
| E02 | 동일 검색 반복 | 새 서지/본문/벡터/파일 추가 0 |
| E03 | 원문 허용 문헌 | 섹션/청구항 및 384D 실제 벡터, 근거 추적 |
| E04 | 원문 미허용 문헌 | `HOLD_RIGHTS`, metadata만 유지 |
| E05 | 실제 공식 PDF 확보 | PDF number/kind/source SHA·열람 성공(없으면 종단간 미완료 명시) |
| E06 | PDF 부재·손상/인증 실패 | PDF 없음/거부만 표시, 텍스트 기반 검색 유지 |
| E07 | WIPS 실패 | NAS 단독 결과와 provider 실패 구분 |
| E08 | NAS 실패 | 저장 성공 주장 금지, WIPS 결과는 별도 표시 |
| E09 | 검색 후보 중복 | 국가+번호+kind 단위 merge, 출처는 모두 보존 |
| E10 | 근거 부족/무관 후보 | HOLD/EXCLUDE, 허위 물성·정량 성능 주장 없음 |
| E11 | 전용 writer/reader 외 계정 접근 | AUTH_DENIED, 타 DB/토큰 사용 실패 |
| E12 | 중단/복원 | 재실행 멱등, 전체 DB + 실제 파일 SHA/role/384D 회복 |
| E13 | 다른 ChatGPT 대화 | WIPS+NAS 단일 연동 도구 확인, 독립 WIPS 호출은 별도 지원 범위 |
| E14 | 사용자 직접 문헌 읽기 | 서지·전체 텍스트·PDF 구분, 관련성/근거/이해도 피드백 |

## 출시/복구 게이트

**출시 전:** 앱 diff·라이브러리 공식 버전/보안/라이선스 검토, 새 code hash pin, 필요한 credential/저장권리, 운영 backup/독립 restore 시점, 기존 서비스 StartedAt, DB ACL/파일 volume quota 확인.

**운영 배포:** 한 기능 단위 변경 → 건강상태/사용자 실제 E2E → 차단·중복/회귀 → 다음 기능. 사용자 승인 경계 밖 NAS/DB/relay/tunnel 재시작 금지. 실패 시 *새 entrypoint* disable 및 사전 백업 기반 복구 가능성 확인; 타 서비스를 포함하는 무차별 rollback 금지.

**데이터 일관성:** 새 PDF object/manifest가 있는 경우 단일 pg_dump만으로 완전 복구되지 않음. 원문 section/chunk hash, 384D index/query, archive 4개 테이블/ACL, PDF 경로·SHA를 **별도 복원**에서 모두 비교.

**최종 인수:** 실제 테스트 결과의 count/status/비용·성능 범위, 사용자 #31 피드백, 남은 제외/제약, GitHub commit과 운영 버전 일치. 외부 리뷰 선택은 `NOT_RUN_OPTIONAL`로만 기록.

## 실패 원인 선별 순서

1. **권한/계약 gate** → 2. 공급자 WIPS/공보 공식 API status → 3. JSON/XML schema·문헌 identity → 4. NAS 원문/벡터 상태 → 5. 읽기 인증·PDF 파일 → 6. UI/ChatGPT 응답 품질.
2. 데이터 누출·권한 위반·무제한 다운로드·원본 변조 시 즉시 신규 기능 차단; 부분 검색결과 유지하더라도 성공으로 표시하지 않는다.
3. 한 단계라도 FAIL/NOT_RUN이면 전체 인수 PASS 아님; 해결 작업을 우선순위로 TASKS에 이관하고 재현 조건/재시도 한도를 남긴다.

## 사용자 최종 확인 질문 (실사용 시)

"검색 결과가 실제 연구 목적에 적합한가? 출처/근거·문헌번호를 확인할 수 있는가? 전체 원문과 공보 PDF를 문제없이 구분하여 열람할 수 있는가? 개선 필요한 기능은 무엇인가?" 사용자 본인 답변을 #31에 반영한 뒤 MVP-06 직접 평가 완료 처리.
