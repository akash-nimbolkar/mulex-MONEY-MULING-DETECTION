import { parse } from 'papaparse'

export function parseTimestamp(s){
  return new Date(String(s).replace(' ', 'T'))
}

export function buildGraph(transactions){
  const nodes = new Map()
  const edges = []
  const adj = new Map()
  const inDeg = new Map()
  const outDeg = new Map()
  const txsByAccount = new Map()

  for(const t of transactions){
    const s = t.sender_id
    const r = t.receiver_id
    if(!nodes.has(s)) nodes.set(s,{id:s})
    if(!nodes.has(r)) nodes.set(r,{id:r})
    edges.push({data:{id:t.transaction_id, source:s, target:r, amount:parseFloat(t.amount||0), ts: t.timestamp}})
    if(!adj.has(s)) adj.set(s,[])
    adj.get(s).push(r)
    outDeg.set(s,(outDeg.get(s)||0)+1)
    inDeg.set(r,(inDeg.get(r)||0)+1)
    txsByAccount.set(s,(txsByAccount.get(s)||0)+1)
    txsByAccount.set(r,(txsByAccount.get(r)||0)+1)
  }

  return {nodes:Array.from(nodes.values()).map(n=>({data:{id:n.id, label:n.id}})), edges, adj, inDeg, outDeg, txsByAccount}
}

export function detectCycles(adj){
  const visited = new Set()
  const stack = []
  const cycles = []
  const onstack = new Set()
  function dfs(u){
    visited.add(u)
    stack.push(u); onstack.add(u)
    const neighbours = adj.get(u) || []
    for(const v of neighbours){
      if(!visited.has(v)) dfs(v)
      else if(onstack.has(v)){
        const idx = stack.indexOf(v)
        if(idx>=0){
          const cycle = stack.slice(idx)
          if(cycle.length>=3 && cycle.length<=5){
            const members = [...cycle]
            members.sort()
            const key = members.join('|')
            if(!cycles.find(c=>c.key===key)) cycles.push({key, members:cycle})
          }
        }
      }
    }
    stack.pop(); onstack.delete(u)
  }
  for(const u of adj.keys()) if(!visited.has(u)) dfs(u)
  return cycles.map((c,i)=>({ring_id:`RING-${String(i+1).padStart(3,'0')}`, member_accounts:c.members, pattern_type:'cycle'}))
}

export function computeSuspicion(graph, cycles, transactions){
  const score = new Map()
  const detectedPatterns = new Map()
  for(const n of graph.nodes){ score.set(n.data.id,0); detectedPatterns.set(n.data.id,[]) }

  for(const ring of cycles){
    for(const m of ring.member_accounts){
      score.set(m, (score.get(m)||0)+45)
      detectedPatterns.get(m).push(`cycle_length_${ring.member_accounts.length}`)
    }
  }

  for(const [acct, cnt] of graph.inDeg){
    if(cnt>=10){ score.set(acct,(score.get(acct)||0)+20); detectedPatterns.get(acct).push('fan_in') }
  }
  for(const [acct, cnt] of graph.outDeg){
    if(cnt>=10){ score.set(acct,(score.get(acct)||0)+20); detectedPatterns.get(acct).push('fan_out') }
  }

  const lowTx = new Set()
  for(const [acct, cnt] of graph.txsByAccount){ if(cnt>=2 && cnt<=3) lowTx.add(acct) }
  for(const [a, neigh] of graph.adj){
    for(const b of neigh){
      const bneigh = graph.adj.get(b)||[]
      for(const c of bneigh){
        const cneigh = graph.adj.get(c)||[]
        for(const d of cneigh){
          if(lowTx.has(b) && lowTx.has(c)){
            score.set(b,(score.get(b)||0)+15); detectedPatterns.get(b).push('shell_intermediate')
            score.set(c,(score.get(c)||0)+15); detectedPatterns.get(c).push('shell_intermediate')
          }
        }
      }
    }
  }

  const timesByAccount = new Map()
  for(const t of transactions){
    const ts = parseTimestamp(t.timestamp).getTime()
    timesByAccount.set(t.sender_id, (timesByAccount.get(t.sender_id)||[]).concat(ts))
    timesByAccount.set(t.receiver_id, (timesByAccount.get(t.receiver_id)||[]).concat(ts))
  }
  for(const [acct, arr] of timesByAccount){
    arr.sort((a,b)=>a-b)
    let j=0
    for(let i=0;i<arr.length;i++){
      while(arr[i]-arr[j] > 72*3600*1000) j++
      if(i-j+1>=6){ score.set(acct,(score.get(acct)||0)+10); detectedPatterns.get(acct).push('high_velocity'); break }
    }
  }

  const suspicious = []
  for(const [acct, s] of score){
    const sc = Math.min(100, Math.round((s + Number.EPSILON)*10)/10)
    const pats = [...new Set(detectedPatterns.get(acct))]
    suspicious.push({account_id:acct, suspicion_score:sc, detected_patterns:pats, ring_id: null})
  }
  suspicious.sort((a,b)=>b.suspicion_score - a.suspicion_score)
  return suspicious
}

export function analyzeTransactions(rows){
  const built = buildGraph(rows)
  const detected = detectCycles(built.adj)
  const susp = computeSuspicion(built, detected, rows)
  const fraud_rings = detected.map((r,i)=>{
    const members = r.member_accounts
    const risk_score = Math.round((members.reduce((acc,m)=>acc + (susp.find(s=>s.account_id===m)?.suspicion_score||0),0)/members.length) * 10)/10
    for(const m of members){ const s = susp.find(x=>x.account_id===m); if(s) s.ring_id = r.ring_id }
    return {ring_id:r.ring_id, member_accounts:members, pattern_type:r.pattern_type, risk_score}
  })

  // filter out zero score accounts and format floats
  const filteredSusp = susp.filter(s=>s.suspicion_score>0).map(s=>({
    account_id: s.account_id,
    suspicion_score: parseFloat((s.suspicion_score).toFixed(1)),
    detected_patterns: s.detected_patterns,
    ring_id: (s.ring_id === undefined || s.ring_id === "") ? null : s.ring_id
  }))

  const total_accounts = built.nodes.length
  const flagged = filteredSusp.length
  return {suspicious_accounts: filteredSusp, fraud_rings, summary:{total_accounts_analyzed: total_accounts, suspicious_accounts_flagged: flagged, fraud_rings_detected: fraud_rings.length}}
}
