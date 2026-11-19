# MVP-02 — 실제 특허 상세 수집 및 증분 적재 검증 (2026-11-19)

## 판정
**PASS — MVP-02 로컬 DB 인수 기준 충족.** 개인 내부 사용을 위한 기존 실제 특허 3건의 상세설명·전체 청구항을 보강하고 신규 1건의 서지·제목·요약·대표청구항을 추가했다. 실제 WIPS 반환 자료를 NAS 전용 private DB에 저장했다. 기존 MCP 운영 서버, 터널 및 NAS 재기동 없음. ChatGPT 실제 특허 도구 연동/MVP-01은 여전히 HOLD.

## 데이터 처리
- [증분 적재 worker](../poc/private_patent_increment.py) commit `9004873b5d78b1b777bc0dc86095d930afb75601`, [추가 스키마](../poc/private_patent_increment.sql) commit `fac216142ac50381e52ecf21ae9135a5c653cf5d`.
- 기존 document identity/원문/해시·청크 보존. 상세설명과 전체 청구항은 별도 immutable section_sources(문헌 식별자, 섹션, provider, language, 원문 필드 JSON, source/body SHA256, claim_count, policy)로 추가; 기존 chunks의 허용 섹션만 확대. 문헌/섹션/offset별 chunk 및 384차원 L2-normalized multilingual E5 저장. 기존 read-only evidence view는 신규 청크를 조회할 수 있으나 section_sources 원문 직접 조회 권한은 없음.
- WIPS 상세 조회: 기존 3건에 대해 문헌별 dtl_desc, all_claim 및 ko 요청(KR), 실제 응답 언어 및 식별자 검증. 상세설명 총 61,407자, 청구항 10+15+7=32개(제공자 count 대조), 전체 청구항 직렬화 텍스트 5,646자. 설명/청구항 내용 및 식별자는 공개 GitHub에 저장하지 않음. 대표청구항/요약과 별도로 저장.
- 한 문헌의 상세 2개 섹션씩 3회 독립 트랜잭션 + 신규 1건 metadata 배치. 동일 입력 재적재 시 0건, 동일 identity/section에 변조된 본문을 입력하는 충돌 테스트 거부. chunk/model/dimension 및 검색 후보 확인. 기존 데이터 fingerprint와 각 컨테이너 StartedAt 검증. 수집 입력 임시 파일은 성공 후 삭제.

## 실행 증거
| 배치 | 신규 문헌 | 신규 섹션 | 신규 청크 | 누적 청크 |
|---|---:|---:|---:|---:|
| 초기 | 3 | 0 | 10 | 10 |
| 상세 보강 1 | 0 | 2 | 49 | 59 |
| 상세 보강 2 | 0 | 2 | 61 | 120 |
| 상세 보강 3 | 0 | 2 | 44 | 164 |
| 신규 metadata | 1 | 0 | 3 | 167 |

- `job_01M7S99EY500HJ6T7P6Y1M98WQ`: preflight 3건/10청크 및 기존 DB/서비스 확인.
- `job_01M7S9GXC300NNDQ47AH4E55TP`: 성공. 변경 전 backup 33,046 bytes; 스키마 적용, 기존 원본 fingerprint 및 접근권한 검증.
- `job_01M7S9R38Y00NWAGXCWPSH537V`: succeeded. 3개 상세 배치 각각 INCREMENTAL_INGEST_PASS, 총 6 section_sources, 164 chunks, duplicate_added=0, conflict_denied=true, dimensions=384, 각 검색 후보 3건. 기존 원본/StartedAt 불변. backup 442,514 bytes.
- `job_01M7SA15NV006V4TH2HQ5R0EZ8`: succeeded. 신규 문헌 1건·청크3개, 최종 4건·6 section_sources·167청크. 재실행 중복 0, 변조 충돌 거부, 벡터 384D, 검색 후보 3건. 기존 보강 3건 fingerprint 및 모든 기존 컨테이너 StartedAt 불변, synthetic DB 4건 유지. 최종 dump 448,812 bytes. 일회성 worker 정리 완료.
- 최종 청크 구성: 제목4·요약4·대표청구항5·전체청구항13·상세설명141=167. 신규 4번째 문헌은 기본 정보만 적재(상세/전체청구항 미수집).

## 한계 및 다음 작업
- 이 결과는 로컬 실제 문헌 적재와 벡터 검색 시험이다. 자동 WIPS→MCP 쓰기 도구 및 ChatGPT 실제 검색 통합, 신규 문헌의 자동 상세 보강은 아직 미완료. 이번 배치는 채팅에서 선택한 제한된 WIPS 호출과 일회성 worker 실행이며 자동 스케줄이나 대량 수집을 설치하지 않았다.
- 실제 자료 dump는 생성했으나 독립 복원·ACL 회귀는 MVP-05에서 수행. 독립 AI 리뷰 NOT RUN(선택). 데이터 제공자 계약 범위 확대/재배포·상업 이용 별도 검토. 기존 재기동 HOLD 유지.
- 다음은 MVP-03: 자연어 연구 질의 분석/검색어 확장/두 소스 호출/신규 자료 적재 흐름 구현 및 비파괴 시험. MVP-01 운영 전환 및 실제 ChatGPT 호출은 별도 조건 충족 후 시행. P1~P3는 backlog.
