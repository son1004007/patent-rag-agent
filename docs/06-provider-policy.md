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
