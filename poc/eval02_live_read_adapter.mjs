// Read-only, dependency-injected ChatGPT/NAS bridge for private purchased patent notes.
// It never writes data, makes WIPS calls, logs patent content or returns provider identifiers.
// The caller must be the authorized AI reviewing evidence in transient memory.
import {evaluateReuseRun} from './eval02_reuse_policy.mjs';

const SHA=/^[a-f0-9]{64}$/, DOC=/^PAT-[a-f0-9]{64}$/;
const REASON=Object.freeze({
  FRESH:'FRESHNESS_REQUIRED',
  SEARCH:'NAS_READ_FAILED',
  BAD:'INVALID_OR_UNSTABLE_EVIDENCE',
  DETAIL:'DETAIL_READ_FAILED',
  REVIEW:'AI_REVIEW_UNAVAILABLE',
  MISSING:'INSUFFICIENT_DIRECT_EVIDENCE',
  GROUND:'EVIDENCE_GROUNDING_FAILED',
  VALID:'AI_REVIEWED_REUSABLE'
});

function unwrap(value){
  if(value?.text && typeof value.text==='string')return JSON.parse(value.text);
  return value;
}

function validDetail(detail,searchRow){
  if(detail?.found!==true||!DOC.test(detail.document_id||'')||detail.document_id!==searchRow.document_id||
    detail.source_sha256!==searchRow.source_sha256||detail.country!==searchRow.country||
    detail.publication!==searchRow.publication||detail.kind!==searchRow.kind||
    detail.title!==searchRow.title||!Array.isArray(detail.evidence)||detail.evidence.length<1||detail.evidence.length>3)return false;
  return detail.evidence.every(e=>e&&typeof e.section==='string'&&e.section.length>0&&e.section.length<=80&&
    SHA.test(e.chunk_sha256||'')&&typeof e.excerpt==='string'&&e.excerpt.trim().length>0&&
    [...e.excerpt].length<=300&&Number.isInteger(e.start_offset)&&Number.isInteger(e.end_offset)&&
    e.start_offset>=0&&e.end_offset>=e.start_offset&&e.end_offset-e.start_offset<=300);
}

function output(caseId,decision,calls,extra={}){
  return {caseId,decision,source:'NAS_LOCAL_READ_ONLY',aiGrounded:decision===REASON.VALID,
    calls:{nasSearch:calls.search,nasDetail:calls.detail,wips:0},...extra};
}

// "review" is an explicit authorized AI callback. It must review full in-memory
// title/abstract/representative claim; similarity/distance must never be its label.
// Expected: null (hold) or {rank:1..3,label:2,section,chunkSha256,quote,rationale}.
// quote is verified against a returned evidence excerpt but is NEVER emitted.
export async function runNasReadOnlyReview({caseId,group,query,freshnessRequired=false,search,detail,review}={}){
  if(!/^Q\d{2}$/.test(caseId||'')||!['IN','OUT'].includes(group)||
    typeof query!=='string'||!query.trim()||query.length>2000||
    typeof freshnessRequired!=='boolean'||typeof search!=='function'||typeof detail!=='function')
    throw Error('BAD_INPUT');
  const calls={search:0,detail:0};
  if(freshnessRequired)return output(caseId,REASON.FRESH,calls);
  if(typeof review!=='function')return output(caseId,REASON.REVIEW,calls);
  let first,second;
  try{
    calls.search++;first=unwrap(await search({query,limit:3}));
    calls.search++;second=unwrap(await search({query,limit:3}));
  }catch{return output(caseId,REASON.SEARCH,calls);}
  let consistency;
  try{
    consistency=evaluateReuseRun([{caseId,group,freshnessRequired:false,directEvidenceRank:null,reads:[first,second]}],{
      observedNasCalls:calls.search,observedWipsCalls:0
    }).cases[0];
  }catch{return output(caseId,REASON.BAD,calls);}
  if(!consistency.rankStable||consistency.firstCount===0)
    return output(caseId,consistency.firstCount===0?REASON.MISSING:REASON.BAD,calls);
  const details=[];
  try{
    for(const row of first.results){
      calls.detail++;
      const value=unwrap(await detail({document_id:row.document_id}));
      if(!validDetail(value,row))return output(caseId,REASON.BAD,calls);
      details.push(value);
    }
  }catch{return output(caseId,REASON.DETAIL,calls);}
  let judgement;
  try{
    // All personal data stays inside the process; do not pass this callback to an
    // unrelated cloud provider without separate data-entitlement verification.
    judgement=await review({caseId,question:query,candidates:details});
  }catch{return output(caseId,REASON.REVIEW,calls);}
  if(judgement===null||judgement?.rank===null)
    return output(caseId,REASON.MISSING,calls,{reviewedBy:'AI'});
  if(!judgement||!Number.isInteger(judgement.rank)||judgement.rank<1||judgement.rank>details.length||
    judgement.label!==2)return output(caseId,REASON.MISSING,calls,{reviewedBy:'AI'});
  if(typeof judgement.section!=='string'||!SHA.test(judgement.chunkSha256||'')||
    typeof judgement.quote!=='string'||[...judgement.quote].length<12||
    [...judgement.quote].length>120||typeof judgement.rationale!=='string'||
    judgement.rationale.trim().length<20)return output(caseId,REASON.GROUND,calls,{reviewedBy:'AI'});
  const chosen=details[judgement.rank-1],e=chosen.evidence.find(x=>
    x.section===judgement.section&&x.chunk_sha256===judgement.chunkSha256&&x.excerpt.includes(judgement.quote));
  if(!e)return output(caseId,REASON.GROUND,calls,{reviewedBy:'AI'});
  // Integrity/quote check establishes provenance, NOT independent technical truth.
  return output(caseId,REASON.VALID,calls,{reviewedBy:'AI',rank:judgement.rank,evidenceCitationMatched:true,
    limitations:['AI_NOT_HUMAN_GOLD','NO_FRESHNESS_OR_LEGAL_OPINION']});
}
export {REASON};
