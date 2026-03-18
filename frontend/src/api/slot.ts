import { apiClient } from './apiClient';

export interface Slot {
  id: string;
  office_id: string;
  slot_date: string;
  slot_time: string;
  capacity: number;
  taken: number;
  available: number;
}

export interface SlotSearchParams {
  location?: string;
  date?: string;
  page?: number;
  size?: number;
}

export interface PaginatedSlotResponse {
  items: Slot[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const slotApi = {
  /**
   * Search for available slots by location and date
   * @param params Search parameters (location, date, page, size)
   * @returns Promise with paginated slot search results
   */
  searchSlots: async (params: SlotSearchParams): Promise<PaginatedSlotResponse> => {
    const queryParams = new URLSearchParams();

    if (params.location) queryParams.append('location', params.location);
    if (params.date) queryParams.append('date', params.date);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.size) queryParams.append('size', params.size.toString());

    const response = await apiClient.get(`/api/slots?${queryParams.toString()}`);
    return response.data;
  }
};
