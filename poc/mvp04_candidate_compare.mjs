// Pure read-only reference adapter; no network, storage or LLM calls.
function integrateCandidates(nas,wips,details,criteria){
  const valid=(v,n)=>typeof v==="string"&&v.trim().length>0&&v.length<=n;
  const sha=x=>typeof x==="string"&&/^[a-f0-9]{64}$/.test(x);
  const key=(c,p,k)=>{if(!/^[A-Z]{2}$/.test(c)||!valid(p,80)||!/^[A-Za-z0-9][A-Za-z0-9 .\/-]*$/.test(p)||!/^[A-Z][A-Z0-9]{0,4}$/.test(k))throw Error("BAD_ID");return c+"|"+p.toUpperCase().replace(/[ .\/-]/g,"")+"|"+k};
  const norm=s=>s.replace(/<[^>]{0,500}>/g," ").replace(/&(?:nbsp|amp|lt|gt|quot);/gi," ").replace(/\s+/g," ").trim().normalize("NFKC").toLowerCase();
  const terms=g=>Array.isArray(g)&&g.length<=8&&g.every(t=>valid(t,60)&&norm(t));
  if(!criteria||!terms(criteria.target)||!criteria.target.length||!terms(criteria.excludeTitle)||!Array.isArray(criteria.properties)||!criteria.properties.length||criteria.properties.length>5||!criteria.properties.every(p=>valid(p.name,60)&&terms(p.terms)&&p.terms.length))throw Error("BAD_CRITERIA");
  if(!Array.isArray(details)||details.length>3)throw Error("BAD_DETAILS");
  const m=new Map(),status={nas:"NOT_RUN",wips:"NOT_RUN"},counts={nas:0,wips:0,duplicates:0};
  const get=(c,p,k)=>{const id=key(c,p,k);if(!m.has(id))m.set(id,{id,country:c,publication:p,kind:k,sources:{},evidence:[]});return m.get(id)};
  const ne=(e,h)=>{if(!valid(e.section,80)||!valid(e.excerpt,600)||[...e.excerpt].length>300||!Number.isInteger(e.start_offset)||!Number.isInteger(e.end_offset)||e.start_offset<0||e.end_offset<e.start_offset||e.end_offset-e.start_offset>300||!sha(e.chunk_sha256))throw Error("BAD_EVIDENCE");return {source:"NAS",section:e.section,start:e.start_offset,end:e.end_offset,chunk_sha256:e.chunk_sha256,source_sha256:h,excerpt:e.excerpt}};
  if(nas!==null){
    if(nas?.scope!=="private_purchased_patents_local_only"||nas.ranking!=="exact_cosine_best_chunk_per_document"||!Array.isArray(nas.results)||nas.results.length>3)throw Error("BAD_NAS");
    status.nas="PASS";counts.nas=nas.results.length;
    for(const [i,x] of nas.results.entries()){
      if(!/^PAT-[a-f0-9]{64}$/.test(x.document_id)||!sha(x.source_sha256)||!valid(x.title,1000)||!valid(x.provider,80)||!Number.isFinite(x.distance)||x.distance<0||x.distance>2||(i&&x.distance<nas.results[i-1].distance))throw Error("BAD_NAS_ROW");
      const c=get(x.country,x.publication,x.kind);if(c.sources.NAS)throw Error("DUP_NAS");
      c.sources.NAS={rank:i+1,distance:x.distance,documentId:x.document_id,title:x.title,provider:x.provider,source_sha256:x.source_sha256};c.evidence.push(ne(x,x.source_sha256));
    }
  }
  const seen=new Set();
  for(const d of details){
    if(d?.found!==true||seen.has(d.document_id))throw Error("BAD_DETAIL");seen.add(d.document_id);
    const c=m.get(key(d.country,d.publication,d.kind)),s=c?.sources.NAS;
    if(!s||s.documentId!==d.document_id||s.source_sha256!==d.source_sha256||s.title!==d.title||s.provider!==d.provider||!Array.isArray(d.evidence)||d.evidence.length>3)throw Error("DETAIL_MISMATCH");
    for(const e of d.evidence){const a=ne(e,d.source_sha256);if(!c.evidence.some(x=>x.source===a.source&&x.section===a.section&&x.start===a.start&&x.end===a.end&&x.chunk_sha256===a.chunk_sha256))c.evidence.push(a);}
  }
  if(wips!==null){
    if(wips?.success!==true||!Array.isArray(wips.data?.row_list)||wips.data.row_list.length>3)throw Error("BAD_WIPS");status.wips="PASS";counts.wips=wips.data.row_list.length;
    for(const [i,x] of wips.data.row_list.entries()){
      if(!/^[0-9]{1,24}$/.test(x.SKEY)||!valid(x.TIK,1000)||!valid(x.ABK,24000)||!(x.CLK==null||typeof x.CLK==="string"&&x.CLK.length<=24000))throw Error("BAD_WIPS_ROW");
      const c=get(x.CC,x.XN_D,x.KC_D);if(c.sources.WIPS)throw Error("DUP_WIPS");c.sources.WIPS={rank:i+1,skey:x.SKEY,title:x.TIK,provider:"WIPS"};
      for(const field of ["ABK","CLK"]){const raw=x[field];if(!raw?.trim())continue;const chars=[...raw];c.evidence.push({source:"WIPS",section:field,start:0,end:Math.min(chars.length,300),excerpt:chars.slice(0,300).join(""),truncated:chars.length>300});}
    }
  }
  const match=(s,ts)=>ts.some(t=>norm(s).includes(norm(t)));
  const ref=({excerpt,...metadata})=>metadata;
  const candidates=[...m.values()].map(c=>{
    const title=c.sources.NAS?.title??c.sources.WIPS.title,titles=Object.values(c.sources).map(x=>x.title);
    const target=match(title,criteria.target)||c.evidence.some(e=>match(e.excerpt,criteria.target));
    const excluded=titles.some(t=>match(t,criteria.excludeTitle));
    const properties=criteria.properties.map(p=>({name:p.name,mentions:c.evidence.filter(e=>match(e.excerpt,p.terms)).map(ref)}));
    const all=properties.every(p=>p.mentions.length>0),complete=status.nas==="PASS"&&status.wips==="PASS";
    if(c.sources.NAS&&c.sources.WIPS)counts.duplicates++;
    return {...c,title,target,properties,decision:excluded||!target?"EXCLUDE":all&&complete?"REVIEW_CANDIDATE":"HOLD",reason:excluded?"EXCLUDED_TITLE":!target?"TARGET_NOT_EVIDENCED":!all?"PROPERTY_EVIDENCE_MISSING":!complete?"SOURCE_COVERAGE_PARTIAL":"TERM_MENTIONS_REQUIRE_HUMAN_VERIFICATION"};
  });
  return {status,counts:{...counts,unique:candidates.length},candidates,warning:"Lexical mentions only; no relevance probability, measured performance, legal opinion, or cross-source score. Review candidates are not validated recommendations."};
}
export {integrateCandidates};
