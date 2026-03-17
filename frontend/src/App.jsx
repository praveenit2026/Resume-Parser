import { useState } from 'react'
import UploadZone from './components/UploadZone'
import ResultsPanel from './components/ResultsPanel'
import { analyzeResume } from './hooks/useApi'
import styles from './App.module.css'

export default function App() {
  const [file, setFile] = useState(null)
  const [resumeText, setResumeText] = useState('')
  const [jobDesc, setJobDesc] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const canSubmit = (file || resumeText.trim().length > 30) && jobDesc.trim().length > 30

  const handleSubmit = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await analyzeResume({ file, resumeText, jobDescription: jobDesc })
      setResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setFile(null)
    setResumeText('')
    setJobDesc('')
    setError('')
  }

  return (
    <div className={styles.app}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.badge}>
          <span className={styles.pulse} />
          AI-Powered · FastAPI + SambaNova
        </div>
        <h1 className={styles.title}>
          Resume<em> meets</em><br />the Role
        </h1>
        <p className={styles.subtitle}>
          Upload your resume and paste the job description.<br />
          Get an instant ATS score, skill gap analysis, and coaching.
        </p>
      </header>

      <main className={styles.main}>
        {result ? (
          <ResultsPanel result={result} onReset={handleReset} />
        ) : (
          <>
            <div className={styles.inputGrid}>
              {/* Resume */}
              <div className={styles.inputCard}>
                <label className={styles.inputLabel}>
                  <span className={styles.labelNum}>01</span>
                  Your Resume
                </label>
                <UploadZone
                  file={file}
                  onFile={setFile}
                  resumeText={resumeText}
                  onText={setResumeText}
                />
              </div>

              {/* JD */}
              <div className={styles.inputCard}>
                <label className={styles.inputLabel}>
                  <span className={styles.labelNum}>02</span>
                  Job Description
                </label>
                <textarea
                  className={styles.jdTextarea}
                  placeholder="Paste the full job description here…&#10;&#10;Include: title, responsibilities, required skills, nice-to-haves, and any other details for the most accurate analysis."
                  value={jobDesc}
                  onChange={(e) => setJobDesc(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className={styles.errorBox}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {error}
              </div>
            )}

            <button
              className={styles.analyzeBtn}
              disabled={!canSubmit || loading}
              onClick={handleSubmit}
            >
              {loading ? (
                <>
                  <span className={styles.spinner} />
                  Analyzing your match…
                </>
              ) : (
                <>
                  Analyze Match
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </>
              )}
            </button>

            {/* Architecture note */}
            <div className={styles.archNote}>
              <div className={styles.archFlow}>
                {['Web UI', 'FastAPI', 'SambaNova', 'Match Score'].map((step, i) => (
                  <div key={i} className={styles.archFlowItem}>
                    <span className={styles.archStep}>{step}</span>
                    {i < 3 && <span className={styles.archArrow}>→</span>}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
