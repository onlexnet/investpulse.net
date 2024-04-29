package onlexnet.demo;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

import io.grpc.BindableService;
import io.grpc.stub.StreamObserver;
import lombok.Data;
import lombok.experimental.Accessors;
import onlexnet.agent.rpc.AgentGrpc;
import onlexnet.agent.rpc.BuyOrder;
import onlexnet.agent.rpc.State;

@Component
class AgentGrpcApi extends AgentGrpc.AgentImplBase {

    // TODO use DAPR KV storage
    private Map<Store.ClientKey, Store.ClientValue> state = new ConcurrentHashMap<>();

    @Override
    public void buy(BuyOrder request, StreamObserver<State> responseObserver) {
        var value = State.newBuilder().build();
        responseObserver.onNext(value);
        responseObserver.onCompleted();
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