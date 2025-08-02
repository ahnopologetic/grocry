# Grocery Price Finder App

A comprehensive single-page React Native app showcasing grocery price comparison and product discovery features.

## Features Implemented

### 🏪 Store Selection Based on Location
- **Multiple Store Support**: Choose from Trader Joe's, Star Market, Stop & Shop, and Safeway
- **Location-Based Selection**: Each store shows its location (Boston, Cambridge, Somerville, Arlington)
- **Interactive Store Cards**: Easy-to-use horizontal scrollable store selection with visual feedback

### 💰 Price Input & Calculator
- **Current Price Input**: Manual entry field for current product prices
- **On-Demand Calculator Modal**: Built-in calculator for complex price calculations
  - Supports mathematical expressions (e.g., "2.99 * 2" for bulk pricing)
  - Real-time calculation results
  - Automatic transfer of calculated price to current price field

### 🎯 Target Price Management
- **Manual Target Price Input**: Set your desired maximum price
- **Recommended Target Price**: Smart recommendation system
  - Calculates 15% savings from current price
  - One-click application of recommended price
  - Shows savings percentage

### 📦 Product Recommendations
- **Smart Filtering**: Products filtered based on target price criteria
- **Real Product Data**: Uses actual scraped data from grocery stores
- **Product Count Display**: Shows number of matching products

### 🏷️ Category-Based Organization
- **Multiple Categories**: Produce, Snacks, Pantry, Ready Meals, Dairy, Meat, Bakery
- **Filter by Category**: Horizontal scrollable category filter
- **"All" Option**: View products across all categories
- **Visual Category Indicators**: Clear category labeling on each product

### 🔗 Product Page Integration
- **Direct Product Links**: "View Product" button on each item
- **External Browser Support**: Opens actual product pages from store websites
- **Error Handling**: Graceful handling of link failures

## Technical Implementation

### UI/UX Features
- **Responsive Design**: Optimized for mobile devices
- **Smooth Scrolling**: Horizontal and vertical scroll views
- **Interactive Elements**: Touch feedback on all buttons and selections
- **Modal Interfaces**: Calculator modal with backdrop
- **Color-Coded Interface**: Consistent color scheme with semantic meaning

### Data Structure
```typescript
interface Product {
  id: string;
  product_name: string;
  product_price: string;
  product_url: string;
  category: string;
  store: string;
}
```

### State Management
- React hooks for local state management
- Real-time filtering and calculations
- Responsive UI updates based on user interactions

## Usage Flow

1. **Select Store**: Choose your preferred grocery store by location
2. **Set Current Price**: Either manually input or use calculator for complex pricing
3. **Define Target**: Set target price manually or use smart recommendations
4. **Filter by Category**: Browse products by specific categories
5. **Browse Results**: View filtered, price-appropriate product recommendations
6. **Visit Products**: Click "View Product" to see full product details on store website

## Mock Data

The app includes representative data from actual grocery store scraping, including:
- Trader Joe's products with real names and prices
- Multiple product categories
- Actual product URLs for external linking

## Future Enhancements

- Real-time data integration with backend scrapers
- Location-based store discovery using GPS
- Price history tracking
- User favorites and shopping lists
- Push notifications for price drops
- Barcode scanning for quick price entry