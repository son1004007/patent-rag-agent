# P0-3 실행 계획서 — 문헌별 상세 수집·임베딩

- [설계서](P0-3-design.md) / 현재: 기존 소량 실자료 적재 6문헌·10섹션·417청크, 신규 서지83건은 별도 보관.
- **전제:** 서지 자동보관100건 허가는 추가 문헌 원문/임베딩 수집 허가가 아니다. 범위 확인 전 **HOLD_RIGHTS**.

## 실행 단계

| 단계 | 구현/재사용 | 최소 선행 테스트 | 완료 증거 |
|---|---|---|---|
| 1. 대상 선정 | `mvp43_document_selection.py` 신규 | 기존 `patent_archive` ↔ `private_docs` country/number/kind exact 매칭, 현재 소유자 허용문헌 1건만 | candidate=1, matched/unknown 분리, 무단 호출0 |
| 2. 서지→원문 row 변환 | `mvp43_wips_enrich.mjs` 신규, WIPS `get_patent_by_skey`/`get_patent_spec_text` | `ABK/CLK` 필수, 정확한 `FIELDS` 7개, 두 section lang/ID 일치, 180000자/600 chunks cap | 기존 `private_patent_ingest.validate`와 `sections` 유효성 PASS |
| 3. 단건 check/apply/reuse | 기존 [adapter](../../poc/mvp03_ingest_adapter.py), [transport](../../poc/mvp03_local_transport.py) | 정책 `packet_sha256`, `new/enrich` mode, writer lock, pinned E5 | dry-run preflight, 실제 한 문헌만 변경 |
| 4. 상태 기록 | `mvp43_collection_state.sql` 제안 | metadata/text/vector/pdf 독립 projection/ACL 및 identity link | 저장 상태가 DB 실측과 일치, PDF는 없는 경우 NONE |
| 5. 읽기 회귀 | [reader](../../poc/private_patent_reader.py) | search_patents/get_patent, 기존 evidence 3개×300자 유지 | 실제 새 문헌 근거 검색, 기존 문헌 순위/해시 변화 기록 |
| 6. 복구·운영 적용 | 기존 [private backup](../../poc/private_backup_restore.sh) | 운영 사전 백업 및 격리 복원, source fingerprint | 새 section/chunk 추가만, 기존 행/다른 서비스 불변 |

## 테스트 목록

- [ ] 올바른 row 7필드와 `APSTH/XD` 포함 서지 row 혼용 오류를 사전 탐지
- [ ] `dtl_desc_list`·`cl_list`, 실제 section/lang fallback/문헌번호/청구항 중복 검증
- [ ] 비어 있는 `ABK`/`cl_list`와 country/number mismatch → HOLD, 쓰기0
- [ ] 2개 section·동일 lang/approved packet hash 검증, 임의 정책 `true`는 차단
- [ ] 1건 신규/기존 enrich/reuse/메타데이터 충돌, append-only 및 idempotency
- [ ] char/token/chunk cap, 벡터384, 모델 pin/`query: ` / `passage: `, memory/timeout
- [ ] `archive.metadata=STORED`이지만 `private_docs` 미보유이면 text=NONE/vector=NONE
- [ ] 승인 자료 1건 실제 운영 적재·RAG 검색, 백업/복원 및 기존 컨테이너 StartedAt
- [ ] 83건 전부 자동 수집하는 batch/후속 WIPS 페이지 호출이 없음을 검증

## 재작업 최소화 점검 순서

1. **유효한 권리 정책** → 2. WIPS 식별/언어/본문 2개 section 응답 → 3. 기존 파서와 packet 계약 → 4. 토큰/임베딩 CPU 자원·384D → 5. DB lock/append-only/중복 → 6. 운영 배포/복구.
2. WIPS raw text를 출력/log/공개 저장소에 옮기지 않고 **스키마·길이·개수·status만** 확인한다.
3. 기존 단건 적재 엔진이 이미 안정적이면 새 writer/임베딩 코드를 중복 구현하지 않고 wrapper/상태·정책만 추가한다.

## 실패 시 처리

- 권리/비용 미확인: `HOLD_RIGHTS`, 저장 안 함; 사용자 승인 범위 확대를 임의 생성하지 않는다.
- 상세 텍스트 불완전: `PARTIAL_NOT_INGESTED`로 남기고 빈 문자열 임베딩 금지.
- stored source hash와 신규 원문 hash 불일치: `CONFLICT_HOLD`, 기존 데이터 UPDATE하지 않음.
- 임베딩/DB 일시 실패: 실제 commit 여부 DB id/hash 확인 후 동일 packet 재실행. 무한 재시도·무한 WIPS 재호출 금지.
- 운영 기존 데이터/role 상태 변질: 신규 수집만 정지; 복구 전 실제 영향 범위/백업 일치 확인.

## 인수

본 단계의 완료는 **새롭게 허용된 문헌 1건의 정확한 텍스트·청크/벡터 실제 운영 적재와 재사용 증거**다. 전체 서지83건 일괄 적재를 완료 기준으로 삼지 않는다. 판정/검증 로그는 [WORKS](../../WORKS.md), 최신 완료 상태는 [CURRENT_STATE](../../CURRENT_STATE.md).
