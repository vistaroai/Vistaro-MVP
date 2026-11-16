import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * shadcn/ui class merge helper (identical to the one the shadcn CLI writes;
 * hand-seeded here so the review diff stays small and explicit).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}
