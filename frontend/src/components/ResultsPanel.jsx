import ScoreGauge from './ScoreGauge'
import styles from './ResultsPanel.module.css'

function verdictColor(verdict) {
  if (verdict === 'Strong Match') return styles.verdictGreen
  if (verdict === 'Good Match') return styles.verdictGreen
  if (verdict === 'Partial Match') return styles.verdictAmber
  return styles.verdictRed
}

export default function ResultsPanel({ result, onReset }) {
  const { score, verdict, summary, matchedSkills, missingSkills, suggestions, experienceAlignment, educationAlignment } = result

  return (
    <div className={styles.panel}>

      {/* Hero Score */}
      <div className={styles.hero}>
        <ScoreGauge score={score} />
        <div className={styles.heroText}>
          <span className={`${styles.verdict} ${verdictColor(verdict)}`}>{verdict}</span>
          <h2 className={styles.heroTitle}>Match Analysis</h2>
          <p className={styles.summary}>{summary}</p>
        </div>
      </div>

      {/* Skills Grid */}
      <div className={styles.skillsGrid}>
        <div className={`${styles.skillCard} ${styles.matched}`}>
          <h3 className={styles.skillTitle}>
            <span className={styles.dot} data-type="match" />
            Matched Skills
            <span className={styles.count}>{matchedSkills.length}</span>
          </h3>
          <div className={styles.tags}>
            {matchedSkills.map((s, i) => (
              <span key={i} className={`${styles.tag} ${styles.tagMatch}`}>{s}</span>
            ))}
          </div>
        </div>

        <div className={`${styles.skillCard} ${styles.missed}`}>
          <h3 className={styles.skillTitle}>
            <span className={styles.dot} data-type="miss" />
            Missing Skills
            <span className={styles.count}>{missingSkills.length}</span>
          </h3>
          <div className={styles.tags}>
            {missingSkills.map((s, i) => (
              <span key={i} className={`${styles.tag} ${styles.tagMiss}`}>{s}</span>
            ))}
            {missingSkills.length === 0 && <span className={styles.none}>None identified</span>}
          </div>
        </div>
      </div>

      {/* Alignment */}
      <div className={styles.alignGrid}>
        <div className={styles.alignCard}>
          <h4 className={styles.alignLabel}>Experience Fit</h4>
          <p className={styles.alignText}>{experienceAlignment}</p>
        </div>
        <div className={styles.alignCard}>
          <h4 className={styles.alignLabel}>Education Fit</h4>
          <p className={styles.alignText}>{educationAlignment}</p>
        </div>
      </div>

      {/* Suggestions */}
      <div className={styles.suggestionsCard}>
        <h3 className={styles.suggestionsTitle}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          How to Improve Your Resume
        </h3>
        <ol className={styles.suggestionsList}>
          {suggestions.map((s, i) => (
            <li key={i} className={styles.suggestionItem}>
              <span className={styles.suggNum}>{String(i + 1).padStart(2, '0')}</span>
              <span className={styles.suggText}>{s}</span>
            </li>
          ))}
        </ol>
      </div>

      <button className={styles.resetBtn} onClick={onReset}>
        ← Analyze another resume
      </button>
    </div>
  )
}
