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

실제 자료는 사용자 구매 확인에 따른 개인 NAS 내부 소량 적재 범위로 분리한다. 공개 저장소 원문 보존 및 재배포는 하지 않는다. 기존 기술사 개발 볼륨과 시안 서비스 유지. 작업별 실행 증거를 확인한 뒤 결과를 갱신한다. 개인 터널 및 실제 ChatGPT 도구 호출은 별도 검증이 필요하다.
