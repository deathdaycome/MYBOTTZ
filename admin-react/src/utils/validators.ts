/**
 * Validation utilities
 */

export const validators = {
  email: (email: string): boolean => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  },

  phone: (phone: string): boolean => {
    const re = /^[\+]?[1-9][\d]{0,15}$/
    return re.test(phone.replace(/\s+/g, ''))
  },

  url: (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  },

  required: (value: any): boolean => {
    return value !== null && value !== undefined && value.toString().trim() !== ''
  },

  minLength: (value: string, min: number): boolean => {
    return value && value.length >= min
  },

  maxLength: (value: string, max: number): boolean => {
    return value && value.length <= max
  },

  numeric: (value: string | number): boolean => {
    return !isNaN(Number(value)) && !isNaN(parseFloat(String(value)))
  },

  integer: (value: string | number): boolean => {
    return Number.isInteger(Number(value))
  },

  positive: (value: string | number): boolean => {
    return Number(value) > 0
  },
}

export default validators
