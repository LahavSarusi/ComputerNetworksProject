import { toast } from "react-toastify";
import type { ToastOptions } from "react-toastify";

/**
 * Custom hook for displaying toast notifications throughout the app
 * Provides convenient functions for success and error toasts
 *
 * @returns Object containing showSuccessToast and showErrorToast functions
 */
export function useToast() {
  /**
   * Display a success toast notification
   * @param message - The message to display
   * @param options - Optional toast configuration
   */
  const showSuccessToast = (message: string, options?: ToastOptions) => {
    toast.success(message, {
      position: "top-right",
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  };

  /**
   * Display an error toast notification
   * @param message - The error message to display
   * @param options - Optional toast configuration
   */
  const showErrorToast = (message: string, options?: ToastOptions) => {
    toast.error(message, {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  };

  /**
   * Display an info toast notification
   * @param message - The message to display
   * @param options - Optional toast configuration
   */
  const showInfoToast = (message: string, options?: ToastOptions) => {
    toast.info(message, {
      position: "top-right",
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  };

  /**
   * Display a warning toast notification
   * @param message - The message to display
   * @param options - Optional toast configuration
   */
  const showWarningToast = (message: string, options?: ToastOptions) => {
    toast.warning(message, {
      position: "top-right",
      autoClose: 4000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  };

  return {
    showSuccessToast,
    showErrorToast,
    showInfoToast,
    showWarningToast,
  };
}
