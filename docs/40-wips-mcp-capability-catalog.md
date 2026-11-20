# WIPS MCP 제공 데이터·도구 전체 목록 및 특허 RAG 구현 현황

- **확인일:** 2026-11-20
- **대상:** 개발자, 운영자, 다른 AI, 연구 사용자
- **검증 근거:** 현재 ChatGPT에 연결된 `wipsclip` 도구 정의 28개 전체 확인 + 실제 검색/`spec_text`/`section` 호출 구조 확인 + [운영 적재 인수](39-mvp-archive-100-live-acceptance.md)와 [원문 적재 인수](35-mvp03-actual-ingest-acceptance.md)
- **범위:** *현재 ChatGPT에 노출된 WIPS MCP 인터페이스*. WIPS 제품/유료 API/브라우저 기능 전체에 대한 부존재 증명이 아니다. 28개가 모두 운영 앱에 통합되어 있거나 실제 호출 검증된 것은 아니다.
- **상태 정본:** [CURRENT_STATE](../CURRENT_STATE.md), [TASKS](../TASKS.md). 본 문서는 기능 카탈로그 및 구현 갭 설명; 원시 특허 텍스트·특허 ID·계약정보·비밀은 공개 저장소에 기록하지 않는다.

## 1. 결론: MCP 반환값과 NAS 파생데이터는 다르다

| 데이터 / 기능 | 현재 WIPS MCP | 실제 확인 범위 | 현행 NAS |
|---|---|---|---|
| 키워드/필드 검색 및 메타데이터 | `get_patent_search_onlyengine` | 실제 WIPS 83건 반환 및 운영 NAS 저장 PASS | **83건 서지정보** (국가·번호·종류·제목·출원인·문헌일·SKEY), 검색 페이지 1개 |
| AI 유사 특허 후보 검색 | `get_patent_ai_search`, `get_patent_aisearch_num` | 도구 정의 확인. 개별 최신 결과·정확도 미검증 | 별도 통합·상시 비교 미완료 |
| 명칭/요약/대표청구항 | `get_patent_by_skey` 또는 검색 결과의 `ABK`/`CLK` | 응답 필드/형태 확인 | 기존 허용 문헌 일부 보존 |
| 상세설명/전체·독립청구항 등 | `get_patent_spec_text` | 실제 `dtl_desc_list`, `cl_list` 구조 확인 | **기존 문헌 6건, 원문 섹션 10개**. 83건에 대해 자동 본문 수집하지 않음 |
| 도면 | `get_patent_section`의 `draw`/`indv_draw` | 대표/개별도면 **경로 문자열**과 도면 설명 확인; 이미지 바이트 다운로드는 미검증 | 도면 파일 보관 기능 미구현 |
| 분류·패밀리·인용·권리/심사/소송/출원계보 등 | 아래 총 28개 도구 중 전문 조회 도구 | 도구 정의 확인, 개별 결과·국가별 충족률 미검증 | 통합 보존·색인 미구현 |
| **특허 공보 PDF 바이너리/다운로드** | **전용 도구 노출 없음** | 검색/`spec_text`/`draw`/`indv_draw` 실제 응답에서 PDF 바이트나 PDF URL 확인되지 않음 | **0건**. WIPS 다른 상품/API 또는 공식 공보 제공기관 경로 확인 필요 |
| **청크 분할** | **제공 기능 아님** | WIPS 텍스트를 NAS 로컬 코드로 분할 | 기존 **417개 텍스트 청크** |
| **벡터 임베딩** | **제공 기능 아님** | NAS 로컬 `multilingual-e5-small` (384차원) 이용 | PostgreSQL + pgvector에 기존 **417개** |

**정확한 해석:** MCP는 JSON 형태의 식별정보·텍스트·참조 경로를 제공한다. PDF 파일을 직접 전달하거나 청크/벡터를 생성하는 것은 현재 노출된 MCP의 기능이 아니다. 저장된 서지 83건과 본문·벡터가 있는 기존 6건은 **서로 다른 집계**이며, 중첩 여부를 근거 없이 추정하거나 83건의 임베딩이 완료됐다고 간주하지 않는다.

## 2. 현재 노출된 28개 WIPS MCP 도구 — 빠짐없는 카탈로그

검증 표기: **실제 호출 확인**은 이 대화 및 운영 기록에서 구조/결과를 실측한 대표 도구만, **정의 확인**은 도구가 노출됐다는 뜻이지 해당 기능의 반환/품질/비용이 검증됐다는 뜻이 아니다. 실제 사용 가능 필드·국가·수집 한도는 각 도구의 연결된 정의를 따른다.

| 영역 | MCP 도구 | 주요 획득 정보 | 검증 수준 |
|---|---|---|---|
| 검색 | `get_patent_search_onlyengine` | 검색식 기반 문헌 목록, 서지/옵션 선택 텍스트 필드, total_count/row_list | **실제 호출 및 83건 목록 적재** |
| 검색 | `get_patent_ai_search` | 키워드·문장 기반 WIPS 유사도 검색 (KR/JP/US/CN/EP/PCT) | 정의 확인 |
| 검색 | `get_patent_aisearch_num` | 지정 문헌번호 기반 AI 유사 특허 검색 | 정의 확인 |
| 검색 보조 | `get_patent_search_guide` | 검색식 작성 가이드: basic/biblio/advanced/num_search | 정의 확인 |
| 기본 문헌 | `get_patent_by_skey` | 단일 SKEY의 명칭·요약·대표청구항 | 정의 확인 |
| 명세서 | `get_patent_spec_text` | 명칭·요약·청구항·상세설명·해결과제·수단 | **실제 상세설명·청구항 응답 확인** |
| 명세서·도면 | `get_patent_section` | 배경기술·기술분야·효과·도면/설명·정정·Certificate 등 | **실제 draw/indv_draw 경로·설명 확인** |
| 분류 | `get_patent_category` | 현재/원래 CPC·IPC, F-term/FI/USPC, 디자인/로카르노 분류 | 정의 확인 |
| 인용 | `get_patent_citn` | 인용·피인용, 설명상 문헌 인용, EP/국제 인용 | 정의 확인 |
| 패밀리 | `get_patent_family` | WIPS 확장 패밀리·EPO simple 패밀리·법적 상태 | 정의 확인 |
| 인명 | `get_patent_person` | 출원인·발명자·대리인·심사관·대표출원인 | 정의 확인 |
| 출원 부가 | `get_patent_apply_misc` | 국가별 키워드·연구과제·유사문헌·조사분야·예외 등 | 정의 확인 |
| 출원 계보 | `get_patent_related_appl` | 출원/공개/등록번호·일자, 관련·분할·우선권 정보 | 정의 확인 |
| 국제출원 | `get_patent_intl_appl` | PCT 국제출원과 지정국 | 정의 확인 |
| 행정 | `get_patent_admin_history` | 출원·심사·행정 기록과 국가별 권리상태 | 정의 확인 |
| 심사 | `get_patent_office_action` | 심사청구·의견제출·거절·재심사·이의 등 | 정의 확인 |
| 권리 공통 | `get_patent_rights` | 현재권리자, 양도·변동, 만료·연차료 | 정의 확인 |
| KR 권리 | `get_patent_kr_rights` | 실시권·설정/변동·권리자 | 정의 확인 |
| CN 권리 | `get_patent_cn_rights` | 중국 양도·라이선스·질권 | 정의 확인 |
| US 권리 | `get_patent_us_rights` | 미국 Assignment·PTA | 정의 확인 |
| EP 법적상태 | `get_patent_ep_history` | 유럽 심사 절차/지정국·EPO Legal Status | 정의 확인 |
| KR 심판 | `get_patent_kr_trial` | 한국 심판 유무·이력·내용·관계인·인용 | 정의 확인 |
| JP 심판 | `get_patent_jp_trial` | 일본 심판·정정·관계인·소송 | 정의 확인 |
| EP 심판 | `get_patent_ep_trial` | 유럽 이의신청·심판·관련 기록 | 정의 확인 |
| US 심판 | `get_patent_us_trial` | BPAI/PTAB 심판·관계인·인용·docket | 정의 확인 |
| US 심사 | `get_patent_us_exam_history` | 미국 AIA·사업체 지위·행정/심사 이력 | 정의 확인 |
| US 소송 | `get_patent_us_litigation` | 미국 소송 기록·당사자/사건·docket | 정의 확인 |
| US 의약 | `get_patent_orangebook` | 미국 FDA Orange Book 제품·독점권·관련 특허 | 정의 확인 |

**전체 28개 확인**. 각 도구의 `section` 종류는 국가·문헌·제공자 데이터 유무에 따라 비어 있거나 지원되지 않을 수 있다. 별도 도구가 노출됐다는 사실만으로 기능을 전수 운영 수집하도록 권장하지 않는다.

### 2.1 상세 조회 section 인덱스 (실제 필드명)

| 도구 | 가능한 `section` 값 |
|---|---|
| `get_patent_spec_text` | `inv_ti` (명칭), `ab` (요약), `rept_claim` (대표청구항), `all_claim` (전체청구항), `indp_claim` (독립청구항), `dtl_desc` (발명의 설명), `prb` (해결과제), `sol` (해결수단) |
| `get_patent_section` | `bckg_tech` (배경기술), `tech_fld` (기술분야), `inv_eff` (발명효과), `inv_smry` (발명요지), `exe_mthd` (구체실시방식), `draw` (대표도면), `indv_draw` (개별도면), `correct` (정정), `certificate` (발행이력), `jp_prcd_pttn` (일본 수속보정) |
| `get_patent_category` | `cur_cpc`, `cur_ipc`, `cur_f_term`, `cur_fl`, `cur_us_cls`, `org_cpc`, `org_ipc`, `org_f_term`, `org_fl`, `org_us_cls`, `locarno`, `dcsn_cls` |
| `get_patent_citn` | `backward`, `forward`, `desc`, `ep`, `intl` |
| `get_patent_family` | `wips_fmly`, `epo_fmly`, `legal_stts` |
| `get_patent_person` | `agt`, `appt`, `examn`, `invt`, `rept_applicant` |
| `get_patent_related_appl` | `num_dt`, `rel_appl`, `org_appl`, `erlr_appl`, `in_add_div`, `pr`, `pr_back` |
| `get_patent_rights` | `assn_hist`, `crrt_assn`, `exist_assn`, `exts_rght`, `fee_grt`, `grt_expiry_date`, `std_assn` |
| `get_patent_admin_history` | `apply_history`, `stts`, `au_adm_info`, `cn_legal_history`, `kr_adm_info`, `kr_final_exam` |
| `get_patent_office_action` | `au_oppnt`, `exam_req`, `opinion_info`, `preexam`, `reexam`, `refusal_stts`, `refuse_info`, `rfs_noti_num` |

나머지 국가별 세부 section은 각 도구 명세를 우선하며, 위 목록이 전체 특허 DB의 데이터 항목을 보장하지 않는다.

## 3. 실제 응답 구조 (합성 예시 / 실제 호출 형태)

### 3.1 검색 (서지정보 기본)

```json
{
  "success": true,
  "data": {
    "total_count": 83,
    "row_list": [
      {
        "SKEY": "SYNTHETIC_PROVIDER_KEY",
        "XN_D": "SYNTHETIC_PUBLICATION_NUMBER",
        "CC": "KR",
        "KC_D": "B1",
        "TIK": "예시 발명의 명칭",
        "APSTH": "예시 출원인",
        "XD": "20250101"
      }
    ]
  }
}
```

- `total_count`는 **검색 조건에 부합한 전체 건수**, `row_list`는 **현재 페이지 반환 건수**다. 위 JSON의 목록 길이는 1개짜리 형태 예시이고, 83건 실조회는 별도 운영 실측.
- `outitem`에 `ABK`(요약), `CLK`(대표청구항), `CLIK`(독립청구항) 등을 명시하면 제공되는 국가/데이터에 한해 검색 목록에서 추가 텍스트를 반환할 수 있다. **NAS의 83건 아카이브는 서지 7개 필드만** 수집했으므로 검색에서 응답 가능한 다른 텍스트까지 저장된 것은 아니다.
- WIPS 도구 자체는 지정 출력 필드/텍스트 크기에 따라 최대 500 또는 50 결과의 페이지 반환 조건이 있다. **우리 애플리케이션 정책은 검색당 첫 페이지 최대 100건**이며 WIPS 서비스의 일반 상한으로 오해하면 안 된다.

### 3.2 본문·청구항·도면

| 호출 | 실제 응답 필드 | 해석 |
|---|---|---|
| `get_patent_spec_text(section="dtl_desc", skey=...)` | `data.dtl_desc_list[].dtl_desc` 및 `lang_cd` | 상세설명 원문 **텍스트**. 언어 요청이 없거나 해당 언어가 없을 때 fallback 가능 |
| `get_patent_spec_text(section="all_claim", skey=...)` | `data.cl_list[].cl_num`, `data.cl_list[].cl` | 전체 청구항 **텍스트** 및 번호/배열 |
| `get_patent_section(section="draw", skey=...)` | `data.rept_draw`, `data.org_content_src` | 실제 표본은 대표도면 **파일 경로 문자열**; 이미지 바이너리 아님 |
| `get_patent_section(section="indv_draw", skey=...)` | `data.indv_draw_list[].draw`, `data.draw_desc`, `data.draw_sign_list` | 실제 표본은 개별도면 경로/설명/부호. URI 접근·바이너리 파일 다운로드 **미검증** |

이 실측에서 PDF 파일, PDF 다운로드 URL 또는 base64 PDF 반환을 확인하지 못했다. `org_content_src`는 호출 표본에서 비어 있었으나 다른 특허에서 반드시 비어 있다고 단정하지 않는다. 대표도면 경로를 공보 PDF 경로로 오인하지 않는다.

## 4. 실제 NAS 구현 상태와 잔여 기능

| 영역 | 현행 구현 | 증거·코드 | 아직 구현/검증할 것 |
|---|---|---|---|
| ChatGPT↔WIPS MCP | 도구 직접 호출 가능; 실제 검색·명세서/청구항 및 도면 조회 구조 확인 | 이 문서 2·3절; [검색 계획](23-mvp03-research-flow.md) | 한 앱 엔드포인트에서 WIPS 검색+NAS 저장을 자동으로 호출하는 도구/오케스트레이터 |
| 검색 목록 보관 | **운영 서지 83건**, 검색당 최대100, 100건 CHECK, 중복 재실행 신규0, 별도 writer/운영 policy | [실제 인수](39-mvp-archive-100-live-acceptance.md), [저장모듈](../poc/mvp37_archive.py), [전송모듈](../poc/mvp37_local_transport.py) | ChatGPT가 WIPS 도구만 단독 호출한 경우에는 **자동으로** NAS에 보내지지 않음. 통합 도구/실사용 새 채팅 E2E 필요 |
| WIPS 본문 추출 및 증분 적재 | 승인된 일부 문헌의 WIPS 텍스트·청구항 저장, 해시/중복·정책·실제 운영 시험 | [실제 단건](35-mvp03-actual-ingest-acceptance.md), [증분](22-mvp02-incremental-patent-ingest.md), [적재기](../poc/mvp03_ingest_adapter.py) | 나머지 검색 목록의 본문 보유 상태 확인, 문헌별 원문 처리 권리/비용에 맞춘 승인 범위의 수집·재실행 회복 |
| NAS 청크·벡터 | **6문헌/10섹션/417청크**, `multilingual-e5-small`, 384차원, pgvector | [실제 인수](35-mvp03-actual-ingest-acceptance.md), [벡터 통합](11-mcp-vector-integration.md) | 신규 승인 본문 수집 때의 자동 증분 임베딩 및 목록 상태 연계. **83건 벡터화 완료가 아님** |
| NAS 읽기 MCP | 실제 `search_patents`/`get_patent` 동작, 근거 최대 3개·각 300자 | [운영 전환](24-mvp01-production-cutover.md), [읽기 MCP](19-private-patent-reader-mcp.md) | 인간이 전체 원문·모든 청구항을 인증된 페이지 단위로 보는 기능 |
| 검색 통합·후보 비교 | JS 참조 구현과 두 MCP 직접 호출 범위 한정 시험, 중복 제거·보류 판단 PASS | [비교/판정](25-mvp04-candidate-comparison.md) | 상시 엔드포인트 내 자동 호출/검색 순위 품질, 실제 사용자 피드백 |
| 도면 파일 | WIPS 도면 경로/설명 반환 **확인**, 파일 다운로드·저장 없음 | 이 문서 3.2절 | 경로 실접근·이미지 형식/권리/다운로드 안정성 1건 검증 → 선택 저장 |
| **공보 PDF** | **아직 0건/직접 MCP 다운로드 도구 없음** | [PDF 별도 수집 설계](36-mvp-automatic-archive.md) | WIPS 별도 제공파일/다운로드 경로 가능성 확인, 없으면 KIPRIS Plus·EPO 등 공식 공보 소스 연동. 파일 SHA/문헌ID/종류/출처/접근권한 검증 |
| 백업·권한·기존 서비스 | 운영 DB 독립 백업/복원, ACL, 기존 문헌/벡터/컨테이너 불변 PASS | [100건 운영 인수](39-mvp-archive-100-live-acceptance.md) | 새 PDF 파일 보관 경로/백업·복원, 실제 운영 rollback 및 변경 시 회귀 |
| 실제 사용자 평가 | 안내 문서·실조회 시험 존재 | [사용자 시험](31-mvp06-user-trial.md) | 사용자 결과 평가 [중앙 #31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31) |

**중요:** `get_patent_search_onlyengine`의 83건 목록에는 현재 요약/상세설명/청구항/청크/벡터/PDF를 일괄 적재하지 않았다. 기존 6문헌의 원문 일부와 417청크가 별도로 존재한다.

## 5. 우선순위별 다음 구현

### P0 — 개인 특허 MVP 완료에 직접 필요한 작업

1. **P0-1: 검색→목록 보관 단일 도구 연결.** WIPS 검색을 실행하는 경로에서만 서지 최대100건을 operator 전용 NAS 저장기로 전달하고, 검색 결과와 `total/returned/inserted/reused/blocked/failed`를 구분해 응답한다. **별도 연결된 WIPS MCP 모든 호출을 가로챌 수 있다고 가정하지 않는다.** 실제 새 대화 E2E. 기존 RAG reader에 writer DB 자격증명 부여하지 않는다.
2. **P0-2: 공보 PDF 수집 가능성 결정.** 우선 WIPS 연결 도구의 PDF 다운로드 도구 부재를 기정 사실로 기록한다. WIPS 별도 파일/문서 API 또는 도면 경로의 공식 파일 제공 가능성을 공급사 문서·1건 시험으로 확인한다. 없으면 KIPRIS Plus(국내 공보) 또는 EPO(해외 범위) 등 별도 공식 공보 경로를 검증한다. PDF/도면 파일 크기·MIME·문헌번호/종류 매칭·해시·중복/보관 권한을 검증하고 **본문 텍스트에서 생성한 PDF를 원본 공보 PDF로 표시하지 않는다.**
3. **P0-3: 허용 문헌의 본문→청크→벡터 증분 적재.** 검색 목록의 미보유/부분보유/완료, 텍스트/벡터/공보 파일 확보 상태를 별도 필드로 관리한다. 상세설명/청구항을 `get_patent_spec_text`로 얻고 승인 범위·호출량에 따라 NAS E5로 임베딩한다. **서지100건 허용은 본문100건 수집 권한이 아니다.**
4. **P0-4: 원문·공보 열람.** `get_patent` 제한 발췌와 별개로, 인증된 전체 원문 페이지 조회 및 공보 PDF 파일 보기를 구현한다(파일 취득 가능성 검증 이후).
5. **P0-5: 실사용 인수.** 저장/재사용/보류/실패/문헌 대조·상태 표시, 운영 백업·복원 및 사용자 평가 [#31](https://github.com/son1004007/ai-agent-workflow-playbook/issues/31)를 통과해야 완료 처리.

### P1 — 기본 MVP 이후 확장 후보 (28개 전수 구현 불필요)

- `get_patent_category`·`get_patent_citn`·`get_patent_family`를 검색 필터·근거 연결에 선택적으로 도입한다. 국가별 데이터 품질과 개인정보·보존정책을 먼저 확인한다.
- `get_patent_rights`·`get_patent_admin_history`·`get_patent_office_action`을 공보 문헌에 연결해 법적 상태와 기술 설명을 분리한다. 법률적 확정 판단/권리 보장을 AI가 단정하지 않는다.
- `get_patent_ai_search`/`get_patent_aisearch_num`와 NAS 검색 결과의 랭킹 품질 평가, Hybrid/RRF/reranker는 실제 사용자 피드백 후 결정한다.
- 국가별 심판·소송·Orange Book은 업무에서 필요할 때만 선택적으로 활성화한다.

## 6. 추가 조사·운영 주의 사항

- 이 카탈로그의 도구 목록은 **현재 연결에 노출된 정의 28개** 기준이다. WIPS 서버 업데이트나 계정 권한 변경 시 재조회한다. **도구 노출**과 **실제 반환·구독 권리·이용료**는 구분한다.
- WIPS 검색량: 실제 `total_count`와 반환 `row_list.length`는 별도. 도구 공급자 최대 페이지 크기(필드별 500/50)와 **사용자 지정 NAS 보관 최대100**을 혼동하지 않는다. 무제한 paging/재호출 금지.
- 실제 문헌 ID/SKEY·원문·상세 이미지 경로·개별 파일·credential·API key를 공개 GitHub에 게시하지 않는다. 개인 NAS의 비공개 보관 및 권한/백업 경계 유지.
- **저장 권리 구분:** 검색 서지의 지속 보관 최대100건은 사용자 직접 승인(계약서는 별도 독립 검증 안 됨). 과거 승인된 일부 원문/벡터 적재를 다른 83건 전체에 일반화하거나 PDF/도면 파일의 자동 다운로드 승인으로 취급하지 않는다.
- 참고 문서: [자동 보관/원문 PDF 요구사항](36-mvp-automatic-archive.md), [실제 83건 운영 적재](39-mvp-archive-100-live-acceptance.md), [MVP 전체 작업](../TASKS.md), [제공자·권리 정책](06-provider-policy.md).

**이번 작업은 카탈로그/작업 목록 문서화만 수행하며 WIPS 재수집, 신규 본문·PDF 저장, 서버 변경, 신규 플러그인 등록 및 운영 배포는 수행하지 않는다.**

## 별도 서비스: WIPS MyFolder MCP (기존 검색 28도구에 포함되지 않음)
2026-11-20 WIPS 공식 발표 확인: [WIPS MyFolder MCP 조사/접속 가능성 및 NAS 통합 한계](41-wips-myfolder-mcp-assessment.md). 윈텔립스 MyFolder의 기존 폴더/SKEY 목록을 가져오는 별도의 읽기 전용 서비스로 안내되며, 공개 도구명 `myfolder_list_folders`, `myfolder_get_folder_skeys`는 제3자 카탈로그 기준(실사용 미검증). **WIPS 검색 결과를 MyFolder에 쓰거나 NAS에 자동 저장하는 기능, 공보 PDF 다운로드 기능을 의미하지 않는다.** 현재 도구/개인 플러그인에 MyFolder 연결 확인되지 않았고, 위 28개는 기존 WIPS 검색 MCP만의 카탈로그다.
