import '../styles/globals.css'
import { SWRConfig } from 'swr'
import axios from 'axios'

axios.defaults.baseURL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'

function MyApp({ Component, pageProps }) {
  return (
    <SWRConfig value={{ fetcher: (url) => axios.get(url).then(r => r.data) }}>
      <Component {...pageProps} />
    </SWRConfig>
  )
}

export default MyApp
