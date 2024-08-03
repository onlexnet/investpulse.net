package onlexnet.agent.domain;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.modulith.test.ApplicationModuleTest;
import org.springframework.modulith.test.Scenario;

import onlexnet.agent.rpc.BuyOrder;
import onlexnet.agent.rpc.State;

@ApplicationModuleTest
public class ModuleTest {

    @Autowired
    AgentService agentService;

    @Test
    void nothingYet(Scenario scenario) {
        var observer = new TestObserver<State>();
        scenario.stimulate(() -> {
            var order = BuyOrder.newBuilder().build();
            agentService.buy(order, observer);
        })
    }
}
