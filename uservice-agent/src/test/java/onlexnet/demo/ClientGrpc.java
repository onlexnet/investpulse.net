package onlexnet.demo;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;

import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;

@TestConfiguration
public class ClientGrpc {

    @Value("${DAPR_GRPC_PORT}")
    int port;

    @Bean
    Channel daprChannel() {
        return ManagedChannelBuilder
                .forAddress("localhost", port)
                .usePlaintext()
                .intercept(GrpcUtils.addTargetDaprApplicationId("app"))
                .build();

    }
}
