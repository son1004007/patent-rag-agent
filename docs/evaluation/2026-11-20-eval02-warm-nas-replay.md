# EVAL-02 — NAS 기존 원문 재검색 10문항×2 실측

- 실행일: 2026-11-20 / 상태: **WARM_REPLAY_PASS, AI_REVIEWED_LIMITED_GO_FOR_IN_SCOPE, FULL_ROI_INCONCLUSIVE**
- 실행 경로: ChatGPT → 연결된 NAS read-only `search_patents(limit=3)`, 4건 `get_patent` read-only 근거 재확인. 새로운 원문/PDF/벡터/서지 INSERT·권한·서버 설정/재시작 없음.
- 출처: [EVAL-01 질문/검색 기준선](2026-11-20-eval01-live-retrieval-baseline.md), [AI 근거 라벨](2026-11-20-eval01-ai-provisional-score.md), [EVAL-02 계획](../46-reuse-value-verification-plan.md).
- 보안: 공개 GitHub에는 CASE·분류·집계·판정만 기록하고 실제 쿼리·문헌ID/SKEY/개인 NAS 메타데이터/원문·excerpt 및 credential/공급자 결과 저장 금지.

## 1. 읽기 전용 실제 호출과 일치성

- Q01~Q10 **동일 자연어 질문**으로 NAS 조회를 **첫 반복 10회 + 두 번째 반복 10회 = 검색 20회**. `IN` 문항5, `OUT` 문항5. 각 반환 상위3개.
- 결과: 첫 조회 성공 **10/10**, 반복 조회 성공 **10/10**, 총 검색 결과 슬롯 **30+30=60**, 양 회차 모두 발췌 30/30, 첫 회차 각 문헌의 출처/청크 해시·섹션/오프셋 존재 **30/30**.
- 같은 문항/순위의 **동일 문헌10/10**, **동일 청크10/10**. 이 실험은 모델·데이터가 변동 없는 같은 대화 세션의 짧은 반복이고 DB 전체 불변성 점검을 별도로 실행한 것은 아니다.
- 추가 증거 확인: Q01~Q04는 별도 **NAS 검색4회 + `get_patent`4회**, **4/4 found=true**, 출처 문서ID와 source_sha256 검색 결과 일치 **4/4**, 각각 근거3개 및 abstract/representative_claim 포함 **4/4**.
- **EVAL-02 단계에서의 NAS reader 호출 총 28회**(검색24 + 상세4), **WIPS 호출 실제0회**. 앞선 EVAL-01에서 WIPS를 실제 사용했던 횟수는 이 실험의 0회에 넣지 않는다.
- 두 병렬 wave의 JS 호출 구간 측정 참고치 4624ms/3197ms. 대화/LLM 추론·WIPS COLD 경로와 계측 범위가 다르므로 **서비스 응답시간·사용자 완료 시간·20% latency 절감률로 사용 금지**.

## 2. AI 근거 검토 및 캐시 사용 판정

| case | 데이터 분류 | 두 반복의 문헌/청크 안정성 | AI 직접 근거 | 재사용 결정 |
|---|---|---|---|---|
| Q01 | IN | PASS | 끝단 밀봉 | **AI_REVIEWED_REUSABLE** |
| Q02 | IN | PASS | 박막 봉지 | **AI_REVIEWED_REUSABLE** |
| Q03 | IN | PASS | POE 스코치/가교 | **AI_REVIEWED_REUSABLE** |
| Q04 | IN | PASS | 형광 봉지재 | **AI_REVIEWED_REUSABLE** |
| Q05 | IN | PASS | 저온 접합+습열 두 필수 조건 미입증 | **HOLD: INSUFFICIENT_DIRECT_EVIDENCE** |
| Q06 | OUT | PASS | 난연 전해질 근거 없음 | **HOLD** |
| Q07 | OUT | PASS | 수처리 분리막 근거 없음 | **HOLD** |
| Q08 | OUT | PASS | SiC 전력소자 근거 없음 | **HOLD** |
| Q09 | OUT | PASS | 경량 전력케이블 도체 근거 없음 | **HOLD** |
| Q10 | OUT | PASS | 흡수성 봉합사 근거 없음 | **HOLD** |

- 전체 AI 직접 근거 재사용률 **4/10(40%)**; IN **4/5(80%)**, OUT **0/5(0%)**. 이 수치는 **AI 자체 채점/기존 보유 문헌**, 독립 사람 평가·법적/기술적 확증이 아니다.
- OUT 질문에서도 NAS는 세 문헌을 반환한다. 벡터 근접도가 곧 직접 관련성은 아니다. 도메인 밖 답변을 자동 생성하지 않고 HOLD/WIPS 필요로 분기하는 것이 안전.
- `FRESHNESS_REQUIRED` (최신 공보·권리 상태·최신 동향) 질의는 **과거 자료가 검색되어도 NAS 단독 답변 금지**. 본 질문은 일반 선행기술 탐색의 과거 문헌 범위로만 평가.

## 3. 실제 호출/가정상 절감/원가 분리

| 지표 | 이번 측정 | 의미 |
|---|---:|---|
| NAS WARM read tool calls | 28 | 24 search +4 detail, 실제 MCP |
| WIPS WARM calls | **0** | 추가 provider 재검색 없이 기존 자료의 근거를 반환할 수 있었음 |
| AI answerable without WIPS | **4/10** | 기존 자료에 질문의 핵심 근거가 있는 제한된 경우 |
| 실측 WIPS 호출 절감률 | **NOT MEASURED** | 동일 조건의 직접적인 COLD/WIPS 대조 회차 없음 |
| counterfactual avoided WIPS | **NOT ESTIMATED** | '동일 질문의 매번 WIPS 1회' 등의 근거 없는 가정을 수치로 채택하지 않음 |
| 원화 요금/토큰·CPU 비용 | **N/A** | 사용량·요금 확인 불가, 무료라는 뜻 아님 |
| 동일 조건 end-to-end time 절감률 | **NOT MEASURED** | 병렬 wave 메타 시간과 실제 대화 완료시간 비교 금지 |

## 4. 코드/시험

- [순수 read-only 재사용 판정](../../poc/eval02_reuse_policy.mjs) 및 [합성 fixture 테스트](../../poc/eval02_reuse_policy.test.mjs).
- 로컬 Node.js v22.16.0에서 **합성 테스트 16개 PASS**. 스키마/ID/출처·청크 불일치와 stale/FRESHNESS_REQUIRED, 중복 ID, 오류값 차단 검증. 원문·검색어·문헌 식별자를 반환·출력하지 않는 인터페이스. 이번 실제 NAS 결과를 코드에 **비공개 저장·자동 replay 주입하지 않았으며**, 실제 EVAL-02의 위 집계는 직접 호출의 관측 원장에 기반.
- 실제 리플레이 파이프라인의 자동 실행/운영 배포 및 WIPS 호출 대체 라우팅은 **NOT IMPLEMENTED**. 사용자 명시적 ChatGPT 호출 하에서만 실행됨.

## 5. 결정

- **`AI_REVIEWED_LIMITED_GO`**: 현재 6개 NAS 보유 문헌을 **과거 자료 재열람, 동일 주제 반복 질문에 한해** 유지. Q01~Q04는 실제 관련 근거가 있어 WIPS 없이 재사용 가능. 신규 DB 전체 수집·권리상태 답변·고급 Hybrid 추가 개발은 **자동 시작하지 않는다**.
- **`WIPS_REQUIRED_OR_HOLD`**: Q05·OUT5처럼 필수 기술의 직접 근거가 없거나 최신성이 필요한 경우 NAS가 3건을 반환해도 결과를 추천하지 않는다. WIPS 재검색 권리·호출 예산은 별도 승인 경계 유지.
- **`ROI_INCONCLUSIVE`**: 실제 통제된 COLD 대조·비용/지연 미계측 → 외부 호출 50% 절감 또는 금액 ROI를 **확정하지 않는다**.
- 사용자는 2026-11-20 **'사람 검증하지 말고 AI가 다 채점'**으로 정정했다. 사용자 자체 평가를 필수 게이트로 요청하지 않는다. AI가 요약·대표청구항 및 NAS 근거를 검토하되 독립 gold label 부재 사실은 투명하게 남긴다. **법률/계약/권한 승인이나 기밀 전송 규칙은 완화하지 않는다**.

**다음 기술 작업**: `poc/eval02_reuse_policy.mjs`를 실제 읽기 전용 워크플로에 통합할 때는 scope/암호화/비공개 결과 유지·사용자의 범위 승인·배포 최소 테스트가 필요. 현재는 운영 변경 없이 AI가 범위 한정 재사용 여부를 결정하는 수준의 실증.
