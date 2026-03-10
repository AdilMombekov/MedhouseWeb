// База URL бэкенда: в проде (Vercel) задаётся VITE_API_BASE (например https://xxx.railway.app), локально — пусто (запросы идут на /api через прокси).
export const API_BASE = import.meta.env.VITE_API_BASE || ''
