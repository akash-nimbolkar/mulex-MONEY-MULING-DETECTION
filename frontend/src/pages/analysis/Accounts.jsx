import React, { useMemo, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Users, Search } from 'lucide-react'

export default function Accounts() {
  const { rows, result } = useOutletContext()
  const suspicious = result?.accounts || []
  const [q, setQ] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 500

  // Build normalized accounts list: prefer server `result.accounts`, else derive from `rows`.
  const accounts = useMemo(() => {
    if (result && Array.isArray(result.accounts) && result.accounts.length > 0) {
      return result.accounts.map(a => ({
        id: a.account_id,
        score: a.score || a.suspicion_score || 0,
        patterns: a.tags || a.detected_patterns || [],
        transactions: a.transactions || 0
      }))
    }

    if (!rows || rows.length === 0) return []

    const map = new Map()
    for (const t of rows) {
      const s = t.sender || t.sender_id || t.from
      const r = t.receiver || t.receiver_id || t.to
      if (s) {
        if (!map.has(s)) map.set(s, { id: s, score: 0, patterns: [], transactions: 0 })
        map.get(s).transactions += 1
      }
      if (r) {
        if (!map.has(r)) map.set(r, { id: r, score: 0, patterns: [], transactions: 0 })
        map.get(r).transactions += 1
      }
    }

    // Merge suspicious scores if available
    const suspMap = new Map()
    for (const s of suspicious) if (s.account_id) suspMap.set(s.account_id, s)

    return Array.from(map.values()).map(acc => {
      const sus = suspMap.get(acc.id)
      return {
        id: acc.id,
        score: sus?.score || sus?.suspicion_score || acc.score || 0,
        patterns: sus?.tags || sus?.detected_patterns || acc.patterns || [],
        transactions: acc.transactions || 0
      }
    }).sort((a, b) => b.score - a.score)
  }, [rows, result])

  const filteredAll = accounts.filter(a => (a.id || '').toString().toLowerCase().includes(q.toLowerCase()))
  const total = filteredAll.length
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const start = page * pageSize
  const paged = filteredAll.slice(start, start + pageSize)

  const flaggedCount = accounts.filter(a => a.score > 0).length

  return (
    <div style={{ padding: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #334155' }}>
        <div style={{ padding: '8px 12px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '8px', color: '#8b5cf6' }}>
          <Users size={20} />
        </div>
        <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f1f5f9', margin: 0 }}>Account Analysis</h3>
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#94a3b8', background: 'rgba(139, 92, 246, 0.1)', padding: '4px 12px', borderRadius: '20px' }}>{flaggedCount} flagged</span>
      </div>

      <div style={{ marginBottom: '20px', position: 'relative' }}>
        <Search size={18} style={{ position: 'absolute', left: '12px', top: '12px', color: '#94a3b8' }} />
        <input
          placeholder="Search accounts..."
          value={q}
          onChange={e => { setQ(e.target.value); setPage(0) }}
          style={{
            width: '100%',
            padding: '10px 12px 10px 40px',
            borderRadius: '8px',
            border: '1px solid #334155',
            background: 'rgba(30, 41, 59, 0.6)',
            color: '#f1f5f9',
            fontSize: '14px',
            transition: 'all 0.3s'
          }}
        />
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #334155', backgroundColor: 'rgba(15, 23, 42, 0.4)' }}>
              <th style={headerStyle}>Account ID</th>
              <th style={headerStyle}>Score</th>
              <th style={headerStyle}>Patterns</th>
              <th style={headerStyle}>Transactions</th>
              <th style={headerStyle}>Status</th>
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>No accounts found</td></tr>
            ) : (
              paged.map((a, i) => (
                <tr key={a.id} style={rowStyle(i)}>
                  <td style={{ padding: '12px', color: '#e2e8f0', fontFamily: 'monospace', fontSize: '13px' }}>{a.id}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={scoreBadgeStyle(a.score)}>{Number(a.score || 0).toFixed(1)}</span>
                  </td>
                  <td style={{ padding: '12px', color: '#cbd5e1', fontSize: '13px' }}>{a.patterns && a.patterns.length > 0 ? a.patterns.join(', ') : '-'}</td>
                  <td style={{ padding: '12px', color: '#e2e8f0', fontWeight: '600' }}>{a.transactions || 0}</td>
                  <td style={{ padding: '12px' }}><span style={statusBadgeStyle(a.score)}>{a.score > 0 ? '⚠ Flagged' : '✓ Clean'}</span></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {total > pageSize && (
        <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <button disabled={page === 0} onClick={() => setPage(p => Math.max(0, p - 1))} style={pagerButtonStyle}>Previous</button>
          <button disabled={page + 1 >= totalPages} onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} style={pagerButtonStyle}>Next</button>
          <div style={{ marginLeft: 'auto', color: '#94a3b8', fontSize: 12 }}>Page {page + 1} / {totalPages} • {total} accounts</div>
        </div>
      )}

    </div>
  )
}

// inline styles
const headerStyle = { padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }
const rowStyle = (i) => ({ borderBottom: '1px solid #334155', backgroundColor: i % 2 === 0 ? 'transparent' : 'rgba(30, 41, 59, 0.3)' })
const scoreBadgeStyle = (score) => ({ padding: '4px 10px', borderRadius: '6px', fontSize: '13px', fontWeight: '700', background: score > 70 ? 'rgba(239, 68, 68, 0.1)' : score > 40 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(59, 130, 246, 0.1)', color: score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#3b82f6' })
const statusBadgeStyle = (score) => ({ display: 'inline-block', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: '700', background: score > 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)', color: score > 0 ? '#f87171' : '#86efac' })
const pagerButtonStyle = { padding: '6px 10px' }
