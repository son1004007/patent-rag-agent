# EVAL-01 실행 계획서 — WIPS vs NAS vs 통합 검색·근거 정확도 비교

- 작업 ID: **EVAL-01**, 우선순위 **P0 / MVP 사용자 인수 검증**
- 상태: **계획서 작성 완료 / 새 실험·정답 라벨링·운영 변경 NOT RUN**
- 목적: WIPS 단독 검색보다 NAS RAG 또는 WIPS+NAS 통합이 **실제 사용자에게 유효한 추가 문헌과 근거**를 주는지 확인한다.
- 선행: [판단 기준](44-mvp-evaluation-decision-criteria.md), [기존 검색·비교 근거](25-mvp04-candidate-comparison.md), [사용자 평가](31-mvp06-user-trial.md), [작업 인덱스](evaluation/INDEX.md).

## 1. 실험 범위 및 해석 제한

- **질문 10개**: 현재 NAS 원문6문헌이 다루는 기술 범위 내 **5개**, 다른 범위 **5개**(비교 왜곡 파악용). 먼저 실무 공개 가능 질문 5개로 스모크 후 나머지 5개 확장. 동의어/필수 특성/제외 조건을 **검색 전 봉인**한다.
- 기존 NAS는 **원문6건/10섹션/417청크**지만 WIPS는 더 넓은 특허 검색을 수행한다. NAS 미보유 영역의 열등한 결과를 **임베딩 모델 품질 문제로 오판하지 않는다**.
- WIPS 검색 결과에는 일부 요약/대표청구항이 있지만 상세설명·전체 청구항은 문헌별 조회가 필요할 수 있다. 현행 보관된 서지83건은 요약/벡터가 없으므로 근거 없는 행을 검색 성공·정답으로 간주하지 않는다.
- 평가 중에는 **추가 원문 인제스트/임베딩/공보 PDF 다운로드/새 비공개 파일의 GitHub 게시를 하지 않는다.** 기존 승인 자료 읽기와 사용자 지정·허용 범위의 **제한된 WIPS 조회**만 한다.
- provider별 결과수 **3개**와 동일한 문헌 해석 조건을 비교한다. W/N rank top3 자체는 비교 가능하지만 **통합 결과는 up to 6개 pool**이므로 직접 같은 P@3라고 표시하면 안 된다.

## 2. 검색 입력 및 실제 API 계약

| 구간 | 구동 대상 | 필수 호출/검증 | 현재 구현과 주의사항 |
|---|---|---|---|
| 질문 등록 | **신규 제안** `evaluation/questions.json` (비공개 NAS, 공개 GitHub에서는 스키마/합성 fixture만) | `question_id,domain,question,required_properties,exclude_terms,query,corpus_scope`. 공개 저장소에는 실문헌/연구주제 입력 금지 | 실험 시작 전 10개 고정, 입력 변경 시 새로운 run_id |
| WIPS | `mcp__wipsclip__get_patent_search_onlyengine` | `pgrow=3,pgnum=1,outitem="SKEY,CC,XN_D,KC_D,TIK,ABK,CLK"`. 실제 공급자 가능 필드/최대 요청 검증 | 키워드·검색식은 WIPS 문법; 결과 `row_list, total_count` 구분 |
| NAS | `mcp__NAS_RAG__search_patents` | 동일 자연어 `query` + `limit=3`. 반환 `document_id, publication,country,kind,source_sha256,excerpt,distance` | cosine distance는 **문헌 관련성 점수 아님** |
| NAS evidence | `mcp__NAS_RAG__get_patent` | 찾은 ID별 최대3 근거, 각 300자; 실제 `source_sha256`·문헌키·섹션/offset 일치 검증 | 기존 MCP는 전체 원문 읽기 서비스가 아님. 부족한 근거는 UNKNOWN |
| 통합 | [`poc/mvp04_candidate_compare.mjs`](../poc/mvp04_candidate_compare.mjs) | 기존 반환 구조 adapters에 맞춰 dedup, 국가+공보번호+kind, 조건·HOLD/EXCLUDE | **어휘일치 기반**. 별도 reranker·확률 점수/정량 성능 판정 아님 |
| 품질 채점 | `poc/eval_quality_score.py` **신규 제안, 현재 파일 없음** | 실제 정답 라벨만 입력 받아 deterministic 지표 계산 및 JSON/CSV 출력 | 모델이 자동으로 자기 응답의 정답을 판정하지 않음 |

**초기 JSON 스키마(가상 데이터 예시):**

```json
{
  "run_id":"eval01-20261120-v1",
  "question_id":"Q001",
  "domain":"in_corpus",
  "question":"SYNTHETIC_QUESTION_PRIVATE_IN_NAS",
  "wips_query":"(synthetic).ti.",
  "required_properties":["property_a","property_b"],
  "exclude_terms":["excluded_term"],
  "top_k_per_source":3,
  "corpus_version":"SHA256_of_baseline_manifest",
  "candidate_labels":[
    {
      "publication_key":"KR|SYNTHETIC_NO|A1",
      "source_set":["WIPS","NAS"],
      "wips_rank":1,
      "nas_rank":2,
      "relevance":2,
      "evidence_verified":true,
      "verification_scope":"EXCERPT",
      "human_judge":"USER",
      "decision":"HOLD"
    }
  ]
}
```

실제 WIPS 상세 근거/원문은 개인 NAS에만 있으며 외부 보고서에는 **익명 집계만** 남긴다. 실제 gold 라벨은 같은 문헌에 대해 W/N/C가 공통으로 참조한다.

## 3. 계획된 구현·평가 단계

| 단계 | 실행 단위(착수 전 점검) | 산출물·PASS 조건 |
|---|---|---|
| Q0. 기준선 동결 | 현재 GitHub main/AGENTS/TASKS, 사용 WIPS 28개 중 도구·계정 연결, NAS docs6/sections10/chunks417/reader role, 운영 DB fingerprint **read-only** | `run_id`·날짜·도구 스키마·DB snapshot hash **비공개 기록**, 다른 컨테이너 불변 |
| Q1. 질문 10개 | 5 in-corpus + 5 out-of-corpus, 같은 사용자 목적·특성 기준·제외어를 실제 WIPS 호출 전 결정 | 10문항 고정, 중복/민감/실제 자료 소유권 확인, 사용자 평가 대상 명시 |
| Q2. 각 소스 검색 | WIPS 1회/질의(상위3), NAS 1회/질의(상위3) 및 해당 NAS ID 상세 조회. 공급자 실패는 상황 그대로 보존 | `search_status`, 반환 count/rank, provider call count, 입력 문서 출처·서지/근거 상태 |
| Q3. 통합 비교 | 기존 `integrateCandidates` 적용. WIPS/NAS 동일 문헌 exact match, 후보 분포와 근거 0/1+ 표시 | 고유 후보 최대6, WIPS+NAS 중복 및 HOLD/EXCLUDE 분류, 모호한 번호 별도 확인 |
| Q4. 사람 평가 | 라벨0/1/2(무관/간접/직접), 문헌별 출처 확인 및 속성 근거 일치, 편향 감소 위해 소스 비표시 선평가 후 출처 대조 | 사용자 또는 지정 검토자가 10문항 전수 평가, `UNKNOWN`은 UNKNOWN으로 기록 |
| Q5. 분석 | W/N P@3·Hit@3, C의 **WIPS에 없는 직접관련 문헌 수**, 근거 검증률, 잘못된 추천/무리한 단정, 실패·품질 변화 | 원시 분모/건수·질의별 표, in/out-corpus 별도 통계, 합계 및 제한 보고 |
| Q6. 결정·인수 | [판정 규칙](44-mvp-evaluation-decision-criteria.md) 10문항 적용·#31 사용자 피드백 반영 | GO / LIMITED_GO / NO_GO / INCONCLUSIVE + 이유·다음 조치. 실행하지 않은 테스트는 NOT_RUN |

**문서화와 실행 구분:** 이 계획만 작성한 지금은 Q0~Q6 **NOT RUN**이다. 기존 과거 3+3→5 결과는 입력·판정 스모크 참고로만 쓰고 10문항의 신규 실측을 대체하지 않는다.

## 4. 지표 계산 명세 및 예외

- `P@3_W(question) = count(relevance=2 among rank 1..3)/3`, `P@3_N(question)` 동일. 결과 부족은 0으로 채우고 별도 `availability` 유지. 질문 단위 macro-average, 질문 수/분모 병기.
- `Hit@3 = 1` iff 직접 관련 1건 이상; 미실행·오류를 무조건 0으로 간주하지 않고 **availability failure 별도 보고**.
- `C_marginal_relevant = |(C ∩ relevance2) \\ W_top3|`. **추가 후보를 검토한 비용이 증가한다는 점을 표기**. C는 자체 랭크가 없으므로 `P@3_C`를 산출하지 않는다.
- `EvidenceVerifiedRate = verified_citations / judged_citations`; 0개일 때 N/A. "근거를 실제 확인하지 못함"은 `UNKNOWN`, 검증 실패는 false로 구분.
- `UnsupportedRecommendationCount`: 최종 REVIEW_CANDIDATE인데 사람이 "필수 속성 미증명" 또는 "인용 불일치"로 판정한 건수. 키워드 일치 자체는 물성 실측이 아니므로 필수 특성의 **문헌 명시**와 **실제 입증** 두 축 분리.
- `HOLD`는 자동 실패가 아니다. 한정 발췌 때문에 **확인 불가**가 많을 수 있으므로 원문 접근 가능 범위에서 추가 검토 필요 상태로 기록.
- 결과가 1~2개만 나오는 도메인과 3개인 도메인은 분모/coverage 별도 공개. **Recall@3은 완전한 전수 정답셋이 없는 한 미산출**.

## 5. 실패 예방·안전 시험

| 실패 요인 | 사전 검증/대응 |
|---|---|
| WIPS/NAS corpus 규모 차이 | 5/5 strata, in/out-corpus 분리, 추가 후보수와 동일 K 지표 분리 |
| WIPS 검색식과 NAS 자연어 다름 | 질문/의도 공통, WIPS 문법만 별도 변환하고 변환본 사전 고정; 질의 반복 최적화 금지 |
| 공보 종류/특허번호 중복 정규화 오류 | 국가+문헌번호+kind exact; 다른 국가/종류는 독립, 불명확은 ID_CONFLICT |
| WIPS summary·대표 청구항 300자 제한 | 전체 문헌 미검증을 무관으로 단정 금지; 근거 없음/UNKNOWN 분리 |
| 비교 함수의 review 추천이 기술성능 입증으로 오해 | 사용자 적합도 평가에서 근거 필요, \`REVIEW_CANDIDATE\`도 전문 확인 전 추천 확정 아님 |
| 사용자 라벨 없이 LLM 자신이 맞다고 평가 | 사용자/사람 증거 확인 필수; 모델은 후보 및 표의 집계만 |
| 실제 자료 유출 | 공개 repo에는 스키마/익명 통계만; 실제 질문·SKEY·문헌/근거·ID는 개인 NAS에만 |
| WIPS 사용량/비용 초과 | 각 질의 1회 WIPS 검색 예산, **추가 상세·재검색은 승인 범위 확인 전 HOLD** |
| 데이터 변경으로 공정성 상실 | corpus snapshot 고정, DB 적재/변형 금지; 변동 시 run_id 새로 |

## 6. 제출 형식·인수

- 비공개 run files (제안): `runs/eval01/<run_id>/questions.json`, `wips_meta.json`, `nas_meta.json`, `human_labels.json` — 실제 연구 자료이므로 **공개 GitHub에 업로드 금지**.
- 공개 합성 schema/집계: `docs/evaluation/results/EVAL-01-summary.md` **신규 제안(실제 파일 아직 없음)**, 질의별 익명 QID·W/N/C 집계, 분모·대표 실패·스냅샷 구분.
- 코드 제안: `poc/eval_quality_score.py`, `poc/test_eval_quality_score.py` — 실제 구현 전 현재 repo tree 확인.
- 사용자: 10개 질문의 결과 관련성·출처/근거·보류 적절성을 평가하고 [중앙 #31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31)에 본인 승인/수정 의견 남겨야 인수 완료.
- **최종 종료 기준:** 실제 10문항(사람 평가 포함), 지표 계산 재현, 데이터/권한 변경 없음, 구분된 판정과 다음 실행 결정. 그 전에는 `PLAN_READY` 또는 `INCONCLUSIVE`이지 `EVAL_PASS`가 아니다.
