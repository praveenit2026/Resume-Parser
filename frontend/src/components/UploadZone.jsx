import { useRef, useState } from 'react'
import styles from './UploadZone.module.css'

export default function UploadZone({ file, onFile, resumeText, onText }) {
  const [drag, setDrag] = useState(false)
  const inputRef = useRef()

  const handleDrop = (e) => {
    e.preventDefault()
    setDrag(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) onFile(dropped)
  }

  const hasContent = file || resumeText.length > 10

  return (
    <div className={styles.wrapper}>
      <div
        className={`${styles.zone} ${drag ? styles.drag : ''} ${hasContent ? styles.filled : ''}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={(e) => e.target.files[0] && onFile(e.target.files[0])}
        />
        <div className={styles.icon}>
          {hasContent ? (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M9 12l2 2 4-4M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          ) : (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </div>
        {file ? (
          <>
            <p className={styles.filename}>{file.name}</p>
            <p className={styles.sub}>Click to replace</p>
          </>
        ) : (
          <>
            <p className={styles.title}>Drop resume here</p>
            <p className={styles.sub}>PDF, DOCX, or TXT · or paste below</p>
          </>
        )}
      </div>

      {!file && (
        <textarea
          className={styles.textarea}
          placeholder="…or paste your resume text directly here"
          value={resumeText}
          onChange={(e) => onText(e.target.value)}
          rows={5}
        />
      )}

      {file && (
        <button
          className={styles.clear}
          onClick={(e) => { e.stopPropagation(); onFile(null) }}
        >
          ✕ Remove file
        </button>
      )}
    </div>
  )
}
