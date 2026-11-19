# 검증 계획 — 초안

| 영역 | 테스트 |
|---|---|
| Query expansion | 짧은 입력, profile 변경, 허위 수치 금지, 원문 보존 |
| Provider | mock/live 분리, 429/timeout/동시 요청/NOT_FOUND, budget |
| Ranking | 중복, score 단위 차이, label 평가 및 중요 결과 누락 |
| Ingest | default deny, 부분 권한, 중복/재시도, 취소/expiry |
| Security | 인증·권한, CSRF, prompt injection, 비밀 및 로그, SSRF 방지 |
| DB | migration, idempotency, grant, backup/restore |
| Deployment | HTTPS, 인증서·redirect, 외부 IP 차단(운영자 장비), DB 비공개, rollback |
| Docs | 목차 누락, 상대 링크, Mermaid 렌더 확인 |

각 실행을 PASS/FAIL/NOT RUN/BLOCKED로 기록. 독립 설계/최종 리뷰 및 finding 조정 별도. 지금은 모든 구현·배포 테스트 NOT RUN.
