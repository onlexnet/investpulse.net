package net.investpulse.configserver.bus;

import net.investpulse.configserver.ConfigServerStartupPublisher;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.cloud.stream.function.StreamBridge;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ConfigServerStartupPublisherTest {

    @Mock
    private StreamBridge streamBridge;

    @Mock
    private ApplicationReadyEvent applicationReadyEvent;

    private ConfigServerStartupPublisher publisher;

    @BeforeEach
    void setUp() {
        publisher = new ConfigServerStartupPublisher(streamBridge);
    }

    @Test
    void shouldPublishRefreshEventOnApplicationReady() {
        // Given
        when(streamBridge.send(anyString(), any())).thenReturn(true);

        // When
        publisher.publishStartupEvent();

        // Then
        verify(streamBridge).send(eq("springCloudBus-out-0"), any());
    }

    @Test
    void shouldPublishEventToCorrectBinding() {
        // Given
        when(streamBridge.send(anyString(), any())).thenReturn(true);

        // When
        publisher.publishStartupEvent();

        // Then
        verify(streamBridge).send(eq("springCloudBus-out-0"), any());
    }

    @Test
    void shouldPublishOnlyOncePerStartup() {
        // Given
        when(streamBridge.send(anyString(), any())).thenReturn(true);

        // When
        publisher.publishStartupEvent();

        // Then
        verify(streamBridge, times(1)).send(eq("springCloudBus-out-0"), any());
    }

    @Test
    void shouldHandleMultipleInvocations() {
        // Given
        when(streamBridge.send(anyString(), any())).thenReturn(true);

        // When - Call multiple times
        publisher.publishStartupEvent();
        publisher.publishStartupEvent();

        // Then - Should publish twice (once per call)
        verify(streamBridge, times(2)).send(eq("springCloudBus-out-0"), any());
    }

    @Test
    void shouldNotThrowExceptionWhenPublishingEvent() {
        // Given
        when(streamBridge.send(anyString(), any())).thenReturn(true);

        // When/Then - Should not throw
        publisher.publishStartupEvent();
        
        verify(streamBridge).send(eq("springCloudBus-out-0"), any());
    }

    @Test
    void shouldHandleFailedSend() {
        // Given
        when(streamBridge.send(anyString(), any())).thenReturn(false);

        // When/Then - Should not throw but log error
        publisher.publishStartupEvent();
        
        verify(streamBridge).send(eq("springCloudBus-out-0"), any());
    }
}
