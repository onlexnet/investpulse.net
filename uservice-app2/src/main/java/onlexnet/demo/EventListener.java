package onlexnet.demo;

public interface EventListener<E> {
    
    Class<E> getEventClass();

    void onEvent(E event);
}
