# 데이터 연동·계약 — 초안

WIPS는 문장 기반 특허 검색 및 MCP 연동을 공식 설명한다. 채팅에서 짧은 질의/확장 질의/상세 조회 성공은 별도 앱의 접속 또는 저장 권리를 증명하지 않는다.

| 확인 항목 | 미확인 기본 동작 |
|---|---|
| 독립 MCP client 인증, endpoint, transport | mock만 |
| 상업적/다중 사용자 제공 | 금지 |
| 특허 원문 자동 보존 | 금지 |
| 임베딩 및 자체 DB 재사용 | 금지 |
| 외부 LLM으로 문헌 및 기밀 질의 전송 | 금지 |
| 검색/원문/다운로드 과금 및 동시성 | bounded sequential, live 전 계약 확인 |
| 정책 만료/철회 | 차단, 적법한 삭제/보존 절차 |

공급자별 데이터 권한을 versioned policy로 관리한다. 허가된 공개 또는 합성 fixture로 별도 검증 가능. MCP 연결 방식은 vendor 공식 안내 및 설치 SDK 버전을 검증한 뒤 확정. 비용은 사용자/검색/작업 단위로 측정; 베타 무료를 운영 단가로 가정하지 않는다.

공식 참고 (2026-11-19 확인):
- [WIPS MCP 베타 공지](https://www.wipscorp.com/news-view?id=265)
- [WIPS AI 활용 가이드](https://docs.channel.io/wips-lounge/ko/articles/wintelips-ai-guide-9de41012)
- [WIPS MCP 안내](https://docs.channel.io/wips-lounge/ko/articles/wintelips-mcp-7f649324)
- [MCP Python client transports](https://py.sdk.modelcontextprotocol.io/client/transports/)

## 2026-11-19 후속 검증
[동일 대화 실측 및 확인 요청 항목](17-dual-mcp-workflow.md): WIPS 베타 공지에서 윈텔립스 고객 무료/DB 호출 비용 없음/AI 토큰 별도 소진 확인. 정식 가격 및 별도 계약의 데이터 저장·벡터화·외부 전송·상업 이용은 미확인. 실제 연계는 서로 독립된 일반 주제의 순차 읽기, WIPS 반환을 NAS에 전달하지 않음. 참조 정책 17/17, 아직 서버 통합 미실행. 공급자 문의 미발송.

## 사용자 구매 자료 적재 결정 (2026-11-19)
사용자는 유료 확보 특허 자료 적재를 명시 지시하였다. 개인 NAS 내부 소량 적재 3건만 별도 private DB에서 실증했다. [적재 결과](18-private-patent-ingest.md). 공급사 계약 원문과 상업 이용/대량 동기화/재배포 권리는 미확인. 기존 synthetic MCP 외부 반환 범위는 변경하지 않는다.
