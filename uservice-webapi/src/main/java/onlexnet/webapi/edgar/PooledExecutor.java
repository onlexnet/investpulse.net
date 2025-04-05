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

  @SneakyThrows
  // Fix with Try! InterruptedException, ExecutionException
  <R> R exec(Function<T, R> fn) {
    var result = new CompletableFuture<R>();
    Runnable futureCall = () -> { 
      try {
        var callResult = fn.apply(it);
        result.complete(callResult);
      } catch (Exception e) {
        result.completeExceptionally(e);
        return;
      }
    };
    calls.add(futureCall);
    return result.get();
  }


  private final Thread virtualThread = Thread.ofVirtual().unstarted(this::startAsyncInternal);

  public void startAsync() {
    virtualThread.start();
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
