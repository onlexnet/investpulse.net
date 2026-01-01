package net.investpulse.x.infra;

import lombok.extern.slf4j.Slf4j;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Lightweight scheduler for executing tasks at fixed intervals.
 * Uses Java's ScheduledExecutorService with a single-threaded pool.
 */
@Slf4j
public class Scheduler {
    
    private static final int THREAD_POOL_SIZE = 1;
    
    private final ScheduledExecutorService executorService;
    
    public Scheduler() {
        this.executorService = Executors.newScheduledThreadPool(THREAD_POOL_SIZE);
    }
    
    /**
     * Schedules a task to execute at fixed intervals.
     * 
     * @param task the task to execute
     * @param initialDelayMs initial delay before first execution in milliseconds
     * @param periodMs period between successive executions in milliseconds
     * @return AutoCloseable handle to cancel the scheduled task
     */
    public AutoCloseable scheduleAtFixedRate(Runnable task, long initialDelayMs, long periodMs) {
        log.debug("Scheduling task with initial delay: {}ms, period: {}ms", initialDelayMs, periodMs);
        
        var scheduledFuture = executorService.scheduleAtFixedRate(
            task,
            initialDelayMs,
            periodMs,
            TimeUnit.MILLISECONDS
        );
        
        return () -> {
            log.debug("Cancelling scheduled task");
            scheduledFuture.cancel(false);
        };
    }
    
    /**
     * Shuts down the scheduler and awaits termination.
     * Should be called when the scheduler is no longer needed.
     */
    public void shutdown() {
        log.info("Shutting down scheduler");
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                log.warn("Executor did not terminate in time, forcing shutdown");
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("Interrupted while waiting for executor shutdown", e);
            executorService.shutdownNow();
        }
    }
}
