# WIPS + NAS RAG 동일 대화 연계 — 2026-11-19

## 판정
**PASS: 현재 ChatGPT에서 두 개인 MCP를 순차 호출하는 읽기 연계, 합성 문헌 idempotent save, fail-closed 정책 17/17 단위 시험.** 실제 WIPS 원문/서지/응답의 NAS 전달·적재·임베딩, 상업 운영, 자동 ingest, 통합 순위의 품질은 미검증/금지. 기존 서비스 재기동 없음.

## 실측
- WIPS 검색식: `(태양광 태양전지).ti. AND (봉지재 봉지).ti.`, 처음 3건 한정, 필드 SKEY,XN_D,CC,KC_D. 실제 반환 구조 data.row_list 배열 3개, 각 식별 필드 문자열. 원래 응답/실제 식별자/특허 내용은 GitHub·NAS에 기록하지 않았다. 한 번만 호출, 상세 원문 호출 없음.
- 독립 작성된 일반 주제 `태양광 모듈 봉지재의 내습성과 광투과율`로 실제 NAS search_documents(limit=3) 시행. scope=synthetic_candidates_only, 3건, Top1 DEMO-P4, cosine distance=0.07150849913085955. WIPS 응답에 유래한 데이터를 NAS 요청에 넣지 않았다. get_document(P4) found=true; 기존 허용 합성 본문 동일 save created=false. 새로운 문헌 생성 없음.
- 실데이터 공급자 반환과 합성 검색 결과를 비교 가능한 동일 척도로 보지 않고 분리한다. 동일 대화 내 도구 순차 연계이며 WIPS 자동 원문 가져오기/실제 데이터 전달의 종단간 시험이 아니다. 별도 모델 API 직접 호출 없음.
- 오케스트레이션 참조 [코드](../poc/dual_search_policy.mjs) commit `7fa6042678fde3e32beec82855542ca918c84b4f`; [테스트](../poc/dual_search_policy.test.mjs) commit `eaf419dc383d65a6b7cbcb6e7d705205ebed8c8d`.
- ChatGPT 격리 JS 실행기에서 동일 함수 및 ledger 17/17 PASS: 고정 fixture만 허용, WIPS/unknown/self-asserted approval/변조/누락/프로토타입 ID 거부, 쓰기 인수 최소화, 순차 호출 및 외부 sentinel 미전송, 한쪽 오류시 다른 쪽 안전 조회, scope/unknown ID/상한/NaN 거부. mock callbacks로 실행; 커밋된 Node 파일 자체를 Node로 실행하지 않았으며 MCP에 통합·배포하지 않았다. 실제 저장 방어는 기존 NAS 서버의 exact fixture allowlist로 별도 유지.
- 재현: Node.js 호환 환경에서 `node poc/dual_search_policy.test.mjs` (별도 의존성 없음; 이번 Node 실행 NOT RUN).

## 공급자 비용·권리
2026-11-19 공식 확인:
- [WIPS 2026-10-12 베타 공지](https://www.wipscorp.com/news-view?id=265): 베타 기간 윈텔립스 고객은 무료, WIPS DB 호출비 없음, AI 플랫폼 토큰/크레딧 별도 소진. 정식 출시 시 가격/범위/대상/기간 변경 가능. 개별 계약 및 청구 내역은 미검증.
- [공식 MCP 이용 안내](https://docs.channel.io/wips-lounge/ko/articles/wintelips-mcp-7f649324): AI 앱에서 검색·분석 제공, 연결된 AI 플랫폼이 자체 데이터 처리 정책 결정. 기존 계약 외 독립 서비스의 외부 DB 저장/임베딩/재배포를 허용한다고 명시한 근거는 확인하지 못함.
- 기본 정책 유지: WIPS 검색 결과의 NAS 전송/원문·요약·서지 보존·벡터화는 명시 승인 전 금지. metadata라도 예외를 추정하지 않음. 별도 공개 데이터는 출처·라이선스·가공/저장/외부 반환 권리를 자료별 확인 후 신규 corpus 허용 정책을 설계한다.

### 공급자 확인 요청 항목 (미발송)
WIPS 담당자 또는 help@wips.co.kr에 다음 권리와 조건을 서면 확인: (1) 독립 내부 RAG DB 내 문헌번호/서지/원문/요약의 저장 허용 범위·보존 기간, (2) 임베딩 및 벡터 검색·재활용·삭제 조건, (3) AI 플랫폼과 내부 서비스 전송/사용 범위, (4) 사내 여러 사용자·고객 제공/상업적 이용, (5) 정식 MCP 요금, 호출 제한, 독립 클라이언트 인증 및 서비스 SLA. 확인 전 기존 계약 제한 유지. 이번에 문의 이메일을 발송하지 않았다.

## 다음 단계
권리 승인과 독립적인 합성/권리 명시 자료 전용 ingest 설계, 문헌 출처·정책·버전 및 원문 해시 provenance, chunk/embedding, 중복/충돌/거부 및 평가를 격리 시험한다. 실제 NAS 서비스 업데이트/재기동은 사용자 HOLD 상태를 유지하고, 기존 기술사 영속 배포 차단도 우회하지 않는다.
