import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Modal,
  Linking,
  Alert,
} from 'react-native';
import { useProductsByPrice } from '../hooks/useProductsByPrice';
import { useApiHealth } from '../hooks/useApiHealth';

const stores = [
  { id: 'traderjoes', name: 'Trader Joes', location: 'Boston, MA' },
  { id: 'starmarket', name: 'Star Market', location: 'Cambridge, MA' },
  { id: 'stopandshop', name: 'Stop & Shop', location: 'Somerville, MA' },
  { id: 'safeway', name: 'Safeway', location: 'Arlington, MA' },
];

export const GroceryApp = () => {
  const [selectedStore, setSelectedStore] = useState(stores[0]);
  const [currentPrice, setCurrentPrice] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [showCalculator, setShowCalculator] = useState(false);
  const [calculatorInput, setCalculatorInput] = useState('');
  const [calculatorResult, setCalculatorResult] = useState('');

  // API Health Check
  const { isHealthy, isLoading: isHealthLoading } = useApiHealth();

  // Get target price as number for API call
  const targetPriceNum = useMemo(() => {
    if (!targetPrice) return 0;
    const cleaned = targetPrice.replace('$', '');
    const num = parseFloat(cleaned);
    return isNaN(num) ? 0 : num;
  }, [targetPrice]);

  // Fetch products matching target price from API
  const {
    products,
    isLoading: isProductsLoading,
    isError: isProductsError,
    error: productsError,
    refetch: refetchProducts,
  } = useProductsByPrice(
    { price: targetPriceNum, maxProducts: 20 },
    { enabled: targetPriceNum > 0 }
  );

  // Transform API products to match UI expectations
  const recommendedProducts = useMemo(() => {
    return products.map((product, index) => ({
      id: index.toString(),
      product_name: product.name,
      product_price: `$${product.price.toFixed(2)}`,
      product_url: product.url,
      category: 'Unknown', // API doesn't provide category info
      store: 'Various', // API doesn't provide store info
    }));
  }, [products]);

  const handleCalculatePrice = () => {
    // Simple calculator for demonstration
    try {
      const result = eval(calculatorInput);
      setCalculatorResult(`$${result.toFixed(2)}`);
      setCurrentPrice(`$${result.toFixed(2)}`);
    } catch {
      Alert.alert('Error', 'Invalid calculation');
    }
  };

  const handleProductPress = (url: string) => {
    Linking.openURL(url).catch(() => {
      Alert.alert('Error', 'Could not open product page');
    });
  };

  const getRecommendedTargetPrice = () => {
    if (!currentPrice) return '';
    const current = parseFloat(currentPrice.replace('$', ''));
    const recommended = (current * 0.85).toFixed(2); // 15% savings
    return `$${recommended}`;
  };

  return (
    <ScrollView className="flex-1 bg-gray-50">
      <View className="p-4">
        {/* Header */}
        <Text className="mb-2 text-3xl font-bold text-gray-800">Grocery Price Finder</Text>
        <Text className="mb-2 text-gray-600">Find the best deals near you</Text>

        {/* API Health Status */}
        <View className="mb-6">
          {isHealthLoading ? (
            <Text className="text-sm text-gray-500">Connecting to server...</Text>
          ) : isHealthy ? (
            <Text className="text-sm text-green-600">✓ Connected to price database</Text>
          ) : (
            <View className="flex-row items-center">
              <Text className="mr-2 text-sm text-red-600">✗ Server offline</Text>
              <TouchableOpacity
                onPress={() => window.location.reload()}
                className="rounded bg-red-100 px-2 py-1">
                <Text className="text-xs text-red-600">Retry</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Store Selection */}
        <View className="mb-6">
          <Text className="mb-3 text-lg font-semibold text-gray-800">Select Store by Location</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} className="mb-2">
            {stores.map((store) => (
              <TouchableOpacity
                key={store.id}
                onPress={() => setSelectedStore(store)}
                className={`mr-3 min-w-32 rounded-lg p-3 ${
                  selectedStore.id === store.id ? 'bg-blue-500' : 'border border-gray-200 bg-white'
                }`}>
                <Text
                  className={`text-center font-medium ${
                    selectedStore.id === store.id ? 'text-white' : 'text-gray-800'
                  }`}>
                  {store.name}
                </Text>
                <Text
                  className={`mt-1 text-center text-sm ${
                    selectedStore.id === store.id ? 'text-blue-100' : 'text-gray-600'
                  }`}>
                  {store.location}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Price Inputs */}
        <View className="mb-6">
          <Text className="mb-3 text-lg font-semibold text-gray-800">Price Comparison</Text>

          {/* Current Price Input */}
          <View className="mb-4">
            <Text className="mb-2 text-sm font-medium text-gray-700">Current Price</Text>
            <View className="flex-row">
              <TextInput
                value={currentPrice}
                onChangeText={setCurrentPrice}
                placeholder="$0.00"
                className="flex-1 rounded-l-lg border border-gray-300 bg-white p-3"
                keyboardType="decimal-pad"
              />
              <TouchableOpacity
                onPress={() => setShowCalculator(true)}
                className="rounded-r-lg bg-blue-500 px-4 py-3">
                <Text className="font-medium text-white">Calculator</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Target Price Input */}
          <View className="mb-4">
            <Text className="mb-2 text-sm font-medium text-gray-700">Target Price</Text>
            <View className="flex-row">
              <TextInput
                value={targetPrice}
                onChangeText={setTargetPrice}
                placeholder="$0.00"
                className="flex-1 rounded-l-lg border border-gray-300 bg-white p-3"
                keyboardType="decimal-pad"
              />
              <TouchableOpacity
                onPress={() => setTargetPrice(getRecommendedTargetPrice())}
                className="rounded-r-lg bg-green-500 px-4 py-3">
                <Text className="font-medium text-white">Recommend</Text>
              </TouchableOpacity>
            </View>
            {currentPrice && (
              <Text className="mt-1 text-sm text-gray-600">
                Recommended: {getRecommendedTargetPrice()} (15% savings)
              </Text>
            )}
          </View>
        </View>

        {/* Product List */}
        <View className="mb-6">
          <View className="mb-3 flex-row items-center justify-between">
            <Text className="text-lg font-semibold text-gray-800">
              Recommended Products ({recommendedProducts.length})
            </Text>
            {isProductsLoading && <Text className="text-sm text-blue-600">Loading...</Text>}
          </View>

          {/* API Error Handling */}
          {isProductsError && (
            <View className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4">
              <Text className="mb-2 font-medium text-red-800">Error loading products</Text>
              <Text className="mb-3 text-sm text-red-600">
                {productsError?.message || 'Unable to fetch products from server'}
              </Text>
              <TouchableOpacity
                onPress={() => refetchProducts()}
                className="self-start rounded-lg bg-red-500 px-4 py-2">
                <Text className="font-medium text-white">Try Again</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Loading State */}
          {isProductsLoading && targetPriceNum > 0 && (
            <View className="rounded-lg border border-blue-200 bg-blue-50 p-6">
              <Text className="text-center text-blue-800">
                Finding products under ${targetPriceNum.toFixed(2)}...
              </Text>
            </View>
          )}

          {/* Products List */}
          {!isProductsLoading &&
            !isProductsError &&
            recommendedProducts.map((product) => (
              <View
                key={product.id}
                className="mb-3 rounded-lg border border-gray-200 bg-white p-4">
                <View className="mb-2 flex-row items-start justify-between">
                  <Text className="mr-2 flex-1 font-medium text-gray-800">
                    {product.product_name}
                  </Text>
                  <Text className="text-lg font-bold text-green-600">{product.product_price}</Text>
                </View>

                <View className="flex-row items-center justify-between">
                  <View>
                    <Text className="text-sm text-gray-600">From database</Text>
                    <Text className="text-sm text-gray-500">Various stores</Text>
                  </View>

                  <TouchableOpacity
                    onPress={() => handleProductPress(product.product_url)}
                    className="rounded-lg bg-blue-500 px-4 py-2">
                    <Text className="font-medium text-white">View Product</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}

          {/* No Results State */}
          {!isProductsLoading &&
            !isProductsError &&
            recommendedProducts.length === 0 &&
            targetPriceNum > 0 && (
              <View className="rounded-lg border border-gray-200 bg-white p-6">
                <Text className="mb-2 text-center text-gray-600">
                  No products found under ${targetPriceNum.toFixed(2)}
                </Text>
                <Text className="text-center text-sm text-gray-500">
                  Try increasing your target price to see more results.
                </Text>
              </View>
            )}

          {/* No Target Price State */}
          {!targetPrice && (
            <View className="rounded-lg border border-gray-200 bg-gray-50 p-6">
              <Text className="mb-2 text-center text-gray-600">
                Enter a target price to see product recommendations
              </Text>
              <Text className="text-center text-sm text-gray-500">
                Products will be sorted by closest match to your target price.
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Calculator Modal */}
      <Modal
        visible={showCalculator}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowCalculator(false)}>
        <View className="flex-1 items-center justify-center bg-black/50">
          <View className="w-80 max-w-sm rounded-lg bg-white p-6">
            <Text className="mb-4 text-xl font-bold text-gray-800">Price Calculator</Text>

            <TextInput
              value={calculatorInput}
              onChangeText={setCalculatorInput}
              placeholder="Enter calculation (e.g., 2.99 * 2)"
              className="mb-4 rounded-lg border border-gray-300 bg-gray-50 p-3"
              multiline
            />

            {calculatorResult && (
              <View className="mb-4 rounded-lg bg-green-50 p-3">
                <Text className="font-medium text-green-800">Result: {calculatorResult}</Text>
              </View>
            )}

            <View className="flex-row space-x-3">
              <TouchableOpacity
                onPress={handleCalculatePrice}
                className="flex-1 rounded-lg bg-blue-500 py-3">
                <Text className="text-center font-medium text-white">Calculate</Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => {
                  setShowCalculator(false);
                  setCalculatorInput('');
                  setCalculatorResult('');
                }}
                className="flex-1 rounded-lg bg-gray-500 py-3">
                <Text className="text-center font-medium text-white">Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};
