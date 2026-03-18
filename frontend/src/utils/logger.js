/**
 * Simple logger utility for consistent logging
 */
class Logger {
  constructor(componentName) {
    this.componentName = componentName;
  }

  /**
   * Log an informational message
   * @param {string} message - The message to log
   * @param {Object} [data] - Optional data to include
   */
  info(message, data) {
    console.info(`[${this.componentName}] ${message}`, data || '');
  }

  /**
   * Log a warning message
   * @param {string} message - The message to log
   * @param {Object} [data] - Optional data to include
   */
  warn(message, data) {
    console.warn(`[${this.componentName}] ${message}`, data || '');
  }

  /**
   * Log an error message
   * @param {string} message - The message to log
   * @param {Error|Object} [error] - The error object or data
   */
  error(message, error) {
    console.error(`[${this.componentName}] ${message}`, error || '');
  }
}

export default Logger;
