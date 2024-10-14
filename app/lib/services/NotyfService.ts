import { Notyf } from 'notyf'

export default class NotyfService {
    public notyf: Notyf | undefined

    constructor() {
        this.init()
    }

    private init(): void {
        if (!this.notyf) {
            this.setNotyf()
        }
    }

    private setNotyf(): void {
        const notyf: Notyf = new Notyf()
        notyf.options = {
            ...notyf.options,
            dismissible: true,
            duration: 3500,
            position: {
                x: 'right',
                y: 'top',
            },
        }
        this.notyf = notyf
    }

    public success(message: string): void {
        if (this.notyf) {
            this.notyf.success(message)
        }
    }

    public error(message: string): void {
        if (this.notyf) {
            this.notyf.error(message)
        }
    }

    public info(message: string): void {
        if (this.notyf) {
            this.notyf.open({ type: 'info', message })
        }
    }

    public warn(message: string): void {
        if (this.notyf) {
            this.notyf.open({ type: 'warn', message })
        }
    }

    public dismissAll(): void {
        if (this.notyf) {
            this.notyf.dismissAll()
        }
    }
}
