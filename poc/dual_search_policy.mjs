// Synthetic-only orchestration reference; NO live provider write or credentials.
const FIXTURES=Object.freeze({
  "DEMO-P1": "가상 문헌: 구리 피복 알루미늄 전선 도체의 경량화 및 전기 전도성.",
  "DEMO-P2": "가상 문헌: 해양 케이블의 염수 부식과 내식성 표면 처리.",
  "DEMO-P3": "가상 문헌: 열가소성 절연 재료의 난연 성능과 화재 안전.",
  "DEMO-P4": "가상 문헌: 태양광 발전 모듈의 봉지재 내습성과 광투과율."
});
const PUBLIC_QUERY=Object.freeze({
  "wips": "(태양광 태양전지).ti. AND (봉지재 봉지).ti.",
  "nas": "태양광 모듈 봉지재의 내습성과 광투과율"
});
function syntheticSaveRequest(record) {
  // No caller-asserted license or approval unlocks another provider.
  if(!record||typeof record!=="object"||record.source!=="synthetic"||!Object.hasOwn(FIXTURES,record.id)||record.text!==FIXTURES[record.id])return {allowed:false,reason:"SOURCE_NOT_APPROVED"};
  return {allowed:true,args:{document_id:record.id,text:FIXTURES[record.id]}};
}
async function dualSearch(readWips,readNas){
  // Fixed independently authored nonconfidential queries. No provider result
  // enters the NAS call, logs, or returned status. Never write implicitly.
  let external={ok:false,count:0};
  try{
    const r=await readWips({query:PUBLIC_QUERY.wips,pgrow:3,outitem:"SKEY,XN_D,CC,KC_D",pgnum:1});
    if(r?.success===true&&Array.isArray(r?.data?.row_list)&&r.data.row_list.length<=3)external={ok:true,count:r.data.row_list.length};
  }catch{}
  let local={ok:false,count:0,topId:null};
  try{
    const r=await readNas({query:PUBLIC_QUERY.nas,limit:3});
    if(r?.scope==="synthetic_candidates_only"&&Array.isArray(r.results)&&r.results.length<=3&&r.results.every(x=>Object.hasOwn(FIXTURES,x?.id)&&Number.isFinite(x.distance)&&x.distance>=0&&x.distance<=2)){
      local={ok:true,count:r.results.length,topId:r.results[0]?.id??null};
    }
  }catch{}
  return {external,local,storage:"NOT_ATTEMPTED",merge:"NO_CROSS_SOURCE_RANKING"};
}
export {FIXTURES,PUBLIC_QUERY,syntheticSaveRequest,dualSearch};
