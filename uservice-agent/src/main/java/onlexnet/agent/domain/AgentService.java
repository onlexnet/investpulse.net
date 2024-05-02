package onlexnet.agent.domain;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

import io.grpc.stub.StreamObserver;
import jakarta.annotation.PostConstruct;
import lombok.Data;
import lombok.experimental.Accessors;
import onlexnet.agent.app.EventListener;
import onlexnet.agent.rpc.AgentGrpc;
import onlexnet.agent.rpc.BuyOrder;
import onlexnet.agent.rpc.State;
import onlexnet.pdt.bank.events.BankAccountStateChanged;

@Component
class AgentService extends AgentGrpc.AgentImplBase
        implements EventListener<onlexnet.pdt.bank.events.BankAccountStateChanged> {

    // TODO use DAPR KV storage instead of local Map
    private Map<Store.ClientKey, Store.ClientValue> state = new ConcurrentHashMap<>();

    @PostConstruct
    void init() {
        var key = new Store.ClientKey().clientId("app");
        var value = new Store.ClientValue().budget(BigDecimal.ZERO);
        state.put(key, value);
    }

    @Override
    public void buy(BuyOrder request, StreamObserver<State> responseObserver) {
        var clientId = request.getClientId();
        var clientKey = new Store.ClientKey().clientId(clientId);
        var clientValue = state.get(clientKey);
        var budget = clientValue.budget();
        var response = State.newBuilder().setBudget(budget.doubleValue()).build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
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

interface Store {
    @Data
    @Accessors(chain = true, fluent = true)
    class ClientKey {
        String clientId;
    }

    @Data
    @Accessors(chain = true, fluent = true)
    class ClientValue {
        BigDecimal budget = BigDecimal.ZERO;
        Map<Symbol, BuyOrder> buyOrders = new HashMap<>();
    }

    @Data
    @Accessors(chain = true, fluent = true)
    class BuyOrder {
        Symbol symbol;
        int amount;
    }

    @Data
    @Accessors(chain = true, fluent = true)
    class Symbol {
        String yahooTicker;
    }
}