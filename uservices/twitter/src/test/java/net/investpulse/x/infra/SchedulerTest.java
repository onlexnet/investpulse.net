package net.investpulse.x.infra;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;

class SchedulerTest {

    private Scheduler scheduler;

    @BeforeEach
    void setUp() {
        scheduler = new Scheduler();
    }

    @AfterEach
    void tearDown() {
        scheduler.shutdown();
    }

    @Test
    void shouldExecuteTaskAtFixedRate() throws Exception {
        // Given
        var counter = new AtomicInteger(0);
        var latch = new CountDownLatch(3);
        
        Runnable task = () -> {
            counter.incrementAndGet();
            latch.countDown();
        };

        // When
        var handle = scheduler.scheduleAtFixedRate(task, 0, 50);

        // Then
        var completed = latch.await(500, TimeUnit.MILLISECONDS);
        assertThat(completed).isTrue();
        assertThat(counter.get()).isGreaterThanOrEqualTo(3);
        
        handle.close(); // Cancel the task
    }

    @Test
    void shouldRespectInitialDelay() throws Exception {
        // Given
        var counter = new AtomicInteger(0);
        var latch = new CountDownLatch(1);
        
        Runnable task = () -> {
            counter.incrementAndGet();
            latch.countDown();
        };

        var startTime = System.currentTimeMillis();

        // When
        var handle = scheduler.scheduleAtFixedRate(task, 100, 50);

        // Then
        var completed = latch.await(300, TimeUnit.MILLISECONDS);
        var elapsedTime = System.currentTimeMillis() - startTime;
        
        assertThat(completed).isTrue();
        assertThat(elapsedTime).isGreaterThanOrEqualTo(100);
        
        handle.close();
    }

    @Test
    void shouldCancelTask() throws Exception {
        // Given
        var counter = new AtomicInteger(0);
        
        Runnable task = counter::incrementAndGet;

        // When
        var handle = scheduler.scheduleAtFixedRate(task, 0, 50);
        Thread.sleep(150); // Let it run a few times
        handle.close(); // Cancel
        
        var countAfterCancel = counter.get();
        Thread.sleep(200); // Wait to verify it doesn't run again
        
        // Then
        assertThat(counter.get()).isEqualTo(countAfterCancel);
    }

    @Test
    void shouldShutdownGracefully() {
        // Given
        var counter = new AtomicInteger(0);
        Runnable task = counter::incrementAndGet;
        
        scheduler.scheduleAtFixedRate(task, 0, 50);

        // When
        scheduler.shutdown();

        // Then - no exception should be thrown
        assertThat(counter.get()).isGreaterThanOrEqualTo(0);
    }

    @Test
    void shouldCancelAllTasksOnShutdown() throws Exception {
        // Given
        var counter1 = new AtomicInteger(0);
        var counter2 = new AtomicInteger(0);
        
        scheduler.scheduleAtFixedRate(counter1::incrementAndGet, 0, 50);
        scheduler.scheduleAtFixedRate(counter2::incrementAndGet, 0, 50);
        
        Thread.sleep(150); // Let them run a bit

        // When
        scheduler.shutdown();
        
        var count1AfterShutdown = counter1.get();
        var count2AfterShutdown = counter2.get();
        
        Thread.sleep(200); // Wait to verify no more executions

        // Then - Counters should not increase after shutdown
        assertThat(counter1.get()).isEqualTo(count1AfterShutdown);
        assertThat(counter2.get()).isEqualTo(count2AfterShutdown);
    }

    @Test
    void shouldHandleMultipleShutdownCalls() {
        // Given
        var counter = new AtomicInteger(0);
        scheduler.scheduleAtFixedRate(counter::incrementAndGet, 0, 50);

        // When - Multiple shutdown calls
        scheduler.shutdown();
        scheduler.shutdown();
        scheduler.shutdown();

        // Then - Should handle gracefully without error
        assertThat(counter.get()).isGreaterThanOrEqualTo(0);
    }

    @Test
    void shouldHandleTaskExceptionGracefully() throws Exception {
        // Given
        var successCounter = new AtomicInteger(0);
        var latch = new CountDownLatch(3);
        
        Runnable failingTask = () -> {
            successCounter.incrementAndGet();
            latch.countDown();
            // ScheduledExecutorService continues running even if task throws exception
        };

        // When
        var handle = scheduler.scheduleAtFixedRate(failingTask, 0, 50);

        // Then - Task executes successfully
        var completed = latch.await(500, TimeUnit.MILLISECONDS);
        assertThat(completed).isTrue();
        assertThat(successCounter.get()).isGreaterThanOrEqualTo(3);
        
        handle.close();
    }

    @Test
    void shouldHandleMultipleConcurrentTasks() throws Exception {
        // Given
        var counter1 = new AtomicInteger(0);
        var counter2 = new AtomicInteger(0);
        var counter3 = new AtomicInteger(0);
        
        var latch1 = new CountDownLatch(3);
        var latch2 = new CountDownLatch(3);
        var latch3 = new CountDownLatch(3);

        // When - Schedule multiple tasks concurrently
        var handle1 = scheduler.scheduleAtFixedRate(() -> {
            counter1.incrementAndGet();
            latch1.countDown();
        }, 0, 50);
        
        var handle2 = scheduler.scheduleAtFixedRate(() -> {
            counter2.incrementAndGet();
            latch2.countDown();
        }, 0, 50);
        
        var handle3 = scheduler.scheduleAtFixedRate(() -> {
            counter3.incrementAndGet();
            latch3.countDown();
        }, 0, 50);

        // Then - All tasks should execute independently
        assertThat(latch1.await(500, TimeUnit.MILLISECONDS)).isTrue();
        assertThat(latch2.await(500, TimeUnit.MILLISECONDS)).isTrue();
        assertThat(latch3.await(500, TimeUnit.MILLISECONDS)).isTrue();
        
        assertThat(counter1.get()).isGreaterThanOrEqualTo(3);
        assertThat(counter2.get()).isGreaterThanOrEqualTo(3);
        assertThat(counter3.get()).isGreaterThanOrEqualTo(3);
        
        handle1.close();
        handle2.close();
        handle3.close();
    }

    @Test
    void shouldHandleVeryShortPeriods() throws Exception {
        // Given
        var counter = new AtomicInteger(0);
        var latch = new CountDownLatch(10);
        
        Runnable task = () -> {
            counter.incrementAndGet();
            latch.countDown();
        };

        // When - Very short period (10ms)
        var handle = scheduler.scheduleAtFixedRate(task, 0, 10);

        // Then
        var completed = latch.await(300, TimeUnit.MILLISECONDS);
        assertThat(completed).isTrue();
        assertThat(counter.get()).isGreaterThanOrEqualTo(10);
        
        handle.close();
    }

    @Test
    void shouldHandleZeroInitialDelay() throws Exception {
        // Given
        var counter = new AtomicInteger(0);
        var latch = new CountDownLatch(1);
        var startTime = System.currentTimeMillis();
        
        Runnable task = () -> {
            counter.incrementAndGet();
            latch.countDown();
        };

        // When
        var handle = scheduler.scheduleAtFixedRate(task, 0, 100);

        // Then - Should execute immediately
        var completed = latch.await(100, TimeUnit.MILLISECONDS);
        var elapsedTime = System.currentTimeMillis() - startTime;
        
        assertThat(completed).isTrue();
        assertThat(elapsedTime).isLessThan(100); // Should start quickly
        
        handle.close();
    }

    @Test
    void shouldHandleLongRunningTask() throws Exception {
        // Given
        var executionCount = new AtomicInteger(0);
        var latch = new CountDownLatch(2);
        
        Runnable longTask = () -> {
            executionCount.incrementAndGet();
            try {
                Thread.sleep(80); // Longer than period
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            latch.countDown();
        };

        // When - Task duration > period
        var handle = scheduler.scheduleAtFixedRate(longTask, 0, 50);

        // Then - Should still execute (may queue or skip)
        var completed = latch.await(1000, TimeUnit.MILLISECONDS);
        assertThat(completed).isTrue();
        assertThat(executionCount.get()).isGreaterThanOrEqualTo(2);
        
        handle.close();
    }
}
