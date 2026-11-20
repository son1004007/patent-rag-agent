# EVAL-03 화면 P0-3 — NAS RAG/WIPS 공통 검색 결과 및 선택 문헌 상세 연결

- 날짜: **2026-11-21**
- 상태: **CHATGPT_CODE_MODE_BOTH_SOURCES_LIVE_E2E_PASS**, **SERVER_SIDE_ALWAYS_ON_TOOL_NOT_INSTALLED**
- [공통 결과 구현](../../poc/eval03_unified_display.mjs) · [18 신규 테스트](../../poc/eval03_unified_display.test.mjs) · [NAS 검증 후 안전 콜백](../../poc/eval02_live_read_adapter.mjs) · [라우터 연결](../../poc/eval03_patent_router.mjs) · [WIPS 전체 텍스트 페이징](../../poc/eval03_wips_detail.mjs)
- **작업 ID 구분:** 이전 대화의 사용자용 **화면 P0-3**을 완료한 것으로, 예전 [P0-3 승인 본문/벡터 자동 증분 적재](../mvp-implementation/P0-3-design.md)는 여전히 미완료이다. 새 원문·공보·벡터 저장 없음.

## 1. 사용자 입력과 출력 계약

호출은 현재 ChatGPT Code Mode에서 이미 인증된 `NAS_RAG.search_patents/get_patent` 및 `wipsclip.get_patent_search_onlyengine/get_patent_spec_text` 의존성을 명시적으로 주입한다. 새 상시 MCP, 백엔드 WIPS 키 복사, 공개 포트, DB 권한 확대 없음.

- `lookupPatentForUser(args)`: 기존 NAS search2 → 상세 최대3 → ChatGPT AI 직접근거/출처 검증 통과 시 NAS 문헌1건, WIPS0. 관련 근거 부족이면 별도 승인된 WINTELIPS 검색식으로 WIPS search1 → 후보 최대3건. NAS 고장/무결성 불일치/AI 인용 불일치는 HOLD/WIPS0.
- 공통 특허 필드: `rank,source,country,publicationNumber,documentKind,title,abstract,representativeClaim,evidence,detailLevel,truncated`. NAS에서 제목·공개 문헌번호·요약/대표청구항의 **최대3개/각300자** 발췌를 반환. WIPS에서는 이미 승인된 표시용 문헌번호·명칭·요약·대표청구항과 제한/절단 상태를 반환.
- **NAS 보안 변경:** 기존 NAS adapter는 기본적으로 ID/원문을 전혀 반환하지 않음. 새 선택적 `onAccepted` 동기 프로세스 콜백은 AI 리뷰의 출처·인용·필수 특성 검증이 통과한 **선택된 문헌1건**만 새 공통 결과기에게 전달. 기본 호출 및 기존 반환은 불변, 콜백 실패는 HOLD. 외부 provider, WIPS 쿼리, 공개 GitHub에는 콜백 근거를 전달하지 않는다. 응답에는 NAS 내부 `document_id,source_sha256,chunk_sha256` 등을 싣지 않는다.
- `getUnifiedPatentDetail({lookup,index,getSpecText,pageSize,descriptionOffset,claimsOffset})`는 **직전 검색 반환 후보의 index만** 선택한다. NAS라면 `EXCERPT_ONLY`와 출처별 근거(전체 원문 가용하지 않음). WIPS라면 P0-2 어댑터로 `dtl_desc/all_claim` 2회 호출, 선택 후보 문헌번호와 공급자 `doc_num`/국가를 대조 후 제한 페이지 반환.
- WIPS 결과 오류/없는 결과, NAS 일관성 오류/AI 인용 불일치, 잘못된 후보 번호/상세 문헌번호 불일치를 HOLD/NO_RESULTS 등으로 구분. **유사도 95% 기준 적용 안 함.**

## 2. 실제 두 소스 종단간 검증

| 실제 사용자 질문 분류 | 호출 | 결과 | 판정 |
|---|---|---|---|
| Q01: NAS에 직접 근거가 있는 태양광 봉지재·끝단 밀봉 | NAS search2 + get3, WIPS 검색0, WIPS 명세0 | 공통 결과 NAS1건, 제목/공개번호/요약/대표청구항/인용3개 확인; 상세 요청 `EXCERPT_ONLY` | **PASS** |
| Q06: NAS에 직접 근거가 없는 배터리 난연 전해질 | NAS search2 + get3, WIPS 검색1, WIPS spec2 | WIPS 공통 후보3건, 선택1번 상세설명 및 청구항 페이지: 정제 상세 **27,923자**, 청구항 **8개** | **PASS** |
| WIPS 선택1번의 다음 페이지 | 추가 WIPS spec2 (첫 상세 이후 누적4) | 페이지당 1,100자, 다음 페이지 시작 offset 1,100, 문자열이 서로 다르고 페이지 연속 | **PASS** |

실제 WIPS 반환에는 추가 후보를 판단하기 위한 공개 자료가 들어가지만 개별 문헌 번호·명칭·요약·청구항 원문 및 SKEY·NAS 해시/ID는 **공개 GitHub 보고서에 싣지 않음**. 검색은 공개 일반 기술 주제로 제한했다.

## 3. 계약/회귀 검증

- 기존 EVAL02 재사용 정책 **16**, 실제 NAS 읽기 어댑터 **29**, WIPS fallback 라우터 **25**, 선택문헌 상세/P0-2 **18**, 신규 공통 조회/P0-3 **18** = **106/106 PASS**.
- 실행 환경: GitHub 최신 코드 읽기 후 **ChatGPT Code Mode V8 격리 실행기**. **Node.js CI NOT RUN**.
- 신규 18 테스트: 두 출처 공통 필드, NAS 근거3개 이하, 내부ID/SHA·WIPS SKEY 비노출, NAS WIPS0, NAS 근거 부족 WIPS1, 후보 상세 일치, 틀린 WIPS 문헌/나라 HOLD, NAS read 장애/HOLD, 조작된 인용 HOLD, 콜백 실패 시 fail-closed, 빈 WIPS 결과, WIPS 예외 보호, freshness 차단, 인덱스 범위, 출처 변조 거부, HTML/script 평문 정제, 승인되지 않은 provider 자료의 자동 출력 방지.
- 실제 운영 서버/장애 주입/고객사 계정·AI 독립 전문가 관련성 판정/PDF·도면 파일 다운로드·반복 대규모 재현성 측정은 **NOT RUN**.

## 4. 남은 사항

1. 이 기능은 **현재 ChatGPT에서 명시적으로 호출되는 코드 합성**이다. 상시 통합 MCP 서비스/모든 신규 채팅 자동 실행이나 별도 웹 UI/선택 버튼이 아니다.
2. NAS는 현재 3건×300자 읽기 권한만 제공하므로 **전체 명세서 상세 제공 불가능**. WIPS에서 별도 조회할 수 있는 후보만 전문 페이지를 보여준다. NAS 원문 권한·보관범위/독립 전용 뷰어 확대는 별도 승인 필요.
3. AI 검색 관련성은 ChatGPT 자체 판정이며 인용 일치가 독립적인 기술 정확도 보증이 아니다. `search_patents` 상위3 근거 부재는 전체 NAS DB에 해당 문헌이 없다는 완전한 존재 판정이 아니다.
4. 사용자 문헌 탐색·표시 성공과 NAS 영구 원문·벡터 적재·공보 PDF/도면·상시 자동 검색/저장을 혼동하지 않는다. 기존 **서지83/원문6/벡터417/PDF0** 불변. 95% 임계값 미적용.
5. 원문 페이지는 해당 페이지를 요청할 때 WIPS 2개 섹션을 **다시 조회**하며, 동일 시점 고정 버전/변경 탐지나 영속 캐시를 구현하지 않았다.

## 5. 실행 방법 (다른 ChatGPT 세션)

먼저 [전역 CONTROL](https://github.com/son1004007/ai-agent-workflow-playbook/blob/main/CONTROL.md)과 [AGENTS](../../AGENTS.md), [DOC_INDEX](../../DOC_INDEX.md), [CURRENT_STATE](../../CURRENT_STATE.md), [TASKS](../../TASKS.md)를 읽는다. `poc/eval02_reuse_policy.mjs`, `poc/eval02_live_read_adapter.mjs`, `poc/eval03_patent_router.mjs`, `poc/eval03_wips_detail.mjs`, `poc/eval03_unified_display.mjs`의 최신 버전과 도구 설명 확인 후 Code Mode 내 임포트 불가 조건에서 정의를 조합해 `lookupPatentForUser`를 호출. `reviewNas`는 반드시 실제 근거를 읽고 ChatGPT가 명시적으로 검토하여 인용/필수 특성 근거를 제시하며, `wipsQuery`는 승인된 공개 기술 검색식으로만 작성한다.

최종 후보 선택 시 해당 반환 객체를 `getUnifiedPatentDetail`로 보내 `index`를 지정한다. NAS는 발췌 제한, WIPS는 2개 spec-text 반환과 페이지 이어 읽기. 결과 본문을 GitHub/별도 로그에 복제하지 않는다.
