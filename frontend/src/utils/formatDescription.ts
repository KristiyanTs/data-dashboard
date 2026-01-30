/**
 * Inserts newlines before section labels (e.g. "TITLE:", "DESCRIPTION:", "CONTRACT PERIOD:")
 * so scraped contract descriptions display with clear structure in the modal.
 */
export function formatDescriptionText(raw: string): string {
  if (!raw || typeof raw !== 'string') return raw;
  return raw
    /* After a period, break before next section label */
    .replace(/\. ([A-Z][A-Za-z/ ]+): /g, '.\n\n$1: ')
    /* Break before label when preceded by space (e.g. "value Overall BUYER:") - only for known section-style labels */
    .replace(/\s+(TITLE|DESCRIPTION|CONTRACT PERIOD|Overall BUYER|ITEMS\/REQUIREMENTS|ESTIMATED VALUE): /g, '\n\n$1: ')
    .replace(/\n\n+/g, '\n\n')
    .trim();
}
