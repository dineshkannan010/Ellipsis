// src/hooks/usePodcastSSE.ts
import { useEffect } from 'react'

const SSE_URL = 'http://localhost:5000/stream'

export type Stage =
  | 'crawling'
  | 'initialResponses'
  | 'debate'
  | 'scriptReady'
  | 'audioGenerating'
  | 'audioError'
  | 'audioReady'

interface UsePodcastSSEArgs {
  setStage: React.Dispatch<React.SetStateAction<Stage>>
  setResponses: React.Dispatch<
    React.SetStateAction<{ general_public?: string; critic?: string }>
  >
  setScript: React.Dispatch<React.SetStateAction<string>>
  setAudioSrc: React.Dispatch<React.SetStateAction<string>>
}

export function usePodcastSSE({
  setStage,
  setResponses,
  setScript,
  setAudioSrc,
}: UsePodcastSSEArgs) {
  useEffect(() => {
    console.log('📡 [SSE] mounting…')
    const es = new EventSource(SSE_URL)

    es.onopen = () => console.log('✅ SSE connection opened')
    es.onerror = (err) =>
      console.error('❌ SSE error (readyState=' + es.readyState + ')', err)

    // catch any un-typed “message” events
    es.onmessage = (e) => console.log('[SSE message]', e.data)

    es.addEventListener('status', (e) => {
      console.log('[SSE status]', e.data)
      const { status } = JSON.parse(e.data)
      switch (status) {
        case 'initial_response_generation_started':
          setStage('initialResponses')
          break
        case 'mad_started':
          setStage('debate')
          break
        case 'script_ready':
          setStage('scriptReady')
          break
        case 'audio_generation_started':
          setStage('audioGenerating')
          break
        case 'audio_error':
          setStage('audioError')
          break
        case 'podcast_generated':
          setStage('audioReady')
          break
      }
    })

    es.addEventListener('persona', (e) => {
      console.log('[SSE persona]', e.data)
      const { persona, response } = JSON.parse(e.data)
      if (persona === 'Sarah') {
        setResponses((r) => ({ ...r, general_public: response }))
      } else if (persona === 'John') {
        setResponses((r) => ({ ...r, critic: response }))
      }
    })

    es.addEventListener('script', (e) => {
      console.log('[SSE script]', e.data)
      const { script } = JSON.parse(e.data)
      setScript(script)
    })

    es.addEventListener('audio', (e) => {
      console.log('[SSE audio]', e.data)
      const { audio } = JSON.parse(e.data)
      setAudioSrc(`http://localhost:5000${audio}`)
    })

    return () => {
      console.log('📴 [SSE] unmounting')
      es.close()
    }
  }, [setStage, setResponses, setScript, setAudioSrc])
}