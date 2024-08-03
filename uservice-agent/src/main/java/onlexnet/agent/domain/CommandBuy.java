package onlexnet.agent.domain;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import jakarta.annotation.PostConstruct;
import onlexnet.agent.grpcu.Either;
import onlexnet.agent.grpcu.RpcCommandHandler;
import onlexnet.agent.rpc.BuyOrder;
import onlexnet.agent.rpc.State;

final class CommandBuy implements RpcCommandHandler<BuyOrder, State> {

    // TODO use DAPR KV storage instead of local Map
    private Map<Store.ClientKey, Store.ClientValue> state = new ConcurrentHashMap<>();

    void init() {
        var key = new Store.ClientKey().clientId("app");
        var value = new Store.ClientValue().budget(BigDecimal.ZERO);
        state.put(key, value);
    }

    @Override
    public Either<State, ? extends Throwable> apply(BuyOrder cmd) {
        var clientId = cmd.getClientId();
        var clientKey = new Store.ClientKey().clientId(clientId);
        var clientValue = state.get(clientKey);
        var budget = clientValue.budget();
        var response = State.newBuilder().setBudget(budget.doubleValue()).build();
        return Either.ofSuccess(response);
    }
}
