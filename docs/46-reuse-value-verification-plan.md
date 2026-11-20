# EVAL-02 실행 계획서 — NAS 보관 자료 반복 사용의 시간·호출·품질 가치 검증

- 작업 ID: **EVAL-02**, 우선순위 **P0 / 의사결정 검증**(EVAL-01 질문·라벨 스키마 재사용)
- 상태: **계획서 작성 완료 / 반복 실험·비용 실측·운영 변경 NOT RUN**
- 목적: 이미 보관한 특허를 재사용했을 때 WIPS MCP **추가 호출을 줄이고**, 사용자에게 충분한 근거를 더 빨리 제공하는지 확인한다. 비용 절감은 **직접 관측값과 counterfactual 추정**으로 나누어 기록한다.
- 선행: [판단 기준](44-mvp-evaluation-decision-criteria.md), [품질 비교 계획](45-search-quality-comparison-plan.md), [실제 서지 보관](39-mvp-archive-100-live-acceptance.md), [선택문헌 원문 적재](35-mvp03-actual-ingest-acceptance.md), [MVP41 검색→서지 보관](42-mvp41-code-mode-gateway-archive.md), [평가 인덱스](evaluation/INDEX.md).

## 1. 현행 시스템에서 실제 재사용 가능한 것

| 데이터 | 현재 실제 상태 | 재사용 가치·한계 |
|---|---|---|
| WIPS 첫 페이지 서지정보 | **83건**·7필드/페이지1, 동일 응답 재사용 0 INSERT | 문헌번호·제목·출원인·목록 중복 확인; **텍스트/벡터로 의미검색 불가능** |
| NAS 승인 특허 | **6문헌/10섹션/417 청크**·로컬 E5 384D | 현재 NAS `search_patents`/`get_patent`로 의미검색/제한 근거 재사용 |
| 전체 청구항·상세설명 | 기존 일부 허용 문헌에서 텍스트 확보, `get_patent`은 최대3개×300자 근거 | **새 WIPS 본문 호출 완전 대체 보장 아님** |
| 공보 PDF | **0건** | 현재 파일 재열람/파일 저장비 절감 검증 불가능 |
| WIPS 검색→서지 NAS 브리지 | ChatGPT 명시적 합성 경로 83건 REUSED_VERIFIED | 같은 WIPS 조회를 수행한 **뒤에 DB 중복 저장을 피한 것**. **WIPS 검색 호출 자체를 절감한 실증이 아님** |

**중요한 구분:** 기존 `REUSED_VERIFIED`가 의미하는 것은 **DB 재삽입 0건**이다. 이 사실만으로 **WIPS API 호출 0회**, 검색 지연·요금·토큰 비용 절감을 주장하지 않는다. NAS reader의 실제 6개 보유 문헌만 *추가 외부 호출 없이* 검색할 수 있다.

## 2. 대조 실험과 캐시/신선도 정책

**질문/분류**는 EVAL-01의 10문항(가능 시 동일 `run_id` baseline)을 재사용하고, 5문항은 원문6개가 검색될 수 있는 범위, 5문항은 미보유/새로운 범위로 분리한다.

| 경로 | 실제 호출 | 측정 목적 | 공정성 제약 |
|---|---|---|---|
| **COLD (최초 연구)** | 승인된 WIPS search(필요 시 기존 NAS search) → 연구 결과·출처 기록 | 첫 조회 호출수·사용자 완료시간, snapshot 구축 | **새 본문/벡터 수집 안 함**. 기존 83서지 메타데이터는 현행 정책만 |
| **WARM-NAS (동일 질문 반복)** | **NAS `search_patents` + `get_patent`**로 답변 생성, 외부 WIPS 검색은 호출하지 않음 | 실제 외부 WIPS 호출0 가능 여부, NAS 응답시간, 관련성 유지 | 6문헌 밖의 83서지는 **상세 근거 부재**, 부재는 명시하고 사실로 보완하지 않음 |
| **WARM-CHECK (선택/통제)** | 필요한 경우 승인된 **작은 표본**만 WIPS 재검색 → 새로운 문헌/권리·상태 변경 확인 | stale/누락 위험 진단 | 외부 WIPS 재호출은 실제 호출수/요금에 그대로 가산, 무승인 자동 재호출 금지 |
| **WIPS-ONLY (대조 설명)** | 최초 COLD에서 확보한 WIPS 결과를 기준 답변으로 사용 | 반복 연구 때 WIPS에 요청할 필요가 있었을 **가상 호출** 추정 | 실제 두 번째 WIPS 조회를 하지 않았다면 `counterfactual_estimated`로 표기; 실제 절감 확정 금지 |

**신선도 규칙:** 동일 문서/같은 연구 의도라는 사실이 확인되고, 사용자가 **과거 자료 분석**을 원할 때 NAS 재사용을 허용한다. **현재 권리 상태·최신 공보/최신 연구·시점 민감 질의**이면 WIPS 재검증 필요로 `STALE_OR_FRESHNESS_UNVERIFIED` 표시하고, 사용자가 허용한 범위/호출 예산이 있을 때만 provider를 다시 조회한다. 7일 등 임의 TTL을 "공식 WIPS 최신 보장"이라고 주장하지 않는다. 최초 실험에서는 24시간 이내의 반복 질문을 기본 단위로 삼되, 이는 **실험 통제 조건**이지 보편적 freshness 정책이 아니다.

## 3. 실행 데이터 계약 (제안, 아직 신규 파일 없음)

- 공개 코드/합성 스키마 후보: `poc/eval_reuse_metrics.py`, `poc/test_eval_reuse_metrics.py`.
- 비공개 실험 원장(예): `runs/eval02/<run_id>/events.jsonl`. 실제 검색어·문헌ID/SKEY/원문·credential/비공개 해시·경로를 공개 repo/CI 로그에 쓰지 않는다.
- 기능을 서비스에 붙이는 작업이 아니라 **직접 사용자 호출을 검증하는 read-only 실험**부터 시작한다. 새 영구 로그 테이블/백그라운드 데몬/DB role 확대는 이번 범위 밖.

```json
{
  "run_id": "eval02-20261120-v1",
  "question_id": "Q001",
  "scenario": "WARM_NAS",
  "baseline_corpus": "SYNTHETIC_MANIFEST_HASH",
  "observations": {
    "wips_search_calls_actual": 0,
    "wips_detail_calls_actual": 0,
    "nas_search_calls_actual": 1,
    "nas_get_patent_calls_actual": 3,
    "elapsed_ms_measured": 850,
    "relevant_evidence_count_human_verified": 2,
    "unsupported_recommendations": 0,
    "cache_read_success": true,
    "freshness_status": "HISTORICAL_SCOPE"
  },
  "counterfactual": {
    "would_repeat_wips_calls_estimate": 1,
    "avoided_wips_calls_estimate": 1,
    "source": "COLD baseline workflow; NOT DIRECTLY OBSERVED"
  },
  "costs": {"wips_actual_charge": null, "llm_tokens_actual": null}
}
```

**합성 예시**. `null`은 금액 미확인이지 0원이 아니다. `elapsed_ms_measured`는 실제 계측된 end-to-end 시간만 허용하고, UI 응답 추측/지연 계산으로 채우지 않는다.

## 4. 단계별 개발·실험 실행 순서

| 단계 | 작업(미구현은 신규 제안) | 확인·완료 증거 |
|---|---|---|
| R0. baseline/권리 확인 | 최신 AGENTS/TASKS, read-only NAS 검색 정상, WIPS 호출 권한, 파일 공개 제한, 기존 83서지/6문헌·417벡터를 당시 실측 기록 | 실험 범위·run_id·실제 snapshot·사용 WIPS 도구 지정, DB write0 |
| R1. 질문 고정·분류 | EVAL-01의 Q001~Q010과 동일 질의 텍스트·필수 특성/도메인·질문 목적(과거 분석 vs 최신성)을 비공개로 기록 | 대상10개 고정; **in/out-corpus**·historical/freshness 각각 표시 |
| R2. COLD 수집 | 기존 승인 범위 내 실제 WIPS 검색 **최대 1회/질문**, 초기 NAS 검색과 필요 evidence, 시도/성공·시간/호출수 계측; WIPS 청구항·상세 추가 호출은 별도 승인·필요성 확인 후 | `actual_calls`, 답변 상태/후보·증거/실측, 처음 baseline 데이터 **저장 상태 분리** |
| R3. WARM-NAS 반복 | 질문마다 **동일 조건으로 재실행**, WIPS 추가 호출 없이 NAS 검색·상세 조회, 동일 사용자 평가 질문. 각 질문 최소2회 반복하고 첫 실행/warm-up 모델 캐시 영향을 기록 | `wips_calls_actual=0`이면서 실제 근거가 반환됐는지, latency / 관련성·인용 품질 |
| R4. 안전한 실증 | 재사용 결과가 없거나 근거가 부족한 질문은 `NEEDS_WIPS`/`INSUFFICIENT_EVIDENCE`, 권리·최신성 요구는 `STALE_OR_FRESHNESS_UNVERIFIED`. 무리하게 NAS로만 답하지 않음 | 허위 완전성 주장0, 근거 없는 추천0, 보류율/누락 건수 |
| R5. 선택적 WIPS 재검증 | 필요한 경우 선택된 **최대2문항**만 새 실조회(권한/비용 확인), cold snapshot과 번호·날짜·종류 비교 | 실제 검색 사용량을 따로 기록하고 freshness drift 여부만 측정. **권리·예산 미확인 시 NOT RUN** |
| R6. 차이 분석 | `actual_wips_calls` vs 명시된 `counterfactual_est`, 품질 non-inferiority, 사용자가 판정할 때까지 걸린 시간, 검색·LLM·CPU 비용 가시성 | in/out-corpus 별도 수치/분모, 관측/추정 분리 |
| R7. 최종 결정 | [판정 기준](44-mvp-evaluation-decision-criteria.md) 적용, 사용자 #31 평가와 동일 기록으로 연계 | `LIMITED_GO/GO/NO_GO/INCONCLUSIVE` 및 다음 기능 개발 범위 확정 |

**재작성 필요 없는 기존 자산:** [서지 아카이브](../poc/mvp37_archive.py), [원문 검색 reader](../poc/private_patent_reader.py), [WIPS/NAS 비교](../poc/mvp04_candidate_compare.mjs). 본 계획은 **관측/평가용 코드와 데이터 계약만** 신규 제안한다.

## 5. 정량 지표와 초기 판정 게이트

| 지표 | 계산 | 초기 실무 판단 |
|---|---|---|
| `actual_wips_calls` | 실험 호출 로그의 **실제 WIPS search/detail 호출 합계** | WARM-NAS에 0이어야 "직접 WIPS 없이 재사용" 성공 |
| `estimated_avoided_wips_calls` | cold workflow에 필요했던 반복 검색 호출의 **가정상 횟수** − warm 실제 호출 | 추정임을 명확히; **절감 실제 청구액이 아님** |
| 재사용 커버리지 | 사용자 질문 중 NAS가 **사람이 검증 가능한 최소 1개 관련 근거를 제공**한 질문 수 / 전체 질문 수 | in-corpus 5개와 out-of-corpus 5개 별도, 전체 10만으로 합치지 않음 |
| 품질 비열화 | WARM-NAS의 직접 관련 문헌/근거 검증 결과가 COLD/WIPS baseline보다 줄었는지 | **직접 관련 필수 근거 누락 0건**을 희망, 누락 시 제한 범위만 재사용 |
| 지연 절감 | `(median_cold_ms−median_warm_ms)/median_cold_ms`, 둘 다 실제 동일 계측 범위일 때만 | 초기 목표 **≥20%**. 측정 환경/질문 차이 크면 단정 금지 |
| 외부 호출 절감 | `1−actual_warm_wips_calls/estimated_repeat_baseline_calls`, 분모 및 가정 명시 | 초기 목표 **≥50%**, 품질 유지 전제 |
| 불필요한 반복 DB 쓰기 | 동일 보관 데이터 삽입·업데이트 건수 | **0**. 서지 기존 reuse=0 INSERT와 WIPS 호출수는 다른 지표 |
| 비용/요금 | 실제 provider 청구/사용 내역 확인 시 KRW 등 실제 단위, token/CPU 별도 | **미확인은 N/A**, MCP가 공짜라고 주장 금지 |

**결정 규칙:** in-corpus 질의 중 관측된 재사용 커버리지와 품질이 유지되고 실제 WIPS 없는 대화가 가능하면 **LIMITED_GO**(NAS 재사용 유지). 외부 반복 호출 회피 추정이 ≥50%이고 동등한 근거 품질을 유지하면 재사용 가치가 있다는 **초기 가설**을 지지. 반대로 out-of-corpus 질문에서 NAS-only가 근거를 못 찾으면 **정상적인 한계**이며, WIPS가 필요한지 분기하도록 설계한다. 금액 ROI는 실제 요금/토큰/운영비가 확인되기 전 보류.

## 6. 사전 문제 차단

| 위험 | 사전 대응 |
|---|---|
| `REUSED_VERIFIED`를 WIPS 호출 절감으로 착각 | DB INSERT 수 vs 외부 WIPS 실제 호출수 **별도 지표**. 지난 83건 재사용은 WIPS 호출 직후 발생 |
| 메타데이터 83건으로 NAS 벡터 검색 성공 주장 | 원문/섹션/청크 있는 6문헌만 `search_patents` 가능, 메타데이터-only 별도 |
| 비교 기준 질문·데이터셋이 서로 다름 | EVAL-01의 질문/라벨·snapshot 동일하게 사용, 차이는 실행 시나리오만 |
| warm-up/네트워크 지연으로 latency 왜곡 | 같은 날짜/기기/측정 구간, cold/warm 2회 이상, p50 + 범위, sample 작음을 명시 |
| 새 특허·권리 변동을 오래된 NAS만으로 확답 | `HISTORICAL_SCOPE`/`FRESHNESS_UNVERIFIED` 별도, 최신성 요구 WIPS 확인 |
| 토큰 과금·캐시 비용 미측정 | 공급자 청구/호출·LLM usage 보이는 경우만 수치, 없으면 `N/A` |
| 사용자 연구질문/실문헌 ID 노출 | 공개 GitHub에 질문·제목·SKEY·본문/민감 네트워크 정보 금지, 비공개 기록도 정책 확인 |
| 새 WIPS 호출을 줄인다면서 반복시험에서 과다 사용 | 10문항 기준 최대 10회 cold 검색, 필요할 때 추가 2문항 통제 재검색, 중단/중복 재호출 금지 |
| 반복 질문이 실제로 달라 연구 결론을 바꿈 | `question_id` 동일, 필요한 신규 요구는 새 run_id/분리 평가 |
| 등록되지 않은 NAS 자동 배치 기대 | ChatGPT 명시 오케스트레이션만 사용, 플랫폼 후킹/독립 MyFolder 자동화는 없음 |

## 7. 안전한 검증과 완료 조건

1. **계약 테스트(향후 구현):** 0건·없는 문헌·출처 미확인·provider 실패·NAS 실패·metadata-only·freshness-sensitive·도메인 out-of-corpus를 입력하면 저장 성공/품질 성공으로 오판하지 않아야 한다.
2. 실제 NAS 검색은 **읽기 전용**, 원문6·청크417 등 기존 baseline과 컨테이너 변경 전후 보존. 새로운 유료 API·PDF·별도 URL·새 writer 권한 추가하지 않는다.
3. 질문 10개에 대해 cold baseline, warm-only 2회 이상, 최소 사람 판단 근거/직접관련 정보, 실제/가정 호출수 분리, latency 실제 계측/미측정 표시.
4. 실측 결과를 [`docs/evaluation/results/EVAL-02-summary.md`](evaluation/INDEX.md) **신규 예정**에 집계만 작성하고, EVAL-01과 합쳐 [판정 규칙](44-mvp-evaluation-decision-criteria.md)에 따라 GO/LIMITED_GO/NO_GO/INCONCLUSIVE 결정. **사람 사용자 #31 평가 없으면 인수 완료 선언 금지.**
5. 개인정보·제공자 계약·보안 정책·WIPS 100건 서지 보관 범위를 유지. **MyFolder 작업 HOLD.**

**진행 상태:** EVAL-02 실행/실측 NOT RUN, 계획 문서만 반영함. 실제 개발 시 [전역 Control](https://github.com/son1004007/ai-agent-workflow-playbook/blob/main/CONTROL.md) → [AGENTS](../AGENTS.md) → [TASKS](../TASKS.md) → [평가 인덱스](evaluation/INDEX.md) → 이 계획 → 해당 repo 최신 코드 → 비공개 run scope 순으로 진입한다.
