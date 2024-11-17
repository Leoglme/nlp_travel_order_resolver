import BaseApiService from '@/core/services/BaseApiService'
import type { ErrorResponse } from '~/core/types/response'

/**
 * Response type for retrieving HTML documentation.
 */
export type HtmlDocumentationResponse = string;

/**
 * Service to interact with the documentation HTML API.
 */
export default class DocumentationHtmlService extends BaseApiService {
    /**
     * Fetches the HTML evaluation report for the travel intent classifier.
     * @returns {Promise<HtmlDocumentationResponse | ErrorResponse>} A promise resolved with the HTML report as a string, or an error response.
     */
    static async getTravelIntentClassifierEvaluation(): Promise<HtmlDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<HtmlDocumentationResponse>('/api/travel_intent_classifier_evaluation/index.html');
        } catch (error) {
            return { error: 'Unable to fetch the evaluation report.' } as ErrorResponse;
        }
    }
}
