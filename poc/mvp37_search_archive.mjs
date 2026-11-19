// Search-page wrapper for an explicitly configured, trusted metadata archive.
// Not a listener on the third-party plugin. No automatic paging or fulltext.
const fields="SKEY,XN_D,CC,KC_D,TIK,APSTH,XD";
async function searchAndArchive({query,page=1,page_size=10},adapters){
  if(typeof query!=="string"||!query.trim()||query.length>2000||!Number.isInteger(page)||page<1||page>10000||!Number.isInteger(page_size)||page_size<1||page_size>50)throw Error("INVALID_REQUEST");
  if(await adapters.allowSearch({provider:"WIPS",query})!==true)return {search:"BLOCKED_POLICY",archive:"NOT_RUN"};
  let response;
  try{response=await adapters.searchWips({query,pgrow:page_size,pgnum:page,outitem:fields});}catch{return {search:"FAILED",archive:"NOT_RUN"};}
  const d=response?.data;
  if(response?.success!==true||!Number.isInteger(d?.total_count)||d.total_count<0||!Array.isArray(d?.row_list)||d.row_list.length>page_size||d.row_list.length>Math.max(0,d.total_count-(page-1)*page_size))return {search:"FAILED",archive:"NOT_RUN"};
  const rows=d.row_list.map(r=>Object.fromEntries(fields.split(",").map(k=>[k,r?.[k]??null])));
  const result={search:"PASS",total_count:d.total_count,returned_count:rows.length,rows};
  try{
    // Local transport owns policy evaluation; no credentials or approval in packet.
    const a=await adapters.archivePage({query,page,page_size,response:{success:true,data:{total_count:d.total_count,row_list:rows}}});
    if(a?.status==="BLOCKED_POLICY")return {...result,archive:"BLOCKED_POLICY"};
    if(!["PASS","REUSED_VERIFIED"].includes(a?.status)||a.verified!==true||a.returned_count!==d.row_list.length||a.total_count!==d.total_count||a.body_writes!==0||!Number.isInteger(a.unique_count)||a.unique_count<0||a.unique_count>d.row_list.length||![a.saved,a.reused].every(v=>Number.isInteger(v)&&v>=0)||a.saved+a.reused!==a.unique_count||![a.fulltext_complete,a.fulltext_partial,a.fulltext_missing].every(v=>Number.isInteger(v)&&v>=0)||a.fulltext_complete+a.fulltext_partial+a.fulltext_missing!==a.unique_count||(a.status==="REUSED_VERIFIED"&&a.saved!==0))throw Error("UNVERIFIED_ARCHIVE");
    return {...result,archive:a.status,storage:{saved:a.saved,reused:a.reused,unique:a.unique_count,fulltext_complete:a.fulltext_complete,fulltext_partial:a.fulltext_partial,fulltext_missing:a.fulltext_missing}};
  }catch{return {...result,archive:"FAILED_OR_UNCONFIRMED"};}
}
export {searchAndArchive};
