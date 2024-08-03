package onlexnet.agent.domain;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

import io.grpc.stub.StreamObserver;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import onlexnet.agent.app.EventListener;
import onlexnet.agent.rpc.AgentGrpc;
import onlexnet.agent.rpc.BuyOrder;
import onlexnet.agent.rpc.State;
import onlexnet.pdt.bank.events.BankAccountStateChanged;

@Component
@RequiredArgsConstructor
class AgentService extends AgentGrpc.AgentImplBase
        implements EventListener<BankAccountStateChanged> {

    private final CommandBuy commandBuy = new CommandBuy();

    // TODO use DAPR KV storage instead of local Map
    private Map<Store.ClientKey, Store.ClientValue> state = new ConcurrentHashMap<>();

    @PostConstruct
    void init() {
        commandBuy.init();
    }

    @Override
    public void buy(BuyOrder request, StreamObserver<State> responseObserver) {
        commandBuy.command(request, responseObserver);
    }

    @Override
    public Class<BankAccountStateChanged> getEventClass() {
        return BankAccountStateChanged.class;
    }

    @Override
    public void onEvent(BankAccountStateChanged event) {
        var budget = event.getAccountState();
        var key = new Store.ClientKey().clientId("app");
        var value = new Store.ClientValue().budget(BigDecimal.valueOf(budget));
        state.put(key, value);
    }

}
