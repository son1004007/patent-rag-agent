# AGENTS.md

## 필수 읽기 순서
전역 Control(접근 가능시 son1004007/ai-agent-workflow-playbook/CONTROL.md 및 registry) → 이 파일 → DOC_INDEX.md → AI_CONTEXT.md → CURRENT_STATE.md → TASKS.md → 관련 문서·최신 commit/PR/실행 증거.

## 문서화 규칙 (필수)
- 모든 신규/이동/삭제 Markdown 문서는 같은 변경에서 DOC_INDEX.md의 링크·한 줄 용도를 갱신한다. 하위 INDEX도 상위에서 연결한다.
- 비개발자용 사업 설명서와 개발 설계서는 분리하되 중요한 흐름·정책 변경은 함께 갱신한다.
- 업무 흐름, 데이터 흐름, 역할 및 의사결정은 GitHub에서 렌더되는 Mermaid 도식과 쉬운 설명을 사용한다. 색상만으로 의미를 전달하지 않는다.
- 각 문서는 목적·대상·상태를 명시한다. CURRENT_STATE/TASKS가 상태 정본이며 인덱스에는 진행률을 중복하지 않는다.
- 문서 인덱스 누락/깨진 상대 링크 검사를 CI에 추가한다.

## 보안 및 구현
공개 repo에는 일반화된 개인 PoC 설계·합성 fixture만 허용한다. 고객 소스·연구 내용·내부 네트워크·credential은 기록하지 않는다. 외부 저장/embedding/LLM 전송/공유는 허가 확인 전 기본 금지. IP 제어는 운영자의 외부 네트워크 장비 책임; NAS에서는 HTTPS와 인증, 서비스 격리 유지. 운영 승인·실행 증거 없는 완료 주장은 금지. 독립 AI 검토는 아래 프로젝트별 최신 사용자 결정에 따라 선택 사항으로 처리한다. 공용 저장소를 기존 trusted runner에 임의 연결하지 않는다.

## AI 모델 선택
2026-11-19 사용자 결정: AGY/Gemini 사용 금지. ChatGPT/Codex 중심으로 진행한다. 독립 AI 검토는 선택 사항이며 미실행만으로 main 병합 또는 배포를 막지 않는다. 사용자 재승인 없는 AGY/Gemini 자동 호출 금지.

## 배포 우선 반복 개발 (2026-11-19 사용자 결정)
- 적용 범위: 이 개인 PoC 프로젝트. 기존 독립 검토 필수 게이트와 REVIEW_DEBT 병합/배포 보류 규칙을 대체한다. 별도 AI 리뷰 없이도 개발 및 배포를 진행한다.
- 기본 흐름: 작은 기능 구현 → 필수 최소 점검 → 커밋/병합 → 시범 배포 → 실제 환경 테스트 및 사용자 피드백 → 수정/재배포 → 상태/목차 갱신.
- 사전 전체 테스트와 독립 리뷰를 대기하지 않는다. 단, 빌드/기동·실행 가능성, 비밀 노출/권한/데이터 손상 위험, 복구 가능성은 기능에 맞게 최소 점검한다. 외부 공개 전 HTTPS·인증·외부 네트워크 접근 통제 확인 및 DB 비공개를 유지한다. 확인된 중대한 취약점이나 데이터 계약 위반은 공개하지 않는다.
- 미실행 외부 AI 리뷰는 NOT RUN (owner-approved optional)로 명시한다. 실제 테스트 없이 성공 또는 완료를 주장하지 않는다. 실패 시 이전 정상 버전 복구 또는 시범 경로 차단.
- 실제 고객 자료·제공자 연동 권리·유료 호출·외부 노출의 승인 경계는 별도이며 이 결정으로 완화되지 않는다.

## 2026-11-19 MVP 화면 우선
전체 기능 구현 전 정적 화면 시안을 NAS의 격리된 사설 HTTPS 경로에 배포하고 사용자가 구성/흐름을 확인한다. 가상 자료와 현재 브라우저 탭의 메모리만 사용한다. 실제 API/DB/AI/계정 기능은 미연동으로 표시한다. 화면 승인 및 개선 의견 반영 이후 실기능을 단계별 구현한다. 실제 구현이 완성된 뒤 간결한 사용자 설명서와 관리자(설계·운영) 설명서를 추가한다. 기존 사업 설명서는 재작성하지 않고 설계 참고로 유지한다.

## 2026-11-19 최신 MCP 우선 결정
README의 목표 설계가 현재 우선이며 기존 웹 AI Agent 설계는 대체안이다. 먼저 독립 synthetic-only MCP 도구(저장/조회/검색), 계정·터널·권한 검증. 기존 기술사 pgvector/임베딩 자산 재사용은 별도 DB/서비스 역할과 cross-domain 거부 테스트, 백업/복구 확인 전 실제 공유 금지. 기존 기술사 배포 차단을 우회하지 않는다. WIPS 권리 미확인 원문/벡터 저장 금지. 실기능 확대 및 설명서 작성은 앞선 검증 후 진행.

## 2026-11-19 최신 사용자 결정 — 개인 MVP 우선
[TASKS.md](TASKS.md)의 MVP-01~06이 실행 순서 정본이다. 개인 ChatGPT의 기존 WIPS/NAS RAG 연동으로 실제 연구 질문 → 검색 → 허용 자료 수집·증분 적재 → 기본 근거 기반 비교/추천 → 재사용을 먼저 실증한다. 정적 웹 확인·별도 Agent/UI·고급 Hybrid/Reranking·공용 DB 운영 전환·관리 기능·기업 구축/SSH는 MVP 이후 backlog이며, 기업 작업은 별도 착수 승인 전 하지 않는다. 이전 화면 우선 지시보다 이 최신 순서를 우선하되 시안은 보존한다. NAS/기존 컨테이너 재기동 금지 유지: MVP-01 운영 전환이 보류되면 MVP-02 이후의 비파괴 구현/격리 시험을 수행한다. 기존 승인·보안·계약·실제 실행 증거 요구는 그대로 유지한다.

## 2026-11-19 최신 승인 — 특허 MCP API 단독 전환
사용자 명시 승인으로 특허 MCP API 컨테이너만 재시작 및 통합 운영 배포 완료(56/56). [실측 및 Refresh 절차](docs/24-mvp01-production-cutover.md). 이전 전체 재기동 HOLD 중 이 단독 전환만 예외이며 NAS/DB/relay/tunnel/다른 서비스 재시작과 자동 시작은 별도 승인 대기. 기존 플러그인 유지, 신규 도구 Refresh/새 대화 실제 읽기 E2E PASS. 실제 rollback 및 쓰기 adapter 미완료. 기업 및 기술사 운영 변경 금지 유지.

## 2026-11-20 최신 사용자 결정 — 운영 우선 적용
개인 patent-rag-agent의 작고 되돌릴 수 있는 승인 범위 변경은 최소 사전 점검 및 필요한 백업 후 운영에 바로 반영하고 실제 기능 및 변경 전후 무결성을 검증한다. 이미 검증한 격리 시험을 이유 없이 반복하지 않는다. 문제가 있으면 새 경로 중지 또는 안전한 복구, 이후 GitHub 상태와 증거를 갱신한다. 기존 재시작·자동 기동·타 서비스·권한 확대·외부 공개·계약/유료 호출 승인 제한은 유지한다. 운영 반영 지시는 미확인 자료의 지속 수집 승인으로 확대하지 않는다. 독립 AI 검토는 기존 선택 사항.

## 2026-11-20 사용자 승인 — WIPS 메타데이터 자동 저장 상한
WIPS 검색 반환 서지정보를 개인 NAS에 지속 보관하는 것을 사용자가 허용했으며 **검색당 최대 100건**으로 정정했다. 기존 50건 제한보다 최신 지시를 적용한다. 범위는 서지 7개 필드, 첫 페이지 100건 이내, 원문·벡터·PDF/도면 자동 저장은 제외. 실제 운영 83건 저장 및 동일 결과 재사용 PASS [실측](docs/39-mvp-archive-100-live-acceptance.md). 독립 계약 증빙은 user-confirmed/not-independently-verified. 임의 WIPS 플러그인 호출이 NAS에 자동 반영되는 hook은 아직 미구현으로, 별도 사용자 재확인 없이 백그라운드 자동 수집이 동작한다고 주장하지 않는다. 신규 비용·재배포·무단 증분 페이지 수집 금지.

## WIPS 도구 제공 범위와 구현 상태
[WIPS MCP 28개 도구 카탈로그](docs/40-wips-mcp-capability-catalog.md)에서 도구별 반환 데이터, 실제 응답 확인/정의 확인 구분, PDF 파일·NAS 로컬 벡터 분리 및 구현 갭을 확인한다. 구현 상태와 우선순위의 정본은 CURRENT_STATE/TASKS. 단순 MCP 도구 노출을 앱 기능 완료로 판정하지 않는다.

## 2026-11-20 P0 작업별 상세 설계·실행 문서 진입 규칙
특허 MCP·공보 PDF·본문/벡터·전체 원문·MVP 인수 관련 구현을 시작할 때는 최신 TASKS/CURRENT_STATE를 확인하고 **[P0-1~P0-5 설계/계획 인덱스](docs/mvp-implementation/INDEX.md)**에서 **해당 작업의 설계서와 실행 계획서를 둘 다 읽는다**. 실제 코드와 운영 환경은 별도 최신 Source of Truth로 확인한다. 명세에 제안된 신규 파일/권한/공급자 API는 아직 생성·실증되었다고 가정하지 않는다. 각 설계의 사전 위험과 Stop/Go/수용 테스트를 구현 전에 확인하되 사용자 최신 '작은 변경 → 최소 점검 → 운영 반영 → 실제 테스트' 원칙을 유지한다. 문서화만으로 코드·운영 검증 완료를 주장하지 않는다.

## 2026-11-20 최신 P0-1 실제 WIPS 검색→NAS 저장 작업 규칙
사용자가 이 특허 RAG 맥락에서 WIPS 특허 검색·서지 자동 저장을 요청하면 [MVP41 ChatGPT Code Mode→NAS 안전한 단일 실행 경로](docs/42-mvp41-code-mode-gateway-archive.md)와 [P0-1 설계·계획](docs/mvp-implementation/INDEX.md)을 확인한다. 현재 WIPS plugin + Gateway 승인 owner-local stdin wrapper로 WIPS 첫 페이지 최대100건을 검색해 NAS 보관하고, 검색 성공과 보관 verified 결과를 별도로 확인한다. 임의의 독립 WIPS MCP 호출을 자동 가로채는 플랫폼 hook은 미구현. WIPS 키/원문/공보 PDF/벡터 수집·새 외부 서버/리더 권한 확대 금지, 예상 실패 시 우회나 조용한 새 provider 검색 재시도 금지. **WIPS MyFolder 플러그인·폴더 연동 개발만** 사용자 재요청 전 중지한다. 기존 WIPS 검색 MCP와 NAS RAG의 승인된 P0 후속 개발은 계속 진행한다.

## 2026-11-20 최신 평가 우선순위 및 다른 AI 진입점
개인 특허 RAG MVP 1차 기능은 범위 한정 실증 완료했지만 WIPS 단독 대비 **실제 효용**은 미판정. 다음 우선작업은 [평가 인덱스](docs/evaluation/INDEX.md) → [DECISION-01 판단 기준](docs/44-mvp-evaluation-decision-criteria.md) → [EVAL-01 검색 품질 비교 계획](docs/45-search-quality-comparison-plan.md) → [EVAL-02 반복 재사용 가치 계획](docs/46-reuse-value-verification-plan.md). WIPS만/기존 NAS만/통합의 corpus·후보 예산·근거 차이를 구분하고 ChatGPT AI 근거 판정(독립 사람 판정 아님) 및 실제 WIPS 호출 vs counterfactual 절감 수치를 분리한다. 실제 질문·특허ID·원문·SKEY/credential은 공개 repo에 저장 금지. **후속 AI 평가·EVAL-02 warm 리플레이 실제 수행, 사용자 #31 평가는 최신 지시로 취소됨.** MyFolder HOLD, 재시작·신규 수집·비용 정책 변경 없음.


## 2026-11-20 사용자 최신 WIPS AI 검색 조건 — 설명 300자 이상
WIPS 일반 키워드/Boolean 검색식(`get_patent_search_onlyengine`)과 AI 유사 검색(`get_patent_ai_search`)을 구분한다. **AI 유사 검색**의 기술 입력은 사용자가 제공한 목적·배경·소재·공정·제외 조건을 구조화하여 **가능하면 300자 이상** 준비하고, 임의의 수치/기능/고객 비밀을 창작하거나 반복 문장으로 분량만 늘리지 않는다. 근거가 부족해 300자를 못 채우면 SHORT_INPUT으로 표시하고 필요한 내용을 확인한다. 출처가 없는 '300자 정확도 보장' 주장은 하지 않는다. EVAL-01 실제 A/B는 [장문 대 단문 비교](docs/evaluation/2026-11-20-eval01-wips-ai-300char-ab.md)에서 확인. 10문항 KR-only/Top3 AI 자체 채점: 6/30→8/30, U 노이즈13→0, 사람 판정은 미완료. 실문헌/고객 자료 공개 GitHub·무승인 원문 적재 금지. MyFolder HOLD 계속.

## 2026-11-20 최신 사용자 결정 — AI만으로 EVAL-01/02 품질 채점
사용자는 **'사람 검증 안해. 니가 다해.'**라고 명시했다. 개인 특허 RAG PoC의 검색 후보 관련성0/1/2, 요약/대표청구항·기존 NAS 근거 확인, 검색 질의 정밀화, 반복 재사용 여부 평가는 **ChatGPT가 직접 실행·자체 검증하고 기록한다. 사용자/전문가 gold-label 수집을 필수 선행 작업으로 만들거나 사용자에게 반복 채점을 요구하지 않는다.** 앞선 평가 계획의 '사람 라벨 필수'·중앙 #31 사용자 피드백 게이트와 충돌하면 이 최신 결정을 우선한다. 다만 자체 AI 평가임을 `AI_REVIEWED`로 명시하고 독립 사람 평가/전체 원문 대조/법적 확증을 수행했다고 주장하지 않는다. 실측 없는 금전·지연·정확도 우위 주장도 금지. 기존 제공자 계약/기밀/신규 수집·DB/권한·재시작·MyFolder HOLD 경계를 변경하지 않는다. 최신 결과: [실패 문항 재작성](docs/evaluation/2026-11-20-eval01-targeted-query-rewrite.md) → [EVAL-02 10문항×2 NAS 리플레이](docs/evaluation/2026-11-20-eval02-warm-nas-replay.md). 제한적 재사용 `AI_REVIEWED_LIMITED_GO`, 통제 COLD ROI `INCONCLUSIVE`.

## 2026-11-20 최신 EVAL-02 NAS 읽기-only 재사용 판정 적용
[실제 Code Mode 검증](docs/evaluation/2026-11-20-eval02-live-read-adapter-acceptance.md): [`poc/eval02_live_read_adapter.mjs`](poc/eval02_live_read_adapter.mjs)이 기존 `eval02_reuse_policy.mjs`를 연결해 동일 질문 search2 → 상위 최대3 상세 근거 → ChatGPT AI review callback → 출처/인용 실제 일치 확인 뒤 REUSABLE/HOLD를 반환한다. 사용자 별도 채점 불필요. Q01/Q04 REUSE, Q05/Q08 HOLD, 최신성 플래그는 읽기0으로 차단; 합성39 PASS(Code Mode V8). 이 코드는 **이미 연결된 NAS 도구를 ChatGPT Code Mode에서 명시적으로 조합한 것**으로 NAS MCP 서비스 자동 배포·전역 플러그인 자동실행이 아니다. 고객 원문을 별도 AI에 넘기거나 WIPS·운영 DB 새 쓰기·재시작·권한 변경은 금지.

## 2026-11-20 최신 EVAL-02 전체 10문항 AI 근거 재사용 완료
[10문항 실경로 결과](docs/evaluation/2026-11-20-eval02-full10-feature-grounding.md): 기존4문항+새6문항의 실제 NAS read-only 검증으로 AI 관련 재사용 Q01~Q04 **4/10**, 필수 근거 미충족 Q05~Q10 **6/10 HOLD**. 기존 대표청구항만의 제한으로 Q01 false HOLD를 낸 것을 해결하기 위해 [live adapter](poc/eval02_live_read_adapter.mjs)에서 `requiredFeatures` 및 청구항/요약 **다중 인용 출처 필드**를 검증한다. 실제 Q01 3요구조건 재확인 PASS, 기존 테스트16+adapter29=**V8 격리계약45 PASS**. 모든 신규 코드/예비 평가의 자동 NAS 운영 서비스/플러그인 적용은 아직 미구현, 외부 human-gold는 사용자 최신 결정으로 필수 아님. 비용·권리·원문 재적재 관련 보안 조건 유지.

## 2026-11-20 EVAL-03 ChatGPT 내 NAS 우선/WIPS 보완 라우터
[실제 두 경로 인수](docs/evaluation/2026-11-20-eval03-on-demand-nas-wips-router.md) 및 [Code Mode 라우터](poc/eval03_patent_router.mjs). Q01은 NAS 재사용(검색2·상세3/WIPS0), Q06은 NAS 직접 근거 부족 시 WIPS 검색(검색2·상세3/WIPS1). 기존 16+29+새14=**V8 계약59 PASS**. WIPS 키 이동·서비스 권한·원문/PDF/벡터/서지 쓰기·재시작 없이 기존 두 MCP를 ChatGPT에서 명시적 조합. NAS 벡터 top3는 **정확한 전체 문헌 보유 여부 증거 아님**; `INSUFFICIENT_DIRECT_EVIDENCE`에서만 WIPS 전환, 읽기 오류/불안정/인용 불일치는 HOLD. 서버 상시 단일 MCP 자동 등록은 **NOT RUN/NOT IMPLEMENTED**. 사용자에게 다른 채팅 전역 동작이나 고객사 연동 완료라고 주장하지 않는다.

## 2026-11-21 EVAL-03 화면 P0-2 선택 WIPS 특허 상세 조회

[읽기 전용 상세 조회 구현](poc/eval03_wips_detail.mjs) / [실제 시험](docs/evaluation/2026-11-21-eval03-p0-2-selected-wips-detail.md). 공개 문헌번호·국가·문헌종류로 `get_patent_spec_text(dtl_desc/all_claim)` 2회 호출, 동일 문헌 검증, 최대4000자 평문 페이지·nextOffset·전체 청구항 번호 조회. 코드 V8 88/88 계약 PASS, WIPS 실제 8개 청구항·상세설명 27923자·2페이지 조회 PASS. 기존 NAS/WIPS AI 분기 불변, 95% 미적용. 이것은 이전 대화의 **화면 P0-2**이며 전역 기존 P0-2인 공보 PDF 수집은 미완료. 새 MCP 도구 등록·NAS 운영 적용·원문 저장/청킹·고객사 배포 없음.

## 2026-11-21 EVAL-03 화면 P0-3 통합 검색·상세 결과 실검증

[공통 read-only 표시 구현](poc/eval03_unified_display.mjs)·[실제 NAS/WIPS 인수](docs/evaluation/2026-11-21-eval03-p0-3-unified-user-lookup.md). NAS 직접 근거가 충족되면 기존 구매코퍼스의 **검증한 문헌1건/최대3개 300자 발췌**만 공통 결과 형식으로 반환; WIPS 후보 top3도 같은 필드로 표시하고 선택 문헌은 기존 P0-2 spec-text 페이지로 상세조회. 실제 Q01 NAS search2/get3/WIPS0 및 Q06 NAS search2/get3/WIPS search1+spec2, WIPS 2페이지 이어 읽기 PASS. 기존16+29+25+18+신규18=**V8 106/106 PASS**, Node CI/운영 NAS·상시 MCP 배포 미실행. **화면 P0-3과 기존 P0-3 원문·벡터 자동 증분 적재는 별개**이고 후자는 미완료. AI 분기/95% 미적용/MyFolder HOLD/권한·서버·DB 불변.
