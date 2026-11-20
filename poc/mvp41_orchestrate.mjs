/**
 * ChatGPT Code Mode, explicitly requested WIPS search -> owner NAS archiver.
 * This is NOT a server-side MCP interceptor and cannot capture other WIPS calls.
 * Data and credentials are never printed or included in error messages.
 */
const FIELDS = Object.freeze(['SKEY', 'XN_D', 'CC', 'KC_D', 'TIK', 'APSTH', 'XD']);
const MAX_STDIN_BYTES = 60_000; // Gateway's stdin input is at most 65,536 bytes.
const TERMINAL = new Set(['succeeded', 'failed', 'cancelled', 'timed_out']);

function utf8Length(s) {
  let n = 0;
  for (const char of s) {
    const c = char.codePointAt(0);
    n += c < 0x80 ? 1 : c < 0x800 ? 2 : c < 0x10000 ? 3 : 4;
  }
  return n;
}
function toolData(x) {
  if (x?.structuredContent) return x.structuredContent;
  if (x?.result?.structuredContent) return x.result.structuredContent;
  if (x?.result && typeof x.result === 'object' && 'success' in x.result) return x.result;
  return x;
}
function archiveToolData(x) {
  const d = toolData(x);
  if (d?.job && d?.output) return d;
  return d;
}
function badNumber(n) {return !Number.isSafeInteger(n) || n < 0;}
function validateProvider(x, size) {
  const d = toolData(x);
  if (d?.success !== true || badNumber(d?.data?.total_count) || !Array.isArray(d?.data?.row_list)) {
    throw new Error('SEARCH_FAILED');
  }
  const rows = d.data.row_list;
  if (rows.length > size || rows.length > d.data.total_count) throw new Error('SEARCH_FAILED');
  const projected = rows.map(r => {
    if (!r || typeof r !== 'object' || Array.isArray(r)) throw new Error('SEARCH_FAILED');
    const v = {};
    for (const field of FIELDS) {
      if (!Object.prototype.hasOwnProperty.call(r, field) && !['APSTH','XD'].includes(field)) {
        throw new Error('SEARCH_FAILED');
      }
      const item = r[field];
      if (item != null && typeof item !== 'string') throw new Error('SEARCH_FAILED');
      v[field] = item ?? '';
    }
    return v;
  });
  return {total: d.data.total_count, projected};
}
function validateSaved(result, expected) {
  if (!result || !['PASS','REUSED_VERIFIED'].includes(result.status) || result.verified !== true) return false;
  const keys = ['total_count','returned_count','unique_count','saved','reused','fulltext_complete','fulltext_partial','fulltext_missing','body_writes'];
  if (keys.some(k => badNumber(result[k]))) return false;
  return result.total_count === expected.total && result.returned_count === expected.returned &&
    result.unique_count <= result.returned_count &&
    result.saved + result.reused === result.unique_count &&
    result.fulltext_complete + result.fulltext_partial + result.fulltext_missing === result.unique_count &&
    result.body_writes === 0 &&
    (result.status !== 'REUSED_VERIFIED' || result.saved === 0);
}
function parseGateway(x) {
  const r = archiveToolData(x);
  if (!['succeeded', 'failed'].includes(r?.job?.status)) throw new Error('ARCHIVE_UNCONFIRMED');
  const chunks = r.output?.chunks;
  if (!Array.isArray(chunks)) throw new Error('ARCHIVE_UNCONFIRMED');
  const out = chunks.filter(c => c.stream === 'stdout').map(c => c.text).join('');
  if (!out || out.length > 4096) throw new Error('ARCHIVE_UNCONFIRMED');
  try {
    const parsed=JSON.parse(out.trim());
    if (r.job.status === 'failed' && (parsed?.status !== 'BLOCKED_POLICY' || parsed?.verified !== false || parsed?.saved !== 0)) throw new Error('ARCHIVE_UNCONFIRMED');
    return parsed;
  } catch {throw new Error('ARCHIVE_UNCONFIRMED');}
}

/**
 * @param {{query:string, limit?:number}} request
 * @param {{searchWips:Function,executeArchive:Function,waitArchive:Function,allowSearch:Function}} adapters
 * - executeArchive receives only bounded stdin JSON and must execute a FIXED,
 *   owner-authorized NAS command, never an arbitrary command from query/rows.
 * - waitArchive receives the durable Gateway job ID (no blind retries).
 */
export async function runWipsArchive(request, adapters) {
  const query = request?.query;
  const limit = request?.limit ?? 100;
  if (typeof query !== 'string' || !query.trim() || query.length > 2000 || /[\u0000-\u001f\u007f]/.test(query) ||
      !Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('INVALID_REQUEST');
  if (!adapters || ['searchWips', 'executeArchive', 'waitArchive', 'allowSearch'].some(k => typeof adapters[k] !== 'function')) {
    throw new Error('INVALID_ADAPTER');
  }
  if (await adapters.allowSearch({provider:'WIPS',purpose:'metadata_only',query}) !== true) {
    return {search:'BLOCKED_POLICY',archive:'NOT_RUN'};
  }
  let provider;
  try {provider = await adapters.searchWips({query,pgrow:limit,pgnum:1,outitem:FIELDS.join(',')});}
  catch {return {search:'FAILED',archive:'NOT_RUN'};}
  let data;
  try {data = validateProvider(provider,limit);}
  catch {return {search:'FAILED',archive:'NOT_RUN'};}
  const result={search:'PASS',total_count:data.total,returned_count:data.projected.length};
  const packet={query,page:1,page_size:limit,response:{success:true,data:{total_count:data.total,row_list:data.projected}}};
  const raw=JSON.stringify(packet);
  // No partial transfer or silent truncation. WIPS server request isn't retried.
  if (utf8Length(raw) > MAX_STDIN_BYTES) return {...result,archive:'PAYLOAD_TOO_LARGE'};
  try {
    let remote=await adapters.executeArchive(raw);
    let job=archiveToolData(remote);
    if (job?.job?.id && !TERMINAL.has(job.job.status)) {
      remote=await adapters.waitArchive(job.job.id);
    }
    const saved=parseGateway(remote);
    if (saved.status==='BLOCKED_POLICY') return {...result,archive:'BLOCKED_POLICY'};
    if (!validateSaved(saved,{total:data.total,returned:data.projected.length})) {
      return {...result,archive:'FAILED_OR_UNCONFIRMED'};
    }
    return {...result,archive:saved.status,storage:{saved:saved.saved,reused:saved.reused,
      unique:saved.unique_count,fulltext_complete:saved.fulltext_complete,
      fulltext_partial:saved.fulltext_partial,fulltext_missing:saved.fulltext_missing}};
  } catch {return {...result,archive:'FAILED_OR_UNCONFIRMED'};}
}
