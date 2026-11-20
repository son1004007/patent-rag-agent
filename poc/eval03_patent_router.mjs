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
function validWips(obj){
  const d=obj?.data;
  return obj?.success===true && d && typeof d==='object' &&
    Number.isInteger(d.total_count)&&d.total_count>=0 &&
    Array.isArray(d.row_list)&&d.row_list.length<=3 &&
    d.total_count>=d.row_list.length &&
    d.row_list.every(r=>r&&typeof r==='object'&&
      typeof r.SKEY==='string'&&/^[0-9]{5,30}$/.test(r.SKEY)&&
      typeof r.TIK==='string'&&r.TIK.trim().length>0);
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
  searchNas,detailNas,reviewNas,searchWips
}={}){
  if(typeof wipsQuery!=='string'||!wipsQuery.trim()||wipsQuery.length>1000||
     typeof searchWips!=='function')throw Error('BAD_ROUTER_INPUT');
  const calls={wips:0};
  const local=await runNasReadOnlyReview({
    caseId,group,query,freshnessRequired,requiredFeatures,
    search:searchNas,detail:detailNas,review:reviewNas
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
  const count=w.data.row_list.length;
  return safeResult('WIPS_MCP',count?ROUTE.REMOTE:ROUTE.EMPTY,local,calls,
    {returnedCount:count,totalCount:w.data.total_count,
      limitations:['NAS_TOP3_UNVERIFIED_ABSENCE','WIPS_SEARCH_NOT_FULLTEXT_OR_LEGAL_OPINION']});
}
export {ROUTE};
