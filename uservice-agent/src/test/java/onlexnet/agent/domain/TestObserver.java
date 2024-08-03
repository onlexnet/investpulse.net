package onlexnet.agent.domain;

import java.util.concurrent.LinkedBlockingQueue;

import io.grpc.stub.StreamObserver;
import lombok.Getter;

public final class TestObserver<T> implements StreamObserver<T> {

    @Getter
    private final LinkedBlockingQueue<T> items = new LinkedBlockingQueue<>();

    @Override
    public void onNext(T value) {
        items.add(value);
    }

    @Override
    public void onError(Throwable t) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'onError'");
    }

    @Override
    public void onCompleted() {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'onCompleted'");
    }

}
