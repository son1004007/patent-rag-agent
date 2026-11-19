# ChatGPT 개인 NAS RAG 플러그인 E2E 실측 — 2026-11-19

## 판정
PASS — ChatGPT 개인 플러그인의 실제 저장(최초 INSERT), 조회, 벡터 검색, 중복/덮어쓰기 거부 및 synthetic namespace 검증. 사용자 등록 완료 보고 후 현재 ChatGPT의 NAS RAG 도구 3개 직접 호출. 개인 플러그인 목록에서 USER / PRIVATE 확인(동일 계정 WIPS도 존재). 실제 WIPS 자료는 호출·저장하지 않았으며 양 플러그인 연계 검증은 별도.

## 검증 기록

| 검사 | 실제 결과 |
|---|---|
| get_document(DEMO-P1) | found=true, 기존 본문 및 E5 model_id 확인 |
| search_documents(바닷물 환경에서 케이블 부식을 방지하는 내식성 소재, limit=3) | P2/P1/P3, cosine distances 0.1162846421 / 0.1832400779 / 0.1840346212 |
| save_document(DEMO-P1, 기존 허용 본문) | created=false (중복 방지) |
| get_document(DEMO-S1) | found=false (합성 특허 scope 외 ID) |
| save_document(DEMO-P1, 변경된 합성 본문) | INVALID_ARGUMENT: Only exact synthetic fixtures are allowed; 후속 get 원문 유지 |
| get_document(DEMO-P4), insert 전 | found=false |
| save_document(DEMO-P4, 허용 본문) | created=true, 실제 E5 embedding/INSERT |
| get_document(DEMO-P4), insert 후 | found=true, 본문 일치 |
| search_documents(태양전지 모듈의 투명 봉지재로 습기 침투를 방지하는 기술, limit=3) | P4/P3/P1, cosine distances 0.1070144240 / 0.1732530347 / 0.1870612725 |
| save_document(DEMO-P4, 동일 본문 재요청) | created=false (중복 방지) |

신규 합성 문헌 P4: "가상 문헌: 태양광 발전 모듈의 봉지재 내습성과 광투과율." 최초 INSERT 증명을 위해 기존 allowlist에 이 한 건만 추가. 실제 문서 자유 저장 권한은 열지 않음. 검색값은 cosine distance이며 1-distance는 정규화 임베딩 cosine similarity이지 정답 확률 아님. 4개 fixture에 대한 소규모 기능 시험이지 실제 특허 품질 평가 아님.

## 구현·NAS 확인
- [서비스 코드](../poc/stage_service.py) commit `f269892012dae97687e5bccd7750e2946111bf15`: P4 exact fixture 한 건 추가. API 컨테이너만 순차 restart, 기존 버전과 diff/구문 검증, 이전 파일 백업 및 실패 시 이전 버전 복귀 경로. DB/relay/tunnel/preview 변경 없음.
- Gateway job `job_01M7S445KZ00CE8KD3HVJBNTRJ` succeeded: ALLOWLIST_ONLY_CHANGE_PASS, 기존 16/16 HTTP 회귀 PASS, DB 3건/P4 0건 (ChatGPT 저장 전).
- Gateway job `job_01M7S46HPW00KTGZ5DE8PZRKC0` succeeded: DB 4건, DEMO-P4 384차원 E5 모델 ID 확인, DB/API/relay/tunnel/preview running, published ports=0, DB_POSTCHECK_PASS.
- 개인 플러그인 등록 및 실제 도구 호출 PASS. 별도 GPT 모델 API 호출 없음(ChatGPT 구독 사용); 비용 절대 0 보장 아님. 모델 API 과금과 tunnel runtime key 분리. 기존 기술사 DB/실자료 미마운트, WIPS 권리 제한 및 사용자별 OAuth 미구현 상태 유지. NAS 전체 재부팅 자동 기동 및 운영 SLA/대규모 데이터/실제 공용 DB 미검증. 기존 세 개 데이터 시점의 backup/restore 검증과 이번 네 번째 문헌 생성은 별개이며 최신 dump 재생성/복원은 향후 작업.

## 다음
[작업 목록](../TASKS.md) 기준: 실제 운영 공용 DB의 별도 DB/role·백업 복구 및 기동 순서 검증, 합성 자료 기반 WIPS+NAS RAG 연계 흐름(실자료 저장권/전송권 확인 전 차단); 운영용 자유 문서 ingest 및 정책은 별도 설계. 중앙 user action #24의 personal tunnel/등록/read/write E2E 조건 충족. 외부 공유 금지.