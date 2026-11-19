# 보안 및 NAS 배포 — 초안

```mermaid
flowchart LR
  U[승인 사용자] --> G[운영자 관리 외부 IP 제한]
  G --> H[HTTPS reverse proxy]
  H --> A[웹/API 인증]
  A --> D[(비공개 DB network)]
  A --> W[허용된 외부 검색 API]
  M[관리자 전용 사설 연결] --> O[운영 관리]
```

외부 IP 제어는 별도 L3/네트워크 장비에서 담당. NAS 앱 IP allowlist는 요구하지 않음. HTTPS만 외부 서비스에 사용하며 사용자 인증·권한 유지. DB/API 내부 포트, DSM/SSH는 외부 공개하지 않는다. 기존 공유기/네트워크 정책은 임의 변경 금지. 신뢰되는 proxy header만 사용; secure cookie, CSRF, rate limit, audit metadata, credential 비공개 환경변수/secret. Docker Compose isolated network/volume, 최소 권한, health check, backup/restore 및 이미지/DB migration rollback. 실제 장비·도메인·IP·credential은 공개 repo 밖에서 관리. staging→연동→승인된 경로 배포→허용/차단 외부 클라이언트 실측. 현재 배포 NOT RUN.
