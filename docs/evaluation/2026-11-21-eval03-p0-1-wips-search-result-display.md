# EVAL-03 후속 P0-1 — WIPS 특허 검색 결과 4필드 반환 (2026-11-21)

- 범위: 이전 대화에서 지정된 **화면 출력 P0-1** (기존 P0-1 WIPS 서지 NAS 자동저장 작업과 구분).
- [라우터](../../poc/eval03_patent_router.mjs) / [계약 테스트](../../poc/eval03_patent_router.test.mjs)
- WIPS fallback top3 결과는 `publicationNumber,country,documentKind,title,abstract,representativeClaim,rank,truncated` 표시 전용 projection으로 반환한다. SKEY/공급자 원본/추가 비밀 필드와 NAS 비공개 ID/원문은 외부 출력하지 않는다. 요약·청구항이 미제공이면 null, 길이 제한 제목240/요약1500/대표청구항1500 코드포인트와 truncation 상태.
- HTML/script/style 제거, 잘못된 필드/타입/식별자 거부, error/freshness/NAS 근거 검증 fail-closed. **AI 근거 기반 분기 규칙 유지**, 사용자 제안 95% 임계값 미적용.
- 검증: Code Mode V8 격리 계약 기존 정책16+NAS 어댑터29+라우터14+신규 표시11=**70/70 PASS**. 별도 Node CI 실행하지 않았음.
- **실제 공급자 데이터 계약 검사**: WIPS 공개 연구 주제 Boolean 검색 1회(top3) 결과에서 `SKEY,XN_D,CC,KC_D,TIK,ABK,CLK` 값·문자열 형식 확인. 실제 특허번호/SKEY/제목·요약/청구항은 공개 GitHub에 기록 안 함.
- **E2E 및 운영 상태 구분**: 신규 표시 라우터와 실제 두 MCP 동시 E2E는 이후 검증. 새로운 상시 MCP 등록/운영 NAS 서비스 설치/DB·원문·벡터·인증·PDF·WIPS MyFolder 변경 없음.
- 남은 기능: NAS 성공 분기의 문헌 상세 출력과 사용자 선택 문헌 상세설명/전체 청구항 WIPS 후속 조회는 화면 P0-2/P0-3. WIPS 후보는 검색 결과이고 최종 권리·기술 적합성 검증 아님.
