# EVAL-03 — ChatGPT 내 NAS RAG 선조회·WIPS MCP 보완 검색 (실제 실행)

- 날짜: 2026-11-20
- 상태: **CODE_MODE_ON_DEMAND_TWO_BRANCH_LIVE_PASS**, **SERVER_SIDE_ALWAYS_ON_ROUTER_NOT_INSTALLED**
- [구현](../../poc/eval03_patent_router.mjs) / [14 합성 계약 테스트](../../poc/eval03_patent_router.test.mjs) / [기존 NAS 근거 게이트](../../poc/eval02_live_read_adapter.mjs)
- 공개 보호: 사용자·고객 실제 질의 전체, WIPS SKEY·번호·명세서·청구항, NAS 내부 문헌 ID·SHA, 네트워크·계정·인증정보를 이 보고서에 기록하지 않는다.

## 1. 연결 구조

ChatGPT Code Mode에서 **이미 연결된** `NAS_RAG.search_patents` + `NAS_RAG.get_patent`, `wipsclip.get_patent_search_onlyengine`을 JS dependency injection으로 단일 함수에 조합한다. 개인 NAS 서비스/API 재배포, WIPS 키 이동, 새 MCP 플러그인 등록/Refresh, Gateway 쓰기·원문/PDF·벡터 증분 수집 없음.

1. 사용자 질문 → NAS 반복 read2·상위3 상세 읽기 → 기존 EVAL02 정책으로 근거 출처/서지 동일성 검사 → **ChatGPT가 리뷰 콜백으로 직접 관련성(2점) 및 실발췌 인용 검토**.
2. `AI_REVIEWED_REUSABLE`인 경우 NAS 결과 경로 선택, **WIPS 호출0**.
3. `INSUFFICIENT_DIRECT_EVIDENCE`인 경우 사용자의 주제에서 **별도 작성한 공개 WINTELIPS 검색식만** WIPS MCP에 전달; NAS 발췌·제목·식별자·사내 프롬프트를 WIPS 쿼리에 재사용하지 않는다. WIPS 기본 반환 필드 top3, 후보 관련성은 별도 판정 대상.
4. NAS 오류/불안정·인용 불일치·review 미제공·freshness 요청은 `HOLD_LOCAL_NOT_VERIFIED`로 중단: NAS 오류를 '미보유'로 오해하지 않음. WIPS 장애/형식 오류 시 `WIPS_READ_FAILED`.
5. 반환은 선택 출처·판정·호출수·후보 건수와 한계만. 특허 ID/SKEY/원문은 함수 반환에 포함하지 않음.

**중요한 의미 차이:** NAS `search_patents`는 cosine nearest-neighbor 상위3 검색이지 **전체 특허 보유 목록 조회**가 아니다. 이 구현의 분기는 '현재 NAS 상위3 후보에서 **직접 관련 기술 근거가 충분함/불충분함**' 기준이다. '해당 공보 번호가 DB에 확실히 없음'이라고 판정하는 기능은 아직 아니다. 정확한 출원/공보번호 보유 판별을 위해서는 접근제한된 별도 read-only existence lookup 또는 저장 문헌 키 전체와의 안전한 매칭이 필요하다.

## 2. 실제 연결 E2E

| 경로 | 입력 종류 | NAS search/get | WIPS MCP | 실제 라우터 반환 |
|---|---|---|---|---|
| 기존 보유 연구 주제 (Q01) | 태양광 봉지재 밀봉 | 2/3 | **0** | `NAS_RAG / SERVED_FROM_NAS_RAG`; 실제 인용 근거 일치, rank1 |
| NAS 저장범위 밖 (Q06) | 배터리 난연 전해질 | 2/3 | **1** | `WIPS_MCP / SERVED_FROM_WIPS_MCP`; 결과 top3 반환, NAS 직접관련 자료 보류 |

실제 WIPS 검색 성공은 응답 top3 목록의 형식과 비어 있지 않음을 검증한 것으로, 모든 문헌의 기술적 적합성/권리·원문 완전성 확인을 뜻하지 않음.

## 3. 계약 검증

- **기존 NAS 정책 테스트16 + 근거 게이트29 + 신규 라우터14 = 59/59 PASS**. 실행 환경은 **GitHub 최신 소스 본문을 가져온 ChatGPT Code Mode V8 격리 평가기**. Node CI 실행이라 주장하지 않음.
- 신규 라우터14개: 보유 시 WIPS0, 미보유 근거시 WIPS1, NAS 빈결과 WIPS1, NAS 순위변화 및 provider 장애 fail-closed, 근거 리뷰 callback 부재 HOLD, 최신성 HOLD, WIPS 장애/불량 payload HOLD, 빈 결과, 민감정보 반환 금지, 가짜 인용 차단, bad query 거부, NAS 비공개 질문이 WIPS에 전달되지 않는 분리.
- 실연동은 **ChatGPT Code Mode에서 요청시** 실제 연결된 두 도구를 순차 조합한 결과이다. 서버사이드 MCP 단일 도구/자동 플러그인 등록·다른 대화/임의 질문에서의 자동 보장은 **NOT_IMPLEMENTED**.
- 읽기 전용. NAS 데이터 저장·원문/벡터 재수집/백업·계약/비용·도면/PDF 처리·서비스 재기동·권한 변경 없음.

## 4. 사용 및 후속 작업

이 채팅 또는 다른 ChatGPT 세션에서 필요하면 저장소 최신 `poc/eval02_reuse_policy.mjs` + `poc/eval02_live_read_adapter.mjs` + `poc/eval03_patent_router.mjs`을 읽어 Code Mode에서 주입할 수 있다. 모델이 **자체 근거 검토**하고 공개/허가된 검색 목적을 위한 별도 WIPS Boolean 검색식을 준비할 때만 WIPS로 분기한다.

- **다음 P0:** 정확한 문헌번호 보유 판정 방식 정의(현 NAS reader는 publication exact lookup 불가), 출처·언어·신선도 판정 강화.
- **선택:** 항상 작동하는 단일 서비스 MCP 도구(`lookup_patent`) 등록을 원하면 NAS의 공식 서버측 WIPS 인증·사용 범위·재시작/복구 기준을 먼저 별도 검증. 이미 ChatGPT가 가진 WIPS 인증을 NAS 서버에 자동 위임할 수 있다고 가정하지 않는다.
- 이번 시점의 상태는 `MCP_ON_DEMAND_CONNECTED`이며 `GLOBAL_AUTO_FALLBACK_NOT_INSTALLED`이다.

## 5. 사용자 요청 재검증 — 2026-11-20 (기존 코드 그대로)

- 사용자가 95% 유사도 기준 **변경하지 말고 현재 AI 근거 분기를 확인**하도록 요청. `eval03_patent_router.mjs` 또는 운영 설정 **수정 안 함**.
- 최신 GitHub 원본 소스의 Code Mode V8 합성/계약 테스트: **16/16 + 29/29 + 14/14 = 59/59 PASS**. Node CI가 아닌 격리 V8 실행임을 명시.
- 실제 MCP 도구 재연결 Q01: NAS search2+get3, 자체 인용 근거 검토와 3개 필수 특성 검증, `AI_REVIEWED_REUSABLE` → **NAS 반환, WIPS0 PASS**.
- 실제 MCP 도구 재연결 Q06: NAS search2+get3, 상위 문헌은 태양광 봉지재로 배터리 전해질 질의에 직접 부합하지 않음 → `INSUFFICIENT_DIRECT_EVIDENCE` → **WIPS 검색1, 3건 반환 확인 PASS**.
- 읽기/무결성 실패·허위 인용·freshness·WIPS 오류는 synthetic 계약 테스트에서 HOLD/실패 확인, **이번 재검증에서 실제 서비스 장애를 주입하지 않음**.
- **정확성 한계:** 관련성 판단은 ChatGPT가 실측 제목/요약/청구항을 확인해 콜백으로 제공한 AI 자체 판정이며 별도의 독립 gold-label 아님. 문헌번호 exact existence 검색 미구현. NAS retrieval 상위3 근거 부족을 전체 NAS 미보유로 해석하면 안 됨.
- **API 결과 한계:** `runPatentRouter` 반환은 출처·판정·호출수 및 WIPS 결과 건수 **메타데이터만 포함**. WIPS에서 조회한 특허 원문/후보 객체는 라우터 반환값에서 전달되지 않으므로 ChatGPT가 원결과를 별도 보유해 출력하지 않는 한 단일 함수만으로 결과 목록/내용을 사용자에게 보여주는 기능은 아직 완결되지 않음.
- **운영 범위:** 기존 두 MCP를 현재 ChatGPT Code Mode에서 명시적 호출할 때만 동작. 글로벌 자동 도구 등록/서버측 상시 실행 NOT RUN. 모든 NAS DB/컨테이너/원문/벡터·권한·WIPS 설정 및 95% 임계값 변경 없음.
