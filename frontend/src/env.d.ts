/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SONAR_API_KEY: string
  readonly VITE_SPOTIFY_CLIENT_ID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 