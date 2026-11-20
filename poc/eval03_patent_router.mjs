// ChatGPT Code Mode read-only router for two already connected private MCPs.
// Not an installed server-side MCP endpoint. No credential forwarding or DB writes.
import {runNasReadOnlyReview,REASON} from './eval02_live_read_adapter.mjs';

const WIPS_FIELDS='SKEY,XN_D,CC,KC_D,TIK,ABK,CLK';
const ROUTE=Object.freeze({
  LOCAL:'SERVED_FROM_NAS_RAG',
  REMOTE:'SERVED_FROM_WIPS_MCP',
  EMPTY:'WIPS_NO_RESULTS',
  BLOCK:'HOLD_LOCAL_NOT_VERIFIED',
  ERROR:'WIPS_READ_FAILED'
});
function unwrap(x){
  if(typeof x?.text==='string')return JSON.parse(x.text);
  return x;
}
// Bounded display projection. Do not return raw WIPS provider reply or SKEY.
const DISPLAY_LIMITS={title:240,abstract:1500,representativeClaim:1500};
function validWips(obj){
  const d=obj?.data;
  return obj?.success===true && d && typeof d==='object' &&
    Number.isInteger(d.total_count)&&d.total_count>=0 &&
    Array.isArray(d.row_list)&&d.row_list.length<=3 &&
    d.total_count>=d.row_list.length &&
    d.row_list.every(r=>r&&typeof r==='object'&&
      typeof r.SKEY==='string'&&/^[0-9]{5,30}$/.test(r.SKEY)&&
      typeof r.CC==='string'&&/^[A-Z]{2,3}$/.test(r.CC)&&
      typeof r.XN_D==='string'&&r.XN_D.trim().length>0&&r.XN_D.length<=80&&
      typeof r.KC_D==='string'&&/^[A-Za-z0-9]{1,6}$/.test(r.KC_D)&&
      typeof r.TIK==='string'&&r.TIK.trim().length>0&&r.TIK.length<=20000&&
      ['ABK','CLK'].every(k=>r[k]==null||
        (typeof r[k]==='string'&&r[k].length<=20000)));
}
function displayText(value,limit){
  if(value==null||value==='')return {text:null,truncated:false};
  // Treat external response as data, never executable markup/instructions.
  const plain=value.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi,' ')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi,' ')
    .replace(/<[^>]*>/g,' ').replace(/[\u0000-\u001f\u007f]/g,' ')
    .replace(/\s+/g,' ').trim();
  const chars=[...plain];
  return {text:chars.length?chars.slice(0,limit).join(''):null,
    truncated:chars.length>limit};
}
function displayPatents(rows){
  return rows.map((r,i)=>{
    const t=displayText(r.TIK,DISPLAY_LIMITS.title);
    const a=displayText(r.ABK,DISPLAY_LIMITS.abstract);
    const c=displayText(r.CLK,DISPLAY_LIMITS.representativeClaim);
    if(!t.text)throw Error('INVALID_WIPS_TITLE');
    return {rank:i+1,publicationNumber:r.XN_D.trim(),country:r.CC,
      documentKind:r.KC_D,title:t.text,abstract:a.text,
      representativeClaim:c.text,
      truncated:{title:t.truncated,abstract:a.truncated,representativeClaim:c.truncated}};
  });
}
function safeResult(source,decision,local,calls,extra={}){
  return {source,decision,localDecision:local?.decision??null,
    calls:{nasSearch:local?.calls?.nasSearch??0,nasDetail:local?.calls?.nasDetail??0,
      wips:calls.wips},...extra};
}
// WIPS receives only a separately authored public search expression, NEVER
// the NAS private query/evidence. Local similarity alone is never existence proof.
// Local technical relevance assessment is explicitly supplied by ChatGPT.
export async function runPatentRouter({
  caseId,group,query,wipsQuery,requiredFeatures=[],freshnessRequired=false,
  searchNas,detailNas,reviewNas,searchWips,onNasAccepted
}={}){
  if(typeof wipsQuery!=='string'||!wipsQuery.trim()||wipsQuery.length>1000||
     typeof searchWips!=='function')throw Error('BAD_ROUTER_INPUT');
  const calls={wips:0};
  const local=await runNasReadOnlyReview({
    caseId,group,query,freshnessRequired,requiredFeatures,
    search:searchNas,detail:detailNas,review:reviewNas,onAccepted:onNasAccepted
  });
  if(local.decision===REASON.VALID)
    return safeResult('NAS_RAG',ROUTE.LOCAL,local,calls,{rank:local.rank,evidenceCitationMatched:true});
  // Inability to read/verify NAS does not mean the patent is absent.
  // Freshness requests require a separately defined legal-state-aware lookup.
  if(local.decision!==REASON.MISSING)
    return safeResult('HOLD',ROUTE.BLOCK,local,calls);
  let w;
  try{
    calls.wips++;
    w=unwrap(await searchWips({query:wipsQuery,pgrow:3,pgnum:1,outitem:WIPS_FIELDS}));
    if(!validWips(w))return safeResult('HOLD',ROUTE.ERROR,local,calls);
  }catch{return safeResult('HOLD',ROUTE.ERROR,local,calls);}
  let patents;
  try{patents=displayPatents(w.data.row_list);}
  catch{return safeResult('HOLD',ROUTE.ERROR,local,calls);}
  const count=patents.length;
  return safeResult('WIPS_MCP',count?ROUTE.REMOTE:ROUTE.EMPTY,local,calls,
    {returnedCount:count,totalCount:w.data.total_count,patents,
      limitations:['NAS_TOP3_UNVERIFIED_ABSENCE','WIPS_SEARCH_NOT_FULLTEXT_OR_LEGAL_OPINION',
        'DISPLAY_TEXT_NOT_FULL_SPECIFICATION']});
}
export {ROUTE};
