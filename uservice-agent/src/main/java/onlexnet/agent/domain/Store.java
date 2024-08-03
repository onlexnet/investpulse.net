package onlexnet.agent.domain;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

import lombok.Data;
import lombok.experimental.Accessors;

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