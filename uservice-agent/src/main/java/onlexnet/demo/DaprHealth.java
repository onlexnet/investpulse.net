package onlexnet.demo;

import org.springframework.stereotype.Component;

import com.google.protobuf.Empty;

import io.dapr.v1.AppCallbackHealthCheckGrpc.AppCallbackHealthCheckImplBase;
import io.dapr.v1.DaprAppCallbackProtos.HealthCheckResponse;
import io.grpc.stub.StreamObserver;

@Component
public class DaprHealth extends AppCallbackHealthCheckImplBase {

    @Override
    public void healthCheck(Empty request, StreamObserver<HealthCheckResponse> responseObserver) {
        responseObserver.onNext(HealthCheckResponse.newBuilder().build());
        // responseObserver.onCompleted();
    }
}
