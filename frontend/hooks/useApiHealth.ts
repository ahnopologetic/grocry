import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';

export interface UseApiHealthResult {
  isHealthy: boolean;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  message: string | null;
}

export const useApiHealth = (): UseApiHealthResult => {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['api-health'],
    queryFn: () => apiService.checkHealth(),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Check every minute
    retry: 1,
  });

  return {
    isHealthy: !isError && !!data,
    isLoading,
    isError,
    error: error as Error | null,
    message: data?.message || null,
  };
};
