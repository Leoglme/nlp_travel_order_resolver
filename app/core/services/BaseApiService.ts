import axios from 'axios'
import type { AxiosError } from 'axios'
import type { ErrorResponse } from '~/core/types/response'

export default class BaseApiService {
    protected static apiUrl: string | undefined = import.meta.env.VITE_API_BASE_URL

    protected static client() {
        return axios.create({
            baseURL: this.apiUrl
        })
    }

    protected static async get<T>(url: string): Promise<T> {
        const response = await this.client().get(url)
        return response.data as T
    }

    protected static async post<T>(url: string, data: unknown): Promise<T | ErrorResponse > {
        try {
            const response = await this.client().post(url, data)
            return response.data as T
        } catch (e) {
            const error = e as AxiosError<ErrorResponse >
            return error.response?.data as ErrorResponse
        }
    }

    protected static async put<T>(url: string, data?: unknown): Promise<T> {
        const response = await this.client().put(url, data)
        return response.data as T
    }

    protected static async delete<T>(url: string): Promise<T> {
        const response = await this.client().delete(url)
        return response.data as T
    }
}
