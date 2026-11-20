# P0-4 실행 계획서 — 전체 텍스트·공보 PDF 뷰어

- [설계서](P0-4-design.md) / 의존: P0-3 기존 원문 텍스트 일부 보유, PDF 보기는 [P0-2](P0-2-plan.md) 실제 파일 확보 뒤 활성화.
- 기존 6문헌 중 전체 섹션을 가진 허용 문헌을 먼저 선택해 텍스트 뷰어만 **작게** 운영 적용; 83건 전체 원문이 있다고 가정하지 않는다.

## 단계/구현 파일

| 단계 | 변경 후보 | 사전 검사 | 완료 근거 |
|---|---|---|---|
| 1. 실제 원문 view 범위 | `poc/mvp44_fulltext_acl.sql` | 기존 read role/view `left(...,300)` 및 `section_sources.body` 권한, 실제 문헌 `body_sha256` 확인 | 별도 제한된 전용 reader만 원문 페이지 조회 |
| 2. 페이지 API | `poc/mvp44_fulltext_reader.py` | section enum, Unicode offset, HMAC cursor, 2000 기본/4000 max, principal scope | 시작·중간·끝 페이지 완전 연결, 4001 거부 |
| 3. 작은 읽기 화면 | `poc/mvp44_reader.html`/JS | 개인 HTTPS/tunnel 실제 인증 경로, text-only 렌더 | 사용자 원문 내용·청구항 번호 확인, XSS 차단 |
| 4. 공보 PDF 보기 | `poc/mvp44_pdf_stream.py` | P0-2 file manifest STORED+실파일 해시·공보번호/종류 일치 | PDF 첫/끝 페이지, 정상 Range·파일 미보유=404 |
| 5. 운영 적용/회귀 | 별도 전용 서비스 또는 현재 승인된 API의 좁은 변경 | diff·backup, 기존 NAS/DB/relay/tunnel 재시작 제한 | 실제 인증, GET page, PDF, 기존 search_patents/get_patent 반환 동일 |
| 6. 독립 복구 | 기존 backup script 확장 + 파일 snapshot | DB/파일/role/토큰 별도 | 새 reader 권한 및 파일/manifest 일치, 기존 service fingerprint PASS |

## 필수 실패 시험

- [ ] `readable_evidence`가 300자로 잘린다는 기존 제약 확인; 별도 원문 함수가 body 전체에서 반환하는지
- [ ] 0/1/마지막/초과 offset, 빈 섹션·없는 문헌·원문 없음/영어 fallback
- [ ] 한글/HTML 태그/인라인 스크립트/이모지 렌더 및 원문 byte/hash 불변
- [ ] 잘못된 cursor/위조·만료·다른 사용자/다른 문헌/다른 body_sha256 → denied
- [ ] 다른 DB role/Tailscale 외부 접근/비인가 HTTP → 401/403
- [ ] PDF 부재 상태(현재 0건)에서는 버튼/파일을 반환하지 않음; 확보 시 range 및 파일 sha/mime 검증
- [ ] 원문 10만자 스트림에서 정해진 페이지 cap/timeout/메모리
- [ ] 기존 MCP 5개 도구 및 사설 HTTPS endpoint regression PASS

## 적용/복구 규칙

- 개발 중 기존 `search_patents`/`get_patent` 로직을 전체 원문 반환으로 변경하지 않는다. 새 제한된 도구/endpoint를 분리하고 실패 시 신규 경로만 OFF.
- 기존 reader/모델에 DB body 전체 읽기 권한을 주지 않는다. 잠시라도 공개 endpoint를 생성해 검증하는 방식 금지.
- PDF 아직 없음/권한 확인 실패 시, 텍스트 viewer 완료는 독립 판정하고 PDF viewer 상태는 BLOCKED_DEPENDENCY. "전체 P0-4 완료"라고 주장하지 않는다.
- 전역 위험·재시작 정책과 사용자 실제 업무를 고려해 작은 배포→실사용 확인→핫픽스→백업 복원 순으로 증거 기록.

## 인수 시나리오

사용자가 실제 승인 문헌을 검색 → "전체 상세설명 열기" → 페이지 이동/청구항 전체 → (PDF 확보 시) "공보 PDF 보기". 각 결과에 `source/provider`, `language`, `publication-kind`, `text_status/pdf_status` 표시. **직접 사용자의 원문 열람 경험**을 검증하고, PDF 다운로드 기능이 없는 동안은 미보유로 정확히 표시한다.
