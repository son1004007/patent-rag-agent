# 작업 진행 기록

실제 완료 상태는 [CURRENT_STATE.md](CURRENT_STATE.md), 다음 작업은 [TASKS.md](TASKS.md), 전체 문서는 [DOC_INDEX.md](DOC_INDEX.md) 참조. 이곳은 진행 과정/검증 근거의 시간순 기록이다.

## 2026-11-19

| 단계 | 결과 및 증거 |
|---|---|
| 설계/화면 시안 | [아키텍처](docs/02-architecture.md), NAS 정적 가상 UI 및 사설 HTTPS 접속 검증 |
| ChatGPT 중심으로 전환 | README 도식 갱신, 기존 독립 웹 Agent는 대체안 유지 |
| 합성 MCP 계약 | [실측](docs/09-mcp-contract-smoke.md), save/get/문자열 검색 및 중복/충돌 거부 PASS |
| 공동 pgvector 격리 | [실측](docs/10-shared-vector-smoke.md), 같은 시험 PG 클러스터 내 도메인별 DB/role 분리 및 18/18 SQL 체크 PASS |
| MCP와 실제 E5/pgvector 통합 | 코드 [Python](poc/mcp_vector_smoke.py), [실행기](poc/mcp_vector_smoke.sh), 커밋 `bf2c368b6dbd75ccc017609f99bac361b130291c`; 24/24 PASS — [실측 및 한계](docs/11-mcp-vector-integration.md); NAS 임시 DB와 실제 E5 통합, 사후 건수/정리 PASS. |
| 합성 전용 영속 MCP 시범 서비스 | [서비스](poc/stage_service.py) / [HTTP 시험](poc/stage_http_test.py) / [배포기](poc/stage_deploy.sh), commit `05c5145960e72721b49d7ba4d8e940c6cdd28455`; [최종 실측](docs/12-persistent-mcp-stage.md) — 최초/재시작 HTTP 16/16씩 (32/32), backup/restore 및 재시작 fingerprint PASS; 사설 격리 DB/API 2개 RUNNING, 외부 포트 0. |
| Secure MCP Tunnel NAS 측 준비 | [실측](docs/13-secure-tunnel-preflight.md): 기존 HTTP 16/16 재검증, Unix socket 14/14 PASS, 공식 CLI v0.0.21 해시/기동 PASS. 개인 계정의 tunnel_id/제한 key 미확인으로 실제 연결 BLOCKED. |
| 개인 터널 인증 준비 갱신 | 사용자 runtime key 생성/저장 보고 및 Gateway metadata 확인. [터널 생성 안내와 다음 단계](docs/13-secure-tunnel-preflight.md). 키 권한·유효성 및 실제 tunnel_id 미확인, 연결 NOT RUN. |
| OpenAI 개인 터널 실연결 | [실측](docs/13-secure-tunnel-preflight.md) — 사용자 ID 및 saved key 적용, 최초 doctor TCP probe 실패 → container-local loopback adapter 적용, doctor PASS. OpenAI metadata/MCP session 및 polling PASS, health/ready 200, port publish 0. 실제 ChatGPT plugin 설치/호출 대기. |
| ChatGPT 개인 NAS RAG E2E | [실측](docs/14-chatgpt-plugin-e2e.md): 직접 get/search/중복 및 변경거부, 새 합성 P4 최초 INSERT created=true, DB 실측 4건 및 384D, Top1 검색 일치. USER/PRIVATE 및 기존 5개 컨테이너 running, published0. WIPS 실자료 금지 유지. |
| 최신 온라인 백업·순차 기동 준비 | [실측](docs/15-online-backup-startup-plan.md) — 4건 최신 dump/빈 클러스터 복원·ACL·HNSW/P4 384D PASS, 기존 모든 StartedAt 불변. 기동 --check 및 ChatGPT 조회 PASS. 사용자 지시로 실제 재기동 및 자동 시작 등록 HOLD. |
| 공용 DB 공동 운영 사전 검증 | [실측](docs/16-shared-db-coexistence.md) — 격리 별도 DB/role, 실제 특허 합성 dump 복제, 모사 학습 corpus/비공개 view 권한, 동시 SQL 400/400, 독립 복원, 24/24 PASS. 기존 시작시각 불변, 실제 영속 전환/기술사 배포 차단 유지. |
| WIPS·NAS MCP 동일 대화 연계 | [실측](docs/17-dual-mcp-workflow.md) — WIPS 식별정보 3건, 독립 주제 NAS P4 Top1, 기존 합성 save created=false; 정책/실패 분기 mock 17/17 PASS. 실제 WIPS 데이터 NAS 전송·저장 없음. 공식 베타 무료/AI 사용량 별도 및 권리 확인 항목 기록, 재기동 없음. |
| 실제 구매 특허 자료 비공개 적재 | [실측](docs/18-private-patent-ingest.md) — 실제 3건·10청크·384D, DB 검색·중복 차단·dump 성공. 전용 private DB, 기존 4건/StartedAt 유지. 공개 repo 실자료 없음, 기존 플러그인 실자료 노출 없음. |
| README 목표 흐름 및 실제 특허 reader MCP | [실측](docs/19-private-patent-reader-mcp.md) — README Mermaid 목표 흐름 추가, 실제 특허 3건 distinct 검색·개별 조회 및 권한 HTTP 23/23, 87.15ms 단일 질의, 별도 role/view, 임시 worker 정리·기존 StartedAt 불변. ChatGPT 실자료 연결 미검증. |
| 기존 연결 재확인 및 통합 MCP 후보 | [실측](docs/20-unified-mcp-candidate.md) — 기존 개인 플러그인 정상/합성 범위 확인, 실제 특허 도구 포함 후보 최초 DB 참조 오류 수정 후 39/39, 86.54ms, 기존 StartedAt 불변; 운영 전환 HOLD. |
| 기업 환경 추가 요구 | [기업용 방화벽·SSH 가이드](docs/21-enterprise-connectivity-firewall-ssh.md) — ChatGPT Business/Enterprise와 Azure 자체 앱 구분, outbound 443 우선, 5-tuple 방화벽 신청, 별도 운영용 MCP/내부 SSH 및 Gateway 대안. 공식 문서 조사 및 설계만, 실제 회사 변경 없음. |
| MVP 우선 계획 재편 | 사용자 최신 지시에 따라 [TASKS.md](TASKS.md) P0 MVP-01~06 인수 기준/실행 순서 정립, P1 품질·UI, P2 운영·공용 DB, P3 기업·SSH backlog 분리. 기존 실측 증거·기업 가이드 및 권한/재기동 보류 유지. 계획 문서 변경만, 운영 배포 및 코드 변경 없음. |
| MVP-02 상세 수집·증분 적재 | [실측](docs/22-mvp02-incremental-patent-ingest.md) — 실제 기존 3건 상세설명 61,407자/청구항32개, 3회 보강 후 신규 metadata 1건. 4건·167청크/384D, 4개 배치 중복0 및 변조 충돌 거부, 원본 fingerprint·StartedAt 불변, 최신 dump 448,812 bytes. 실제 ChatGPT 연결 및 dump 복원은 미완료. |
| MVP-03 자연어 질의·검색/수집 흐름 | [실측](docs/23-mvp03-research-flow.md) — ChatGPT 용어 확장, 정책 21/21, 실제 NAS/WIPS 검색 3+3, 신규 한 건 상세설명 98,067자/청구항5개, 234청크 추가; 5건·401청크, 동일 질의 신규 문헌 NAS 2순위 및 보유 판정, 재검증 쓰기0. 기존 fingerprint·StartedAt 불변, 최신 dump 1,037,393 bytes. 기존 개인 플러그인 자동 통합 HOLD. |
| MVP-01 통합 MCP 운영 전환 | [실측](docs/24-mvp01-production-cutover.md) — 사용자 승인 API만 재시작, 16+24+16=56/56 PASS, 실제 특허 검색 109.78ms, DB·기타 컨테이너 StartedAt·API 설정 불변. 기존 ChatGPT 직접 호출 정상; 새 search_patents/get_patent 도구 Refresh 및 직접 호출 대기. |
| 사용자 플러그인 Refresh 확인 | 사용자 권한 추가·Refresh 수행 보고, 기존 채팅에서 기존 3개 도구 노출 및 DEMO-P4 직접 조회 정상, PRIVATE 유지. 새 채팅 신규 도구 E2E 대기. [기록](docs/24-mvp01-production-cutover.md). |

| 새 ChatGPT 대화 실제 특허 MCP 읽기 E2E | [실측](docs/24-mvp01-production-cutover.md) — 5개 도구 발견, 신규 검색 3건/반복 순위 일치, 상세 3/3·근거 9개·300자 상한, 미존재 found=false, 기존 합성 조회/검색 PASS. 읽기만 수행, 실제 rollback/쓰기/복원 NOT RUN. 실제 자료 식별자/원문 공개 기록 없음. |

| MVP-04 기본 통합·근거 비교 | [실측](docs/25-mvp04-candidate-comparison.md) — 순수 JS 모듈 27/27, 실제 WIPS 재호출 성공 및 NAS 직접 조회 3건, 6→5 중복 제거, 근거 18개, HOLD 3/EXCLUDE 2/후보 0. 중간 WIPS BAD_WIPS 및 부분 소스 추천 차단 기록. 읽기 전용, 새 서버 배포·쓰기·복원 NOT RUN. |

| MVP-03 승인된 적재 adapter | [실측](docs/26-mvp03-approved-ingest-adapter.md) — JS 수집/전송 연결 및 NAS native Python 일회성 worker wrapper 구현. 29/29 JS + 23/23 Python synthetic PASS, 실제 운영 DB 읽기 5건/401청크/4건 상세/384D. 실제 transport/LocalBackend/신규 쓰기 및 복원 NOT RUN. 기존 MCP read-only 경계 유지. |

| MVP-05 실제 특허 DB 복원 | [실측](docs/27-mvp05-private-backup-restore.md) — 최종 job succeeded exit0, 1,037,393 bytes, 5/8/401 및 전체 fingerprint/ACL/HNSW/Top3/384D 일치. 원본·기존 컨테이너 불변, cleanup·SHA256 PASS, 이후 실제 ChatGPT 읽기 3/3. 앞선 cleanup 종료1 두 건 기록, 신규 쓰기/운영 rollback 및 전체 인수 미완료. |

| MVP-05 격리 rollback·인수 | [실측](docs/28-mvp05-rollback-acceptance.md) — 실제 이전/현재 코드 정본 4/4 확인, 복제 DB 2개·HTTP 현재40/이전16/현재40=96/96, 임시 SCRAM/ACL/교차 DB 거부, 복제 및 운영 원본·기존 컨테이너 불변, 정리 성공. 실제 읽기/안전 차단 4/5, 실제 신규 쓰기 BLOCKED [#30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30). 실제 운영 rollback NOT RUN. |

| MVP-06 실제 사용·설명서 | [사용자](docs/29-mvp06-user-guide.md) / [관리자](docs/30-mvp06-operator-guide.md) / [실측](docs/31-mvp06-user-trial.md) — 직전 대화 실제 새 질문 3+3→5, NAS 상세3/3, 근거18, HOLD4/EXCLUDE1. 문서/목차/진입점 갱신, 사용자 평가 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) 대기 및 신규 적재 [#30](https://github.com/son1004007/ai-agent-workflow-playbook/issues/30) 별도. 운영 변경 없음. |

| MVP-03 실제 DB 엔진 격리 적재 | [실측](docs/32-mvp03-isolated-backend-test.md) — schema-only 복제, 가상 2건/4섹션/10청크/384D, CLI·LocalBackend·worker 17/17 PASS, 신규·재사용·부분 복구·충돌·ACL. 첫 외부 종료1(정확한 원인 미확인), 최종 exit0 및 운영 원본/전체 기존 컨테이너 불변, cleanup PASS. 실제 WIPS 구매자료 및 운영 쓰기/transport 미검증. |

| MVP-03 writer 직렬화 | [실측](docs/33-mvp03-writer-serialization.md) — native 35 + 실제 격리 DB 18 = 53/53 PASS; 경쟁 CLI DB 쓰기0, 합성 2/4/10/384D, 운영 fingerprint 및 모든 기존 컨테이너 불변, cleanup PASS. 운영 배포/신규 문헌 승인/transport 미실행. |

| MVP-03 로컬 transport | [실측](docs/34-mvp03-local-transport.md) — 실제 격리 E2E: 교차 컨테이너 lock/check/신규 1·2·5·384D/재실행 쓰기0/코드 pin 차단, 운영 fingerprint 및 모든 기존 컨테이너 불변, cleanup PASS. 실제 구매·운영 배치/ChatGPT 쓰기 미실행. |

| MVP-03/05 사용자 승인 실제 운영 단건 인수 | [실측](docs/35-mvp03-actual-ingest-acceptance.md) — 실제 WIPS 1건, 상세 5,386자·청구항2, 운영 check/apply/reuse PASS, 6/10/417·384D, 기존 행/컨테이너 불변, 전후 backup 0600/hash PASS, 신규 실제 ChatGPT 검색 1위 및 상세 근거3. 상시 자동 쓰기 연결 미구현, 사용자 평가 대기. |

실제 자료는 사용자 구매 확인에 따른 개인 NAS 내부 소량 적재 범위로 분리한다. 공개 저장소 원문 보존 및 재배포는 하지 않는다. 기존 기술사 개발 볼륨과 시안 서비스 유지. 작업별 실행 증거를 확인한 뒤 결과를 갱신한다. 개인 터널 및 실제 ChatGPT 읽기 호출 PASS; 실제 자동 적재와 안전·복구 인수 잔여는 TASKS 참조.

- 사용자 피드백에 따른 [검색 연동 자동 보관 및 원문 조회 요구사항](docs/36-mvp-automatic-archive.md) 등록. 문서·목차·P0 갱신만, 새 실자료 적재 및 배포 미실행.

- [자동 보관 요구사항](docs/36-mvp-automatic-archive.md)에 원본 PDF 별도 수집 경로/공식 자료 링크, 문헌 매칭 및 검증 조건 추가. 문서만 변경. 실제 API/파일 수집 또는 운영 변경 없음.

- 2026-11-20 [P0-1 검색 목록 저장 기반](docs/37-mvp-search-list-archive.md) 구현. wrapper 테스트 9/9, 실제 WIPS 읽기 1행 callback PASS, 저장 보류. Gateway 첫 시험 실행기 손실, 재시도 대기 취소, read-only 운영 preflight 6/10/417에 archive schema 0. 운영 저장 및 배포 미실행, #34 등록.

- 2026-11-20 [P0-1 목록 저장 NAS 통합 재검증](docs/37-mvp-search-list-archive.md): 이전 executor 장애 해소, 모사 및 실제 운영 schema-only 격리 환경 각각 DB 10/10 + CLI 2/2. migration의 명시 CONNECT 및 권한 분리, 별도 새 DB 복원 fingerprint/ACL/원문 상태 PASS. 첫 강화 migration dollar quote 오류 수정 후 최종 exit0. 운영 전 행/컨테이너 불변 및 시험 cleanup. 기존 운영 복구 스크립트 갱신 및 #34/자동 연결 대기.

- 2026-11-20 사용자 운영 우선 지시 AGENTS 반영. [P0-1 운영 schema 및 복구 실측](docs/38-mvp-archive-production-migration.md) PASS: 실제 4 tables/1 view, writer NOLOGIN, 5개 배치 코드 blob 일치. 실제 원문 상태 6건 중 5건 상세/전체청구항 evidence 보유, 트랜잭션 rollback 이후 영속 0행, 기존 원문 6/10/417 및 기존 ACL/index/컨테이너 불변. 전후 백업·실제 신규 dump 격리 복원, ChatGPT 3/3 조회 PASS. 새 API rollback drill 실행 NOT RUN. #34 권리와 실제 자동 저장 연결 잔여.

- 2026-11-20 P0-1 [운영자 로컬 전송 배치/차단 실측](docs/38-mvp-archive-production-migration.md): 운영 배치, 기본 정책 disabled, 기존 실제 승인 보유 서지자료의 local projection BLOCKED_POLICY. 정책/반환 검증, 원문 fingerprint·컨테이너 불변, archive rows 0, writer NOLOGIN/secret 없음/worker 0. 허용 분기·상시 policy·실제 WIPS 자동 연결 및 영속 목록 적재 미완료, #34 승인 권리·한도 확인 대기. 반복 시험 대신 사용자 조치 후 실제 연동.

- 2026-11-20 사용자 명시 확인: WIPS 서지 NAS 지속 보관 허용, 검색당 최대100건. [운영 실측](docs/39-mvp-archive-100-live-acceptance.md): 실제 WIPS 첫 페이지 83건, 운영 archive 83/83/1/83, 동일 응답 재실행 신규0, rank51~83 저장, 본문·벡터 6/10/417 불변, 운영 독립 backup/restore 및 ChatGPT 기존 조회 PASS. 별도 writer role LOGIN+secret0600, 불필요한 worker 0, 원본 응답 임시 파일 제거. 일반 WIPS 플러그인 전체 호출의 상시 자동 가로채기 미구현; 다음 P0. 계약 권리는 사용자 확인(독립 증빙 미검증), 원문/PDF 저장 아님.

- 2026-11-20 [WIPS MCP 28개 도구/구현 갭 카탈로그](docs/40-wips-mcp-capability-catalog.md) 작성: 연결된 모든 도구 이름 및 section/주요 데이터 확인, 검색·dtl_desc·all_claim·draw·indv_draw 실제 응답과 나머지 정의 확인 구분, 공보 PDF/청크·벡터 WIPS 비제공과 NAS 파생 임베딩 분리. 운영 서지83건/기존 본문6건·10섹션/청크417개/PDF0건, 미완료 P0-1~P0-5를 TASKS에 등록. 공개 민감 정보 없이 문서·목차·작업 상태만 갱신, WIPS 신규 수집/운영 실행·재시작/배포 없음. 독립 AI 검토 NOT_RUN_OPTIONAL.

- 2026-11-20 [P0-1~P0-5 독립 구현 설계서+실행 계획서 10개](docs/mvp-implementation/INDEX.md) 문서화: 기존 WIPS/NAS 코드와 실제 DB 스키마/장애 사례, 제공자 공식 자료(KIPRIS Plus XML 공보 download path, EPO PDF/A REST fair use) 대조. 각 작업 단위 Mermaid·API/DB·기술 선택·필드 변환/권한·에러 사전 대응·단계별 운영 검증·rollback/완료 정의. DOC_INDEX/AGENTS/TASKS/CURRENT_STATE/AI_CONTEXT/README 및 전역 pointer 연결. 문서/계획만 변경, 실제 개발·배포·유료 호출·신규 적재/운영 테스트 NOT RUN. 독립 AI 리뷰 NOT_RUN_OPTIONAL.

- 2026-11-20 [WIPS MyFolder MCP 조사](docs/41-wips-myfolder-mcp-assessment.md): WIPS 공식 발표와 공식 소개 및 외부 MCP 도구 카탈로그 확인. 읽기 전용 폴더명/건수 및 폴더 SKEY 페이지 조회를 기존 WIPS 검색 28도구·NAS writer와 분리. 현재 개인 설치 plugin wipsclip/NAS RAG 2개, MyFolder 도구 노출 없음. 외부 도구 세부 제한은 직접 실증 전 보수적으로 기록. DOC_INDEX/TASKS/P0-1/카탈로그에 P1 폴더 import 선택 경로만 표시. 새 플러그인 설치/인증·WIPS 실자료 호출·운영 변경 없음.

- 2026-11-20 [WIPS MyFolder 실제 연결 후 read-only 비교](docs/41-wips-myfolder-mcp-assessment.md): 현재 MyFolder 2개 도구 노출 확인, `myfolder_list_folders({})` 공급자 인증/폴더 미생성 가능 오류로 실패, SKEY 조회 불가/NOT RUN. 기존 NAS RAG `search_patents(limit=1)` 검색 1건/근거 필드 정상 PASS. 별도 기능/인증 경계 확인, 사용자 비밀번호/폴더명/SKEY 미출력, GitHub 기록만 갱신.

- 2026-11-20 [MVP41 P0-1 코드·NAS 실경로 통합](docs/42-mvp41-code-mode-gateway-archive.md): [mvp41_orchestrate.mjs](poc/mvp41_orchestrate.mjs), [test](poc/mvp41_orchestrate.test.mjs), [owner stdin wrapper](poc/mvp41_receive_and_archive.sh) 신규. Node v22 test 17/17, shell syntax PASS, NAS wrapper mode700 SHA256 pin PASS, Gateway stdin 15-byte canary PASS, invalid JSON 요청 exit1+no verified DB write PASS. WIPS 실제 83건/100 요청/첫1페이지 1회 → Gateway 고정 wrapper 2회 → REUSED_VERIFIED saved0/reused83 두 번, body_writes0; 실제 archive83/83/1/83, private_docs6/10/417, worker0 최종 조회. 83건 첫 INSERT는 과거 인수 [39](docs/39-mvp-archive-100-live-acceptance.md), 이번에 신규 INSERT 재실행 하지 않음. 신규 API/DB migration/컨테이너 재시작/상시 MCP server/브라우저 credential/원문PDF·벡터 수집 없음. 모든 WIPS 호출 후킹/새 대화 자동 도구 선택 실증 NOT RUN; 독립 AI 리뷰 NOT_RUN_OPTIONAL.

- 2026-11-20 [MVP 유지/기술 선택 판단 기준과 두 검증 작업의 상세 실행 계획](docs/evaluation/INDEX.md) 작성: (1) [판단 기준](docs/44-mvp-evaluation-decision-criteria.md), (2) [EVAL-01 WIPS/NAS/통합 후보·근거 정확도](docs/45-search-quality-comparison-plan.md), (3) [EVAL-02 cold/warm WIPS 호출·실제 시간·품질/신선도](docs/46-reuse-value-verification-plan.md), (4) 평가 인덱스. 기존 6원문/417청크와 서지83의 차이, 사용자 정답라벨/평가자 편향, 결측·후보수 차이, 임계값·실측/가정 분리, 오류 대응·종료 증거 작성. AGENTS/DOC_INDEX/README/TASKS/AI_CONTEXT/CURRENT_STATE 및 전역 작업 포인터 연결. **GitHub 문서 only: 신규 WIPS 호출·라벨 생성·NAS 변경/배포·성능 실측 NOT RUN**. 독립 AI 리뷰 NOT_RUN_OPTIONAL.


## 2026-11-20 EVAL-01 준비: 계획 중복 정리

- 전역 registry의 `docs/evaluation/INDEX.md`를 단일 평가 진입점으로 확정하고 중복 `docs/validation/EV-01/02` 및 중복 판단 문서를 **Git history에 보존 후 main에서 정리**했다. EVAL-01은 각 source K=3, 통합 최대6, corpus in/out 5/5, 사람 라벨이 필요하며 P@5/20% 임의 게이트 사용 금지.
- 결정 규칙 [DECISION-01](docs/44-mvp-evaluation-decision-criteria.md), [EVAL-01 계획](docs/45-search-quality-comparison-plan.md), [EVAL-02 계획](docs/46-reuse-value-verification-plan.md), [평가 인덱스](docs/evaluation/INDEX.md) 정본으로 일원화했다. 실험 측정 여부는 별도 실행 증거 기록에서 판단. 신규 원문/벡터 저장·운영 변경은 수행하지 않았다.


## 2026-11-20 EVAL-01 읽기-only 10문항 초기 실측

- [10문항 WIPS/NAS 반환 및 통합 후보 실측](docs/evaluation/2026-11-20-eval01-live-retrieval-baseline.md): 공개 기술 주제 5 IN / 5 OUT, WIPS 및 NAS 10/10 결과 top3, 실제 문헌 ID exact 중복2/고유58, WIPS 국문 요약/대표청구항 30/30·NAS excerpt 30/30, NAS get_patent 5/5 근거3개씩·hash 반환. WIPS 일시 실패3은 각1회 retry 성공, 과거 기동/restart 불필요. 신규 원문/PDF/벡터 적재 없음.
- 사용자의 관련성 0/1/2 및 구체 특허·원문 대조는 수행/확정하지 않음. 따라서 P@3, 근거 정확도/오추천·투자 GO 판정은 **NOT RUN / INCONCLUSIVE**. 원문·실문헌 ID/실제 검색식/비밀은 공개 GitHub 미기록, 후속 사람 평가를 위해 비공개 자료 보관권리 확인 필요.


## 2026-11-20 EVAL-01 AI 후보 관련성 직접 채점

- 사용자가 AI 자체 채점을 요청. 같은 질문·검색식을 연결된 WIPS/NAS read-only 도구로 다시 읽고, 요약/대표청구항 및 선정된 NAS `get_patent` 원문 일부를 확인해 0/1/2 등급 부여. **비식별 결과** [보고서](docs/evaluation/2026-11-20-eval01-ai-provisional-score.md): WIPS 직접 1/30, NAS 직접 5/30, IN 분야 편향/OUT 0/15, Q04 중복 계열 추정. 실제 문헌 ID·특허 원문·검색식은 공개 GitHub 저장하지 않음.
- 사람의 gold-label 및 전체 원문 대조는 NOT RUN. 초기 vs 추가 읽기의 동일성 및 WIPS 검색식 순위 편향 미통제. 정확도 우위/GO 판정하지 않고 EVAL-01 `AI_PROVISIONAL_SCORED / OFFICIAL_INCONCLUSIVE`로 유지.


## 2026-11-20 WIPS AI 검색 300자 이상 길이 A/B 실증

- 사용자 300자 기술설명 반영. KR-only AI 유사특허 MCP(`get_patent_ai_search`) 10문항×짧은23~29자/긴413~520자, 각 top3 총60 후보 및 WIPS 상세 `get_patent_by_skey` 60회 읽기. [비식별 집계/채점·한계](docs/evaluation/2026-11-20-eval01-wips-ai-300char-ab.md).
- AI 잠정 2점 직접관련 단문6/30, 장문8/30, 무관 U13→0. 장문이 항상 이기지는 않음(개선3·악화2·동일5). 이번 평가는 설명 길이뿐 아니라 구체성도 변했고 KR 단일 국가이므로 과거 다국가 검색의 인과 비교는 금지. 사용자 독립 검증 및 원문/특허법적 최종 판단 NOT_RUN, 운영 NAS/DB·서비스 변경 없음.


## 2026-11-20 EVAL AI 자율 검토 / 검색식 보완 / NAS warm 검증

- 최신 사용자 결정: 별도 사람 채점 불필요. ChatGPT가 직접 핵심 기술·청구항을 리뷰. 정책 근거 [AGENTS](AGENTS.md) 업데이트. 초기 300자 WIPS AI 비교의 Q04/Q05/Q06/Q08 각각 A/B 장문 8회(24후보) 실측, [분석](docs/evaluation/2026-11-20-eval01-targeted-query-rewrite.md) 기록. Q05 두 필수 조건은 여전히 0, 검색 문맥/중의성 문제 확인.
- [EVAL-02 NAS 10문항 동일 검색×2](docs/evaluation/2026-11-20-eval02-warm-nas-replay.md): 순서+청크 10/10 동일, 60 발췌, 추가 근거4/4, NAS reader28회/WIPS0회, AI 근거4/10 재사용, 6/10 근거 부족으로 HOLD. 최초 provider cold 대비 비용·end-to-end 지연은 미측정.
- [순수 판정기](poc/eval02_reuse_policy.mjs) + [합성 테스트](poc/eval02_reuse_policy.test.mjs) Node v22.16.0 **16 PASS**. 기존 로컬 서비스/운영 DB·원문/PDF/벡터를 수정하지 않음. 코드의 실제 운영 워크플로 자동 연결은 NOT IMPLEMENTED.


## 2026-11-20 EVAL-02 실제 NAS Code Mode 연동 E2E

- GitHub에 [fail-closed read-only 어댑터](poc/eval02_live_read_adapter.mjs), [23 테스트](poc/eval02_live_read_adapter.test.mjs) 작성. 기존 16+새23 합성 시나리오 Code Mode V8 **39/39 PASS**(Node CI NOT RUN).
- 연결된 실제 `NAS_RAG.search_patents`+ `get_patent` 도구로 [선별 4문항 라이브](docs/evaluation/2026-11-20-eval02-live-read-adapter-acceptance.md) 실행. Q01/Q04는 청구항·요약 일부와 실제 chunk quote 일치한 AI 직접 관련 재사용, Q05/Q08은 보류. 최신성 요구=provider 호출0으로 차단. 5건 완료 실행 분모 search10/get15/WIPS0. 첫 Q01 false HOLD→요약+청구항 근거 검토 보정 후 성공. provider 오류/불일치 시 fail closed.
- GitHub 문서만 추가, 기존 NAS API·컨테이너·권한·DB·WIPS 영속 자료/원문/벡터·PDF 변경 및 자동 플러그인 등록 **없음**. EVAL-02 실제 비용/시간 ROI, 10개 전 문항 live adapter 자동 라우팅은 미검증.


## 2026-11-20 EVAL-02 전10문항 완주 / 복수 섹션 근거 게이트

- 이전 EVAL02 실제 4문항에 이어 [나머지6문항(Q02,Q03,Q06,Q07,Q09,Q10)](docs/evaluation/2026-11-20-eval02-full10-feature-grounding.md) NAS MCP read-only `search2/detail3` 실제 어댑터 6회 수행: 12+18, WIPS0. Q02/Q03 REUSE, Q06/Q07/Q09/Q10 HOLD. 총10문항 Q01~04 REUSE4, Q05~10 HOLD6. 동일 질문 Top3 문헌·청크 순위 일치, 독립 fulltext hash 검산 미실시.
- [라이브 어댑터](poc/eval02_live_read_adapter.mjs) `requiredFeatures`와 `featureEvidence`로 같은 문헌의 요약/대표청구항 근거를 섹션별로 여러 개 결속. Q01 기존 false HOLD에 대응해 봉지재·끝단·수분 차단 3특성의 출처 인용 검사 **실제 NAS search2+detail3 PASS**. 복수 요구 feature의 가짜 인용/누락/해시 불일치 차단 테스트6개 추가.
- 기존16 + 신규 adapter29 = **V8 Code Mode 합성/계약 45 PASS**. Node/CI·운영 NAS MCP 서버/DB 변경, 권한 확대, 원문/PDF/벡터 신규 저장 미실행. 통제 WIPS COLD 비교·원가·end-to-end 지연 ROI는 INCONCLUSIVE.


## 2026-11-20 WIPS MCP 개인 테스트 계정 read-only smoke 검증

- [실제 3개 MCP 읽기 확인](docs/evaluation/2026-11-20-wips-mcp-read-smoke.md): 검색식2건 PASS, 388자 KR AI 검색2건 PASS, WIPS 반환 문헌 상세 제목/요약/청구항 1건 PASS. 호출 수3, 오류0. 실제 원 응답·문헌ID/초록/청구항·고객 정보는 공개 git에 보관하지 않음.
- 기술상 결론: **개인 환경에서 WIPS MCP 기본 검색·조회 사용 가능**. 고객 계정 권한/망/서비스 백엔드 연동, 공급사 PDF 원본·신규 영속 저장 및 상용 운영 인수 미확인. 별도 NAS RAG 실증을 고객사 연동 완료로 주장하지 않는다.


## 2026-11-20 EVAL-03 두 MCP Code Mode 분기 실연결

- [새 read-only router](poc/eval03_patent_router.mjs), [합성 검증](poc/eval03_patent_router.test.mjs): 기존 EVAL02 search2/detailTop3/citation 검증을 local 근거 게이트로 사용한 후, 확실한 관련 근거 없으면 외부 WIPS 검색을 한 번 실행. 기술적 판단/출처 검증 없이는 무조건 NAS가 반환하는 NN을 보유 특허라고 간주하지 않음.
- 실제 Q01: NAS search2/detail3 결과 관련성·인용 검증 PASS, `SERVED_FROM_NAS_RAG`, WIPS0. 실제 Q06: NAS search2/detail3 직접근거 부족, `SERVED_FROM_WIPS_MCP`, WIPS Boolean search1 top3 PASS. 사용자/고객 내부 질의·실문헌 식별자/발췌·WIPS 원응답 미기록.
- **Code Mode V8 정책16+게이트29+라우터14=59/59 PASS**. Node CI/임의 채팅 상시 자동 라우터·서버 MCP 신규 도구·NAS 또는 WIPS 권한/서비스/DB 변경 **NOT RUN**. 정확 문헌번호 보유 조회 미구현, WIPS 비용/법적 상태/원문 PDF 별도.
