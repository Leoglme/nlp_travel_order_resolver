import { defineRule, configure } from 'vee-validate'
import { email, min, required, confirmed } from '@vee-validate/rules'

interface FieldValidationMetaInfo {
    field: string
    name: string
    label?: string
    value: unknown
    form: Record<string, unknown>
    rule?: {
        name: string
        params?: Record<string, unknown> | unknown[]
    }
}

// Fonction pour vérifier si params est un tableau
function isArray(params: unknown): params is unknown[] {
    return Array.isArray(params)
}

export default defineNuxtPlugin(() => {
    defineRule('required', required)
    defineRule('email', email)
    defineRule('min', min)
    defineRule('confirmed', confirmed)

    configure({
        generateMessage: (ctx: FieldValidationMetaInfo) => {
            // Définir un type plus spécifique pour l'objet des messages
            const messages: Record<string, (ctx: FieldValidationMetaInfo) => string> = {
                required: (ctx) => `Le champ ${ctx.field} est obligatoire.`,
                email: (ctx) => `Le champ ${ctx.field} doit être une adresse email valide.`,
                min: (ctx) => {
                    // Utilisation de la fonction type guard pour un accès sécurisé
                    const minValue = isArray(ctx.rule?.params) ? ctx.rule?.params[0] : undefined
                    return `Le champ ${ctx.field} doit contenir au moins ${minValue} caractères.`
                },
                confirmed: (ctx) => `Le champ ${ctx.field} ne correspond pas au premier champ.`,
                // Vous pouvez ajouter d'autres messages de validation ici
            }

            const messageGenerator = ctx.rule ? messages[ctx.rule.name] : undefined
            if (messageGenerator) {
                return messageGenerator(ctx)
            }

            return `Le champ ${ctx.field} est invalide.`
        },
        validateOnInput: true, // Valide les champs à chaque saisie
    })
})
