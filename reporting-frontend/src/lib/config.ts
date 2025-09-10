// lib/config.ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'BI Dashboard',
};