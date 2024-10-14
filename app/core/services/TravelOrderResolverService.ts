import BaseApiService from '@/core/services/BaseApiService'
import type { ErrorResponse } from '~/core/types/response'

export default class TravelOrderResolverService extends BaseApiService {

    /**
     * Sends a request to convert audio to text.
     * @param {File} file The audio file to be converted.
     * @returns {Promise<{ sentence: string | ErrorResponse}>} A promise resolved with the text or throws an error.
     */
    static async audioToText(file: File): Promise<{ sentence: string } | ErrorResponse> {
        const formData = new FormData()
        formData.append('file', file)

        return await this.post<{ sentence: string }>('/api/audio-to-text', formData)
    }

    /**
     * Sends a request to validate a travel intent from a sentence.
     * @param {string} sentence The sentence to validate.
     * @returns {Promise<{ is_valid: boolean; reason: string | ErrorResponse}>} A promise resolved with the validation result or throws an error.
     */
    static async validateTravelIntent(sentence: string): Promise<{ is_valid: boolean; reason: string } | ErrorResponse> {
        return await this.post<{ is_valid: boolean; reason: string }>('/api/validate-travel-intent', { sentence })
    }

    /**
     * Sends a request to find the best route between cities extracted from a sentence.
     * @param {string} sentence The sentence containing departure and destination cities.
     * @returns {Promise<{ departure: string; destination: string; route: string[] | ErrorResponse}>} A promise resolved with the route or throws an error.
     */
    static async findRoute(sentence: string): Promise<{ departure: string; destination: string; route: string[] } | ErrorResponse> {
        return await this.post<{ departure: string; destination: string; route: string[] }>('/api/sncf/find-route', { sentence })
    }
}
