export interface PropertyImage {
  img_id: number;
  img_url: string;
  is_cover: boolean;
}

export interface Property {
  prop_id: number;
  owner_id: number;
  image: string;
  images?: PropertyImage[];
  price: string; // Стоимость
  title?: string;
  description?: string;
  square?: string; 
  city?: string;
  floor?: number;
  rooms?: number;
  current_tenants?: number;
  potential_tenants?: number;
  created_at?: string;

}

export interface PropertyFormData {
  owner_id: number;
  image: string;
  price: string;
  title: string;
  description: string;
  city: string;
  floor: number;
  rooms: number;
  current_tenants: number;
  potential_tenants: number;
  images?: PropertyImage[];
}