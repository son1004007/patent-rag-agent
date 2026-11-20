# EVAL-03 화면 P0-2 — 선택 문헌 상세설명·전체 청구항 페이지 조회

- 날짜: **2026-11-21**
- 코드: [선택 문헌 읽기 어댑터](../../poc/eval03_wips_detail.mjs), [18개 계약 테스트](../../poc/eval03_wips_detail.test.mjs)
- **범위 구분:** 여기의 '화면 P0-2'는 사용자가 이전 대화에서 지정한 선택한 **WIPS 후보 상세 텍스트 읽기** 작업. 기존 [P0-2 공식 공보 PDF 획득](../mvp-implementation/P0-2-design.md)은 **여전히 미구현**.
- 상태: **CHATGPT_CODE_MODE_SELECTED_DETAIL_LIVE_PASS**, **GLOBAL_MCP_TOOL_NOT_INSTALLED**, **CUSTOMER_ENV_NOT_TESTED**

## 1. 선택 및 연결

1. 기존 `eval03_patent_router.mjs`의 WIPS fallback 결과 `patents[0..2]`에서 사용자가 특정 후보를 선택한다.
2. 선택 결과의 **공개 식별정보** `{country,publicationNumber,documentKind}`만 `getSelectedWipsPatentDetail({selection,getSpecText})`로 전달한다. WIPS 검색 내부 SKEY를 보존·반환·전달하지 않는다.
3. 어댑터는 이미 인증된 WIPS MCP `get_patent_spec_text`를 두 번 호출한다. 첫 호출 `section=dtl_desc`, 둘째 `section=all_claim`; `ctry,mng_num,doc_kind,mng_num_type=M`을 사용한다. 출원번호가 아닌 **문헌번호**이므로 임의로 `mng_num_type=A`로 재검색하지 않는다.
4. 두 결과의 `ctry` 및 `doc_num`이 선택한 특허와 일치하는지 검증한다. 일부 결과만 정상인 경우에도 서로 다른 문헌 내용을 조합하지 않는다.
5. 상세설명은 **텍스트 1페이지 기본 3000, 최대 4000 코드포인트**, 전체 청구항은 `청구항 N` 번호를 보존한 연속 텍스트를 같은 페이지 크기로 분할한다. `offset,totalChars,nextOffset,hasMore,complete` 반환. 사용자는 다음 offset으로 이어서 요청할 수 있다. 각 페이지는 공급자를 다시 조회하며 **캐시/자동 저장 없음**.
6. `language`는 실제 공급자 `lang_cd`, `totalClaims`는 WIPS `cl_list` 원소 수이다. 없음/부분데이터/오류를 구별해 표기한다.

## 2. 실측 (비공개 식별정보·원문 미게시)

| 검사 | 실제 결과 |
|---|---|
| WIPS `get_patent_search_onlyengine` 일반 공개 연구 질의 top1 | **PASS**. 문헌번호/국가/종류를 반환 |
| 같은 문헌번호로 `get_patent_spec_text(dtl_desc)` | **PASS**. `doc_num`/국가 일치, 언어 KR |
| 같은 문헌번호로 `get_patent_spec_text(all_claim)` | **PASS**. 번호 있는 청구항 **8개** |
| 상세설명 표시용 plain text | 정제 후 **27,923 코드포인트**. 1페이지 1,800자 출력, 다음 offset **1,800** |
| 상세설명 후속 페이지 | **PASS**. offset1,800의 두 번째 구간 반환, 첫 페이지와 다른 내용 확인 |
| 민감한 공급자 식별자/내부 원시 JSON | **반환되지 않음** (SKEY, `dtl_desc_list`, `cl_list` 미노출) |
| 전체 계약/회귀 | 기존 정책16 + NAS 어댑터29 + 라우터25 + 신규 상세18 = **88/88 PASS (Code Mode V8 격리 실행)** |
| Node.js CI 및 운영 단일 MCP 설치/고객사 배포 | **NOT RUN** |

실제 WIPS 읽기 호출은 첫 페이지와 두 번째 페이지에서 **상세설명2 + 전체 청구항2 = 4회**. 최초 후보 선정 검색은 별도 1회. 정제 전 본문은 HTML 유사 태그를 포함할 수 있고, 표시 텍스트에서 태그가 제거되므로 **원본 공보의 표/수식/이미지 서식이 그대로 유지되는 뷰어가 아니다.** 원본 PDF 및 도면 파일 획득은 별도 작업.

## 3. 안전·제약

- 새 기능은 **읽기 전용**이며 서버 인증정보, WIPS 내부 SKEY, NAS 구매특허 원문·청크·벡터, 고객자료를 다른 시스템에 저장·전송하지 않는다. 실제 특허번호·명칭·청구항 원문은 공개 GitHub 문서에 기록하지 않는다.
- 문헌번호/국가 불일치, 비정상 필드 타입, 공급자 장애, 범위 초과 offset은 **fail closed**. 외부 반환 텍스트는 HTML/script/style 제거·평문만 전달(원문 바이트와 같다고 주장하지 않음). 가능한 한 입력을 WIPS 공개 문헌번호·종류로 제한한다.
- 기존 `eval03_patent_router.mjs`의 **AI 근거 기반 조건부 분기 불변**, 95% 유사도 임계값 **미적용**. NAS DB·아카이브·임베딩·WIPS 검색 요금/인증·터널·컨테이너 재시작 및 파일 저장 없음.
- ChatGPT **명시적 Code Mode 호출 시에만** 도구 합성이 가능하다. 검색 후 다음 대화에서 선택하려면 앞서 표시된 공개 특허번호/국가/종류를 다시 전달해야 한다. 전역 자동 라우터·단일 MCP 신규 도구·사용자 UI 선택 버튼은 아직 없음.
- 추가 회귀 보완 여지: 다국어·정정 청구항 등 국가별 예외, provider 원문 크기 제한, 고정 버전의 페이지 일관성, 동일 문헌의 다중 언어 페이지 요청. 또한 자체 NAS 성공 분기에서 사용자용 문헌 요약/인용 표시 통합은 **화면 P0-3 잔여**.

## 4. 실제 사용자 흐름

`ChatGPT: 이 기술과 관련된 특허 찾아줘` → 기존 NAS AI 근거 검증 → 관련 근거 부족 시 WIPS 상위 3개 검색 → 문헌번호·제목·요약·대표청구항 표시 → `2번 특허의 상세설명과 전체 청구항 보여줘` → 해당 결과의 공개 문헌번호를 선택해 어댑터 호출 → `nextOffset`으로 나머지 본문/청구항 이어서 조회.

현재 단계는 **사용자 선택을 ChatGPT가 명시적으로 전달하는 방식의 실증**. 다른 대화에서 자동으로 상태를 유지하거나 서버가 선택 이벤트를 받는 UI 완성을 뜻하지 않는다.
