package onlexnet.webapi.edgar;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Timeout.ThreadMode;

import lombok.SneakyThrows;

/**
 * More: https://www.sec.gov/about/privacy-information#security
 */
public class EdgarHttpPolicyTest {

  @Test
  @Timeout(threadMode = ThreadMode.SEPARATE_THREAD, unit = TimeUnit.SECONDS, value = 5)
  void shouldLimitTo10PerSecondCase10() throws InterruptedException {

    timed(Duration.ofMillis(0), Duration.ofMillis(100), () -> {
      var policy = new EdgarHttpPolicy();
      IntStream.rangeClosed(1, 10) // 10 requests
          .forEach(i -> {
            try {
              policy.submit(() -> { });
            } catch (InterruptedException e) {
              // TODO Auto-generated catch block
              e.printStackTrace();
            }
          });
    });
  }

  @Test
  void shouldLimitTo10PerSecondCase11() throws InterruptedException {

    timed(Duration.ofMillis(1000), Duration.ofMillis(1100), () -> {
      var policy = new EdgarHttpPolicy();
      IntStream.rangeClosed(1, 11) // 11 requests
          .forEach(i -> {
            try {
              policy.submit(() -> { });
            } catch (InterruptedException e) {
              // TODO Auto-generated catch block
              e.printStackTrace();
            }
          });

    });
  }

  @Test
  void shouldLimitTo10PerSecondCase21() throws InterruptedException {

    timed(Duration.ofMillis(2000), Duration.ofMillis(2100), () -> {
      var policy = new EdgarHttpPolicy();
      IntStream.rangeClosed(1, 21)
          .forEach(i -> {
            try {
              policy.submit(() -> { });
            } catch (InterruptedException e) {
              // TODO Auto-generated catch block
              e.printStackTrace();
            }
          });
    });
  }

  @SneakyThrows
  static void timed(Duration from, Duration to, ThrowingRunnable action) {
    var start = LocalDateTime.now();
    action.run();
    var end = LocalDateTime.now();
    var duration = Duration.between(start, end);
    if (duration.compareTo(from) < 0 || duration.compareTo(to) > 0) {
      throw new RuntimeException("Duration " + duration + " is not between " + from + " and " + to);
    }
  }
}

@FunctionalInterface
interface ThrowingRunnable {
  void run() throws Exception;
}
