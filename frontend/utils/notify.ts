/**
 * useNotify - Composable for toast notifications using Quasar
 */

import { useQuasar } from 'quasar';

// Map variant names to Quasar notify types
const variantMap: Record<string, string> = {
    'danger': 'negative',
    'success': 'positive',
    'warning': 'warning',
    'info': 'info',
    'primary': 'info',
    'secondary': 'info'
};

interface ToastProps {
    title?: string;
    body?: string | Error;
    variant?: string;
}

interface ToastOptions {
    props: ToastProps;
}

/**
 * Composable for showing toast notifications
 */
export function useNotify() {
    const $q = useQuasar();

    /**
     * Show a toast notification
     * @param options - Toast options
     */
    function show(options?: ToastOptions) {
        if (!options?.props) return;

        const { title, body, variant = 'info' } = options.props;

        // Convert Error objects to string
        const message = body instanceof Error ? body.message : String(body || '');

        $q.notify({
            message: message,
            caption: title,
            type: variantMap[variant] || 'info',
            position: 'top-right',
            timeout: variant === 'danger' || variant === 'negative' ? 5000 : 3000,
            actions: [
                { icon: 'close', color: 'white', round: true, handler: () => {} }
            ]
        });
    }

    return { show };
}

/**
 * Direct notify function for simpler usage
 */
export function notify(message: string, type: 'positive' | 'negative' | 'warning' | 'info' = 'info', title?: string) {
    const $q = useQuasar();
    $q.notify({
        message,
        caption: title,
        type,
        position: 'top-right',
        timeout: type === 'negative' ? 5000 : 3000,
        actions: [
            { icon: 'close', color: 'white', round: true, handler: () => {} }
        ]
    });
}
