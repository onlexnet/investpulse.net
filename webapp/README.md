# Predictive Trading Dashboard

A React component built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui that displays financial stocks and ETFs ranking similar to Danelfin.com's "Popular Stocks Ranked by Danelfin AI" section.

## Features

- **Responsive Design**: Clean, modern interface that works on all devices
- **TypeScript Support**: Full type safety for props and data structures  
- **shadcn/ui Components**: Professional UI components (Card, Badge, Table)
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Accessible**: Semantic HTML markup and WCAG compliant
- **Dummy Data**: Realistic stock and ETF data with AI scores and returns

## Component Features

### Top Stocks Section
- Displays top-ranked stocks with AI scores (1-10)
- Shows 1-month returns with color coding (green for positive, red for negative)
- Includes change indicators with directional arrows
- Country badges for stock origin
- Hover effects for better interactivity

### Top ETFs Section  
- Similar layout to stocks but for ETFs
- Category badges instead of country
- Same AI scoring and return display system

## Technology Stack

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
