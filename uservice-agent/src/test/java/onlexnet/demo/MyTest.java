package onlexnet.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;

import io.grpc.ManagedChannelBuilder;
import onlexnet.agent.rpc.BuyOrder;

@SpringBootTest(webEnvironment = WebEnvironment.NONE)
public class MyTest {

    @Autowired
    AppGrpcProperties props;

    @Test
    void test1() {
        var port = props.getServerPort();
        var a = ManagedChannelBuilder.forAddress("localhost", port).usePlaintext();
        var channel = a.build();
        var svc = onlexnet.agent.rpc.AgentGrpc.newBlockingStub(channel);
        svc.buy(BuyOrder.newBuilder().build());
    }
}
