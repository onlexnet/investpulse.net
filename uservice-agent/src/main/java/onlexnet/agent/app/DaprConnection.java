package onlexnet.agent.app;

/**
 * Testable representation of DAPR component.
 */
public interface DaprConnection {

    <T> void publish(T event);
}
