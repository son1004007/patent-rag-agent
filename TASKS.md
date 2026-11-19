# Tasks

## P0 — 설계
- [x] 저장소 생성 및 쓰기 권한 확인
- [x] 목차/초안 커밋 및 중앙 registry 연결 검증 (15 문서 조회 및 상대 링크 PASS; Mermaid 렌더 미검증)
- [x] 배포 우선 반복 개발 정책 반영 (독립 AI 검토 선택, AGY/Gemini 제외)
- [ ] (선택) 독립 설계 자문 — 배포 선행 조건 아님
- [ ] 공식 MCP 독립 인증/비용/동시성/저장 권리 확인
## P0.5 — 화면 퍼블리싱 (최우선)
- [x] 가상 자료 기반 반응형 정적 UI (검색/후보 상세/비교/보관소/연구 설정/운영 현황)
- [x] NAS 정적 시안 컨테이너 배포 및 loopback HTML/CSS/JS 응답 검증
- [x] 사설 HTTPS 경로 연결 및 별도 기기 TLS/HTML/CSS/JS HTTP 200 검증
- [ ] 실제 브라우저 UI 동작 확인
- [ ] 사용자 화면 확인 및 피드백 반영 후 실제 기능 구현
## P0.6 — ChatGPT MCP 우선 검증 (최신 사용자 결정)
- [x] README/아키텍처 단순화 및 기존 기술사 RAG DB/SDK 현황 확인
- [x] 합성 문서 MCP save/get/부분문자열 search 및 중복/ID scope/conflict 검증 (ASGI 일회성; [실측](docs/09-mcp-contract-smoke.md))
- [x] 실제 pgvector SQL 검색/저장 및 DB 도메인 격리 시험 (합성 384D, 18/18 PASS; [실측](docs/10-shared-vector-smoke.md))
- [x] MCP→pgvector 통합 및 로컬 E5 실제 임베딩 검증 (24/24 PASS; [실측](docs/11-mcp-vector-integration.md); 합성 ASGI/임시 DB)
- [x] 합성 전용 지속 실행 MCP 서버 및 실제 HTTP·인증·영속 저장/복원 검사 (초기/재시작 각16/16 PASS; [실측](docs/12-persistent-mcp-stage.md))
- [ ] HOLD — NAS/daemon 및 기존 컨테이너 실제 재기동·자동 시작 등록/실증 (사용자 별도 승인 필요; 순차 기동 스크립트 --check PASS)
- [x] Secure MCP Tunnel NAS 측 준비 (공식 CLI v0.0.21 설치 및 Unix socket 14/14 PASS; [실측](docs/13-secure-tunnel-preflight.md))
- [x] 사용자 runtime key 생성 및 Gateway saved metadata 확인 (값 미조회, 권한/유효성 미검증)
- [x] 개인 tunnel_id 생성/확인, Gateway key 파일 안전 전달 및 실제 터널 인증/doctor/polling 검증 ([실측](docs/13-secure-tunnel-preflight.md))
- [x] ChatGPT 개인 플러그인 생성/설치 및 실제 write/get/vector search E2E; 신규 INSERT, 중복/미승인 차단, USER/PRIVATE 확인 ([실측](docs/14-chatgpt-plugin-e2e.md)); 합성 전용, 외부 공개 금지
- [x] 신규 P4 포함 최신 온라인 백업 및 별도 클러스터 복원/ACL/index 검증 ([실측](docs/15-online-backup-startup-plan.md)); 기존 전 서비스 재기동 없음
- [x] 순차 기동 스크립트 작성 및 read-only --check PASS
- [ ] HOLD — 실제 NAS 재기동 및 자동 시작 검증 (위 사용자 승인 조건과 동일)
- [ ] 공용 pgvector 엔진 별도 DB/role 운영·복원·부하 검증 (현재 기술사 배포 차단 우회 금지)
- [ ] WIPS와 자체 MCP의 동일 대화 연동 (저장/전송 권리 확보 전 synthetic-only)
## P1 — Mock MVP (MCP 실증 이후; 독립 웹 Agent 대체안)
- [ ] FastAPI/UI, 계정·profile, 합성 데이터
- [ ] 원문과 300자 확장 생성, 검색 계획 검증, mock provider
- [ ] 결과 합치기/중복 제거/RRF/재정렬 및 근거 표시
- [ ] 승인된 corpus 자동 ingest 및 pgvector
- [ ] 검색 평가·비용·지연 측정, 인덱스/링크 검사 CI
## P2 — Live PoC
- [ ] 승인된 MCP 인증 및 LLM 연동 E2E
- [ ] A/B/C/D 검색 품질 평가 (연구자 검토)
- [ ] 저장권 확보 시 실제 자료 자동 적재 E2E; 미확보 시 공공/합성 자료만
## P3 — NAS
- [ ] 격리 Docker staging, 필수 최소 점검 및 rollback 준비
- [ ] 시범 배포 후 실제 환경 테스트 → 결함 수정/재배포 반복
- [ ] HTTPS 및 로그인·사용량 제한, 외부 네트워크 경계 확인
- [ ] 승인된 서비스 배포, 허용/비허용 접근 시험, 운영문서 갱신

## P4 — 구현 완료 후 문서
- [ ] 실제 화면 기반 간결한 사용자 설명서
- [ ] 관리자 설명서: 시스템 설계, 데이터·권한, 운영·복구 흐름
