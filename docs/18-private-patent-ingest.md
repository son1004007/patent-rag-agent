# 구매 특허 자료 전용 적재 — 2026-11-19

## 사용자 결정 및 범위
사용자가 특허 자료를 유료로 확보했다고 밝히고 실제 적재를 명시 요청했다. 이를 근거로 개인 NAS 내부 연구용 소량 적재를 진행했다. 공급계약 원문/재배포/상업 이용/대량 동기화 권리는 검증하지 않았으며 확대 해석하지 않는다. WIPS [데이터 상품 안내](https://docs.channel.io/wips-lounge/ko/articles/wips-ip-data-purchase-efd789d7)는 서비스 이용과 별도 구매, 데이터 활용 범위의 차이를 설명한다. 기존 기술사 배포 차단과 NAS/기존 컨테이너 재기동 금지 유지.

## 실제 결과 — PASS
- WIPS 조회: 직전 시험과 동일한 태양광·태양전지 봉지재 검색식, 상위 3건, SKEY/XN_D/CC/KC_D/TIK/ABK/CLK. 실제 특허 3건, 제목·요약·대표청구항 포함. 상세설명/전체 청구항/PDF 미수집. 공급 응답 및 원문, 문헌 식별자는 공개 repo/결과 로그에 기록하지 않음.
- [적재 worker](../poc/private_patent_ingest.py), commit `777f8269441c4a472e885f4aa4be463208be2a78` / blob `9f0be1e44afc613c9520f13e7a68740b94448ccb`. 기존 PostgreSQL 인스턴스에 별도 private DB, 전용 writer role, 제한된 schema, SELECT/INSERT-only; PUBLIC CONNECT 차단, 기존 합성 patent_app의 신규 DB 접근 차단. 동일 pgvector 엔진, 기존 E5 로컬 모델 사용. 원문 필드 JSON, SHA256, 정책 ID, 문헌키, section/offset/chunk hash/model ID 저장. 최대 3건, 450-token chunk cap, L2-normalized E5, HNSW 인덱스. 일회성 격리 worker의 외부 port 0, 기존 DB network namespace만 사용.
- Gateway preflight `job_01M7S5XP33005N8H8GTTZSMY6X` succeeded; dedicated schema `job_01M7S61RWR00JXH0YV5T1C9HM2` succeeded. 첫 실행 `job_01M7S63KQB00VEHTGBB254KXC1`은 wrapper가 0건을 성공으로 반환한 결함으로 **FAIL**, 입력 전달 진단 `job_01M7S65Q8H00Z1JJM8ZEAMWBX1`에서 빈 worker 확인. 선행 docker exec -i가 소스 표준입력을 소비한 원인 수정. `job_01M7S6792700GR9QZYVT0MN7WC`에서 git blob SHA 일치, 7404바이트 및 컴파일 검증. 재실행에서는 작업 전 입력을 비공개 임시파일로 먼저 수신하고 worker 성공 marker/DB 건수를 강제 검증.
- 최종 `job_01M7S68VXK00ED08PJQJ05TBHW` terminal succeeded: created_documents=3, created_chunks=10, duplicate_created=0, total_documents=3, total_chunks=10, vector_dimension=384, search_candidates=3, cosine best_distance=0.13506784632599467, cross_db_denied=true, update_denied=true, PRIVATE_PATENT_INGEST_PASS. 별도 SQL 실측 10|384, 신규 dump 30,640 bytes, 기존 synthetic DB 4건 유지, 기존 컨테이너 StartedAt 일치, 일회성 worker 정리 확인. 실데이터 dump 복원은 아직 NOT RUN.
- 실제 자료는 NAS 전용 private DB에 보존. 기존 NAS RAG 플러그인은 여전히 synthetic-only이고 신규 코퍼스 접근/외부 반환을 제공하지 않음. DB/서버 재시작, tunnel 설정 변경, 기술사 자료 변경 없음. 새 worker는 배포된 상시 MCP 도구가 아닌 일회성 실행. 현재 worker postcheck는 초기 배치 총량을 가정하므로 다중 배치 자동 적재 전 수정 필요. 외부 AI 리뷰 NOT RUN(선택).

## 다음
1. 별도 DB의 읽기 전용 MCP 연동 후보와 권한/응답 범위 검증, 기존 서버 무중단 조건 유지. (현재 ChatGPT NAS RAG에서 실제 자료 검색 불가)
2. 상세설명/전체 청구항 수집 및 다중 배치 ingest, 중복·충돌/문서별 정책/취소·보존·백업 복구 검증.
3. 계약 범위 확인 후 규모 확대. 실제 자료는 공개 GitHub/다른 사용자에게 제공하지 않는다.
