# EVAL-02 — 전체 10문항 NAS 실경로 재사용 분기 + 다중 근거 보강

- 작성일: **2026-11-20** / 검증: 사용자 직접 채점 대신 ChatGPT 자체 AI 관련성 분석
- 상태: **TEN_CASE_READ_ONLY_ADAPTER_PASS / MULTI_EVIDENCE_FEATURE_GATE_PASS / ROI_INCONCLUSIVE**
- 소스: [직전 4문항 인수](2026-11-20-eval02-live-read-adapter-acceptance.md), [10문항 warm 기준선](2026-11-20-eval02-warm-nas-replay.md), [기존 평가/정책 코드](../../poc/eval02_reuse_policy.mjs).
- 데이터 보호: 이 문서는 공개 repository에 보관되므로 사용자 사내 연구, 구매한 특허 제목/문헌 ID/SKEY, 원문·청구항·초록, source/chunk SHA, 실제 질의 전체, API 키/개인 주소를 저장하지 않는다. AI 자체 판단은 `AI_REVIEWED`로 표시; 사람 gold label/실제 특허 법률 검증/전문 인수는 실행하지 않음.

## 1. 나머지 6개 문항 실제 NAS 판정기 실행

[Code Mode 전용 NAS read-only 어댑터](../../poc/eval02_live_read_adapter.mjs)를 GitHub 최신 코드에서 읽고, **실제 연결** `mcp__NAS_RAG__search_patents`와 `mcp__NAS_RAG__get_patent`을 주입했다. 별도 모델 API, 신규 NAS 원문/서지/벡터 수집·저장, WIPS 검색, DB 변경이나 서비스 재시작은 없음.

| 문항 | 분야 | 판정 | AI 근거 검토 요지 |
|---|---|---|---|
| Q02 | 페로브스카이트 태양전지 박막 봉지 | **AI_REVIEWED_REUSABLE** | 모듈·PDMS 보호층·UV 레진 도포/경화가 같은 문헌의 요약/대표청구항에 등장 |
| Q03 | 태양광 POE 스코치 저항성/가교 | **AI_REVIEWED_REUSABLE** | 태양광 봉지 필름의 스코치 개선 목적(명칭), 에틸렌-옥텐/폴리올레핀 조성·가교성(요약/청구항)이 맞음 |
| Q06 | 리튬이온 난연성 전해질 | **INSUFFICIENT_DIRECT_EVIDENCE** | NAS 상위 후보가 태양광 봉지 문헌으로 배터리 난연성 전해질 조성과 다른 분야 |
| Q07 | 수처리 분리막 내오염 | **INSUFFICIENT_DIRECT_EVIDENCE** | 태양광 봉지 문헌만 반환; 수처리 분리막·내오염/여과 목적의 근거 없음 |
| Q09 | 경량 고전도성 전력 케이블 | **INSUFFICIENT_DIRECT_EVIDENCE** | 태양광 봉지 문헌만 반환; 전력 케이블 경량 도체 특성 근거 없음 |
| Q10 | 생체흡수성 수술용 봉합사 | **INSUFFICIENT_DIRECT_EVIDENCE** | 태양광 봉지 문헌만 반환; 수술용 봉합사 인장강도·분해 속도 근거 없음 |

- 이 6문항 **실제 어댑터 완료 실행 분모**: NAS `search_patents` **12회(각2)**, `get_patent` **18회(각3)**, WIPS **0회**; 모두 최종 판정을 실제 반환. 독립적인 **진단용 사전 검색 12회 + 상세18회**는 본 어댑터 분모와 **별도**이며 전체 비용에서 생략하지 않는다.
- 직전 보고의 4문항 Q01/Q04=REUSE·Q05/Q08=HOLD와 결합하면 **10문항 최종 재사용 4/10, 보류 6/10**. 이 결과는 신규 10문항 모두를 이번 한 세션에서 처음부터 한 번에 돌렸다는 뜻이 아니다(직전 4문항 실측 재사용).
- 동등 질문의 두 번 검색에서 각3개 상위 문헌 및 근거 청크 식별값이 일치한 것을 확인. `sha256`은 반환 출처를 상호 대조한 것이며 **비공개 원문을 다시 받아 해시를 독립 재계산한 것은 아님**.
- AI reviewer는 관련 분야별 필요 목적/재료/작용을 정해 같은 문헌의 제목·요약·대표청구항에서 일치해야 `label=2`를 출력. `get_patent`의 실제 인용문이 같은 chunk 안에 존재하는지 코드는 검증. 의미·정량 성능·권리 상태가 외부 독립 검증된 결과라는 주장은 하지 않는다.

## 2. 단일 근거 섹션으로 인한 false HOLD 보강

- [어댑터 기능 보강](../../poc/eval02_live_read_adapter.mjs): `requiredFeatures?: string[]`(서로 다른 1~5 식별자), `review().featureEvidence?: [{feature, section, chunkSha256, quote}]` 선택. 복수 필수 조건이 청구항과 요약 **서로 다른 섹션에** 있어도 같은 문헌의 각 인용문·해시를 확인하고 승인할 수 있다.
- 필수 조건마다 evidence 슬롯 하나 이상이 아니라 **명시된 feature 정확히 한 개**를 요구; 누락·중복·가짜 chunk/hash·없는 인용문·다른 문헌의 인용은 `EVIDENCE_GROUNDING_FAILED`. 출력에는 feature 개수만 남겨 비공개 문장·키 유출을 방지.
- 과거 Q01의 **잘못된 보류** 원인: 봉지 시트는 대표청구항에 나오지만 '끝단'과 수분 침투 등 필요 속성은 요약에 더 상세하게 등장. 새 다중근거 방식으로 실제 NAS 질문 Q01 **3개 필수 속성 각각 연결**, `AI_REVIEWED_REUSABLE`, `verifiedFeatureCount=3`, `evidenceCitationMatched=true`를 재실행해 확인함. 실제 추가 실행: NAS search2, detail3, WIPS0.
- **주의:** 인용 문자열이 존재한다는 사실만으로 기술적 주장이 모두 사실/성능이 실증되었다고 의미하지 않는다. 기술적 관련성 2점 자체는 ChatGPT의 결론이며, 필수 속성의 실제 충족 여부를 재료·구조·공정·검증 범위로 분리 평가해야 한다.

## 3. 회귀·기능 검증

- [기존 재사용 판정기](../../poc/eval02_reuse_policy.test.mjs) **16개**, [개선된 live adapter](../../poc/eval02_live_read_adapter.test.mjs) **29개** = **합계 45개 PASS, Code Mode V8 실행**.
- 신규 6테스트: 여러 섹션의 조건별 인용 수용, 필수근거 누락·동일 feature 중복·비정상 식별자·위조 해시 차단, 반환에서 실제 근거문장 제거. 기존 오동작·무관/최신성·provider fail-closed 검증 유지.
- GitHub 최신 코드에서 소스 문자열을 불러와 JS 문법/도메인 로직을 V8 격리 실행했다. **Node.js 테스트 러너, GitHub Actions CI, NAS 운영 컨테이너 자동 기동·배포를 이번 차례에 실행한 것은 아님**.
- Code Mode에서 실제 NAS MCP 도구로 나머지6 + Q01 다중근거 1건의 성공·보류 E2E를 실행했다. **서비스가 이 정책을 자동 강제하는 방식은 여전히 미구현**; ChatGPT가 읽기 도구를 호출하면서 이 어댑터를 명시적으로 적용한 경우만 적용된다.

## 4. 의사결정 및 다음 작업

**한정 GO:** 6개의 기존 NAS 보유 문헌 중 이번 10문항의 **4개 질문**에서 AI 관련성 근거를 확인한 범위만 반복 조회에 활용. Q05·Q06~Q10은 NAS의 벡터 순위가 높아도 직접 근거 부족으로 답변·추천 HOLD. 최신 공보·권리 상태는 항상 별도 검증 필요.

**ROI INCONCLUSIVE:** 이번 live adapter가 WIPS 호출 0이라는 사실은 별도 비용·요금 절감비율을 실측했다는 의미가 아니다. WIPS COLD 동등 비교, 응답시간·요금 계측, 전체 patent-family/legal 판정 미실시.

**다음 우선순위:** 운영 자동 연결을 시작하기 전 입력 질문의 필수 feature/부정요건 정의·선별되지 않은 인용/근거 오류 방어 및 출처·계약·성능 게이트를 확인. 상시 서버 자동 라우팅, 새로운 WIPS 호출, NAS 권한·서비스·DB 구조 변경은 별도 단계로 제한. 사용자 human label 대기는 없음.

**정리:** `EVAL02_TEN_CASE_AUDITED`, `AI_REUSE_4_HOLD_6`, `MULTISECTION_Q01_PASS`, `V8_CONTRACT_45_PASS`, `NAS_SERVER_UNCHANGED`.
