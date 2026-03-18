/**
 * Custom logger utility for application-wide logging
 * In a production app, this would integrate with a monitoring service
 */

const LOG_LEVEL = process.env.REACT_APP_LOG_LEVEL || 'info';

const LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3
};

const getCurrentTimestamp = () => {
  return new Date().toISOString();
};

const shouldLog = (level) => {
  return LEVELS[level] >= LEVELS[LOG_LEVEL];
};

const formatLog = (level, message, ...args) => {
  const timestamp = getCurrentTimestamp();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

  if (args.length === 0) {
    return `${prefix} ${message}`;
  }

  return `${prefix} ${message}`;
};

const logger = {
  debug: (message, ...args) => {
    if (shouldLog('debug')) {
      console.debug(formatLog('debug', message), ...args);
    }
  },

  info: (message, ...args) => {
    if (shouldLog('info')) {
      console.info(formatLog('info', message), ...args);
    }
  },

  warn: (message, ...args) => {
    if (shouldLog('warn')) {
      console.warn(formatLog('warn', message), ...args);
    }
  },

  error: (message, ...args) => {
    if (shouldLog('error')) {
      console.error(formatLog('error', message), ...args);
    }
  },

  // Log application events (user actions, etc.)
  event: (eventName, data = {}) => {
    if (shouldLog('info')) {
      const eventData = { eventName, timestamp: new Date().toISOString(), ...data };
      console.info(formatLog('event', eventName), eventData);

      // In a real app, this might send to analytics or monitoring service
      // trackEvent(eventName, eventData);
    }
  }
};

export default logger;
