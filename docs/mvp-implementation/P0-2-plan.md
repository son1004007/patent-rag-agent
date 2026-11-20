# P0-2 실행 계획서 — 특허 공보 PDF 수집 경로와 NAS 적재

- [설계서](P0-2-design.md) / 현재 실측: WIPS MCP 직접 PDF 미제공, 공보 PDF **0건**
- 작업 성격: **선행 확인이 필요한 개발**. PDF API 인증/상품·정확한 endpoint를 추정해서 구현하지 않는다.

## 단계별 작업 · Stop/Go 게이트

| 단계 | 사전 확인 | 구현 파일(안) | 운영 적용/통과 기준 |
|---|---|---|---|
| 1. 공식 서비스 범위 조사 | [KIPRIS Plus 공보 REST](https://plus.kipris.or.kr/portal/data/service/DBII_000000000000001/view.do) API 명세·호출 자격/이용약관 및 개인 NAS 보관 사용권; WIPS 별도 파일 공급 여부 | `docs/mvp-implementation/P0-2-design.md` 결정표 갱신 | **KEY_AVAILABLE / RIGHTS_OK / API_SPEC_VERIFIED**를 구분. 없으면 해당 공급자 HOLD, 미승인 결제·키 발급 추측 금지 |
| 2. 매칭 규칙 | 기존 83건 서지 중 승인된 KR 문헌 1건(실제 번호는 NAS에서만 다룸) | `poc/pdf_provider_kipris.py` | KR 국가+공개/등록 번호+종류 exact; 모호하면 IDENTITY_HOLD |
| 3. 응답·파일 시험 | 공식 REST 1건에서 다운로드 경로 반환 확인 → 동일 호스트/공식 redirect 정책 | `poc/pdf_acquire.py` | 실제 PDF magic·페이지·크기·번호/종류·공급자 확인, PDF 파일 자체가 맞는지 검증 |
| 4. 별도 manifest/스토리지 | 기존 운영 DB ACL/백업·NAS 파일 볼륨·disk quota 사전 점검 | `poc/pdf_manifest.sql` | additive migration, 비공개 파일 업로드 1건, SHA/권리/취득시각 기록. 기존 reader·원문 테이블 변경 없음 |
| 5. 실패/재실행 검증 | 합성 malformed/URL 공격·실제 같은 문헌 1회 재조회 | `poc/pdf_acquire_test.py` | SSRF/HTML/PDF 위조·20MiB 초과·kind 불일치·auth 거부, 실제 재다운로드0, 반쪽 성공 복구 |
| 6. 독립 복원·사용자 검토 | DB dump + 비공개 파일 object snapshot, credential 분리 | 복구 스크립트 보완 | 완전 복원 뒤 manifest SHA와 파일 SHA 동일, 인증 없이 조회 거부 |
| 7. EP/기타 국가 확대 | EP 필요 + EPS REST 공식 제한 확인 | `poc/pdf_provider_epo.py` | EPS `cc/pn/ki`와 5GB/7일 정책, KR와 별도 통계/권한 |

## TDD/계약 테스트 (실자료를 공개하지 않음)

- [ ] 정상 KIPRIS XML → 링크 형태 파싱/URL 허용/문헌키 exact
- [ ] URI 파라미터·호스트 변경/내부 IP/redirect/장애 응답 거절
- [ ] `text/html`, 잘못된 `%PDF-`, 암호화/손상 PDF, 파일중단/timeout, disk full
- [ ] KR-A vs KR-B, 같은 패밀리 다른 문헌을 잘못 결합하지 않음
- [ ] 파일 첫 저장 + 동일 재사용 + 내용 변경 시 revision 처리
- [ ] PDF 파일 보존 성공과 `section_sources/chunks` 미수정 확인
- [ ] 독립 백업·복원 후 file bytes SHA 일치
- [ ] 사용자 열람은 P0-4에서 구현, 이 단계는 인증된 내부 위치에서 원본 PDF 자체 확인까지

## 장애 발생 시 해결 순서

1. API 응답 401/403/계약 불명 → endpoint 변경·스크래핑 금지, **AUTH_REQUIRED** 기록.
2. XML 다운로드 경로 200인데 파일 응답 HTML → 응답 인증/유효기간 확인, magic 실패 처리 및 파일 폐기.
3. kind/번호 다름 → 저장 보류, 공보/등록/출원 번호 정규화·공식 원문 첫 페이지로 재확인.
4. 파일은 저장됐는데 DB commit 실패 → 임시 object 격리, 해시 일치 재연결 또는 안전 GC; 성공 주장 금지.
5. 기존 컨테이너/DB에 영향 감지 → 신규 다운로드 경로만 disable, 기존 서비스/데이터는 유지.
6. 서비스가 PDF 제공하지 않는 것으로 확정 → **지원 중인 공식 대안으로 분기**, 전체 MVP를 무기한 가짜 진행으로 두지 않음.

## 완료 기록 항목

`status=STORED`(실제 1건), provider/source/rules/version, bytes/SHA 검증 결과(비밀·실문헌 ID 공개금지), duplicate0, invalid/unauthorized blocked, NAS 파일과 DB dump 독립 복원, 기존 데이터/서비스 불변 및 미실행 항목 명시. KEY/RIGHTS가 미확인인 경우 **스펙/adapter 작성은 가능하더라도 실제 PDF 확보 완료 불가**.
