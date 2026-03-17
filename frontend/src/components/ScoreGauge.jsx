import styles from './ScoreGauge.module.css'

function getColor(score) {
  if (score >= 70) return { ring: '#2A6B45', bg: '#E4F0EA', text: '#1A4D30' }
  if (score >= 45) return { ring: '#B86B10', bg: '#FBF0E0', text: '#7A4608' }
  return { ring: '#C8402A', bg: '#F2E8E5', text: '#8B2418' }
}

export default function ScoreGauge({ score }) {
  const { ring, bg, text } = getColor(score)
  const r = 54
  const circ = 2 * Math.PI * r
  const fill = circ - (circ * score) / 100

  return (
    <div className={styles.wrap} style={{ background: bg }}>
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(0,0,0,0.08)" strokeWidth="10" />
        <circle
          cx="70" cy="70" r={r}
          fill="none"
          stroke={ring}
          strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={fill}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)' }}
        />
      </svg>
      <div className={styles.center}>
        <span className={styles.num} style={{ color: text }}>{score}</span>
        <span className={styles.label} style={{ color: text }}>/ 100</span>
      </div>
    </div>
  )
}
