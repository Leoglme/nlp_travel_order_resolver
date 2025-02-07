import BaseApiService from '@/core/services/BaseApiService'
import type {ErrorResponse} from '~/core/types/response'

/**
 * Response type for retrieving HTML documentation.
 */
export type HtmlDocumentationResponse = string;

/**
 * Response type for retrieving Markdown documentation.
 */
export type MarkdownDocumentationResponse = string;

/**
 * Service to interact with the documentation HTML API.
 */
export default class DocumentationService extends BaseApiService {
    /**
     * Fetches the HTML evaluation report for the travel intent classifier.
     * @returns {Promise<HtmlDocumentationResponse | ErrorResponse>} A promise resolved with the HTML report as a string, or an error response.
     */
    static async getTravelIntentClassifierEvaluation(): Promise<HtmlDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<HtmlDocumentationResponse>('/api/travel_intent_classifier_evaluation/index.html');
        } catch (error) {
            return {error: 'Unable to fetch the evaluation report.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the HTML evaluation report for the language identification
     * @returns {Promise<HtmlDocumentationResponse | ErrorResponse>}
     * A promise resolved with the HTML report as a string, or an error response.
     */
    static async getLanguageIdentificationEvaluation(): Promise<HtmlDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<HtmlDocumentationResponse>('/api/language_identification_evaluation/index.html');
        } catch (error) {
            return {error: 'Unable to fetch the evaluation report.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the HTML evaluation report for the departure and arrival extraction.
     * @returns {Promise<HtmlDocumentationResponse | ErrorResponse>}
     * A promise resolved with the HTML report as a string, or an error response.
     */
    static async getSncfRouteFinderEvaluation(): Promise<HtmlDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<HtmlDocumentationResponse>('/api/sncf_route_finder_evaluation/index.html');
        } catch (error) {
            return {error: 'Unable to fetch the evaluation report.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the HTML evaluation report for the departure and arrival extraction.
     * @returns {Promise<HtmlDocumentationResponse | ErrorResponse>}
     * A promise resolved with the HTML report as a string, or an error response.
     */
    static async getCamembertNERModelEvaluation(): Promise<HtmlDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<HtmlDocumentationResponse>('/api/camembert_ner_evaluation/index.html');
        } catch (error) {
            return {error: 'Unable to fetch the evaluation report.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the HTML evaluation report for the departure and arrival extraction.
     * @returns {Promise<HtmlDocumentationResponse | ErrorResponse>}
     * A promise resolved with the HTML report as a string, or an error response.
     */
    static async getCamembertNERModelEvaluationV2(): Promise<HtmlDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<HtmlDocumentationResponse>('/api/camembert_ner_evaluation_v2/index.html');
        } catch (error) {
            return {error: 'Unable to fetch the evaluation report.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the Markdown introduction of the project from the API.
     * @returns {Promise<MarkdownDocumentationResponse | ErrorResponse>} A promise resolved with the Markdown content as a string, or an error response.
     */
    static async getProjectIntroductionMarkdown(): Promise<MarkdownDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<MarkdownDocumentationResponse>('/api/project_introduction_markdown');
        } catch (error) {
            return {error: 'Unable to fetch the project introduction.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the Markdown content for the "Exemple Processing" documentation.
     * @returns {Promise<MarkdownDocumentationResponse | ErrorResponse>} A promise resolved with the Markdown content as a string, or an error response.
     */
    static async getExempleProcessingMarkdown(): Promise<MarkdownDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<MarkdownDocumentationResponse>('/api/exemple_processing_markdown');
        } catch (error) {
            return {error: 'Unable to fetch the exemple processing content.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the Markdown content for the "Decision Analysis" documentation.
     * @returns {Promise<MarkdownDocumentationResponse | ErrorResponse>} A promise resolved with the Markdown content as a string, or an error response.
     */
    static async getDecisionAnalysisMarkdown(): Promise<MarkdownDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<MarkdownDocumentationResponse>('/api/decision_analysis_markdown');
        } catch (error) {
            return {error: 'Unable to fetch the decision analysis content.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the Markdown content for the user guide "How to use" documentation.
     * @returns {Promise<MarkdownDocumentationResponse | ErrorResponse>} A promise resolved with the Markdown content as a string, or an error response.
     */
    static async getHowToUseMarkdown(): Promise<MarkdownDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<MarkdownDocumentationResponse>('/api/user_guide/how_to_use_markdown');
        } catch (error) {
            return {error: 'Unable to fetch the how to use content.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the Markdown content for the "Processus Training" documentation.
     * @returns {Promise<MarkdownDocumentationResponse | ErrorResponse>} A promise resolved with the Markdown content as a string, or an error response.
     */
    static async getProcessusTrainingMarkdown(): Promise<MarkdownDocumentationResponse | ErrorResponse> {
        try {
            return await this.get<MarkdownDocumentationResponse>('/api/processus_training_markdown');
        } catch (error) {
            return {error: 'Unable to fetch the processus training content.'} as unknown as ErrorResponse;
        }
    }

    /**
     * Fetches the PDF file for the "Architecture Schema" documentation.
     * @returns {Promise<Blob | ErrorResponse>} A promise resolved with the PDF file as a Blob, or an error response.
     */
    static async getArchitectureSchemaPdf(): Promise<Blob | ErrorResponse> {
        try {
            return await this.get<Blob>('/api/architecture_schema_pdf', {responseType: 'blob'});
        } catch (error) {
            return {error: 'Unable to fetch the architecture schema PDF.'} as unknown as ErrorResponse;
        }
    }
}
