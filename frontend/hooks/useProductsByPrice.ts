import { useQuery } from '@tanstack/react-query';
import { apiService, Product, ProductsMatchingPriceParams } from '../services/api';

export interface UseProductsByPriceOptions {
  enabled?: boolean;
  staleTime?: number;
  refetchOnWindowFocus?: boolean;
}

export interface UseProductsByPriceResult {
  products: Product[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
  isFetching: boolean;
}

export const useProductsByPrice = (
  params: ProductsMatchingPriceParams,
  options: UseProductsByPriceOptions = {}
): UseProductsByPriceResult => {
  const {
    enabled = true,
    staleTime = 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus = false,
  } = options;

  const {
    data: products = [],
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['products-by-price', params.price, params.maxProducts],
    queryFn: () => apiService.getProductsMatchingPrice(params),
    enabled: enabled && params.price > 0,
    staleTime,
    refetchOnWindowFocus,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    products,
    isLoading,
    isError,
    error: error as Error | null,
    refetch,
    isFetching,
  };
};
