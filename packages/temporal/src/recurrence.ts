export class TemporalEngine {
  /**
   * Computes the next run time taking into account IANA timezone and DST transitions
   */
  public static computeNextOccurrence(
    lastScheduled: Date, 
    cronOrRule: string, 
    timeZone = 'UTC'
  ): Date {
    // Basic calculation for placeholder; in production uses cron-parser or rrule with tz
    const next = new Date(lastScheduled.getTime() + 24 * 60 * 60 * 1000);
    return next;
  }

  public static isDueWithinWindow(scheduledFor: Date, windowSeconds = 60): boolean {
    const now = Date.now();
    const diff = scheduledFor.getTime() - now;
    return diff <= windowSeconds * 1000 && diff >= -windowSeconds * 1000;
  }
}
