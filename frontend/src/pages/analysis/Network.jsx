import React, {useRef, useState} from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import { useOutletContext } from 'react-router-dom'
import { Network as NetworkIcon } from 'lucide-react'

export default function Network(){
  const cyRef = useRef(null)
  const context = useOutletContext()
  const { result, rows } = context || {}
  const [simplify, setSimplify] = useState(false)
  const [showLabels, setShowLabels] = useState(true)

  console.log('🔄 Network component mounted', { contextExists: !!context, result, rowsCount: rows?.length })

  // Prefer server-provided viz data (result.nodes/result.edges) for correctness and performance.
  let nodesSet = new Set()
  const edges = []

  if (result?.nodes && Array.isArray(result.nodes) && result.nodes.length > 0) {
    for (const n of result.nodes) {
      if (n && n.data && n.data.id) nodesSet.add(n.data.id)
    }
    if (result.edges && Array.isArray(result.edges)) {
      for (const e of result.edges) {
        // normalize edge shape: accept {data:{source,target,id}} or {source, target, id}
        if (e && e.data && e.data.source && e.data.target) edges.push(e)
        else if (e && (e.source || e.target)) edges.push({ data: { id: e.id || `${e.source}-${e.target}`, source: e.source, target: e.target } })
      }
    }
  } else if (rows && Array.isArray(rows)) {
    // fallback to rows (smaller datasets)
      for(const t of rows) {
      if (!t) continue
      const s = t.sender || t.sender_id || t.from
      const r = t.receiver || t.receiver_id || t.to
      if (s) nodesSet.add(s)
      if (r) nodesSet.add(r)
      if (t.transaction_id && s && r) edges.push({data:{id:t.transaction_id, source:s, target:r}})
    }
  }

  console.log(`📊 Network: ${nodesSet.size} nodes, ${edges.length} edges`)

  // If edges exist but nodes set is empty, infer nodes from edges' source/target
  if (nodesSet.size === 0 && edges.length > 0) {
    for (const e of edges) {
      const d = e.data || e
      if (d.source) nodesSet.add(d.source)
      if (d.target) nodesSet.add(d.target)
    }
    console.log(`ℹ️ Inferred ${nodesSet.size} nodes from edges`)
  }
  
  // Create account score map
  const scoreMap = new Map()
  const susSet = new Set((result?.accounts||[]).map(s=>s.account_id).filter(Boolean))
  
  if (result?.accounts && Array.isArray(result.accounts)) {
    for (const acc of result.accounts) {
      scoreMap.set(acc.account_id, acc.suspicion_score)
    }
    console.log(`💾 Created score map with ${scoreMap.size} accounts`, Array.from(scoreMap.entries()).slice(0, 5))
  } else {
    console.warn('⚠️ No accounts data in result:', result?.accounts)
  }
  
  const nEls = Array.from(nodesSet).map(id=>{
    const score = scoreMap.get(id) || 0
    const isSuspicious = susSet.has(id)
    // Format: show ID with score as suffix for suspicious accounts
    const label = isSuspicious ? `${id} (${score.toFixed(0)})` : id
    return {
      data:{
        id,
        label: label,
        score: score,
        isSuspicious: isSuspicious
      }
    }
  })
  
  console.log('🎨 Elements created:', { nodeCount: nEls.length, edgeCount: edges.length, suspiciousCount: susSet.size })
  
  const elements = [...nEls.map(n=>({data:n.data, classes: n.data.isSuspicious?'sus':''})), ...edges]

  // For very large graphs, simplify view: use smaller nodes, hide labels, and use grid layout
  const elementCount = elements.length
  const large = elementCount > 2000
  
  console.log('✅ Final elements:', elements.length)

  return (
    <div style={{padding: 0}}>
      <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #334155'}}>
        <div style={{padding: '8px 12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', color: '#3b82f6'}}>
          <NetworkIcon size={20} />
        </div>
        <h3 style={{fontSize: '18px', fontWeight: '700', color: '#f1f5f9', margin: 0}}>Transaction Network</h3>
        <span style={{marginLeft: 'auto', fontSize: '12px', color: '#94a3b8', background: 'rgba(59, 130, 246, 0.1)', padding: '4px 12px', borderRadius: '20px'}}>{nodesSet.size} accounts</span>
      </div>
      <div style={{height: 700, borderRadius: 12, border: '1px solid #334155', overflow: 'hidden', background: 'rgba(15, 23, 42, 0.4)'}}>
        <CytoscapeComponent 
          elements={elements} 
          style={{width:'100%',height:'100%'}} 
          stylesheet={[
            {
              selector: 'node',
              style: {
                'label': showLabels ? 'data(label)' : '',
                'background-color': '#3b82f6',
                'width': large || simplify ? 8 : 70,
                'height': large || simplify ? 8 : 70,
                'font-size': large ? 8 : 12,
                'color': '#fff',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-weight': 'bold'
              }
            },
            {
              selector: 'edge',
              style: {
                'line-color': '#475569',
                'target-arrow-color': '#475569',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 1.0,
                'curve-style': 'bezier',
                'width': large ? 0.6 : 2,
                'opacity': large ? 0.5 : 0.9
              }
            },
            {
              selector: '.sus',
              style: {
                'background-color': '#ef4444',
                'width': large || simplify ? 10 : 80,
                'height': large || simplify ? 10 : 80,
                'border-width': large ? 1 : 3,
                'border-color': '#991b1b'
              }
            }
          ]}
          layout={large ? {name: simplify ? 'grid' : 'grid', rows: Math.ceil(Math.sqrt(nodesSet.size)), animate: false} : {name: 'cose', directed: true, animate: true, animationDuration: 500, avoidOverlap: true, nodeSpacing: 15, padding: 40, randomize: false}}
          cy={(cy)=>{
            cyRef.current=cy
            console.log('✅ Cytoscape initialized with', cy.elements().length, 'elements')
            if (!large) {
              setTimeout(() => {
                const layout = cy.layout({name: 'cose', directed: true, animate: true, animationDuration: 500, avoidOverlap: true, nodeSpacing: 15, padding: 40})
                layout.run()
              }, 100)
            }
            // tune interaction options for performance
            cy.minZoom(0.1)
            cy.maxZoom(4)
          }} 
        />
      </div>
      {/* Controls for large graphs */}
      {large && (
        <div style={{display:'flex', gap:10, marginTop:12}}>
          <button onClick={() => setSimplify(s=>!s)} style={{padding:'6px 10px'}}>Toggle Simplify View</button>
          <button onClick={() => setShowLabels(s=>!s)} style={{padding:'6px 10px'}}>Toggle Labels</button>
        </div>
      )}
    </div>
  )
}
