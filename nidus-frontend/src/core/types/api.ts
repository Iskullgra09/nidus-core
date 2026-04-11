export type ApiStatus = "success" | "error";

export interface ApiError {
  field: string;
  message: string;
}

export interface GenericResponse<T> {
  status: ApiStatus;
  message: string | null;
  data: T | null;
  errors?: ApiError[];
}

export interface PageInfo {
  has_next_page: boolean;
  end_cursor: string | null;
}

export interface CursorPage<T> {
  items: T[];
  page_info: PageInfo;
}
