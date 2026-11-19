# 실제 특허 읽기 전용 MCP 검증 — 2026-11-19

## 판정
**PASS — NAS 로컬 실제 HTTP MCP 23/23.** 사용자 구매·내부 적재 지시에 따른 실제 특허 3건/10청크 대상으로 검색과 개별 조회를 시험하였다. 기존 컨테이너/터널은 재기동·변경하지 않았다. 이 읽기 전용 후보의 ChatGPT 개인 플러그인 연결과 외부 반환은 아직 NOT RUN.

## 코드와 실행 근거
- [읽기 전용 MCP](../poc/private_patent_reader.py) — commit `295c631bdc9876f426d0a26baeea833fbd6b790f`.
- [HTTP 및 권한 회귀 테스트](../poc/private_patent_reader_test.py) — commit `1194430ec946641252489f28937f8f67c0932920`.
- [읽기 전용 role/view SQL](../poc/private_patent_reader.sql) — commit `43d08ef52036ed9b69a8c1af2560e5249b3413a0`. PG16 공식 [CREATE VIEW](https://www.postgresql.org/docs/16/sql-createview.html), [ALTER ROLE](https://www.postgresql.org/docs/16/sql-alterrole.html), [privileges](https://www.postgresql.org/docs/16/ddl-priv.html) 참고.
- Gateway `job_01M7S76WCK00RPJ6AQRERR5WG1` succeeded: PINNED_SOURCE_AND_NEW_SECRETS_PASS; 신규 role 및 security-barrier views 생성, 실제 3건·10청크 확인, 기존 합성 역할의 실제 DB CONNECT 금지 검증, 기존 StartedAt 일치.
- Gateway `job_01M7S78C9700AWK9WQHTX8YHDW` succeeded: 실제 E5 모델과 pgvector에 연결한 임시 격리 worker에서 새로운 loopback HTTP 포트(외부 포트 publish 없음) MCP 서버 구동·시험 후 정리. PRIVATE_READER_MCP_PASS checks=23, SEARCH_LATENCY_MS 87.15, EXISTING_SERVICES_UNCHANGED_AND_TEST_CLEANUP_PASS. 기존 합성 4건/실제 특허3건 유지. 결과 로그에는 테스트명과 수치만 출력.

## 기능
- search_patents: 1~200자, 최대 3개 문헌, cosine distance의 문헌별 최선 chunk를 기준으로 exact ranking, 중복 제거, 출처·문헌번호·제목·해당 근거(최대300자)·해시와 offset 반환. HNSW를 사용한 ANN 벤치마크가 아닌 소량의 exact query이다.
- get_patent: 개별 ID 정규식 검증 및 문헌 정보/최대 3개 근거(각300자) 반환. 원문 전체, SKEY, 내부 source_payload와 embedding의 API 반환 금지. chunk_sha256은 **원래 전체 청크** 해시이며 표시용 발췌문 자체의 해시는 아니다.
- 새로운 reader role은 지정 DB/view SELECT만 부여. 기본 트랜잭션 읽기 전용 및 statement_timeout 5s, 별도 bearer, 인증/Host/Origin/크기 검증. 실제 원본 documents/chunks 직접 SELECT 및 UPDATE와 합성 DB 교차 접속 거부. SQL role에서 view의 벡터 열은 읽을 수 있으나 MCP는 반환하지 않는다. 다른 모든 클러스터 DB 및 반복 발췌에 의한 원문 재구성 방지는 별도 검증 필요.

## 23개 검증 항목
인증 5개(missing/wrong token, bad host/origin, oversize), initialize, read-only tool catalog, 미등록·foreign ID, invalid query/limit, scope, distinct 3개, bounded evidence, distance order, exact fetch, evidence scope, raw payload absent, role default readonly, raw source/chunk denied, write denied, cross domain denied.

87.15ms는 태양광 봉지재 관련 단일 테스트 질의의 NAS 로컬 HTTP 응답시간이며 모델 로딩, ChatGPT/tunnel 통신, 대규모 품질/부하 검증이 아니다.

## 남은 조건
- 기존 synthetic MCP 및 개인 tunnel은 그대로 유지. 임시 reader 컨테이너는 정리했고 신규 외부 연결이나 상시 reader 서비스는 미설치. 실제 검색을 ChatGPT에서 사용하려면 별도 승인된 private channel/도구 등록 또는 재기동 보류 해제 후 검증된 서비스 통합 필요. 사용자별 OAuth·반복 요청 제한·외부 반환 권한/공급 계약 범위 별도 확인.
- 실제 자료 다중 배치, 상세설명/전체 청구항, 실자료 dump 복원, hybrid/relevance 품질 검증 남음. 기술사 배포 차단 우회 및 기존 서비스 재기동 금지 유지.
- [목표 서비스 흐름](../README.md)은 commit `cf119253b42f96158311d190712a01fe05daa39e`에서 추가. 실제 구현 범위와 목표는 구분.
