package onlexnet.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;

import io.grpc.ManagedChannelBuilder;
import io.grpc.internal.GrpcUtil;
import onlexnet.agent.rpc.BuyOrder;

@SpringBootTest(webEnvironment = WebEnvironment.NONE)
public class MyTest {

    @Value("${DAPR_GRPC_PORT}")
    int port;

    @Test
    void test1() {
        var a = ManagedChannelBuilder.forAddress("localhost", port).usePlaintext();
        a = a.intercept(GrpcUtils.addTargetDaprApplicationId("app"));
        var channel = a.build();
        var svc = onlexnet.agent.rpc.AgentGrpc.newBlockingStub(channel);
        svc.buy(BuyOrder.newBuilder().build());
    }
}
