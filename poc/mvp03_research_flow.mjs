// Personal MVP — dependency-injected orchestrator. ChatGPT generates structured
// term groups; this code validates them and never uses arbitrary provider syntax.
// Owner-local storage permission is an operator-controlled adapter, not a plan field.
const FIELDS=["SKEY","XN_D","CC","KC_D","TIK","ABK","CLK"];
const TERM=/^[\p{L}\p{N}][\p{L}\p{N}-]{0,39}$/u;
const BAD=new Set(["AND","OR","NOT"]);
function textOK(t,n){return typeof t==="string"&&t.trim().length>0&&t.length<=n&&!/[\u0000-\u001f\u007f]/u.test(t);}
function planQuestion(question,groups){
  if(!textOK(question,200)||!Array.isArray(groups)||groups.length<2||groups.length>3)throw Error("INVALID_PLAN");
  const safe=groups.map(g=>{
    if(!Array.isArray(g)||g.length<1||g.length>4||!g.every(t=>typeof t==="string"&&TERM.test(t)&&!BAD.has(t.toUpperCase())))throw Error("INVALID_TERM");
    return [...new Set(g)];
  });
  return Object.freeze({question,nasQuery:question,wipsQuery:safe.map(g=>"("+g.join(" ")+").ti,ab.").join(" AND "),groups:safe});
}
function idKey(cc,number,kind){
  if(!/^[A-Z]{2}$/.test(cc)||!textOK(number,80)||!/^[A-Z][A-Z0-9]{0,4}$/.test(kind))throw Error("INVALID_IDENTITY");
  const num=number.normalize("NFKC").toUpperCase().replace(/[^A-Z0-9]/g,"");
  if(!num)throw Error("INVALID_NUMBER");
  return cc+"|"+num+"|"+kind;
}
function parseWips(r){
  if(r?.success!==true||!Array.isArray(r.data?.row_list)||r.data.row_list.length>3)throw Error("BAD_WIPS_RESPONSE");
  const found=new Map();
  for(const x of r.data.row_list){
    const row=Object.fromEntries(FIELDS.map(k=>[k,k==="CLK"&&x[k]==null?"":x[k]]));
    if(!FIELDS.every(k=>typeof row[k]==="string"&&row[k].length<=24000)||!["SKEY","XN_D","CC","KC_D","TIK","ABK"].every(k=>row[k].trim())||!/^[0-9]{1,24}$/.test(row.SKEY))throw Error("BAD_WIPS_ROW");
    const key=idKey(row.CC,row.XN_D,row.KC_D);
    const prev=found.get(key);
    if(prev&&JSON.stringify(prev)!==JSON.stringify(row))throw Error("WIPS_IDENTITY_CONFLICT");
    found.set(key,row);
  }
  return found;
}
function parseLocal(r){
  if(r?.scope!=="private_purchased_patents_local_only"||!Array.isArray(r.results)||r.results.length>3||!Array.isArray(r.catalog)||r.catalog.length>1000)throw Error("BAD_LOCAL_RESPONSE");
  const catalog=new Map();
  for(const x of r.catalog){
    const key=idKey(x.country,x.publication,x.kind);
    if(typeof x.enriched!=="boolean"||catalog.has(key))throw Error("BAD_CATALOG");
    catalog.set(key,x.enriched);
  }
  const seen=new Set();
  for(const x of r.results){
    const key=idKey(x.country,x.publication,x.kind);
    if(!catalog.has(key)||seen.has(key)||!Number.isFinite(x.distance)||x.distance<0||x.distance>2)throw Error("BAD_LOCAL_RANK");
    seen.add(key);
  }
  return catalog;
}
async function research(question,groups,adapters){
  const plan=planQuestion(question,groups);
  const trace={nas:"NOT_RUN",wips:"NOT_RUN",write:"NOT_RUN",localCount:0,wipsCount:0,known:0,newCandidates:0,enrichCandidates:0,writeCount:0};
  let catalog=null,rows=null;
  try{const r=await adapters.searchLocal({query:plan.nasQuery,limit:3});catalog=parseLocal(r);trace.nas="PASS";trace.localCount=r.results.length;}catch{trace.nas="FAILED";}
  // Public, independently authored term groups only. No NAS result content in WIPS.
  // A trusted operator adapter must explicitly approve external search before any call.
  let externalAllowed=false;
  try{externalAllowed=typeof adapters.allowExternalSearch==="function"&&await adapters.allowExternalSearch(Object.freeze({provider:"WIPS",query:plan.wipsQuery,purpose:"public_research_terms"}))===true;}catch{}
  if(!externalAllowed){trace.wips="BLOCKED_POLICY";trace.write="BLOCKED_POLICY";return trace;}
  try{rows=parseWips(await adapters.searchWips({query:plan.wipsQuery,pgrow:3,pgnum:1,outitem:FIELDS.join(",")}));trace.wips="PASS";trace.wipsCount=rows.size;}catch{trace.wips="FAILED";}
  if(!catalog||!rows){trace.write="BLOCKED_SOURCE_FAILURE";return trace;}
  const news=[],enrich=[];
  for(const [key,row] of rows){
    if(catalog.has(key)){trace.known++;if(!catalog.get(key))enrich.push(row);}
    else news.push(row);
  }
  trace.newCandidates=news.length;trace.enrichCandidates=enrich.length;
  // At most ONE write target per run. Prefer completing an existing partial record.
  const target=enrich[0]??news[0];
  if(!target){trace.write="NOT_NEEDED";return trace;}
  let allowed=false;
  try{allowed=typeof adapters.allowLocalWrite==="function"&&await adapters.allowLocalWrite(Object.freeze({provider:"WIPS",purpose:"owner_private_local",count:1}))===true;}catch{}
  if(!allowed){trace.write="BLOCKED_POLICY";return trace;}
  try{
    const mode=enrich.length?"enrich":"new";
    const result=await adapters.ingestOne({mode,row:target});
    if(result?.staged===true&&result?.verified!==true){trace.write="STAGED_PENDING_VERIFICATION";return trace;}
    if(result?.verified!==true||result?.documentsAdded!==(mode==="new"?1:0)||result.sectionsAdded!==2)throw Error("UNVERIFIED_WRITE");
    trace.write="PASS";trace.writeCount=1;
  }catch{trace.write="FAILED_OR_PARTIAL";}
  return trace;
}
export {planQuestion,idKey,parseWips,parseLocal,research};
