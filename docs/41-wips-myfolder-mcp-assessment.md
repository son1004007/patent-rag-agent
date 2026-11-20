# WIPS MyFolder MCP 별도 서비스 검토 (2026-11-20)

- 목적: WIPS 검색 MCP와 **WIPS MyFolder MCP**를 구분하고, NAS 자동 저장·PDF/원문 RAG 통합에 실제 사용할 수 있는지 판정.
- 결과: **별도 서비스 존재 공식 확인 / MyFolder MCP의 실제 사용자 계정 호출 NOT RUN / 연결 미확인**. 현재 프로젝트 운영/데이터/연결 변경 없음.
- 정본: [WIPS 28개 검색/상세 도구](40-wips-mcp-capability-catalog.md), [P0-1 설계](mvp-implementation/P0-1-design.md), [현재 실행 목록](../TASKS.md).

## 1. 확인된 사실과 증거의 수준

| 항목 | 확인 결과 | 근거 |
|---|---|---|
| **WIPS 검색 MCP** | 현재 개인 `wipsclip` 플러그인으로 검색·상세 조회 도구 28개 노출, 검색/명세서 응답 실증 | 실제 ChatGPT 연결 도구 및 [기존 카탈로그](40-wips-mcp-capability-catalog.md) |
| **WIPS MyFolder MCP** | WIPS가 **2026-10-12** 검색 MCP와 별도 서비스로 공식 발표. 윈텔립스 MyFolder에 저장해 둔 관심 특허를 AI 분석에 활용 | [WIPS 베타 공지](https://www.wipscorp.com/news-view?id=265), [WIPS 공식 소개](https://docs.channel.io/wips-lounge/ko/articles/wintelips-mcp-7f649324) |
| MyFolder 도구 이름 | `myfolder_list_folders`(폴더 이름/건수), `myfolder_get_folder_skeys`(지정 폴더 문헌 SKEY 페이지 조회) | [외부 MCP 앱 목록](https://mcp-app-store.keenethics-labs.com/app/wips-myfolder), **제3자 정보이며 실제 WIPS 도구 정의/계정 호출로 재확인 필요** |
| MyFolder MCP 권한 | 외부 앱 목록은 **읽기 전용**: 폴더 생성·수정·삭제/폴더에 특허 추가·공유 지원하지 않는다고 설명. 제목/요약/청구항 직접 반환도 제외 | 같은 제3자 목록. **실제 연결 권한은 연결 후 검증** |
| WIPS 웹 MyFolder | 윈텔립스 사이트에서 특허·검색식·검색이력과 폴더 관리가 가능. **웹의 쓰기 기능 ≠ MCP 쓰기 기능** | [WIPS 공식 온라인 서비스 안내](https://www.wipscorp.com/online/page01), [WIPS 공식 MyFolder 설명](https://docs.channel.io/wips-lounge/ko/articles/wintelips-mcp-7f649324) |
| 연결 조건 | 윈텔립스 고객 대상 베타; MCP 신청 → WIPS 발급 키 → AI MCP 연결. 별도 MyFolder API 권한/키 요구 여부 실제 사용자 확인 필요 | [WIPS 공식 공지](https://www.wipscorp.com/news-view?id=265), 외부 앱 목록 |
| 이 계정에서 조회된 개인 플러그인 | 소유 개인 플러그인 **wipsclip / NAS RAG** 2개, WIPS MyFolder 별도 개인 플러그인은 목록에 없고 현재 연결 도구에도 `myfolder_*` 노출 없음 | 이번 대화 ChatGPT 연결/플러그인 메타데이터 직접 조회, 2026-11-20 |
| 공보 PDF/본문 파일 | MyFolder MCP에서 PDF 바이트/공보 다운로드·본문/임베딩 제공은 **현재 확인되지 않음** | 공개된 MyFolder MCP 도구 2개 범위. 추가 미공개 기능 존재를 부정하는 근거는 아님 |

공식 2026-10-12 발표 당시 **윈텔립스 이용 고객 베타 무료**, AI 사용 토큰은 별도이며 정식 요금·기간·지원 범위는 변경될 수 있다고 명시되어 있다. **현재 계정의 실제 계약/접근 권한을 검증한 것은 아니다.**

## 2. P0-1 자동 보관과의 관계

| 업무 요구 | 사용해야 하는 도구/기술 | MyFolder MCP로 단독 해결 가능한가 |
|---|---|---|
| 자연어로 새 특허 검색 | 기존 WIPS 검색 MCP | **아니오**, MyFolder는 이미 저장해 둔 폴더 목록 출발 |
| WIPS 새 검색 결과를 NAS에 자동 저장 | 기존 P0-1 검색→local writer/통합 bridge | **아니오**, 폴더 MCP 읽기만으로는 새 검색 결과를 가로채거나 NAS DB를 쓰지 못함 |
| 이미 윈텔립스 MyFolder에 분류해 둔 특허 일괄 가져오기 | **MyFolder MCP → SKEY 목록 → 기존 WIPS 검색 MCP 상세·서지 → NAS 저장기** | **보조 입력원으로 활용 가능**. 실제 MyFolder 연결/페이지·ID 계약 테스트 이후에만 |
| 전체 청구항·상세설명 확인 | 기존 WIPS `get_patent_spec_text` 등 | MyFolder의 식별자를 **WIPS 검색/상세 도구에 전달**해야 함 |
| 공보 PDF 수집 | P0-2 공식 PDF 제공처 | **MyFolder MCP에는 PDF 도구 확인 안 됨** |

### 선택적 MyFolder → NAS 입력 흐름 (P1 후보, 아직 미구현)

```mermaid
flowchart LR
 A[WINTELIPS MyFolder] --> B[별도 MyFolder MCP read only]
 B --> C[선택 폴더 SKEY 페이지 목록]
 C --> D[WIPS 검색 MCP 식별자 대조]
 D --> E[서지 최대100건/승인 범위]
 E --> F[NAS patent_archive writer]
```

- 먼저 `myfolder_list_folders` 응답이 실제 계정 권한 내 폴더명/건수를 반환하는지 확인.
- 다음 `myfolder_get_folder_skeys`의 페이지 크기/응답 구조/목록 고유성, 폴더 이름 exact matching을 확인.
- SKEY만으로 파일·전체 원문을 저장했다고 처리하지 말고 기존 WIPS 검색 도구에 식별자 검색해 국가·번호·종류를 일치시킨 후 **서지 7필드**만 기존 운영 인제스터에 전달한다. 기존 최대100·중복·권리 경계 유지.
- MyFolder 내용을 NAS에 가져오는 것은 사용자가 실제 요청했을 때의 **추가 import 경로**이지, P0-1의 **새 WIPS 검색 자동 저장 완성**을 대체하지 않는다.
- 폴더 목록에는 연구 주제·프로젝트명이 노출될 수 있으므로 공개 GitHub·로그에 실제 폴더 이름/SKEY를 기록하지 않는다.

## 3. 다음 단계 판단

1. 현재 **WIPS MyFolder MCP는 연결되지 않은 것으로 관찰**됨. 별도 WIPS 키와 윈텔립스 MyFolder 계정/서비스 사용권 확인 후, 사용자가 연결하면 실제 두 도구의 schema·폴더 목록·1페이지 SKEY 조회를 **읽기 전용**으로 검증한다.
2. **P0-1은 기존 설계대로 우선 실행**: 현재 ChatGPT WIPS 검색 ↔ NAS 서지 writer의 보장되는 연결 도구/호출자 구조 확정. MyFolder 추가 연결을 P0-1 필수 선행 조건으로 만들지 않는다.
3. MyFolder 도구 2개의 실제 호출이 확인되면 P1 선택 작업(큐레이션 폴더를 NAS에 import, 태그/폴더 멤버십 보존)으로 별도 계획. *WIPS 웹 MyFolder의 저장/폴더 쓰기를 MCP 기능으로 추정하지 않는다.*

**검증 상태:** 공식 별도 서비스 존재 CONFIRMED; 외부 카탈로그 도구 설명 VERIFIED_AS_THIRD_PARTY_REFERENCE; 실제 MyFolder MCP tool availability/response E2E NOT RUN; 사용자 플러그인 신규 설치/인증/변경 NOT RUN; NAS·DB 운영 변경 NONE.

## 4. 2026-11-20 실제 설치 후 검증 결과 (최신)
- 사용자 WIPS MyFolder 플러그인 추가 이후 **현재 ChatGPT에서 실제 `mcp__WIPS_MyFolder__myfolder_list_folders`, `mcp__WIPS_MyFolder__myfolder_get_folder_skeys` 두 개의 도구 노출 확인**. 이 연결은 과거 섹션의 "미연결" 상태를 대체한다. 연결/도구 노출과 인증·실데이터 조회 성공은 구분한다.
- `myfolder_list_folders({})` **실제 호출 실패**: 서버 반환 문구 "아이디/비밀번호를 확인해 주세요. 자격증명이 맞다면 마이폴더가 아직 생성되지 않은 계정일 수 있습니다." 따라서 자격증명 불일치 또는 폴더 미생성 가능성을 공급자 응답 수준에서만 확인. 어느 쪽인지 **미확정**. 비밀번호/토큰 조회·출력·공유 없음.
- `myfolder_get_folder_skeys`는 유효한 실제 폴더명이 확인되지 않아 **미실행**. MyFolder의 실제 폴더/SKEY 수집 E2E는 **BLOCKED_AUTH_OR_EMPTY_FOLDER**, 저장/쓰기 수행 없음.
- 기존 별도 NAS RAG `mcp__NAS_RAG__search_patents(query, limit=1)` 실제 호출 **1건 PASS**; 결과에 `document_id,publication,country,kind,title,source_sha256,excerpt,chunk_sha256,distance` 등의 근거 필드 존재. 식별자/실제 텍스트는 로그·공개 문서에 쓰지 않음.
- 기능 차이 확인: MyFolder는 기존 폴더/목록/SKEY를 제공하는 **읽기 전용 2개 도구**, NAS RAG는 별도 **5개 도구**(`save_document,get_document,search_documents,search_patents,get_patent`). `save_document`는 승인된 **합성 테스트 fixture 전용**, 구매 특허 원문 운영 적재를 MyFolder나 이 도구가 수행한다고 오해하지 않는다. 기존 원문 운영 적재는 별도 승인 NAS writer 경로를 사용.
- 다음 확인은 사용자가 윈텔립스 자격증명과 MyFolder 생성 상태를 본인 화면에서 점검한 후 `list_folders` 읽기 재시험 → 반환한 정확한 폴더명으로 `get_folder_skeys` 한 페이지 시험. 현재 WIPS 검색→NAS 자동 보관 P0-1의 선행조건으로 삼지 않는다.
