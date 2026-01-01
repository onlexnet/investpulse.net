package net.investpulse.configserver.bus;

import net.investpulse.configserver.ConfigServerStartupPublisher;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.cloud.bus.event.RefreshRemoteApplicationEvent;
import org.springframework.context.ApplicationEventPublisher;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ConfigServerStartupPublisherTest {

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @Mock
    private ApplicationReadyEvent applicationReadyEvent;

    @Captor
    private ArgumentCaptor<RefreshRemoteApplicationEvent> eventCaptor;

    private ConfigServerStartupPublisher publisher;

    @BeforeEach
    void setUp() {
        publisher = new ConfigServerStartupPublisher(eventPublisher);
    }

    @Test
    void shouldPublishRefreshEventOnApplicationReady() {
        // When
        publisher.publishStartupEvent();

        // Then
        verify(eventPublisher).publishEvent(eventCaptor.capture());
        
        var publishedEvent = eventCaptor.getValue();
        assertThat(publishedEvent).isNotNull();
    }

    @Test
    void shouldPublishEventWithCorrectOriginService() {
        // When
        publisher.publishStartupEvent();

        // Then
        verify(eventPublisher).publishEvent(eventCaptor.capture());
        
        var publishedEvent = eventCaptor.getValue();
        assertThat(publishedEvent.getOriginService()).isEqualTo("config-server");
    }

    @Test
    void shouldPublishEventWithWildcardDestination() {
        // When
        publisher.publishStartupEvent();

        // Then
        verify(eventPublisher).publishEvent(eventCaptor.capture());
        
        var publishedEvent = eventCaptor.getValue();
        assertThat(publishedEvent.getDestinationService()).isEqualTo("**");
    }

    @Test
    void shouldPublishOnlyOncePerStartup() {
        // When
        publisher.publishStartupEvent();

        // Then
        verify(eventPublisher, times(1)).publishEvent(any(RefreshRemoteApplicationEvent.class));
    }

    @Test
    void shouldHandleMultipleInvocations() {
        // When - Call multiple times (unusual but should be safe)
        publisher.publishStartupEvent();
        publisher.publishStartupEvent();

        // Then - Should publish twice (once per call)
        verify(eventPublisher, times(2)).publishEvent(any(RefreshRemoteApplicationEvent.class));
    }

    @Test
    void shouldPublishEventWithPublisherAsSource() {
        // When
        publisher.publishStartupEvent();

        // Then
        verify(eventPublisher).publishEvent(eventCaptor.capture());
        
        var publishedEvent = eventCaptor.getValue();
        assertThat(publishedEvent.getSource()).isEqualTo(publisher);
    }

    @Test
    void shouldNotThrowExceptionWhenPublishingEvent() {
        // When/Then - Should not throw
        publisher.publishStartupEvent();
        
        verify(eventPublisher).publishEvent(any(RefreshRemoteApplicationEvent.class));
    }

    @Test
    void shouldHandleEventPublisherException() {
        // Given
        doThrow(new RuntimeException("Event publishing failed"))
                .when(eventPublisher).publishEvent(any(RefreshRemoteApplicationEvent.class));

        // When/Then - Exception should propagate
        try {
            publisher.publishStartupEvent();
        } catch (RuntimeException e) {
            assertThat(e.getMessage()).contains("Event publishing failed");
        }

        verify(eventPublisher).publishEvent(any(RefreshRemoteApplicationEvent.class));
    }
}
