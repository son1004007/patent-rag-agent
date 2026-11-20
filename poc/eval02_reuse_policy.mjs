// Pure, no-network evaluator. Caller retains provider/source material privately.
// No provider identifiers, excerpts, queries or raw metadata appear in return values.
const HEX64=/^[a-f0-9]{64}$/;
const PAT_ID=/^PAT-[a-f0-9]{64}$/;
const RANKING='exact_cosine_best_chunk_per_document';
const SCOPE='private_purchased_patents_local_only';

function readRows(read){
  if(read?.scope!==SCOPE||read.ranking!==RANKING||!Array.isArray(read.results)||read.results.length>3)throw Error('BAD_NAS_READ');
  const ids=new Set();
  for(const r of read.results){
    if(!PAT_ID.test(r.document_id)||ids.has(r.document_id)||!HEX64.test(r.source_sha256)||!HEX64.test(r.chunk_sha256)||!Number.isInteger(r.start_offset)||!Number.isInteger(r.end_offset)||r.start_offset<0||r.end_offset<r.start_offset||typeof r.excerpt!=='string'||r.excerpt.trim().length===0||typeof r.section!=='string'||r.section.trim().length===0)throw Error('BAD_NAS_EVIDENCE');
    ids.add(r.document_id);
  }
  return read.results;
}

export function evaluateReuseRun(records,{observedWipsCalls=0,observedNasCalls=null,estimatedWipsBaselineCalls=null}={}){
  if(!Array.isArray(records)||records.length<1||records.length>50)throw Error('BAD_CASES');
  if(!Number.isInteger(observedWipsCalls)||observedWipsCalls<0)throw Error('BAD_WIPS_CALLS');
  if(observedNasCalls!==null&&(!Number.isInteger(observedNasCalls)||observedNasCalls<0))throw Error('BAD_NAS_CALLS');
  if(estimatedWipsBaselineCalls!==null&&(!Number.isInteger(estimatedWipsBaselineCalls)||estimatedWipsBaselineCalls<0))throw Error('BAD_COUNTERFACTUAL');
  const seen=new Set();let accepted=0,stable=0,complete=0;
  const cases=records.map(rec=>{
    if(!/^Q\d{2}$/.test(rec?.caseId)||seen.has(rec.caseId)||!['IN','OUT'].includes(rec.group)||!Array.isArray(rec.reads)||rec.reads.length!==2||typeof rec.freshnessRequired!=='boolean'||!(rec.directEvidenceRank===null||Number.isInteger(rec.directEvidenceRank)&&rec.directEvidenceRank>=1&&rec.directEvidenceRank<=3))throw Error('BAD_CASE');
    seen.add(rec.caseId);
    const a=readRows(rec.reads[0]),b=readRows(rec.reads[1]);
    const exact=a.length===b.length&&a.every((r,i)=>r.document_id===b[i].document_id&&r.chunk_sha256===b[i].chunk_sha256&&r.source_sha256===b[i].source_sha256&&r.section===b[i].section&&r.start_offset===b[i].start_offset&&r.end_offset===b[i].end_offset);
    if(exact)stable++;
    if(a.length===3&&b.length===3)complete++;
    const supported=rec.directEvidenceRank!==null&&rec.directEvidenceRank<=a.length;
    const decision=rec.freshnessRequired?'FRESHNESS_REQUIRED':!exact?'UNSTABLE_RETRIEVAL':supported?'AI_REVIEWED_REUSABLE':'INSUFFICIENT_DIRECT_EVIDENCE';
    if(decision==='AI_REVIEWED_REUSABLE')accepted++;
    return {caseId:rec.caseId,group:rec.group,decision,rankStable:exact,firstCount:a.length,repeatCount:b.length};
  });
  const estimatedAvoidedWipsCalls=estimatedWipsBaselineCalls===null?null:Math.max(0,estimatedWipsBaselineCalls-observedWipsCalls);
  return {status:'AI_SELF_REVIEWED_NOT_HUMAN_GOLD',cases,totals:{questions:records.length,stable,complete,aiReviewedReusable:accepted,hold:records.length-accepted,observedWipsCalls,observedNasCalls,estimatedWipsBaselineCalls,estimatedAvoidedWipsCalls,actualCost:null,measuredEndToEndLatency:null},warnings:['Review labels are supplied by one AI, not independent human gold.','Counterfactual calls are estimates, not actual savings.','No fresh patent/legal-status verification or corpus parity.']};
}
