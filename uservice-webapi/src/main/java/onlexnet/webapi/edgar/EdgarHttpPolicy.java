package onlexnet.webapi.edgar;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

import lombok.extern.slf4j.Slf4j;

/** Used to be sure max throughput is 10 method runs per second. */
public class EdgarHttpPolicy {

  private final ReentrantLock lock = new ReentrantLock();
  private final List<LocalDateTime> lastRuns = new ArrayList<>(10);
  private final Duration oneSec = Duration.ofSeconds(1);
  
  public void submit(Runnable action) throws InterruptedException {
    lock.lock();
    try {
      var now = LocalDateTime.now();

      if (lastRuns.size() < 10) {
        lastRuns.add(now);
        action.run();
        return;
      }

      var theOlder = lastRuns.getFirst();
      var diff = Duration.between(now, theOlder.plus(oneSec));
      Thread.sleep(diff);
      lastRuns.removeFirst();
      var newNow = LocalDateTime.now();
      lastRuns.add(newNow);
      action.run();

      
    } finally {
      lock.unlock();
    }
    action.run();
  }
  
}
