# Fix Dashboard, Insights, and Chatbot Loading Issues

## Root Cause
`frontend/services/api.ts` throws a hard error at module load time if `NEXT_PUBLIC_API_URL` is missing. Since Dashboard, Insights, and Chat all import `api.ts`, the entire JS bundle crashes immediately on page load.

## Steps
- [x] Fix `frontend/services/api.ts` - remove hard throw, add runtime fallback
- [x] Delete duplicate `frontend/next.config.js`
- [x] Rebuild frontend
- [x] Verify static files exist (build/dashboard.html, build/insights.html, build/chat.html)

