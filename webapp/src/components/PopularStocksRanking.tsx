import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

// Types
interface StockData {
  rank: number
  symbol: string
  name: string
  aiScore: number
  change: number
  monthReturn: number
  country: string
}

interface ETFData {
  rank: number
  symbol: string
  name: string
  aiScore: number
  change: number
  monthReturn: number
  category: string
}

// Dummy data for stocks
const topStocks: StockData[] = [
  {
    rank: 1,
    symbol: 'NOK',
    name: 'Nokia Corp ADR',
    aiScore: 10,
    change: 0,
    monthReturn: -2.26,
    country: 'FI'
  },
  {
    rank: 2,
    symbol: 'BTG',
    name: 'B2gold Corp',
    aiScore: 10,
    change: 1,
    monthReturn: 42.21,
    country: 'CA'
  },
  {
    rank: 3,
    symbol: 'KMI',
    name: 'Kinder Morgan Inc',
    aiScore: 9,
    change: 1,
    monthReturn: -0.04,
    country: 'US'
  },
  {
    rank: 4,
    symbol: 'IAG',
    name: 'Iamgold Corp',
    aiScore: 9,
    change: 0,
    monthReturn: 36.24,
    country: 'CA'
  },
  {
    rank: 5,
    symbol: 'KGC',
    name: 'Kinross Gold Corp',
    aiScore: 9,
    change: 0,
    monthReturn: 73.57,
    country: 'CA'
  }
]

// Dummy data for ETFs
const topETFs: ETFData[] = [
  {
    rank: 1,
    symbol: 'XLE',
    name: 'Energy Select Sector SPDR Fund',
    aiScore: 10,
    change: 2,
    monthReturn: 8.45,
    category: 'Energy'
  },
  {
    rank: 2,
    symbol: 'GDX',
    name: 'VanEck Gold Miners ETF',
    aiScore: 9,
    change: 1,
    monthReturn: 12.34,
    category: 'Precious Metals'
  },
  {
    rank: 3,
    symbol: 'XLF',
    name: 'Financial Select Sector SPDR Fund',
    aiScore: 9,
    change: 0,
    monthReturn: 5.67,
    category: 'Financial'
  },
  {
    rank: 4,
    symbol: 'IWM',
    name: 'iShares Russell 2000 ETF',
    aiScore: 8,
    change: -1,
    monthReturn: 3.21,
    category: 'Small Cap'
  },
  {
    rank: 5,
    symbol: 'EEM',
    name: 'iShares MSCI Emerging Markets ETF',
    aiScore: 8,
    change: 1,
    monthReturn: 7.89,
    category: 'Emerging Markets'
  }
]

// Helper functions
const getAIScoreBadgeColor = (score: number): string => {
  if (score >= 9) return 'bg-green-500 hover:bg-green-600'
  if (score >= 7) return 'bg-yellow-500 hover:bg-yellow-600'
  if (score >= 5) return 'bg-orange-500 hover:bg-orange-600'
  return 'bg-red-500 hover:bg-red-600'
}

const getReturnColor = (returnValue: number): string => {
  return returnValue >= 0 ? 'text-green-600' : 'text-red-600'
}

const getChangeIndicator = (change: number): string => {
  if (change > 0) return '↑'
  if (change < 0) return '↓'
  return '→'
}

const getChangeColor = (change: number): string => {
  if (change > 0) return 'text-green-600'
  if (change < 0) return 'text-red-600'
  return 'text-gray-500'
}

// Stock table component
const StockTable = ({ stocks, title }: { stocks: StockData[], title: string }) => (
  <Card className="w-full">
    <CardHeader>
      <CardTitle className="text-xl font-semibold text-gray-900">{title}</CardTitle>
      <p className="text-sm text-gray-600">
        Stocks are ranked according to the AI Score, which rates the probability of beating the market in the next 3 months.
      </p>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Rank</TableHead>
            <TableHead>Company</TableHead>
            <TableHead className="w-20 text-center">AI Score</TableHead>
            <TableHead className="w-16 text-center">Change</TableHead>
            <TableHead className="w-24 text-right">1M Return</TableHead>
            <TableHead className="w-20 text-center">Country</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {stocks.map((stock) => (
            <TableRow key={stock.symbol} className="hover:bg-gray-50">
              <TableCell className="font-medium">{stock.rank}</TableCell>
              <TableCell>
                <div>
                  <span className="font-semibold text-blue-600">{stock.symbol}</span>
                  <div className="text-sm text-gray-600">{stock.name}</div>
                </div>
              </TableCell>
              <TableCell className="text-center">
                <Badge 
                  variant="secondary" 
                  className={`${getAIScoreBadgeColor(stock.aiScore)} text-white font-bold`}
                >
                  {stock.aiScore}
                </Badge>
              </TableCell>
              <TableCell className="text-center">
                <span className={`font-semibold ${getChangeColor(stock.change)}`}>
                  {getChangeIndicator(stock.change)} {Math.abs(stock.change)}
                </span>
              </TableCell>
              <TableCell className={`text-right font-semibold ${getReturnColor(stock.monthReturn)}`}>
                {stock.monthReturn > 0 ? '+' : ''}{stock.monthReturn.toFixed(2)}%
              </TableCell>
              <TableCell className="text-center">
                <Badge variant="outline" className="text-xs">
                  {stock.country}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
)

// ETF table component
const ETFTable = ({ etfs, title }: { etfs: ETFData[], title: string }) => (
  <Card className="w-full">
    <CardHeader>
      <CardTitle className="text-xl font-semibold text-gray-900">{title}</CardTitle>
      <p className="text-sm text-gray-600">
        ETFs are ranked according to the AI Score, which rates the probability of beating the market in the next 3 months.
      </p>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Rank</TableHead>
            <TableHead>ETF</TableHead>
            <TableHead className="w-20 text-center">AI Score</TableHead>
            <TableHead className="w-16 text-center">Change</TableHead>
            <TableHead className="w-24 text-right">1M Return</TableHead>
            <TableHead className="w-32 text-center">Category</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {etfs.map((etf) => (
            <TableRow key={etf.symbol} className="hover:bg-gray-50">
              <TableCell className="font-medium">{etf.rank}</TableCell>
              <TableCell>
                <div>
                  <span className="font-semibold text-blue-600">{etf.symbol}</span>
                  <div className="text-sm text-gray-600">{etf.name}</div>
                </div>
              </TableCell>
              <TableCell className="text-center">
                <Badge 
                  variant="secondary" 
                  className={`${getAIScoreBadgeColor(etf.aiScore)} text-white font-bold`}
                >
                  {etf.aiScore}
                </Badge>
              </TableCell>
              <TableCell className="text-center">
                <span className={`font-semibold ${getChangeColor(etf.change)}`}>
                  {getChangeIndicator(etf.change)} {Math.abs(etf.change)}
                </span>
              </TableCell>
              <TableCell className={`text-right font-semibold ${getReturnColor(etf.monthReturn)}`}>
                {etf.monthReturn > 0 ? '+' : ''}{etf.monthReturn.toFixed(2)}%
              </TableCell>
              <TableCell className="text-center">
                <Badge variant="outline" className="text-xs">
                  {etf.category}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
)

// Main component
export default function PopularStocksRanking() {
  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Popular Stocks Ranked by AI</h1>
        <p className="text-gray-600">
          July 27, 2025. For next 3 months.
        </p>
      </div>
      
      <div className="grid gap-8 md:grid-cols-1 lg:grid-cols-2">
        <StockTable stocks={topStocks} title="Top Stocks" />
        <ETFTable etfs={topETFs} title="Top ETFs" />
      </div>
    </div>
  )
}
