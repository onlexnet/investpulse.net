package onlexnet.webapi.edgar;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Function;

import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;

/** Allows to limit invocation of subject methods based on internal policy. */
@RequiredArgsConstructor
public class PooledExecutor<T> implements AutoCloseable {

  private final LinkedBlockingQueue<Runnable> calls = new LinkedBlockingQueue<>(10);
  private final T it;
  private final EdgarHttpPolicy policy;

  @SneakyThrows
  // Fix with Try! InterruptedException, ExecutionException
  <R> R exec(Function<T, R> fn) {
    var result = new CompletableFuture<R>();
    Runnable futureCall = () -> {
      try {
        policy.submit(() -> {
          var callResult = fn.apply(it);
          result.complete(callResult);
        });
      } catch (Exception e) {
        result.completeExceptionally(e);
        return;
      }
    };
    calls.add(futureCall);
    return result.get();
  }

  private final Thread virtualThread = Thread.ofVirtual().unstarted(this::startAsyncInternal);

  public interface Run {
    <T, R> R exec(Function<T, R> fn);
  }

  public Run startAsync() {
    virtualThread.start();
    return fn -> this.exec(fn);
  }

  public void startAsyncInternal() {
    while (true) {
      try {
        var call = calls.take();
        call.run();
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        return;
      }
    }
  }

  @Override
  @SneakyThrows
  public void close() {
    virtualThread.interrupt();
    virtualThread.join();
  }

}
