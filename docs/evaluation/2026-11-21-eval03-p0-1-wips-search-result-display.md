# EVAL-03 후속 P0-1 — WIPS 특허 검색 결과 4필드 반환 (2026-11-21)

- 범위: 이전 대화에서 지정된 **화면 출력 P0-1** (기존 P0-1 WIPS 서지 NAS 자동저장 작업과 구분).
- [라우터](../../poc/eval03_patent_router.mjs) / [계약 테스트](../../poc/eval03_patent_router.test.mjs)
- WIPS fallback top3 결과는 `publicationNumber,country,documentKind,title,abstract,representativeClaim,rank,truncated` 표시 전용 projection으로 반환한다. SKEY/공급자 원본/추가 비밀 필드와 NAS 비공개 ID/원문은 외부 출력하지 않는다. 요약·청구항이 미제공이면 null, 길이 제한 제목240/요약1500/대표청구항1500 코드포인트와 truncation 상태.
- HTML/script/style 제거, 잘못된 필드/타입/식별자 거부, error/freshness/NAS 근거 검증 fail-closed. **AI 근거 기반 분기 규칙 유지**, 사용자 제안 95% 임계값 미적용.
- 검증: Code Mode V8 격리 계약 기존 정책16+NAS 어댑터29+라우터14+신규 표시11=**70/70 PASS**. 별도 Node CI 실행하지 않았음.
- **실제 공급자 데이터 계약 검사**: WIPS 공개 연구 주제 Boolean 검색 1회(top3) 결과에서 `SKEY,XN_D,CC,KC_D,TIK,ABK,CLK` 값·문자열 형식 확인. 실제 특허번호/SKEY/제목·요약/청구항은 공개 GitHub에 기록 안 함.
- **수정 라우터 실제 E2E 재검증 PASS**: 기존 연결 NAS RAG + WIPS MCP를 최신 코드의 동일 함수에 실제 주입하여 Q01 NAS search2/detail3, WIPS0, `SERVED_FROM_NAS_RAG`; Q06 NAS search2/detail3, WIPS1, `SERVED_FROM_WIPS_MCP`, 반환 후보3건 모두 특허번호·명칭·요약·대표청구항 문자열과 절단 상태 확인. 결과에 SKEY 키·공급자 원시 응답·NAS 비공개 근거 없음. 평가용 공개 연구 질의만 사용; 개별 문헌 원문·식별자는 공개 문서에 보존하지 않음.
- **운영 상태 구분**: 실제 도구 E2E는 ChatGPT **명시적 Code Mode 실행**이며 새로운 상시 MCP 등록/운영 NAS 서비스 설치/DB·원문·벡터·인증·PDF·WIPS MyFolder 변경 없음.
- 남은 기능: NAS 성공 분기의 문헌 상세 출력과 사용자 선택 문헌 상세설명/전체 청구항 WIPS 후속 조회는 화면 P0-2/P0-3. WIPS 후보는 검색 결과이고 최종 권리·기술 적합성 검증 아님.


## 2026-11-21 후속 화면 P0-2

P0-1에서 반환된 `country/publicationNumber/documentKind`를 사용해 [선택 문헌 상세설명 및 전체 청구항 페이지 조회](2026-11-21-eval03-p0-2-selected-wips-detail.md)를 구현하고 실제 WIPS 읽기 검증했다. WIPS 별도 SKEY 노출/저장 없이 문헌번호 기준 선택 가능하다. 상시 MCP 서버 설치는 별개 미완료.
