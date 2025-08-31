import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Utility to map custom design tokens to Tailwind classes
export const themeClasses = {
  background: "bg-white dark:bg-gray-900",
  foreground: "text-gray-900 dark:text-gray-50",
  card: "bg-white dark:bg-gray-800",
  cardForeground: "text-gray-900 dark:text-gray-50",
  primary: "bg-blue-600 dark:bg-blue-500",
  primaryForeground: "text-white",
  secondary: "bg-gray-100 dark:bg-gray-700",
  secondaryForeground: "text-gray-900 dark:text-gray-50",
  muted: "bg-gray-100 dark:bg-gray-800",
  mutedForeground: "text-gray-500 dark:text-gray-400",
  accent: "bg-gray-100 dark:bg-gray-700",
  accentForeground: "text-gray-900 dark:text-gray-50",
  border: "border-gray-200 dark:border-gray-700",
  input: "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800",
} as const