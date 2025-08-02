const API_BASE_URL = 'http://localhost:8000';

export interface Product {
  name: string;
  price: number;
  url: string;
}

export interface ProductsMatchingPriceParams {
  price: number;
  maxProducts?: number;
}

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async getProductsMatchingPrice({
    price,
    maxProducts = 10,
  }: ProductsMatchingPriceParams): Promise<Product[]> {
    const url = new URL('/products-matching-price', this.baseURL);
    url.searchParams.set('price', price.toString());
    url.searchParams.set('max_products', maxProducts.toString());

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async checkHealth(): Promise<{ message: string }> {
    const response = await fetch(`${this.baseURL}/`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();
