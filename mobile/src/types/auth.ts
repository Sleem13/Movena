export type User = { user_id: string; email: string; full_name?: string | null; role: string; is_active?: boolean };
export type LoginResponse = { access_token: string; token_type: string; expires_in: number; user: User };
