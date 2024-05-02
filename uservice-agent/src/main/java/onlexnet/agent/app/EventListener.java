package onlexnet.agent.app;

public interface EventListener<E> {

    Class<E> getEventClass();

    void onEvent(E event);
}
