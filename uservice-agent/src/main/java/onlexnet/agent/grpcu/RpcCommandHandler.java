package onlexnet.agent.grpcu;

import com.google.protobuf.GeneratedMessageV3;

import io.grpc.stub.StreamObserver;

/**
 * Designed to be extended by all Command rpc operations.
 *
 * @param <Q> - request type
 * @param <S> - response type
 */
public interface RpcCommandHandler<Q extends GeneratedMessageV3, S extends GeneratedMessageV3> {

    /***
     * PLease override such behavior. It will be inoked automatically thanks to
     * 'command' method.
     */
    Either<S, ? extends Throwable> apply(Q cmd);

    /**
     * Executes the command and sends the result to the client.
     *
     * @param request        - the request
     * @param responseStream - the response stream
     */
    default void command(Q request, StreamObserver<S> responseStream) {
        var result = this.apply(request);
        if (result.success() != null) {
            responseStream.onNext(result.success());
        } else {
            responseStream.onError(result.failure());
        }
        responseStream.onCompleted();
    }
}
