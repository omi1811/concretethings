// Middleware disabled temporarily - i18n will be re-enabled once proper [locale] folder structure is implemented
// import createMiddleware from 'next-intl/middleware';
 
// export default createMiddleware({
//   // A list of all locales that are supported
//   locales: ['en', 'hi'],
 
//   // Used when no locale matches
//   defaultLocale: 'en',
  
//   // Don't use a prefix for the default locale
//   localePrefix: 'as-needed'
// });
 
// export const config = {
//   // Match only internationalized pathnames
//   matcher: ['/', '/(hi|en)/:path*', '/((?!api|_next|_vercel|.*\\..*).*)']
// };

export function middleware(request) {
  // Simple pass-through middleware
  return;
}
