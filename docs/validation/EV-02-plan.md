# EV-02 실행 계획 — 반복 조회·검토시간·비용 검증

2026-11-20 / PLAN ONLY, 실측 NOT RUN / [설계](EV-02-design.md)

| 단계 | 실행 방법 | 수용/중단·대응 |
|---|---|---|
| 1. 경계 확인 | CONTROL/AGENTS/TASKS, 서지83·원문6/10·청크417, 39/42 운영 증거, reader 권한, WIPS 호출/요금 확인 | 계약·신규 유료 호출 불명확하면 실제 새 조회 중지. 승인된 이전 증거로 dry-run 가능 |
| 2. 문제·시점 | EV-01에서 5~10개; warm 최소3(원문 보유/서지만 보유/신선도 필요 각각 포함), cold 최소2. 동일 질문/국가/기간/K=5 | 비교 질문·출처·시점/모델 drift 기록 |
| 3. 최소 코드 | 기존 Code Mode/Gateway A안·NAS reader 우선. 필요시 poc/validation/eval_reuse.mjs/tests 구현 | synthetic: baseline0, METADATA_ONLY, FULLTEXT_MISS, valid hit, freshness, provider fail, missing cost, source drift |
| 4. 1-case pilot | 허용 범위 내 A WIPS-only 반복 기준선과 B NAS-first+fallback을 한 질문에서 시험. 검색/상세/검토 시간 및 근거 기록 | 호출·실제 값이 안 잡히면 NOT RUN/DRY_RUN으로 정정, 절감 실증으로 보고하지 않음 |
| 5. 나머지 재사용 | cold→warm 조건에서 각각 측정. 단순 ID 보유를 verified hit로 계산하지 않음. 최신 상태/신규성 검증은 WIPS 호출 | 오류와 검토자의 수작업 복구 시간 포함, 과도한 호출/권리 범위 넘으면 STOP |
| 6. 짝비교 | 검색/상세 호출 감소, 검토 시간, latency p50/p95, hit율, 근거 정확도/오추천, 공식 금액 확인 여부 | 단가 없으면 비용 UNKNOWN; 같은 라벨로 품질 확인 |
| 7. 결정 | warm의 20% 절감 가설과 0/10/20/30% 민감도, 한계·실패와 품질 비열화 평가 | 절감 안되면 HOLD, 허위 추천/위반 STOP, 표본 부족 INCONCLUSIVE |
| 8. 기록 | 사용자 인수 #31과 함께 TASKS/CURRENT_STATE/WORKS 및 44 판단 문서 링크로 근거 기록 | 서지 자동 저장의 성공을 fulltext 자동화 성공으로 변경 금지 |

시험은 기본 읽기 전용이며 DB와 외부 서비스 변경이 없어야 한다. 기존 원문/서지 row fingerprint 및 승인 범위 내 회귀 체크를 하되 실패한 경우 원인을 추적하고 조용히 재시도하지 않는다. **DONE은 trace/측정표/근거·품질/사용자 검토와 판정 기록까지**; 지금은 문서만 완료했다.
