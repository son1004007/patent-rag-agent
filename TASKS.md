# Tasks — MVP 우선 실행 계획

> 2026-11-19 최신 사용자 결정: 기업용 구축 등 확장 기능은 MVP 이후 백로그로 이동한다. 지금은 개인 ChatGPT + WIPS + NAS RAG 조합에서 실제 연구 질문을 끝까지 처리하는 최소 기능을 우선 완성한다. 이 파일이 실행 순서의 정본이다. [현재 검증 상태](CURRENT_STATE.md), [실측 이력](WORKS.md), [변경 전 계획](https://github.com/son1004007/patent-rag-agent/blob/5822b64649a867340d84fc321900fcec93c3a6ba/TASKS.md).

## P0 — 개인용 MVP (최우선)

목표: 사용자가 자연어로 연구 목적만 설명하면 ChatGPT가 NAS 기존 특허 검색 → WIPS 추가 검색 → 허용 자료 수집/적재 → 중복 제거 → 근거 기반 후보 비교·추천을 수행하고, 이후 동일 질문에서 저장 자료를 재사용할 수 있다. 별도 웹 Agent/관리 UI/외부 모델 API는 MVP 필수 조건이 아니다. 기존 개인 플러그인과 권한 경계를 활용한다.

| ID | 우선순위 / 작업 | 현재 상태 | 완료 기준 |
|---|---|---|---|
| MVP-01 | 기존 NAS RAG 통합 MCP 전환 및 개인 ChatGPT 도구 갱신 | 로컬 후보 39/39 PASS, 운영 전환 HOLD | 기존 플러그인을 유지하면서 실제 search_patents/get_patent 호출 성공, 기존 기능 회귀, rollback 검증 |
| MVP-02 | 실제 문헌 상세 조회 및 증분 적재 | 로컬 PASS — 기존 3건 보강·신규 1건, 167청크/384D, 4배치 중복/충돌 검증 ([실측](docs/22-mvp02-incremental-patent-ingest.md)) | 기존 3건의 허용된 요약·청구항·상세설명 보강 또는 권리 명시 시험 자료, 2개 이상 소량 배치 신규/중복/충돌 검증, 문헌/섹션별 provenance와 건수/벡터 검증 |
| MVP-03 | 자연어 연구 질문 → 검색 계획 → NAS/WIPS 호출 | 개별 호출 및 읽기 연계 PASS, 자동 흐름 미검증 | ChatGPT가 질문에 따라 검색어 확장, 검색 범위 결정, 두 소스 구분, 권한 내 신규 자료만 수집 및 적재 재사용; 자유로운 대량 수집 없이 제한된 on-demand batch |
| MVP-04 | 기본 검색·중복 제거·근거 기반 후보 비교/추천 | NAS exact vector 검색 PASS, 통합 분석 미검증 | NAS 벡터 결과와 WIPS 키워드 검색을 출처별로 수집 후 문헌번호/종류 단위 중복 제거; 근거 위치·문헌 출처·불확실성 표시, 무관하거나 근거 부족 시 추천 보류. 고급 Hybrid/RRF·reranker는 P1 |
| MVP-05 | 최소 안전·복구·종단간 인수 시험 | 합성 백업 복원 PASS, 실제 자료 dump만 생성 | 실제 자료별 백업 복원/ACL/무결성, 인증/권한/실패 시 차단, 회귀 및 rollback, 최소 5개 질의(정상·반복 재사용·신규 적재·근거 부족·실패/거부)의 기대 결과/실측 기록, 개인 ChatGPT의 실제 end-to-end 증거 |
| MVP-06 | 최소 사용자 확인 및 사용법 | 미완료 | ChatGPT에서 실제 연구 질문 한 건으로 사용자가 결과 평가 가능; 짧은 사용법·제약·운영/복구 런북 제공 |

- [ ] MVP-01 운영 전환·실제 ChatGPT 조회 (HOLD: 기존 컨테이너/서비스 재기동 금지 해제 또는 기존 서비스 무중단이 실증된 승인 경로 필요. 기존 플러그인 중복 생성 금지).
- [x] MVP-02 기존 3건 상세설명/전체 청구항 32개 보강, 신규 문헌 1건, 4개 배치 적재·중복/충돌·출처·벡터 확인 ([실측](docs/22-mvp02-incremental-patent-ingest.md)). 신규 1건 상세 수집·자동 흐름은 MVP-03 이후.
- [ ] MVP-03 연구 목적 분석·검색어 확장·WIPS/NAS 검색 및 적재 오케스트레이션 (현재는 수동 개별 호출).
- [ ] MVP-04 기본 결과 통합·중복 제거·근거 표시 및 후보 비교/추천.
- [ ] MVP-05 최소 보안·복원·인수/E2E 검증.
- [ ] MVP-06 개인 ChatGPT 실제 사용 확인 및 최소 사용법/복구 가이드.

**다음 실행 규칙:** MVP-01의 운영 전환은 재기동 금지 상태에서 강행하지 않는다. MVP-02 로컬 검증 완료. 승인 대기 동안 MVP-03 → MVP-04의 격리/비파괴 구현과 시험, MVP-05의 온라인 백업·격리 복원을 진행한다. MVP-01이 해소되면 전체 E2E를 실행한다. 인수 기준 충족 전 P1/P2/P3를 선행하지 않는다. 합성/로컬 성공을 실제 ChatGPT E2E 성공으로 표시하지 않는다. 구매 자료의 개인 내부 적재 지시 범위를 유지하고, 실제 외부 반환/LLM 처리·계약상 대량 수집 등 확대는 필요한 확인과 승인 후 수행한다. 필요한 권리 확인은 MVP에서 해당 기능의 gate로 유지하고, 광범위한 기업 계약 검토는 뒤로 보낸다.

## P1 — MVP 사용 피드백 이후 품질 고도화 (BACKLOG)

- [ ] NAS 키워드 검색 + 벡터 검색 Hybrid RAG, RRF/재정렬, 근거 정확도 및 중복 제거 개선.
- [ ] 검색어 확장 A/B/C/D 및 300자 실험, 평가용 질의 세트/연구자 판단과 검색 품질·지연·비용 측정 고도화.
- [ ] 지속적 연구 profile/개인화, 이력/검색 조건 관리, 후보 기술 비교 기능 확장.
- [ ] 승인된 corpus의 수집량 확대·대량/정기 동기화·문헌 보강/갱신, 보존·삭제·재시도 정책. 권리/정식 요금·동시성 확인 전 범위 확대 금지.
- [ ] 사용자 피드백 후 기존 정적 UI 실제 브라우저 확인 및 개선. 필요 시 별도 FastAPI/UI 계정·profile·mock provider/독립 웹 Agent 대체안, 로그인/OAuth·사용량 제한. 실제 독립 모델 API/LLM 연동은 별도 필요성/비용/권리를 확인한 뒤 선택.

## P2 — MVP 이후 운영 및 공용 인프라 확장 (BACKLOG)

- [ ] 관리자 웹페이지, 수집/적재 현황, 접근 권한/로그, 운영 상태 및 관리 기능.
- [ ] 자동 백업·보존 주기/복원 자동화, 장애복구 및 관측. MVP 최소 실제 DB 복원은 MVP-05에 포함.
- [ ] HOLD — NAS/daemon 및 기존 컨테이너 실제 재기동·자동 시작 등록/실증 (별도 사용자 승인 필요, 순차 기동 --check PASS).
- [ ] 실제 기술사·특허 공용 영속 DB 운영 전환 및 migration/인증/복원 회귀 — 기술사 기존 배포 차단 정식 해소 및 승인 후.
- [ ] 인덱스/상대 링크 검사 CI, 승인된 격리 Docker staging 및 운영 배포, 실제 환경 테스트·회귀·rollback·HTTPS/인증/허용·비허용 접근 시험의 규모 확대.
- [ ] 최종 화면 기반 사용자 및 관리자 설명서. 독립 AI 설계 자문은 선택(배포 선행 게이트 아님).

## P3 — 기업용 구축 및 관리용 SSH (MVP 이후; 별도 착수 승인)

- [x] [기업용 ChatGPT 연결·방화벽 5-tuple·SSH 가이드](docs/21-enterprise-connectivity-firewall-ssh.md) 작성 및 공식 자료 조사.
- [ ] 실제 기업 제품(Workspace Business/Enterprise vs Azure OpenAI 자체 앱), 계약/데이터·조직 권한 확인.
- [ ] 회사 FQDN/IP/port/NAT/proxy/IdP를 반영한 방화벽 신청서 확정 및 승인.
- [ ] 회사 전용 터널/MCP/DB, OAuth/네트워크·권한·기업 RAG E2E.
- [ ] 운영 관리 전용 MCP + 내부 SSH, 최소권한/승인/감사/차단 검증. 외부 Gateway는 별도 공급사 승인 시 대안.
- [ ] 기업용 설치 패키지·기업 실제 배포/인수 및 운영 가이드 완성. 회사 서버/방화벽 변경 NOT RUN.
- 위 기업 업무는 개인 MVP의 완료 조건이 아니다. 기존 문서 보존, 추가 구현·기업 환경 조작은 별도 착수 요청까지 제외.

## 완료한 기반 작업 (기존 검증 이력 보존)

- [x] 저장소 생성 및 쓰기 권한 확인
- [x] 목차/초안 커밋 및 중앙 registry 연결 검증 (15 문서 조회 및 상대 링크 PASS; Mermaid 렌더 미검증)
- [x] 배포 우선 반복 개발 정책 반영 (독립 AI 검토 선택, AGY/Gemini 제외)
- [x] 가상 자료 기반 반응형 정적 UI (검색/후보 상세/비교/보관소/연구 설정/운영 현황)
- [x] NAS 정적 시안 컨테이너 배포 및 loopback HTML/CSS/JS 응답 검증
- [x] 사설 HTTPS 경로 연결 및 별도 기기 TLS/HTML/CSS/JS HTTP 200 검증
- [x] README/아키텍처 단순화 및 기존 기술사 RAG DB/SDK 현황 확인
- [x] 합성 문서 MCP save/get/부분문자열 search 및 중복/ID scope/conflict 검증 (ASGI 일회성; [실측](docs/09-mcp-contract-smoke.md))
- [x] 실제 pgvector SQL 검색/저장 및 DB 도메인 격리 시험 (합성 384D, 18/18 PASS; [실측](docs/10-shared-vector-smoke.md))
- [x] MCP→pgvector 통합 및 로컬 E5 실제 임베딩 검증 (24/24 PASS; [실측](docs/11-mcp-vector-integration.md); 합성 ASGI/임시 DB)
- [x] 합성 전용 지속 실행 MCP 서버 및 실제 HTTP·인증·영속 저장/복원 검사 (초기/재시작 각16/16 PASS; [실측](docs/12-persistent-mcp-stage.md))
- [x] Secure MCP Tunnel NAS 측 준비 (공식 CLI v0.0.21 설치 및 Unix socket 14/14 PASS; [실측](docs/13-secure-tunnel-preflight.md))
- [x] 사용자 runtime key 생성 및 Gateway saved metadata 확인 (값 미조회; 이후 실제 터널 인증 PASS)
- [x] 개인 tunnel_id 생성/확인, Gateway key 파일 안전 전달 및 실제 터널 인증/doctor/polling 검증 ([실측](docs/13-secure-tunnel-preflight.md))
- [x] ChatGPT 개인 플러그인 생성/설치 및 실제 write/get/vector search E2E; 신규 INSERT, 중복/미승인 차단, USER/PRIVATE 확인 ([실측](docs/14-chatgpt-plugin-e2e.md)); 합성 전용, 외부 공개 금지
- [x] 신규 P4 포함 최신 온라인 백업 및 별도 클러스터 복원/ACL/index 검증 ([실측](docs/15-online-backup-startup-plan.md)); 기존 전 서비스 재기동 없음
- [x] 순차 기동 스크립트 작성 및 read-only --check PASS
- [x] 공용 pgvector 엔진 별도 DB/role·개별 복원·동시 부하 사전 시험 (24/24, 400/400; [실측](docs/16-shared-db-coexistence.md); 합성/격리)
- [x] WIPS와 자체 MCP 동일 대화 순차 읽기 연계, 기존 합성 save/idempotency 및 mock 정책 17/17 ([실측](docs/17-dual-mcp-workflow.md))
- [x] 사용자 구매 특허 소량 실제 비공개 적재/provenance/chunk/embedding, 3건/10청크/384D 및 중복·권한 시험 ([실측](docs/18-private-patent-ingest.md))
- [x] README 목표 서비스 흐름 추가 및 실제 특허 읽기 전용 MCP 로컬 HTTP·권한 23/23 검증 ([실측](docs/19-private-patent-reader-mcp.md)); 기존 서비스 유지
- [x] 기존 NAS RAG/wipsclip 개인 플러그인 연결 재확인 및 통합 MCP 후보 39/39 로컬 시험 ([실측](docs/20-unified-mcp-candidate.md))

기존 개인 연결/실제 특허 4건(3건 상세 보강)/167청크/통합 후보 39/39까지 확인됨. 운영 전환·실제 ChatGPT 조회·자동 흐름은 미완료. 별도 웹 시안의 실제 사용자 조작은 P1으로 이동. 이전 세부 작업과 미완료 내역은 [변경 전 계획](https://github.com/son1004007/patent-rag-agent/blob/5822b64649a867340d84fc321900fcec93c3a6ba/TASKS.md) 및 [실측 로그](WORKS.md)에서 추적한다.
