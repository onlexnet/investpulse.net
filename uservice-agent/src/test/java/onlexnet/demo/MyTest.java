package onlexnet.demo;

import java.util.concurrent.LinkedBlockingDeque;
import java.util.concurrent.TimeUnit;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Timeout.ThreadMode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

import io.grpc.Channel;
import io.grpc.stub.StreamObserver;
import lombok.SneakyThrows;
import onlexnet.agent.rpc.AgentGrpc;
import onlexnet.agent.rpc.BuyOne;
import onlexnet.agent.rpc.BuyOrder;
import onlexnet.agent.rpc.State;

@SpringBootTest(webEnvironment = WebEnvironment.NONE)
@Import(value = { ClientGrpc.class })
@ActiveProfiles(profiles = "test")
public class MyTest {

    @Autowired
    Channel daprChannel;

    @Autowired
    DaprConnection daprConnection;

    @Test
    @SneakyThrows
    void buy_order_without_amount() {
        var svc = AgentGrpc.newBlockingStub(daprChannel);

        var event = new onlexnet.pdt.bank.events.BankAccountStateChanged("app", 2_000d);
        daprConnection.publish(event);

        Thread.sleep(1_000);
        var state = svc.buy(newBuyOrder().build());

        Assertions.assertThat(state.getBudget()).isEqualTo(2_000);
    }

    // @Test
    // @Timeout(threadMode = ThreadMode.SEPARATE_THREAD, unit = TimeUnit.SECONDS,
    // value = 3)
    void buy_order_max() throws InterruptedException {
        var svc = AgentGrpc.newStub(daprChannel);
        var result = new LinkedBlockingDeque<State>();
        StreamObserver<State> observer = new StreamObserver<State>() {

            @Override
            public void onNext(State value) {
                result.add(value);
            }

            @Override
            public void onError(Throwable t) {
            }

            @Override
            public void onCompleted() {
            }
        };

        svc.buy(newBuyOrder()
                .setBuyOne(BuyOne.newBuilder().build())
                .build(), observer);

        Assertions.assertThat(result.take()).isNotNull();
    }

    static BuyOrder.Builder newBuyOrder() {
        return BuyOrder.newBuilder().setClientId("app");
    }
}
