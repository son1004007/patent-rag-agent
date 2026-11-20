# EV-01 실행 계획 — 검색 정확도 파일럿

2026-11-20 / PLAN ONLY / 실제 실행 NOT RUN / [설계](EV-01-design.md)

| 단계 | 구현·실행 | 확인 기준 / 예상 장애 대응 |
|---|---|---|
| 1. Preflight | 전역 CONTROL, 대상 AGENTS/TASKS/CURRENT_STATE, 기존 MVP-04 비교 모듈·운영 read-only WIPS/NAS 계약·권리 재확인 | 사용자 승인 서지 100건을 신규 fulltext/벡터/PDF 허가로 확대하지 않음. 실제 원문 비공개 |
| 2. 고정 문제세트 | 5~10개 공개·합성 질문(원문6 안/밖/음성 케이스), 동일 키워드/국가/기간/K=5, gold 평가자 선정 | 대표성·중복·금지 고객 주제 필터, case/version 식별 |
| 3. 최소 harness | 기존 poc/mvp04_candidate_compare.mjs 재사용; 필요한 경우에만 poc/validation/eval_common.mjs, eval_quality.mjs와 테스트 작성 | synthetic: 0문헌, 5미만, 등급 0/1/2, 중복 ID, 국가/공보종류, provider error, 불일치 출처, missing evidence, rank tie |
| 4. Bounded smoke | 우선 1문항 A/B/C를 실제 기존 도구로 읽기 수행. 응답 스키마·ID 매핑과 질문별 WIPS/NAS 호출수·시간 확인 | 공급자 권리/계약·신규 과금 불명확하면 실제 신규 호출 STOP, 기존 승인 증거 기반 dry-run은 별도 표시 |
| 5. 나머지 케이스 | 같은 조건으로 4~9문항 측정, 실제 응답은 허가된 비공개 evidence에서만 관리 | 실패/결측 포함, 5개 미만 유효면 INCONCLUSIVE; 호출 무제한 재시도 금지 |
| 6. 사람 채점 | 출처·모드를 가리고 관련성 0/1/2, 근거 섹션 검증, HOLD/EXCLUDE 적절성 채점 | 유사도=실제 성능이라는 잘못된 판정 차단 |
| 7. 평가 계산 | P@5, nDCG@5, 후보 증가, evidence_match_rate, 오추천, latency/호출수, overlap-only/전체 비교 | 분모·결측·품질 저하·실패 이유 명시, 5~10표본은 탐색적 |
| 8. 종료판정 | DEC-RAG-01의 95% 근거 목표/허위 단정 0 등 확인, 사용자 인수 #31 연계 | TASKS/CURRENT_STATE/WORKS에 결과·한계·GO/HOLD/STOP/INCONCLUSIVE 기록 |

실제 변경은 가급적 읽기 전용·서비스 재시작 없음. 합성 테스트가 실패하면 수정 후 범위 제한 재검증. NAS 원문과 임베딩/서지의 상태 스냅샷을 전후 확인할 수 있을 경우 6/10/417 및 83 불변 여부 기록. 실제 제품 품질 PASS는 사람의 라벨·근거·측정 결과가 있어야 가능. 시작은 **1-case 작은 실측→수정→5~10 확대** 순서.
