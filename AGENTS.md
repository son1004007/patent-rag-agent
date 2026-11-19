# AGENTS.md

## 필수 읽기 순서
전역 Control(접근 가능시 son1004007/ai-agent-workflow-playbook/CONTROL.md 및 registry) → 이 파일 → DOC_INDEX.md → AI_CONTEXT.md → CURRENT_STATE.md → TASKS.md → 관련 문서·최신 commit/PR/실행 증거.

## 문서화 규칙 (필수)
- 모든 신규/이동/삭제 Markdown 문서는 같은 변경에서 DOC_INDEX.md의 링크·한 줄 용도를 갱신한다. 하위 INDEX도 상위에서 연결한다.
- 비개발자용 사업 설명서와 개발 설계서는 분리하되 중요한 흐름·정책 변경은 함께 갱신한다.
- 업무 흐름, 데이터 흐름, 역할 및 의사결정은 GitHub에서 렌더되는 Mermaid 도식과 쉬운 설명을 사용한다. 색상만으로 의미를 전달하지 않는다.
- 각 문서는 목적·대상·상태를 명시한다. CURRENT_STATE/TASKS가 상태 정본이며 인덱스에는 진행률을 중복하지 않는다.
- 문서 인덱스 누락/깨진 상대 링크 검사를 CI에 추가한다.

## 보안 및 구현
공개 repo에는 일반화된 개인 PoC 설계·합성 fixture만 허용한다. 고객 소스·연구 내용·내부 네트워크·credential은 기록하지 않는다. 외부 저장/embedding/LLM 전송/공유는 허가 확인 전 기본 금지. IP 제어는 운영자의 외부 네트워크 장비 책임; NAS에서는 HTTPS와 인증, 서비스 격리 유지. 운영 승인·실행 증거 없는 완료 주장은 금지. 전역 독립 설계 및 최종 리뷰 규칙을 적용한다. 공용 저장소를 기존 trusted runner에 임의 연결하지 않는다.
