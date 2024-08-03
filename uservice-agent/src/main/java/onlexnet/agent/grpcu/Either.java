package onlexnet.agent.grpcu;

import org.springframework.util.Assert;

public record Either<S, F extends Throwable>(S success, F failure) {

    public Either {
        Assert.isTrue(success == null ^ failure == null,
                "Either can contain only success of failure. Not both, not none.");
    }

    public static <S> Either<S, ?> ofSuccess(S value) {
        return new Either<S, IllegalArgumentException>(value, null);
    }

    public static <F extends Throwable> Either<?, F> ofFailure(F value) {
        return new Either<Object, F>(null, value);
    }
}
