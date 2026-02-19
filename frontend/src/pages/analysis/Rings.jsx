import React, {useState} from 'react'
import { useOutletContext } from 'react-router-dom'
import { Shield, Eye } from 'lucide-react'

export default function Rings(){
  const { result } = useOutletContext()
  const rings = result.rings || []
  const [filterType, setFilterType] = useState('All Types')
  const [selectedRing, setSelectedRing] = useState(null)
  
  console.log('🔄 Rings component mounted', { ringCount: rings.length, rings })
  
  const patternColors = {
    cycle: {bg: 'rgba(59, 130, 246, 0.1)', text: '#3b82f6', border: '#3b82f6', label: 'Circular'},
    shell: {bg: 'rgba(168, 85, 247, 0.1)', text: '#a855f7', border: '#a855f7', label: 'Shell'},
    smurfing: {bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: '#f59e0b', label: 'Smurfing'},
    hub: {bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: '#f59e0b', label: 'Hub'}
  }
  
  const filterTypes = ['All Types', 'Circular', 'Shell', 'Smurfing']
  
  const filteredRings = rings.filter(r => {
    if (filterType === 'All Types') return true
    const ptype = patternColors[r.pattern_type]?.label || r.pattern_type
    return ptype === filterType
  })
  
  const riskLevel = (score) => {
    if (score >= 70) return { color: '#ef4444', label: 'High', bg: 'rgba(239, 68, 68, 0.1)' }
    if (score >= 40) return { color: '#f59e0b', label: 'Medium', bg: 'rgba(245, 158, 11, 0.1)' }
    return { color: '#3b82f6', label: 'Low', bg: 'rgba(59, 130, 246, 0.1)' }
  }

  return (
    <div style={{padding: 0}}>
      <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #334155'}}>
        <div style={{padding: '8px 12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', color: '#ef4444'}}>
          <Shield size={20} />
        </div>
        <h3 style={{fontSize: '18px', fontWeight: '700', color: '#f1f5f9', margin: 0}}>Fraud Rings Detected</h3>
        <span style={{marginLeft: 'auto', fontSize: '12px', color: '#94a3b8', background: 'rgba(239, 68, 68, 0.1)', padding: '4px 12px', borderRadius: '20px'}}>{rings.length} rings</span>
      </div>
      
      {/* Filter Dropdown */}
      <div style={{marginBottom: '20px', position: 'relative'}}>
        <div style={{
          display: 'inline-block',
          position: 'relative'
        }}>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              background: 'rgba(30, 41, 59, 0.6)',
              color: '#f1f5f9',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s',
              appearance: 'none',
              paddingRight: '32px',
              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2394a3b8' d='M6 9L1 4h10z'/%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 8px center'
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#3b82f6'
              e.currentTarget.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.2)'
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = '#334155'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            {filterTypes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>
      
      {rings.length === 0 ? (
        <div style={{padding: '40px', textAlign: 'center', color: '#94a3b8'}}>
          <p>No fraud rings detected</p>
        </div>
      ) : (
        <>
          {/* Table */}
          <div style={{overflowX: 'auto'}}>
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead>
                <tr style={{borderBottom: '1px solid #334155', backgroundColor: 'rgba(15, 23, 42, 0.4)'}}>
                  <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Ring ID</th>
                  <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Pattern Type</th>
                  <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Member Count</th>
                  <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Risk Score</th>
                  <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Member Account IDs</th>
                  <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRings.length === 0 ? (
                  <tr><td colSpan={6} style={{padding: '40px', textAlign: 'center', color: '#94a3b8'}}>No rings match filter</td></tr>
                ) : (
                  filteredRings.map((r, i, arr) => {
                    const color = patternColors[r.pattern_type] || patternColors.cycle
                    const risk = riskLevel(r.risk_score)
                    return (
                      <tr 
                        key={r.ring_id}
                        style={{
                          borderBottom: '1px solid #334155',
                          backgroundColor: i % 2 === 0 ? 'transparent' : 'rgba(30, 41, 59, 0.3)',
                          transition: 'background-color 0.3s',
                          cursor: 'pointer',
                          animation: `slideInUp 0.6s ease-out forwards`,
                          animationDelay: `${i * 0.05}s`,
                          opacity: 0
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = i % 2 === 0 ? 'transparent' : 'rgba(30, 41, 59, 0.3)'
                        }}
                      >
                        <td style={{padding: '12px', color: '#cbd5e1', fontWeight: 'bold'}}>{r.ring_id}</td>
                        <td style={{padding: '12px'}}>
                          <span style={{
                            display: 'inline-block',
                            padding: '4px 8px',
                            background: color.bg,
                            color: color.text,
                            borderRadius: '6px',
                            fontSize: '11px',
                            fontWeight: '700',
                            textTransform: 'uppercase'
                          }}>
                            {color.label}
                          </span>
                        </td>
                        <td style={{padding: '12px', color: '#e2e8f0', fontWeight: '600'}}>{r.member_accounts.length}</td>
                        <td style={{padding: '12px'}}>
                          <span style={{
                            padding: '4px 10px',
                            borderRadius: '6px',
                            fontSize: '13px',
                            fontWeight: '700',
                            background: risk.bg,
                            color: risk.color
                          }}>
                            {r.risk_score.toFixed(1)}
                          </span>
                        </td>
                        <td style={{padding: '12px', color: '#cbd5e1', fontSize: '12px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>
                          {r.member_accounts.join(', ')}
                        </td>
                        <td style={{padding: '12px'}}>
                          <button
                            onClick={() => setSelectedRing(selectedRing?.ring_id === r.ring_id ? null : r)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              padding: '6px 12px',
                              borderRadius: '6px',
                              border: '1px solid #334155',
                              background: 'transparent',
                              color: '#3b82f6',
                              fontSize: '13px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              transition: 'all 0.3s'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'
                              e.currentTarget.style.borderColor = '#3b82f6'
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = 'transparent'
                              e.currentTarget.style.borderColor = '#334155'
                            }}
                          >
                            <Eye size={14} />
                            View
                          </button>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
          
          {/* Expanded Detail View */}
          {selectedRing && (
            <div style={{
              marginTop: '20px',
              padding: '16px',
              background: 'rgba(30, 41, 59, 0.6)',
              border: '1px solid #334155',
              borderRadius: '12px',
              animation: `slideInUp 0.3s ease-out forwards`
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
                <h4 style={{fontSize: '14px', fontWeight: '700', color: '#f1f5f9', margin: 0}}>
                  Ring Details: {selectedRing.ring_id}
                </h4>
                <button
                  onClick={() => setSelectedRing(null)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#94a3b8',
                    cursor: 'pointer',
                    fontSize: '20px',
                    fontWeight: '700'
                  }}
                >
                  ×
                </button>
              </div>
              
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px'}}>
                <div>
                  <div style={{fontSize: '12px', color: '#94a3b8', marginBottom: '4px', textTransform: 'uppercase'}}>Pattern Type</div>
                  <div style={{fontSize: '14px', color: '#f1f5f9', fontWeight: '600'}}>
                    {patternColors[selectedRing.pattern_type]?.label || selectedRing.pattern_type}
                  </div>
                </div>
                <div>
                  <div style={{fontSize: '12px', color: '#94a3b8', marginBottom: '4px', textTransform: 'uppercase'}}>Risk Score</div>
                  <div style={{fontSize: '14px', color: '#f1f5f9', fontWeight: '600'}}>
                    {selectedRing.risk_score.toFixed(1)}
                  </div>
                </div>
              </div>
              
              <div>
                <div style={{fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase'}}>Member Accounts</div>
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '8px'
                }}>
                  {selectedRing.member_accounts.map((acc, i) => (
                    <span
                      key={i}
                      style={{
                        padding: '6px 10px',
                        background: 'rgba(59, 130, 246, 0.1)',
                        color: '#3b82f6',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        fontWeight: '600',
                        border: '1px solid #3b82f6'
                      }}
                    >
                      {acc}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
      
      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
