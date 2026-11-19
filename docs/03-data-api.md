# 데이터/API — 초안

| 테이블 | 핵심 항목 |
|---|---|
| users / profiles | id, hash, role, domain, priorities, consent |
| provider_policies | source, version, search/store/embed/llm/share, expiry |
| patent_documents | source, country, doc_no, kind, app_no, family, hash, policy_id, fetched_at |
| patent_sections / chunks | doc_id, section, ordinal, text_hash, text, model_id, embedding |
| search_runs / usage_events | owner, status, counts, latency, budget, 비용 추정 |
| ingestion_jobs | document_key, policy, state, attempts, lease_until |

문헌 unique(source,country,doc_no,kind), chunk 멱등 upsert, 정책 만료 시 조회 금지 및 삭제/백업 만료 절차. profile/history 사용자별 격리. 저장 또는 전송 불가 내용은 영구 DB/로그에 남기지 않는다. embedding 모델/차원/index는 실측 후 결정.

| API | 기능 |
|---|---|
| POST /api/v1/auth/login | 세션 발행 |
| GET/PATCH /api/v1/profile | 본인 연구 설정 |
| POST /api/v1/search | query, mode, country, top_k, profile 여부 |
| GET /api/v1/search/{id} | 본인 결과/진행 |
| GET /api/v1/patents/{id} | 허가된 문헌 상세 |
| GET /api/v1/ingestion/{id} | 적재 진행 |
| GET /api/v1/admin/usage | 관리자 비용 |
| GET /healthz | 비밀 없는 상태 |

세션 폐기/CSRF 및 rate limit, param SQL, 트랜잭션, bounded queue, idempotency key. 실제 contract는 구현 테스트로 확정.
