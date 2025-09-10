// // app/layout.tsx
// import { AuthProvider } from '@/contexts/AuthContext';
// import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
// import type { Metadata } from 'next';
// import { Inter } from 'next/font/google';
// import './globals.css';

// const inter = Inter({ subsets: ['latin'] });

// export const metadata: Metadata = {
//   title: 'BI Dashboard',
//   description: 'Business Intelligence Dashboard with Role-Based Access Control',
// };

// const queryClient = new QueryClient({
//   defaultOptions: {
//     queries: {
//       staleTime: 5 * 60 * 1000, // 5 minutes
//       retry: 1,
//     },
//   },
// });

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="en">
//       <body className={inter.className}>
//         <QueryClientProvider client={queryClient}>
//           <AuthProvider>
//             {children}
//           </AuthProvider>
//           <ReactQueryDevtools initialIsOpen={false} />
//         </QueryClientProvider>
//       </body>
//     </html>
//   );
// }


// app/layout.tsx
// import { AuthProvider } from '@/contexts/AuthContext';
// import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
// import type { Metadata } from 'next';
// import { Inter } from 'next/font/google';
// import './globals.css';

// const inter = Inter({ subsets: ['latin'] });

// export const metadata: Metadata = {
//   title: 'BI Dashboard',
//   description: 'Business Intelligence Dashboard with Role-Based Access Control',
// };

// // Create query client inside component to avoid class instance issues
// function getQueryClient() {
//   return new QueryClient({
//     defaultOptions: {
//       queries: {
//         staleTime: 5 * 60 * 1000, // 5 minutes
//         retry: 1,
//       },
//     },
//   });
// }

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   // Create query client inside the component
//   const queryClient = getQueryClient();

//   return (
//     <html lang="en">
//       <body className={inter.className}>
//         <QueryClientProvider client={queryClient}>
//           <AuthProvider>
//             {children}
//           </AuthProvider>
//           <ReactQueryDevtools initialIsOpen={false} />
//         </QueryClientProvider>
//       </body>
//     </html>
//   );
// }

// import './globals.css';
// import Providers from './providers';

// export const metadata = {
//   title: 'Reporting System',
//   description: 'Next.js + DRF Reporting frontend',
// };

// export default function RootLayout({ children }: { children: React.ReactNode }) {
//   return (
//     <html lang="en">
//       <body>
//         <Providers>{children}</Providers>
//       </body>
//     </html>
//   );
// }
// app/layout.tsx
// import { AuthProvider } from '@/contexts/AuthContext';
// import type { Metadata } from 'next';
// import { Inter } from 'next/font/google';
// import './globals.css';

// const inter = Inter({ subsets: ['latin'] });

// export const metadata: Metadata = {
//   title: 'BI Dashboard',
//   description: 'Business Intelligence Dashboard with Role-Based Access Control',
// };

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="en">
//       <body className={inter.className}>
//         {/* We'll move QueryClientProvider to a client component */}
//         <Providers>
//           {children}
//         </Providers>
//       </body>
//     </html>
//   );
// }

// // Create a separate client component for providers
// 'use client';

// import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
// import { useState } from 'react';

// function Providers({ children }: { children: React.ReactNode }) {
//   // Create QueryClient inside the client component
//   const [queryClient] = useState(() => new QueryClient({
//     defaultOptions: {
//       queries: {
//         staleTime: 5 * 60 * 1000, // 5 minutes
//         retry: 1,
//       },
//     },
//   }));

//   return (
//     <QueryClientProvider client={queryClient}>
//       <AuthProvider>
//         {children}
//       </AuthProvider>
//       <ReactQueryDevtools initialIsOpen={false} />
//     </QueryClientProvider>
//   );
//}
// app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
// If Providers is in the same folder as layout.tsx:
import Providers from './providers';


const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'BI Dashboard',
  description: 'Business Intelligence Dashboard with Role-Based Access Control',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}