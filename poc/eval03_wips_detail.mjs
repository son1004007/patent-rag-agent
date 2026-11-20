// EVAL-03 display P0-2: on-demand, read-only selection by public WIPS
// patent identity. NOT a registered MCP server. No NAS/DB writes.
const SECTIONS=['dtl_desc','all_claim'];
const COUNTRY=/^[A-Z]{2,3}$/,KIND=/^[A-Z0-9]{1,6}$/,
  PUB=/^[A-Za-z0-9][A-Za-z0-9 ._/-]{1,79}$/;
const MAX_PAGE=4000,MAX_SECTION=2000000;
function unpack(x){return x&&typeof x.text==='string'?JSON.parse(x.text):x}
function normalizeNumber(x){return String(x).replace(/[^A-Za-z0-9]/g,'').toUpperCase()}
function plainText(text){
  if(typeof text!=='string')throw Error('NON_TEXT');
  const s=text.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi,' ')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi,' ')
    .replace(/<br\s*\/?>/gi,'\n')
    .replace(/<\/(?:p|div|li|tr|h[1-6])\s*>/gi,'\n')
    .replace(/<[^>]*>/g,' ')
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g,' ')
    .replace(/\r\n?/g,'\n').replace(/[ \t]+/g,' ')
    .replace(/[ \t]*\n[ \t]*/g,'\n')
    .replace(/\n{3,}/g,'\n\n').trim();
  if([...s].length>MAX_SECTION)throw Error('TOO_LARGE');
  return s;
}
function page(text,start,limit){
  const a=[...text];if(start>a.length)return null;
  const end=Math.min(start+limit,a.length);
  return {text:a.slice(start,end).join(''),offset:start,totalChars:a.length,
    hasMore:end<a.length,nextOffset:end<a.length?end:null,
    complete:start===0&&end===a.length};
}
function lang(d){return typeof d.lang_cd==='string'&&/^[A-Z]{2}$/.test(d.lang_cd)?d.lang_cd:null}
function descBody(d){
  if(!Array.isArray(d.dtl_desc_list)||d.dtl_desc_list.length>8)throw Error('BAD_DESC');
  const l=lang(d),items=d.dtl_desc_list.filter(x=>x&&typeof x==='object'&&
    typeof x.dtl_desc==='string'&&(!l||x.lang_cd===l));
  if(d.dtl_desc_list.length&&!items.length)throw Error('BAD_DESC_LANG');
  return {language:l,text:plainText(items.map(x=>x.dtl_desc).join('\n'))};
}
function claimsBody(d){
  if(!Array.isArray(d.cl_list)||d.cl_list.length>1500)throw Error('BAD_CLAIMS');
  const l=lang(d),parts=[];
  for(const x of d.cl_list){
    if(!x||typeof x.cl!=='string'||!['string','number'].includes(typeof x.cl_num))
      throw Error('BAD_CLAIM');
    if(l&&x.lang_cd!==l)continue;
    const num=String(x.cl_num);
    if(!/^[0-9]{1,5}$/.test(num))throw Error('BAD_CLAIM_NUM');
    parts.push('청구항 '+num+'\n'+plainText(x.cl));
  }
  if(d.cl_list.length&&!parts.length)throw Error('BAD_CLAIM_LANG');
  const text=parts.join('\n\n');
  if([...text].length>MAX_SECTION)throw Error('TOO_MANY_CLAIMS');
  return {language:l,totalClaims:parts.length,text};
}
function matches(x,section,s){
  return x?.success===true&&x.section===section&&
    x.data&&typeof x.data==='object'&&x.data.ctry===s.country&&
    typeof x.data.doc_num==='string'&&
    normalizeNumber(x.data.doc_num)===normalizeNumber(s.publicationNumber);
}
function error(status){return {status,source:'WIPS_MCP',calls:2}}
export async function getSelectedWipsPatentDetail({
  selection,descriptionOffset=0,claimsOffset=0,pageSize=3000,getSpecText
}={}){
  if(!selection||typeof selection!=='object'||
    !COUNTRY.test(selection.country??'')||
    !KIND.test(selection.documentKind??'')||
    !PUB.test(selection.publicationNumber??'')||
    typeof getSpecText!=='function'||
    !Number.isSafeInteger(descriptionOffset)||descriptionOffset<0||
    !Number.isSafeInteger(claimsOffset)||claimsOffset<0||
    !Number.isSafeInteger(pageSize)||pageSize<1||pageSize>MAX_PAGE)
    throw Error('INVALID_DETAIL_REQUEST');
  const args={ctry:selection.country,mng_num:selection.publicationNumber,
    doc_kind:selection.documentKind,mng_num_type:'M'};
  let raw;
  try{raw=(await Promise.all(SECTIONS.map(section=>
    getSpecText({...args,section})))).map(unpack)}
  catch{return error('WIPS_DETAIL_READ_FAILED')}
  if(!SECTIONS.every((s,i)=>matches(raw[i],s,selection)))
    return error('WIPS_DOCUMENT_IDENTITY_OR_RESPONSE_MISMATCH');
  let d,c;
  try{d=descBody(raw[0].data);c=claimsBody(raw[1].data)}
  catch{return error('WIPS_DETAIL_INVALID_SECTION')}
  const description=page(d.text,descriptionOffset,pageSize),
    claims=page(c.text,claimsOffset,pageSize);
  if(!description||!claims)return error('PAGE_OFFSET_OUT_OF_RANGE');
  return {status:description.totalChars&&c.totalClaims?'PASS':'PARTIAL_SECTION_UNAVAILABLE',
    source:'WIPS_MCP',country:selection.country,
    publicationNumber:selection.publicationNumber,documentKind:selection.documentKind,
    description:{language:d.language,...description,available:description.totalChars>0},
    claims:{language:c.language,totalClaims:c.totalClaims,...claims,
      available:c.totalClaims>0},calls:2,
    limitations:['PLAIN_TEXT_ONLY','NO_ORIGINAL_PDF_OR_DRAWING',
      'PAGES_ARE_REQUERIED_FROM_PROVIDER','NO_LOCAL_PERSISTENCE']};
}