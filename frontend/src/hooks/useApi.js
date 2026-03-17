import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function analyzeResume({ file, resumeText, jobDescription }) {
  const form = new FormData()
  form.append('job_description', jobDescription)
  if (file) {
    form.append('file', file)
  } else {
    form.append('resume_text', resumeText)
  }
  const { data } = await api.post('/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
